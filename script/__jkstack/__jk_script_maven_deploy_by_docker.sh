#!/bin/bash

# DgroupId           com.jk     
# DartifactId        demo       # 项目名
# Dversion           8.8.0    
# MAVEN_REPO_USER    admin
# MAVEN_REPO_PASSWD  admin
# Durl               nexus.jk.local  
# Dfile              /tmp/java_demo/target/demo-0.0.1-SNAPSHOT.jar         
# RepoName           maven-releases
# MAVEN_VERSION      latest

source /etc/profile >/dev/null 2>&1

DgroupId=$1
DartifactId=$2
Dversion=$3
MAVEN_REPO_USER=$4
MAVEN_REPO_PASSWD=$5
Durl=$6
Dfile=$7
RepoName=$8
MAVEN_VERSION=$9


MVN_SETTING_DIR="/usr/local/jkstack"
DrepositoryId='jknexus_component'


CURRENT_DATE=`date "+%Y-%m-%d-%H_%M_%S_%N"`


if [ $# != 9 ] ; then
    echo "maven deploy"
    echo " args: DgroupId DartifactId Dversion MAVEN_REPO_USER MAVEN_REPO_PASSWD Durl Dfile RepoName MAVEN_VERSION"
    echo "$@"
    exit 1
fi


if [ ! -f $MVN_SETTING_DIR/$DartifactId$CURRENT_DATE'.xml' ]; then
    cp -a $MVN_SETTING_DIR'/jk_maven.xml' $MVN_SETTING_DIR/$DartifactId$CURRENT_DATE'.xml'
    sed -i "s/jkmavenuser/$MAVEN_REPO_USER/g" $MVN_SETTING_DIR/$DartifactId$CURRENT_DATE'.xml'
    sed -i "s/jkmavenpasswd/$MAVEN_REPO_PASSWD/g" $MVN_SETTING_DIR/$DartifactId$CURRENT_DATE'.xml'
fi

docker run -it --rm \
-v $Dfile:$Dfile \
-v $MVN_SETTING_DIR/$DartifactId$CURRENT_DATE'.xml':$MVN_SETTING_DIR/$DartifactId$CURRENT_DATE'.xml' \
-v /var/local/repository:/root/.m2/repository \
maven:$MAVEN_VERSION \
mvn deploy:deploy-file \
-DgroupId=$DgroupId \
-DartifactId=$DartifactId \
-Dversion=$Dversion \
-DgeneratePom=true \
-DrepositoryId=$DrepositoryId \
-s $MVN_SETTING_DIR/$DartifactId$CURRENT_DATE'.xml' \
-Durl=$Durl/repository/$RepoName \
-Dfile=$Dfile
# -v /var/local/repository:/root/.m2/repository \
# -w /tmp/java_demo \