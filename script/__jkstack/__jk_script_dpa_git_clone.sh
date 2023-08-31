#!/bin/sh
#
#  sh __jk_script_dpa_git_clone.sh --branch master --git-url http://user:pwd@www.exemple.com/demo/demo.git --dest-path /tmp
show_usage="args: \
            [-b -t -l -d] \
            [--branch --tag --git-url --dest-path]"
#参数
BRANCH=""
TAG=""
GIT_URL=""
DEST_PATH=""
PULL_BRANCH=""
CURRENT_DATE=`date "+%Y-%m-%d-%H:%M:%S:%N"`
GETOPT_ARGS=`getopt -o b:t:l:d: -al branch:,tag:,git-url:,dest-path: -- "$@"`

eval set -- "$GETOPT_ARGS"

#获取参数
while [ -n "$1" ]
do
	case "$1" in
		-b|--branch) BRANCH=$2; shift 2;;
		-t|--tag) TAG=$2; shift 2;;
		-l|--git-url) GIT_URL=$2; shift 2;;
		-d|--dest-path) DEST_PATH=$2; shift 2;;
		--) break ;;
		*) echo $show_usage; break ;;
	esac
done

# 空
if [ ! $BRANCH ]; then
  PULL_BRANCH=$TAG
else
  PULL_BRANCH=$BRANCH
fi

GitCloneByUser(){
  if [ ! -d $DEST_PATH ]; then
     if [[ $GIT_URL =~ 'http' ]];then
        GIT_SERVER=`echo $GIT_URL | awk -F'://' '{print $2}'`
        out=$(git -c http.sslVerify=false clone -b $PULL_BRANCH http://$GIT_SERVER $DEST_PATH 2>&1)
        if [[ $out =~ 'Authentication' ]];then
          echo "Authentication failed"
        else
          echo $out
        fi
     fi

     if [[ $GIT_URL =~ 'ssh' ]];then
        out=$(git  clone -b $PULL_BRANCH $GIT_URL $DEST_PATH 2>&1)
        if [[ $out =~ 'Authentication' ]];then
          echo "Authentication failed"
        else
          echo $out
        fi
     fi

  else
    mv $DEST_PATH $DEST_PATH$CURRENT_DATE
    if [[ $GIT_URL =~ 'http' ]];then
      GIT_SERVER=`echo $GIT_URL | awk -F'://' '{print $2}'`
      out=$(git -c http.sslVerify=false clone -b $PULL_BRANCH http://$GIT_SERVER $DEST_PATH 2>&1)
      if [[ $out =~ 'Authentication' ]];then
        echo "Authentication failed"
      else
          echo $out
      fi
    fi

    if [[ $GIT_URL =~ 'ssh' ]];then
      out=$(git  clone -b $PULL_BRANCH $GIT_URL $DEST_PATH 2>&1)
      if [[ $out =~ 'Authentication' ]];then
        echo "Authentication failed"
      else
          echo $out
      fi
    fi
  fi
}

GitCloneByUser

if [ $? != 0 ]; then
	echo 'ERROR: git clone failed'
	exit 1
fi