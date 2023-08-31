#!/bin/bash
source /etc/profile >/dev/null 2>&1
# mvn clean package -f /var/local/project/java_demo_master_269/pom.xml

PROJECT_PATH=$1
POM_PATH=$2

if [ ! $PROJECT_PATH ]; then
  echo "项目路径不能为空(Project path is required)"
  exit 1
fi

if [ ! $POM_PATH ]; then
  cd $PROJECT_PATH
  mvn clean package
else
  mvn clean package -f $POM_PATH
fi

if [ ! -d "$PROJECT_PATH/target" ]; then
    echo "target目录不存在(target dir is not exist)"
else
    cd $PROJECT_PATH/target
    PKG_NAME=`ls *.*r`
    echo "_lyx_lzl"$PKG_NAME"_lyx_lzl"
fi



