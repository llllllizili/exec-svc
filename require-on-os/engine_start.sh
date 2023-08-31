#!/bin/bash
base_dir='/opt/jkexec/jksreExecEngine'

source $base_dir/../venv/bin/activate

if [ -e $base_dir/exec_config.py ]; then
    cd $base_dir
    $base_dir/../venv/bin/gunicorn jksreExecEngine.wsgi:application --max-requests 2048 --max-requests-jitter 512 -w 8 -k gthread -b 0.0.0.0:8093

else
    echo "engine_start failed"
    echo "error ---- > mybe init_server failed (exec_config.py)" >> /var/log/jkexec.log
    exit 1
fi
