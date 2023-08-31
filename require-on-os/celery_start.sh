#!/bin/bash
base_dir='/opt/jkexec/jksreExecEngine'

source $base_dir/../venv/bin/activate
cd $base_dir

if [ $DEBUG_TASK ];then
    $base_dir/../venv/bin/celery -A jksreExecEngine worker -l info
else
    $base_dir/../venv/bin/celery -A jksreExecEngine worker
fi
