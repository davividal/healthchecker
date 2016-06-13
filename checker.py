from amazon import get_instances, get_instance_ip
from termcolor import colored

import os
from rules import Rule, ExpectationFailedError
import yaml


class Configer(object):
    def setup(self):
        raise NotImplementedError

    def pre_test(self, *args, **kwargs):
        raise NotImplementedError


class PuppetConf(Configer):
    puppet_common = 'puppet/common.yaml'
    puppet_yml = None

    def setup(self):
        f = open(self.puppet_common)
        self.puppet_yml = yaml.safe_load(f)
        f.close()

    def pre_test(self, ip, hosts):
        print('{:<25}'.format('Changing IP locally... '), end='', flush=True)

        self.puppet_yml['setuphosts::ip'] = ip
        self.puppet_yml['setuphosts::hostname'] = hosts[0]
        self.puppet_yml['setuphosts::host_aliases'] = hosts[1:]

        f = open(self.puppet_common, 'w')
        yaml.dump(self.puppet_yml, f, explicit_start=True)
        f.close()

        os.system('sudo puppet/puppet_wrapper.sh')

        print("{:>8}".format(colored('[ OK ]', 'green')))

    @staticmethod
    def shutdown():
        os.system('sudo puppet/puppet_wrapper.sh shutdown')


class Checker(object):
    name = None
    rule_yaml = None
    hosts = []
    rules = []
    elb = None
    instances = []

    def __init__(self, configer=PuppetConf()):
        self.configer = configer

        self.configer.setup()

        self.get_rules()
        self.get_app_name()
        self.get_hosts()
        self.get_instances()
        self.test()

        self.configer.shutdown()

    def get_rules(self):
        raise NotImplementedError

    def get_app_name(self):
        raise NotImplementedError

    def get_instances(self):
        raise NotImplementedError

    def get_hosts(self):
        raise NotImplementedError

    def test(self):
        print("App: {0}, Instances: {1}".format(self.name, len(self.instances)))
        for instance_id in self.instances:
            instance_ip = get_instance_ip(instance_id)
            print("Testing instance {0}, IP: {1}".format(
                colored(instance_id, 'yellow'),
                colored(instance_ip, 'yellow'))
            )

            self.configer.pre_test(instance_ip, self.hosts)

            self.check()

    def check(self):
        for rule in self.rules:
            error = None
            print("{0:<25}".format(rule), end='', flush=True)

            try:
                check = rule.check()
            except ExpectationFailedError as e:
                msg = colored('[FAIL]', 'red')
                error = e
            else:
                if check:
                    msg = colored('[ OK ]', 'green')
                else:
                    msg = colored('[WARN]', 'yellow')

            print("{:>8}".format(msg))
            if error:
                print(error)


class YamlRules(Checker):
    hosts = []

    rule_file = None

    def get_instances(self):
        raise NotImplementedError

    def get_rules(self):
        self.rules = []

        f = open('rules.d/' + self.rule_file)
        self.rule_yaml = yaml.safe_load(f)
        f.close()

        self.elb = self.rule_yaml['elb']

        for rule in self.rule_yaml['rules']:
            self.rules.append(Rule(**rule))

    def get_app_name(self):
        self.name = self.rule_yaml['name']

    def get_hosts(self):
        if len(self.hosts) == 0:
            hosts = []
            for rule in self.rule_yaml['rules']:
                hosts.append(rule['url'])
                self.hosts = sorted(list(set(hosts)))
        return self.hosts


class AwsElbChecker(YamlRules):
    def get_instances(self):
        self.instances = get_instances(self.elb)
