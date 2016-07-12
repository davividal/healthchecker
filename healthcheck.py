#!/usr/bin/env python3
from checker import Checker, AwsElbChecker

import os
import sys


if __name__ == '__main__':
    rule_filter = []

    run = list(filter(lambda r: r.endswith('.yaml'), os.listdir('rules.d')))

    for app in sys.argv[1:]:
        rule_filter.append(app)
        run = list(filter(lambda r: r.split('.')[0] in rule_filter, run))

    for rule in run:
        checker = Checker(AwsElbChecker(rule))
        checker.run()
