#!/bin/bash
source /etc/profile >/dev/null 2>&1

# sh __jk_script_dpa_ant_build_by_docker.sh --project-path /opt/dpa/ant_demo --build-cmd war --build-file /opt/dpa/ant_demo/build.xml --ant-version 1.10.9 --artifact-dir /opt/dpa/ant_demo/build/war/

show_usage="args: \
            [-p -c -f -v -d] \
            [--project-path --build-cmd --build-file --ant-version --artifact-dir]"
#参数
PROJECT_PATH=""
BUILD_CMD=""
BUILD_FILE=""
ANT_VERSION=""
ARTIFACT_DIR=""

GETOPT_ARGS=`getopt -o p:c:f:v:d: -al project-path:,build-cmd:,build-file:,ant-version:,artifact-dir: -- "$@"`

eval set -- "$GETOPT_ARGS"

#获取参数
while [ -n "$1" ]
do
	case "$1" in
		-p|--project-path) PROJECT_PATH=$2; shift 2;;
		-c|--build-cmd) BUILD_CMD=$2; shift 2;;
		-f|--build-file) BUILD_FILE=$2; shift 2;;
		-v|--ant-version) ANT_VERSION=$2; shift 2;;
		-d|--artifact-dir) ARTIFACT_DIR=$2; shift 2;;
		--) break ;;
		*) echo $show_usage; break ;;
	esac
done



if [ ! $BUILD_FILE ]; then
docker run --rm  -v /opt/dpa/ant_demo:/ant_demo jkstack/ant:1.10.9 war -f /ant_demo/build.xml
    echo 'info - build file not exist'
    docker run -it --rm \
    -v $PROJECT_PATH:$PROJECT_PATH \
    -w $PROJECT_PATH \
    jkstack/ant:$ANT_VERSION \
    $BUILD_CMD

else
    echo 'info -  build file exist'
    docker run -it --rm \
    -v $PROJECT_PATH:$PROJECT_PATH \
    -w $PROJECT_PATH \
    jkstack/ant:$ANT_VERSION \
    $BUILD_CMD \
    -f $BUILD_FILE
fi

if [ $? != 0 ]; then
	echo 'ERROR: ant build failed'
	exit 1
fi

if [ ! -d "$ARTIFACT_DIR" ]; then
    echo "$ARTIFACT_DIR目录不存在($ARTIFACT_DIR is not exist)"
    exit 1
else
    cd $ARTIFACT_DIR
    PKG_NAME=`ls *.*r`
    if [ $? != 0 ]; then
        echo "$ARTIFACT_DIR - package is not exist"
        exit 1
    fi
    echo "_jkstack_"$PKG_NAME"_jkstack_"
fi
