#!/bin/bash

cd puppet
puppet apply --hiera_config hiera.yaml site.pp > /dev/null 2>&1
cd - > /dev/null 2>&1
