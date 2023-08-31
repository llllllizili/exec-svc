#!/bin/bash
source /etc/profile >/dev/null 2>&1

PROJECT_PATH=$1
POM_PATH=$2
MAVEN_VERSION=$3


if [ $# != 3 ] ; then
    echo "maven build "
    echo " args :  PROJECT_PATH POM_PATH MAVEN_VERSION"
    echo "$@"
    exit 1
fi

if [ ! $POM_PATH ]; then
    docker run -it --rm \
    -v $PROJECT_PATH:$PROJECT_PATH \
    -v /var/local/repository:/root/.m2/repository \
    -w $PROJECT_PATH \
    maven:$MAVEN_VERSION \
    mvn clean package
else
    docker run -it --rm \
    -v $PROJECT_PATH:$PROJECT_PATH \
    -v /var/local/repository:/root/.m2/repository \
    -v /usr/local/jkstack/jk_maven.xml:/usr/local/jkstack/jk_maven.xml \
    maven:$MAVEN_VERSION \
    mvn -f $POM_PATH clean package \
        -s /usr/local/jkstack/jk_maven.xml
fi

if [ ! -d "$PROJECT_PATH/target" ]; then
    echo "target目录不存在(target dir is not exist)"
    exit 1
else
    cd $PROJECT_PATH/target
    PKG_NAME=`ls *.*r`
    echo "_lyx_lzl"$PKG_NAME"_lyx_lzl"
fi
