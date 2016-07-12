from termcolor import colored
import requests


class ExpectationFailedError(Exception):
    pass


class Rule(object):
    url = None
    expected_status = None
    expected_target = None
    user_agent = 'Python HealthChecker - github.com/davividal/healthchecker'
    method = 'GET'
    request = '/'
    schema = 'http'
    custom_headers = {}

    def __init__(self, url=None, expected_status=None, expected_target=None, method='GET', request='/', user_agent=None, schema=None):
        if expected_status in (requests.codes.moved_permanently, requests.codes.found):
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
        self.custom_headers['User-Agent'] = user_agent or self.user_agent
        self.schema = schema or self.schema

    def __str__(self):
        return self.schema + '://' + self.url + self.request

    def __format__(self, format_spec):
        return str(self)[:25].__format__(format_spec)

    def add_header(self, header, content):
        self.custom_headers[header] = content

    def check(self):
        try:
            response = getattr(requests, self.method.lower())(
                str(self),
                params={},
                headers=self.custom_headers,
                timeout=5,
                verify=False
            )
        except requests.exceptions.RequestException as e:
            raise ExpectationFailedError(
                'Request error: {0}'.format(colored(e, 'red'))
            )

        if not response.status_code == self.expected_status:
            if len(response.history) > 0 and response.history[0].status_code == self.expected_status:
                self.check_redirect(response)
            else:
                raise ExpectationFailedError(
                    'Expected: {0}. Got: {1} {2}'.format(
                        colored(self.expected_status, 'green'),
                        colored(response.status_code, 'red'),
                        str(self)
                    )
                )

        return True

    def check_redirect(self, response):
        if self.expected_status in (requests.codes.moved_permanently, requests.codes.found):
            if not response.url == self.expected_target:
                raise ExpectationFailedError(
                    'Expected: {0}. Got: {1}'.format(
                        colored(self.expected_target, 'green'),
                        colored(response.url, 'red')
                    )
                )
