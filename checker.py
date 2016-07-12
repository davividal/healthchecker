from amazon import get_instances, get_instance_ip
from termcolor import colored

import os
from rules import Rule, ExpectationFailedError
import yaml


class Settings(object):
    def setup(self):
        raise NotImplementedError

    def pre_test(self, *args, **kwargs):
        raise NotImplementedError


class PuppetConf(Settings):
    puppet_common = 'puppet/common.yaml'
    puppet_yml = None

    def setup(self):
        f = open(self.puppet_common)
        self.puppet_yml = yaml.safe_load(f)
        f.close()

    def pre_test(self, ip, hosts):
        print('{:<45}'.format('Changing IP locally... '), end='', flush=True)

        self.puppet_yml['setuphosts::ip'] = ip
        self.puppet_yml['setuphosts::hostname'] = hosts[0]
        self.puppet_yml['setuphosts::host_aliases'] = hosts[1:]

        f = open(self.puppet_common, 'w')
        yaml.dump(self.puppet_yml, f, explicit_start=True)
        f.close()

        ret = os.system('sudo puppet/puppet_wrapper.sh')

        if ret == 0:
            print("{:>28}".format(colored('[ OK ]', 'green')))
        else:
            print("{:>20}".format(colored('[FAIL]', 'red')))
            raise RuntimeError('Puppet not found')

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
    rule_repository = None

    def __init__(self, rule_repository, settings=PuppetConf()):
        self.settings = settings
        self.rule_repository = rule_repository

    def run(self):
        self.setup()

        try:
            self.test()
        except RuntimeError as e:
            print("An error occurred: " + e.args[0])
        finally:
            self.shutdown()

    def setup(self):
        self.settings.setup()
        self.rule_repository.setup()

    def shutdown(self):
        self.rule_repository.shutdown()
        self.settings.shutdown()

    def test(self):
        for instance in self.rule_repository.get_instances():
            instance_ip = self.rule_repository.get_instance_ip(instance)
            print("Testing instance {0}, IP: {1}".format(
                colored(instance, 'yellow'),
                colored(instance_ip, 'yellow'))
            )
            self.settings.pre_test(instance_ip, self.rule_repository.get_hosts())

            self.rule_repository.check()


class RuleRepository(object):
    rules = []
    hosts = []
    instances = []
    rule_yaml = None
    rule_file = None
    name = None

    def setup(self):
        self.setup_rules()
        self.setup_app_name()
        self.get_hosts()
        self.get_instances()

        print("App: {0}, Instances: {1}".format(self.name, len(self.instances)))

    def check(self):
        for rule in self.rules:
            error = None
            print("{0:<45}".format(rule), end='', flush=True)

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

            print("{:>28}".format(msg))
            if error:
                print(error)

    def setup_rules(self):
        raise NotImplementedError

    def setup_app_name(self):
        raise NotImplementedError

    def get_hosts(self):
        raise NotImplementedError

    def get_instances(self):
        raise NotImplementedError

    def shutdown(self):
        pass


class YamlRules(RuleRepository):
    def __init__(self, rule_name):
        self.rule_file = 'rules.d/' + rule_name

    def setup_rules(self):
        self.rules = []

        f = open(self.rule_file)
        self.rule_yaml = yaml.safe_load(f)
        f.close()

        for rule in self.rule_yaml['rules']:
            r = Rule(**rule)

            for custom_header in self.rule_yaml['custom_headers']:
                header, content = list(custom_header.items())[0]
                r.add_header(header, content)
            self.rules.append(r)

    def setup_app_name(self):
        self.name = self.rule_yaml['name']

    def get_hosts(self):
        if len(self.hosts) == 0:
            hosts = []
            for rule in self.rule_yaml['rules']:
                hosts.append(rule['url'])
                self.hosts = sorted(list(set(hosts)))
        return self.hosts

    def get_instances(self):
        raise NotImplementedError


class AwsElbChecker(YamlRules):
    def get_region_name(self):
        return self.rule_yaml['region_name']

    def get_elb_name(self):
        return self.rule_yaml['elb']

    def get_instances(self):
        if len(self.instances) == 0:
            self.instances = get_instances(self.get_elb_name(), self.get_region_name())
        return self.instances

    def get_instance_ip(self, instance_id):
        return get_instance_ip(instance_id, self.get_region_name())
