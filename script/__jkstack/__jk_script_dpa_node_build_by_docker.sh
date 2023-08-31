#!/bin/bash
source /etc/profile >/dev/null 2>&1

show_usage="args: \
            [-p -w -v -c] \
            [--project-path --build-dir --node-version --config]"
#参数
PROJECT_PATH=""
BUILD_DIR=""
NODE_VERSION=""
NPM_CONFIG="--registry https://registry.npm.taobao.org"

GETOPT_ARGS=`getopt -o p:w:v:c: -al project-path:,build-dir:,node-version:,config: -- "$@"`

eval set -- "$GETOPT_ARGS"


#获取参数
while [ -n "$1" ]
do
	case "$1" in
		-p|--project-path) PROJECT_PATH=$2; shift 2;;
		-w|--build-dir) BUILD_DIR=$2; shift 2;;
		-v|--node-version) NODE_VERSION=$2; shift 2;;
		-c|--config) NPM_CONFIG=$2; shift 2;;
		--) break ;;
		*) echo $show_usage; break ;;
	esac
done


docker run -it --rm \
-v $PROJECT_PATH:$PROJECT_PATH \
-w $PROJECT_PATH \
node:$NODE_VERSION \
npm install $NPM_CONFIG

if [ $? != 0 ]; then
	echo 'ERROR: npm install failed'
	exit 1
fi


docker run -it --rm \
-v $PROJECT_PATH:$PROJECT_PATH \
-w $PROJECT_PATH \
node:$NODE_VERSION \
npm run build

if [ $? != 0 ]; then
	echo 'ERROR: npm build failed'
	exit 1
fi

if [ ! -d "$PROJECT_PATH/$BUILD_DIR" ]; then
    echo "$BUILD_DIR目录不存在($BUILD_DIR dir is not exist)"
    exit 1
else
    cd $PROJECT_PATH
    zip -r $BUILD_DIR.zip $BUILD_DIR
    echo "_jkstack_"$BUILD_DIR.zip"_jkstack_"
fi
