#!/bin/sh



# 此脚本为临时使用脚本 @佳琪

PURGE_DAY='JKSTACK'

REPORT_WORK_DIR='cstc_crawler'

REPORT_DIR="/opt/.jkDpa/jmeter_report/"$REPORT_WORK_DIR

PROJECT_NAME=`date "+%Y-%m-%d-%H_%M_%S_%N"`

mkdir -p $REPORT_DIR/$PROJECT_NAME
chmod 777 -R $REPORT_DIR/$PROJECT_NAME

docker run --rm \
-v $REPORT_DIR/$PROJECT_NAME/tmp/:/tmp/ \
cstc-crawler:1.0.0

if [ $? != 0 ]; then
  echo 'ERROR: execution failed'
  exit 1
fi
	
LOCAL_IP=`/sbin/ifconfig ens160 |grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:"`

echo "_jkstack_http://"$LOCAL_IP/$REPORT_WORK_DIR/$PROJECT_NAME/tmp/items.csv"_jkstack_"

if [ $PURGE_DAY == 'JKSTACK' ]; then
	exit 0
else
	find $REPORT_DIR -mindepth 1 -maxdepth 1 -type d -mtime +$PURGE_DAY | xargs rm -rf
	echo "Purge the report  $PURGE_DAY days ago "
fi
