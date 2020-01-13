# CLI-TOOL

This is a python3 cli-tool for using against localstack

## PYTHON USAGE

How to use it with python:

usage: cli-tool.py {create [stack-file], update [stack-file], delete, list} --sn/stack-name namestack

You can execute some test with test.py

## DOCKER USAGE

The easiest way to use it is with docker. Having the localstack running (I used the docker-compose of their repo: https://github.com/localstack/localstack ) you can run the container wiht the flag --network host, so it will use localhost for connecting with localstack. 

Inside the container you will have some .json files to test, but if it's needed you can mount a folder with some json files using -v, --volume=[host-src:]container-dest


docker run --network host -it registry.hub.docker.com/medtorja/clitool /bin/bash

In the image you can find an alias, so you can call the tool with cli-tool, 

ex: 
cli-tool list stack1

You can pull the docker image from:  https://hub.docker.com/repository/docker/medtorja/clitool