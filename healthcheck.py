#!/usr/bin/env python3
from checker import Checker, AwsElbChecker

import os
import sys


if __name__ == '__main__':
    run = []

    for app in sys.argv[1:]:
        run.append(app)
    run = sorted(list(set(run)))

    if not bool(set(run)):
        run = list(filter(lambda r: r.endswith('.yaml'), os.listdir('rules.d')))

    for rule in run:
        checker = Checker(AwsElbChecker(rule))
        checker.run()
