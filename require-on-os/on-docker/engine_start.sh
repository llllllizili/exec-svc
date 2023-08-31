#!/bin/bash
base_dir='/opt/jkexec/jksreExecEngine'

source $base_dir/../venv/bin/activate

# 如果设置了BUG变量，日志基本改为DEBUG
if [ $DEBUG_TASK ];then
    sed -i "s/DEBUG = False/DEBUG = True/g" $base_dir/jksreExecEngine/settings.py # Django 开启debug
    sed -i "s/ERROR/DEBUG/g" $base_dir/jksreExecEngine/settings.py # 日志开启debug
fi


if [ -e $base_dir/exec_config.py ]; then
    cd $base_dir
    $base_dir/../venv/bin/gunicorn jksreExecEngine.wsgi:application --max-requests 2048 --max-requests-jitter 512 -w 8 -k gthread -b 0.0.0.0:8093

else
    echo "engine_start failed"
    echo "error ---- > mybe init_server failed (exec_config.py)"
    exit 1
fi
