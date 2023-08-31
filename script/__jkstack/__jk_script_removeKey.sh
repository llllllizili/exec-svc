#!/bin/bash

CURR_USER=`whoami`

AuthorizedKeysFile=`cat /etc/ssh/sshd_config | grep AuthorizedKeysFile | awk '{ print $2 }'`

KeyFile=/$CURR_USER/$AuthorizedKeysFile

sed -i -e '/jkexec_engine/d' $KeyFile


