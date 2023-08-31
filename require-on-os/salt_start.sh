#!/bin/bash

base_dir='/opt/jkexec/jksreExecEngine'

source $base_dir/../venv/bin/activate
$base_dir/../venv/bin/salt-master
