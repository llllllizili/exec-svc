#!/bin/bash

ACTION=$1
YAML_PATH=$2

if [ $# != 2 ] ; then
    echo "K8S yaml - action"
    echo "args : ACTION YAML_PATH"
    echo "$@"
    exit 1
fi

kubectl $ACTION -f $YAML_PATH