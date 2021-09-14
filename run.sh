#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

whoami
cd $DIR
/usr/local/bin/python3 zillow.py
