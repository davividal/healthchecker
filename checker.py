from __future__ import print_function

from amazon import get_instances, get_instance_ip
from termcolor import colored, cprint

import os
import yaml


class Configer(object):
    def setup(self):
        raise NotImplementedError

    def pre_test(self, *args, **kwargs):
        raise NotImplementedError


class PuppetConf(object):
    puppet_common = 'puppet/common.yaml'

    def setup(self):
        f = open(self.puppet_common)
        self.puppet_yml = yaml.safe_load(f)
        f.close()

    def pre_test(self, ip, hosts):
        print('{:<25}'.format('Changing IP locally... '), end='')

        self.puppet_yml['setuphosts::ip'] = ip
        self.puppet_yml['setuphosts::hostname'] = hosts[0]
        self.puppet_yml['setuphosts::host_aliases'] = hosts[1:]

        root = os.getcwd()

        f = open(self.puppet_common, 'w')
        yaml.dump(self.puppet_yml, f, explicit_start=True)
        f.close()

        os.chdir('puppet')
        os.system('sudo puppet apply --hiera_config hiera.yaml site.pp > /dev/null 2>&1')
        os.chdir(root)

        print("{:>8}".format(colored('[ OK ]', 'green')))


class Checker(object):
    rule_yaml = None
    hosts = []
    rules = []
    elb = None

    def __init__(self, configer=PuppetConf()):
        self.configer = configer

        self.configer.setup()
        self.get_rules()
        self.get_hosts()
        self.get_instances()
        self.test()

    def get_instances(self):
        raise NotImplementedError

    def get_rules(self):
        raise NotImplementedError

    def get_hosts(self):
        raise NotImplementedError

    def check(self):
        for rule in self.rules:
            error = None
            print("{:<25}".format(rule.url), end='')

            try:
                check = rule.check()
            except rules.ExpectationFailedError, e:
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

    def test(self):
        for instance_id in self.instances:
            instance_ip = get_instance_ip(instance_id)
            print("Testing instance {0}, IP: {1}".format(
                colored(instance_id, 'yellow'),
                colored(instance_ip, 'yellow'))
            )

            self.configer.pre_test(instance_ip, self.hosts)

            self.check()

