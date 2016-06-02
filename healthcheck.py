from amazon import get_instances

import checker
import rules


class SiteChecker(rules.YamlRules, checker.Checker):
    rule_file = 'site.yaml'

    def get_instances(self):
        self.instances = get_instances(self.elb)


if __name__ == '__main__':
    SiteChecker()
