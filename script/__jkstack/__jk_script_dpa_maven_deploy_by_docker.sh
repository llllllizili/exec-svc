#!/bin/bash
source /etc/profile >/dev/null 2>&1

# DgroupId           com.jk     
# DartifactId        demo       # 项目名
# Dversion           8.8.0    
# Username   		 admin
# Password		     admin
# Durl               nexus.jk.local  
# Dfile              /tmp/java_demo/target/demo-0.0.1-SNAPSHOT.jar         
# RepoName           maven-releases
# MavenVersion      latest

# bash __jk_script_dpa_maven_build_by_docker.sh \
# --DgroupId com.jk \
# --DartifactId demo \
# --Dversion 1.1.0 \
# --Durl http://192.168.3.89:8081 \
# --Username admin \
# --Password 4b1HDSHmwyPxDTWP \
# --Dfile /tmp/java_demo/target/demo-0.0.1-SNAPSHOT.jar \
# --RepoName maven-releases \
# --MavenVersion latest


show_usage="args: \
            [-g -a -v -r -f -n -u -p -m] \
            [--DgroupId --DartifactId --Dversion --Durl --Dfile --RepoName Username --Password --MavenVersion]"
#参数
DgroupId=""
DartifactId=""
Dversion=""
Durl=""
Dfile=""
RepoName=""
Username=""
Password=""
MavenVersion=""

MVN_SETTING_DIR="/usr/local/jkstack"
DrepositoryId='jknexus_component'

CURRENT_DATE=`date "+%Y-%m-%d-%H_%M_%S_%N"`


GETOPT_ARGS=`getopt -o g:a:v:r:f:n:u:p:m: -al DgroupId:,DartifactId:,Dversion:,Durl:,Dfile:,RepoName:,Username:,Password:,MavenVersion: -- "$@"`

eval set -- "$GETOPT_ARGS"

#获取参数
while [ -n "$1" ]
do
	case "$1" in
		-g|--DgroupId) DgroupId=$2; shift 2;;
		-a|--DartifactId) DartifactId=$2; shift 2;;
		-v|--Dversion) Dversion=$2; shift 2;;
		-r|--Durl) Durl=$2; shift 2;;
		-f|--Dfile) Dfile=$2; shift 2;;
		-n|--RepoName) RepoName=$2; shift 2;;
		-u|--Username) MAVEN_REPO_USER=$2; shift 2;;
		-p|--Password) MAVEN_REPO_PASSWD=$2; shift 2;;
		-m|--MavenVersion) MAVEN_VERSION=$2; shift 2;;
		--) break ;;
		*) echo $show_usage; break ;;
	esac
done



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

rm -rf $MVN_SETTING_DIR/$DartifactId$CURRENT_DATE'.xml'

if [ $? != 0 ]; then
	echo 'ERROR: mvn deploy failed'
	exit 1
fi


