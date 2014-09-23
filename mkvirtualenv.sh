#!/usr/bin/env bash

#
# Creates python environment for building site, assuming virtualenv is already available
# No need to create this environment when using Travis for deployment
#

# Create virtualenv in ./env
virtualenv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies via pip
pip install -U -r requirements.txt 
