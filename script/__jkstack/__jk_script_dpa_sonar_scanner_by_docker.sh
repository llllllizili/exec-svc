#!/bin/bash

# sh __jk_script_dpa_sonar_scanner_by_docker.sh --language java --project-path /tmp/java_demo --project-name java_demo --project-version v111 --sonar-host http://192.168.3.183:9000/ --sonar-token f9c1d813c71c891105f7700a34b7950ace6f0a19

source /etc/profile >/dev/null 2>&1

show_usage="args: \
            [-l -p -n -v -h -k -c] \
            [--language --project-path --project-name --project-version --sonar-host --sonar-token --sonar-cli]"

LANGUAGE=""
PROJECT_PATH=""
PROJECT_NAME=""
PROJECT_VERSION="default"
SONAR_HOST=""
SONAR_TOKEN=""
SONAR_CLI_VERSION="latest"

GETOPT_ARGS=`getopt -o l:p:n:v:h:k:c: -al language:,project-path:,project-name:,project-version:,sonar-host:,sonar-token:,sonar-cli: -- "$@"`

eval set -- "$GETOPT_ARGS"

while [ -n "$1" ]
do
	case "$1" in
		-l|--language) LANGUAGE=$2; shift 2;;
		-p|--project-path) PROJECT_PATH=$2; shift 2;;
		-n|--project-name) PROJECT_NAME=$2; shift 2;;
		-v|--project-version) PROJECT_VERSION=$2; shift 2;;
		-h|--sonar-host) SONAR_HOST=$2; shift 2;;
		-k|--sonar-token) SONAR_TOKEN=$2; shift 2;;
		-k|--sonar-cli) SONAR_CLI_VERSION=$2; shift 2;;
		--) break ;;
		*) echo $show_usage; break ;;
	esac
done


if [ $LANGUAGE=='java' ]; then
    docker run --rm \
    -e SONAR_HOST_URL=$SONAR_HOST \
    -v $PROJECT_PATH:/usr/src \
    sonarsource/sonar-scanner-cli:$SONAR_CLI_VERSION \
    -Dsonar.projectKey=$PROJECT_NAME \
    -Dsonar.projectVersion=$PROJECT_VERSION \
    -Dsonar.java.binaries=./ \
    -Dsonar.login=$SONAR_TOKEN
elif [ $LANGUAGE=='JavaScript' ]; then
    docker run --rm \
    -e SONAR_HOST_URL=$SONAR_HOST \
    -v $PROJECT_PATH:/usr/src \
    sonarsource/sonar-scanner-cli:$SONAR_CLI_VERSION \
    -Dsonar.projectKey=$PROJECT_NAME \
    -Dsonar.projectVersion=$PROJECT_VERSION \
    -Dsonar.sourceEncoding=UTF-8 \
    -Dsonar.login=$SONAR_TOKEN
else
    docker run --rm \
    -e SONAR_HOST_URL=$SONAR_HOST \
    -v $PROJECT_PATH:/usr/src \
    sonarsource/sonar-scanner-cli:$SONAR_CLI_VERSION \
    -Dsonar.projectKey=$PROJECT_NAME \
    -Dsonar.projectVersion=$PROJECT_VERSION \
    -Dsonar.login=$SONAR_TOKEN
fi

if [ $? != 0 ]; then
	echo 'ERROR: sonar scanner cli failed'
	exit 1
fi

echo "_jkstack_${SONAR_HOST}/dashboard?id=${PROJECT_NAME}_jkstack_"
