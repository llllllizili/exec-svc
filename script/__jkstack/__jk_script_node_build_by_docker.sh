#!/bin/bash
source /etc/profile >/dev/null 2>&1

PROJECT_PATH=$1
PACKAGE_DIR=$2
NODE_VERSION=$3

if [ $# != 3 ] ; then
    echo "npm(node) build "
    echo " args: PROJECT_PATH PACKAGE_DIR NODE_VERSION"
    echo "$@"
    exit 1
fi

docker run -it --rm \
-v $PROJECT_PATH:$PROJECT_PATH \
-w $PROJECT_PATH \
node:$NODE_VERSION \
npm install --registry=https://registry.npm.taobao.org

docker run -it --rm \
-v $PROJECT_PATH:$PROJECT_PATH \
-w $PROJECT_PATH \
node:$NODE_VERSION \
npm run build


if [ ! -d "$PROJECT_PATH/$PACKAGE_DIR" ]; then
    echo "$PACKAGE_DIR目录不存在($PACKAGE_DIR dir is not exist)"
    exit 1
else
    cd $PROJECT_PATH
    zip -r $PACKAGE_DIR.zip $PACKAGE_DIR
    echo "_lyx_lzl"$PACKAGE_DIR.zip"_lyx_lzl"
fi
