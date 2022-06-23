#!/bin/bash

set -e
DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd $DIR
docker build -t tutorial_python -f ./base/Dockerfile ./base/
[ -d "./package" ] && rm -r ./package
mkdir "package"
cd ../eyes_selenium && python setup.py sdist && mv ./dist/* ../tutorials/package/
cd ../eyes_common && python setup.py sdist && mv ./dist/* ../tutorials/package/
cd ../eyes_core && python setup.py sdist && mv ./dist/* ../tutorials/package/
cd ../eyes_images && python setup.py sdist && mv ./dist/* ../tutorials/package/
cd $DIR
docker build --no-cache --build-arg package="$(ls ./package)" -t tutorial_python_basic -f ./basic/Dockerfile .
docker build --no-cache --build-arg package="$(ls ./package)" -t tutorial_python_ufg -f ./ultrafastgrid/Dockerfile .
docker build --no-cache --build-arg package="$(ls ./package)" -t tutorial_python_images -f ./images/Dockerfile .
