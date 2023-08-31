#!/bin/bash
source /etc/profile >/dev/null 2>&1



# bash __jk_script_dpa_maven_build_by_docker.sh --profile dev --project-path /tmp/aaa --pom-path /tmp/aaa/pom.xml  --mvn-version latest
show_usage="args: \
            [-p -w -m -e] \
            [--project-path --pom-path --mvn-version --profile ]"
#参数
PROJECT_PATH=""
POM_PATH=""
MAVEN_VERSION=""
MAVEN_PROFILE=""

GETOPT_ARGS=`getopt -o p:w:m:e: -al project-path:,pom-path:,mvn-version:,profile: -- "$@"`

eval set -- "$GETOPT_ARGS"

#获取参数
while [ -n "$1" ]
do
	case "$1" in
		-p|--project-path) PROJECT_PATH=$2; shift 2;;
		-w|--pom-path) POM_PATH=$2; shift 2;;
		-m|--mvn-version) MAVEN_VERSION=$2; shift 2;;
		-e|--profile) MAVEN_PROFILE=$2; shift 2;;
		--) break ;;
		*) echo $1,$2,$show_usage; break ;;
	esac
done



if [ ! $POM_PATH ]; then
    echo 'pom file not exist'
    docker run -it --rm \
    -v $PROJECT_PATH:$PROJECT_PATH \
    -v /var/local/repository:/root/.m2/repository \
    -v /var/local/repository:/var/local/repository \
    -w $PROJECT_PATH \
    maven:$MAVEN_VERSION \
    mvn clean package -P $MAVEN_PROFILE
else
    echo ' pom file exist'
    docker run -it --rm \
    -v $PROJECT_PATH:$PROJECT_PATH \
    -v /var/local/repository:/root/.m2/repository \
    -v /var/local/repository:/var/local/repository \
    -v /usr/local/jkstack/jk_maven.xml:/usr/local/jkstack/jk_maven.xml \
    maven:$MAVEN_VERSION \
    mvn -f $POM_PATH clean package  -P $MAVEN_PROFILE \
        -s /usr/local/jkstack/jk_maven.xml
fi

if [ $? != 0 ]; then
	echo 'ERROR: mvn build failed'
	exit 1
fi

if [ ! -d "$PROJECT_PATH/target" ]; then
    echo "target目录不存在(target dir is not exist)"
    exit 1
else
    cd $PROJECT_PATH/target
    PKG_NAME=`ls *.*r`
    echo "_jkstack_"$PKG_NAME"_jkstack_"
fi
