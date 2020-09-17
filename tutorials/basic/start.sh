#!/bin/bash

bash ./chrome_setup.sh > /dev/null 2>&1
bash ./bootstrap.sh > /dev/null 2>&1
cd home/project/$1
pytest -s tutorial.py
