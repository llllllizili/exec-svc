#!/bin/bash
source /etc/profile >/dev/null 2>&1

PROJECT_PATH=$1
TAG_NAME=$2

if [ $# != 2 ] ; then
    echo "git tag: "
    echo " args : PROJECT_PATH TAG_NAME"
    echo "$@"
    exit 1
fi


cd $PROJECT_PATH

git tag $TAG_NAME

git push origin $TAG_NAME
