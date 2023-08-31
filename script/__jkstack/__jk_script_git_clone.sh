#!/bin/bash
source /etc/profile >/dev/null 2>&1

# git -c http.sslVerify=false clone -b master https://user:pwd@git.jk.local:8443/devops/java_demo.git /tmp/java_demo"
# sh __jk_script_git_clone.sh  master lizili 123qweASD git.jk.local:8443/devops/java_demo.git /tmp/java_demo
BRANCH=$1
GIT_URL=$2
DEST_PATH=$3

CURRENT_DATE=`date "+%Y-%m-%d-%H:%M:%S:%N"`

if [ $# != 3 ] ; then
    echo "git clone"
    echo " args: BRANCH GIT_URL DEST_PATH"
    exit 1
fi

GitCloneByUser(){
  if [ ! -d $DEST_PATH ]; then
    git -c http.sslVerify=false clone -b $BRANCH $GIT_URL $DEST_PATH
  else
    mv $DEST_PATH $DEST_PATH$CURRENT_DATE
    git -c http.sslVerify=false clone -b $BRANCH $GIT_URL $DEST_PATH
  fi
}

#GitCloneByKey(){
#}

# $(GitCloneByUser)
GitCloneByUser
