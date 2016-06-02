from termcolor import colored
import http.client
import socket
import yaml


class ExpectationFailedError(Exception):
    pass


class Rule(object):
    url = None
    expected_status = None
    expected_target = None
    method = 'GET'
    request = '/'

    def __init__(self, url=None, expected_status=None, expected_target=None, method='GET', request='/'):
        if expected_status in (http.client.MOVED_PERMANENTLY, http.client.FOUND):
            if not expected_target:
                raise TypeError('If you expect a redirect, specify where to.')

        if not url:
            raise TypeError('You must specify the URL')

        if not expected_status:
            raise TypeError('You must specify the expected HTTP status')

        self.url = url
        self.expected_status = expected_status
        self.expected_target = expected_target
        self.method = method
        self.request = request

    def __str__(self):
        return self.url + self.request

    def __format__(self, format_spec):
        return str(self)[:25].__format__(format_spec)

    def check(self):
        conn = http.client.HTTPConnection(self.url, timeout=5)

        try:
            conn.request(self.method, self.request)
        except socket.error as e:
            raise ExpectationFailedError(
                'Socket error: {0}'.format(colored(e, 'red'))
            )
        response = conn.getresponse()

        if not response.status == self.expected_status:
            raise ExpectationFailedError(
                'Expected: {0}. Got: {1}'.format(
                    colored(self.expected_status, 'green'),
                    colored(response.status, 'red')
                )
            )

        if self.expected_status in (http.client.MOVED_PERMANENTLY, http.client.FOUND):
            if not response.getheader('location') == self.expected_target:
                raise ExpectationFailedError(
                    'Expected: {0}. Got: {1}'.format(
                        colored(self.expected_target, 'green'),
                        colored(response.getheader('location'), 'red')
                    )
                )

        return True


class YamlRules(object):
    hosts = []
    rule_file = None

    def get_rules(self):
        f = open('rules.d/' + self.rule_file)
        self.rule_yaml = yaml.safe_load(f)
        f.close

        self.elb = self.rule_yaml['elb']

        for rule in self.rule_yaml['rules']:
            self.rules.append(Rule(**rule))

    def get_hosts(self):
        if len(self.hosts) == 0:
            hosts = []
            for rule in self.rule_yaml['rules']:
                hosts.append(rule['url'])
                self.hosts = sorted(list(set(hosts)))
        return self.hosts
