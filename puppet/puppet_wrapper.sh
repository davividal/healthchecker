#!/bin/bash

cd puppet

if [ $1 = "shutdown" ]; then
	sed -ri 's/(setuphosts::ensure: )present/\1absent/' common.yaml
fi

puppet apply --hiera_config hiera.yaml site.pp > /dev/null 2>&1

if [ $1 = "shutdown" ]; then
	sed -ri 's/(setuphosts::ensure: )absent/\1present/' common.yaml
fi

cd - > /dev/null 2>&1
