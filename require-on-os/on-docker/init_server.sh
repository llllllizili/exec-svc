#!/bin/bash
base_dir='/opt/jkexec/jksreExecEngine'

source $base_dir/../venv/bin/activate

$base_dir/../venv/bin/python3 $base_dir/init_server.py
