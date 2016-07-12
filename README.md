Health Checker
==============

Simple python script to check some rules against a bunch of AWS EC2 instances behind an Amazon ELB.

virtualenvwrapper friendly.

Work in progress.

How to use:

1. Clone this repo
	```
	$ git clone http://github.com/davividal/healthchecker && cd healthchecker
	```
1. Install its dependencies
	```
	$ pip install -r requirements.txt
	```

1. Add to your sudoers:
	```bash
	cat <<EOF | sudo tee /etc/sudoers.d/healthchecker
	$USERNAME  ALL=(ALL) NOPASSWD: $PWD/puppet/puppet_wrapper.sh
	EOF
	```

1. Define your rules at `rules.d/your_awesome_rules.yaml`

1. Execute it:
	```
	$ python healthchecker.py [your_awesome_rules]
	```
