#!/bin/bash
source /etc/profile >/dev/null 2>&1

DgroupId=$1
DartifactId=$2
Dversion=$3
DrepositoryId=$4
Durl=$5
Dfile=$6
RepoName=$7

MVN_SETTING_XML="/usr/local/jkstack/jk_maven.xml"

# sh __jk_script_maven_deploy.sh 
# DgroupId           com.jk     
# DartifactId        demo       # 项目名
# Dversion           8.8.0    
# DrepositoryId      nexus    
# Durl               nexus.jk.local  
# Dfile              /tmp/java_demo/target/demo-0.0.1-SNAPSHOT.jar         
# RepoName           maven-releases

if [ $# != 7 ] ; then
    echo "USAGE: "
    echo " e.g.: ${0##*/} DgroupId DartifactId Dversion DrepositoryId Durl Dfile RepoName"
    echo " e.g.: ${0##*/} com.jk demo 0.8 jknexus 192.168.3.89:8081 /tmp/java_demo/target/demo-0.0.1-SNAPSHOT.jar maven-releases"
    exit 1
fi

mvn deploy:deploy-file \
-DgroupId=$DgroupId \
-DartifactId=$DartifactId \
-Dversion=$Dversion \
-DgeneratePom=true \
-DrepositoryId=$DrepositoryId \
-s $MVN_SETTING_XML \
-Durl=http://$Durl/repository/$RepoName \
-Dfile=$Dfile
