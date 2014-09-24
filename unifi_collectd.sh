#!/bin/bash


cd "$(dirname ${BASH_SOURCE[0]} )"
source "venv/bin/activate"


python unifi_collectd.py $* 
