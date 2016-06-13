#!/usr/bin/env python3

from checker import AwsElbChecker


class SiteChecker(AwsElbChecker):
    rule_file = 'site.yaml'


class BlogChecker(AwsElbChecker):
	rule_file = 'blog.yaml'


if __name__ == '__main__':
    SiteChecker()
    BlogChecker()
