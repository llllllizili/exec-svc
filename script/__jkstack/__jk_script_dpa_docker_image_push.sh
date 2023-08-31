#!/bin/sh
#
show_usage="args: \
            [-u -p -h -o -n] \
            [--username --password --harbor --old-tag --new-tag]"

USERNAME=""
PASSWORD=""
HUB_ADDR=""
OLD_TAG=""   # image:version
NEW_TAG=""   # image:version

GETOPT_ARGS=`getopt -o u:p:h:o:n: -al username:,password:,harbor:,old-tag:,new-tag: -- "$@"`

eval set -- "$GETOPT_ARGS"

#获取参数
while [ -n "$1" ]
do
	case "$1" in
		-u|--username) USERNAME=$2; shift 2;;
		-p|--password) PASSWORD=$2; shift 2;;
		-h|--harbor) HUB_ADDR=$2; shift 2;;
		-o|--old-tag) OLD_TAG=$2; shift 2;;
		-n|--new-tag) NEW_TAG=$2; shift 2;;
		--) break ;;
		*) echo $show_usage; break ;;
	esac
done

docker login -u $USERNAME -p $PASSWORD $HUB_ADDR
if [ $? != 0 ]; then
	echo 'ERROR: docker login failed'
	exit 1
fi


docker tag $OLD_TAG $NEW_TAG
if [ $? != 0 ]; then
	echo 'ERROR: docker tag failed'
	exit 1
fi


docker push $NEW_TAG
if [ $? == 0 ]; then
	docker rmi $NEW_TAG
	docker rmi $OLD_TAG
	docker rmi $(docker images | grep "none" | awk '{print $3}') 2>/dev/null
fi

docker logout $HUB_ADDR
