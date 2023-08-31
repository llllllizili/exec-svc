#!/bin/bash


# sh xx.sh python python_demo 1.1.0 http://192.168.3.89:9000 0a44277b8304a708ff41d5bb95df8e6d2ebeb1bc

LANGUAGE=$1
PROJECT_PATH=$2
PROJECT_NAME=$3
PROJECT_VERSION=$4
SONAR_HOST=$5
SONAR_TOKEN=$6

if [ $# != 6 ] ; then
    echo "sonar scanner "
    echo " args: LANGUAGE PROJECT_PATH PROJECT_NAME PROJECT_VERSION SONAR_HOST SONAR_TOKEN"
    echo "$@"
    exit 1
fi

if [ $LANGUAGE=='java' ]; then
    docker run --rm \
    -e SONAR_HOST_URL=$SONAR_HOST \
    -v $PROJECT_PATH:/usr/src \
    sonarsource/sonar-scanner-cli \
    -Dsonar.projectKey=$PROJECT_NAME \
    -Dsonar.projectVersion=$PROJECT_VERSION \
    -Dsonar.java.binaries=./ \
    -Dsonar.login=$SONAR_TOKEN
else
    docker run --rm \
    -e SONAR_HOST_URL=$SONAR_HOST \
    -v $PROJECT_PATH:/usr/src \
    sonarsource/sonar-scanner-cli \
    -Dsonar.projectKey=$PROJECT_NAME \
    -Dsonar.projectVersion=$PROJECT_VERSION \
    -Dsonar.login=$SONAR_TOKEN
fi