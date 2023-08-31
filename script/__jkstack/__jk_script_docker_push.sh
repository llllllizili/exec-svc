#!/bin/bash

USERNAME=$1
PASSWORD=$2
DOCKER_HUB=$3           # 镜像仓库地址
IMAGE_NAME_VERSION=$4   # 镜像名 & 版本
DOCKERFILE_PATH=$5      # Dockerfile 路径

# cat /etc/docker/daemon.json  将仓库地址 添加进docker
# {
#   "insecure-registries":["192.168.3.89:8082"],
# }

# docker build -t nginx:v3 .  # build 的name 如果未指定镜像仓库 则需 docker tag 

if [ $# != 5 ] ; then
    echo "docker_push"
    echo " args:  USERNAME PASSWORD DOCKER_HUB IMAGE_NAME_VERSION DOCKERFILE_PATH"
    exit 1
fi


cd ${DOCKERFILE_PATH%/*}

docker build -f $DOCKERFILE_PATH -t $IMAGE_NAME_VERSION .

docker login -u $USERNAME -p $PASSWORD $DOCKER_HUB

docker tag $IMAGE_NAME_VERSION ${DOCKER_HUB#*//}/$IMAGE_NAME_VERSION

docker push ${DOCKER_HUB#*//}/$IMAGE_NAME_VERSION

docker rmi ${DOCKER_HUB#*//}/$IMAGE_NAME_VERSION

docker rmi $IMAGE_NAME_VERSION