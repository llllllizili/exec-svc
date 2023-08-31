#!/bin/bash
base_dir='/opt/jkexec/jksreExecEngine'

source $base_dir/../venv/bin/activate

sleep 60

JK_MQ_USER=`cat $base_dir/exec_config.py | grep JK_MQ_USER | awk -F \' '{print $2}'`
JK_MQ_PASSWORD=`cat $base_dir/exec_config.py | grep JK_MQ_PASSWORD | awk -F \' '{print $2}'`
JK_MQ_HOST=`cat $base_dir/exec_config.py | grep JK_MQ_HOST | awk -F \' '{print $2}'`

if [ $? == 0 ]; then
    $base_dir/../venv/bin/celery flower --broker=amqp://$JK_MQ_USER:$JK_MQ_PASSWORD@$JK_MQ_HOST:5672/jksreexec >/var/log/jkexec_flower.log
fi
