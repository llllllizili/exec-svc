#!/bin/bash
source /etc/profile >/dev/null 2>&1

# sh __jk_script_dpa_gradle
# __jk_script_dpa_gradle_build_by_docker.sh --project-path /tmp/jkstack-dpa/gateway --build-cmd 'build -x test' --gradle-version 6.5.1-jre8 --artifact-dir /tmp/jkstack-dpa/gateway/build/libs

show_usage="args: \
            [-p -c -v -d] \
            [--project-path --build-cmd  --gradle-version --artifact-dir]"
#参数
PROJECT_PATH=""
BUILD_CMD=""
GRADLE_VERSION=""
ARTIFACT_DIR=""

GETOPT_ARGS=`getopt -o p:c:v:d: -al project-path:,build-cmd:,gradle-version:,artifact-dir: -- "$@"`

eval set -- "$GETOPT_ARGS"

#获取参数
while [ -n "$1" ]
do
	case "$1" in
		-p|--project-path) PROJECT_PATH=$2; shift 2;;
		-c|--build-cmd) BUILD_CMD=$2; shift 2;;
		-v|--gradle-version) GRADLE_VERSION=$2; shift 2;;
		-d|--artifact-dir) ARTIFACT_DIR=$2; shift 2;;
		--) break ;;
		*) echo $show_usage; break ;;
	esac
done

docker run -it --rm \
-v $PROJECT_PATH:$PROJECT_PATH \
-v /var/local/gradle:/home/gradle/.gradle \
-w $PROJECT_PATH \
gradle:$GRADLE_VERSION gradle \
$BUILD_CMD

if [ $? != 0 ]; then
	echo 'ERROR: gradle build failed'
	exit 1
fi

if [ ! -d "$ARTIFACT_DIR" ]; then
    echo "$ARTIFACT_DIR目录不存在($ARTIFACT_DIR is not exist)"
    exit 1
else
    cd $ARTIFACT_DIR
    PKG_NAME=`ls *.*r`
    echo "_jkstack_"$PKG_NAME"_jkstack_"
fi
