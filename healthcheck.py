#!/usr/bin/env python3
from checker import AwsElbChecker

import sys


class SiteChecker(AwsElbChecker):
    rule_file = 'site.yaml'


class BlogChecker(AwsElbChecker):
    rule_file = 'blog.yaml'


class AlugueCarroChecker(AwsElbChecker):
    rule_file = 'aluguecarro.yaml'


class_lookup = {
    'site': SiteChecker,
    'blog': BlogChecker,
    'alugue': AlugueCarroChecker
}

if __name__ == '__main__':
    run = []

    for app in sys.argv[1:]:
        run.append(app)
    run = sorted(list(set(run)))

    if not bool(set(run)):
        run = ['site', 'blog', 'alugue']

    for app in run:
        class_lookup[app]()