#!/bin/bash

PATH=/opt/puppetlabs/bin:$PATH

which puppet > /dev/null 2>&1
if [ $? -ne 0 ]; then
     exit 1
fi

cd puppet

if [ ! -z "$1" ]; then
	if [ $1 = "shutdown" ]; then
		sed -ri 's/(setuphosts::ensure: )present/\1absent/' common.yaml
	fi
fi

puppet apply --hiera_config hiera.yaml site.pp > /dev/null 2>&1

if [ ! -z "$1" ]; then
	if [ $1 = "shutdown" ]; then
		sed -ri 's/(setuphosts::ensure: )absent/\1present/' common.yaml
	fi
fi

cd - > /dev/null 2>&1
