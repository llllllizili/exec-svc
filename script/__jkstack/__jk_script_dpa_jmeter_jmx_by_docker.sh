#!/bin/sh
#
# --work-dir	 	/opt/.jkDpa/am4008
# --jmx-file 		http://xxx  /opt/.jkDpa/am4008/xxxx.jmx
# --domain-name 	www.xxxx.xxx.com:127.0.0.1
# --jmeter-version  5.3
# --days			3 # 保留三天

# sh -x dpa_jmeter.sh --work-dir /opt/.jkDpa/am4008/java_demobcc0 --jmx-file /opt/.jkDpa/am4008/java_demobcc0/demo.jmx --domain-name localhost:127.0.0.1 --jmeter-version 5.3 

# 暂未作日志保留时间限制 一次大概3-5MB   300G 10W次

show_usage="args: \
            [-w -j -d -v -t] \
            [--work-dir --project-name --domain-name --jmeter-version --purge-day]"

#参数
WORK_DIR=""
JMX_FILE=""
JMETER_VERSION="5.3"
DOMAIN_NAME="localhost:127.0.0.1"
PURGE_DAY='JKSTACK'



GETOPT_ARGS=`getopt -o w:j:d:v:t: -al work-dir:,jmx-file:,domain-name:,jmeter-version:,purge-day: -- "$@"`

eval set -- "$GETOPT_ARGS"

while [ -n "$1" ]
do
	case "$1" in
		-w|--work-dir) WORK_DIR=$2; shift 2;;
		-j|--jmx-file) JMX_FILE=$2; shift 2;;
		-d|--domain-name) DOMAIN_NAME=$2; shift 2;;
		-v|--jmeter-version) JMETER_VERSION=$2; shift 2;;
		-t|--purge-day) PURGE_DAY=$2; shift 2;;
 		--) break ;;
		*) echo $show_usage; break ;;
	esac
done

REPORT_WORK_DIR=`echo ${WORK_DIR} | awk -F '/'  '{print $(NF-1)}'`

REPORT_DIR="/opt/.jkDpa/jmeter_report/"$REPORT_WORK_DIR
PROJECT_NAME=`date "+%Y-%m-%d-%H_%M_%S_%N"`



mkdir -p $REPORT_DIR/$PROJECT_NAME
chmod 777 -R $REPORT_DIR/$PROJECT_NAME


if echo $JMX_FILE | grep -q "http"; then
	wget \'"$JMX_FILE"\' -O $REPORT_DIR/$PROJECT_NAME.jmx
  if [ $? -ne 0 ]; then
    echo 'wget download jmx file failed，retry with curl'
    curl "$JMX_FILE" -o $REPORT_DIR/$PROJECT_NAME.jmx
    if [ $? -ne 0 ]; then
      echo 'curl download jmx file failed'
      exit 1
    fi
	fi

	docker run -it --rm --privileged=true \
	--add-host=$DOMAIN_NAME \
	-v $REPORT_DIR/$PROJECT_NAME:$REPORT_DIR/$PROJECT_NAME \
	-v $REPORT_DIR/$PROJECT_NAME.jmx:$REPORT_DIR/$PROJECT_NAME.jmx \
	jkstack/jmeter:$JMETER_VERSION \
	-n -t $REPORT_DIR/$PROJECT_NAME.jmx \
	-l $REPORT_DIR/$PROJECT_NAME/$PROJECT_NAME.jtl \
	-e -o $REPORT_DIR/$PROJECT_NAME

	if [ $? != 0 ]; then
		echo 'ERROR: jmx - execution failed'
		exit 1
	fi
	
	# LOCAL_IP=`ip route | grep -v br- | grep -v docker | grep -v default | awk -F '/'  '{print $1}'`
	LOCAL_IP=`/sbin/ifconfig ens160 |grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:"`

	echo "_jkstack_http://"$LOCAL_IP/$REPORT_WORK_DIR/$PROJECT_NAME"_jkstack_"

	rm -rf $REPORT_DIR/$PROJECT_NAME.jmx 2>/dev/null
fi


if [ $PURGE_DAY == 'JKSTACK' ]; then
	exit 0
else
	find $REPORT_DIR -mindepth 1 -maxdepth 1 -type d -mtime +$PURGE_DAY | xargs rm -rf
	echo "Purge the report  $PURGE_DAY days ago "
fi
