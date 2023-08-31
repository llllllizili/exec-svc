#!/bin/sh
#
show_usage="args: \
            [-f -t] \
            [--dockerfile --image-tag]"


DOCKERFILE_PATH=""      # Dockerfile
IMAGE_NAME_TAG=""   # image:tag

GETOPT_ARGS=`getopt -o f:t: -al dockerfile:,image-tag: -- "$@"`

eval set -- "$GETOPT_ARGS"

#获取参数
while [ -n "$1" ]
do
	case "$1" in
		-f|--dockerfile) DOCKERFILE_PATH=$2; shift 2;;
		-t|--image-tag) IMAGE_NAME_TAG=$2; shift 2;;
		--) break ;;
		*) echo $show_usage; break ;;
	esac
done

if [ ! -f $DOCKERFILE_PATH ]; then
  echo "$DOCKERFILE_PATH is not exist"
  exit 1
fi

cd ${DOCKERFILE_PATH%/*}
docker build -f $DOCKERFILE_PATH -t $IMAGE_NAME_TAG .
if [ $? != 0 ]; then
	echo 'ERROR: docker build failed'
	exit 1
fi
