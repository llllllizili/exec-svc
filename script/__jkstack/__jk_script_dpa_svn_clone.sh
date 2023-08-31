#!/bin/sh
#
#  sh __jk_script_dpa_svn_clone.sh --svn-url svn://192.168.3.196:3690/java_demo --user lizili --passwd 12345678 --dest-path /tmp
show_usage="args: \
            [-l -u -p -d] \
            [--svn-url --user --passwd --dest-path]"
#参数
SVN_URL=""
USER=""
PASSWD=''
DEST_PATH=""

CURRENT_DATE=`date "+%Y-%m-%d-%H:%M:%S:%N"`
GETOPT_ARGS=`getopt -o l:u:p:d: -al svn-url:,user:,passwd:,dest-path: -- "$@"`

eval set -- "$GETOPT_ARGS"

#获取参数
while [ -n "$1" ]
do
	case "$1" in
		-l|--svn-url) SVN_URL=$2; shift 2;;
		-u|--user) USER=$2; shift 2;;
		-p|--passwd) PASSWD=$2; shift 2;;
		-d|--dest-path) DEST_PATH=$2; shift 2;;
		--) break ;;
		*) echo $show_usage; break ;;
	esac
done


SvnCloneByUser(){
  if [ ! -d $DEST_PATH ]; then
    svn checkout --non-interactive --no-auth-cache $SVN_URL --username $USER --password $PASSWD $DEST_PATH
  else
    mv $DEST_PATH $DEST_PATH$CURRENT_DATE
    svn checkout --non-interactive --no-auth-cache $SVN_URL --username $USER --password $PASSWD $DEST_PATH
  fi
}

SvnCloneByUser

if [ $? != 0 ]; then
	echo 'ERROR: svn clone failed'
	exit 1
fi