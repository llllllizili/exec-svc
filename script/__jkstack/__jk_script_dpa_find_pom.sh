#!/bin/bash
source /etc/profile >/dev/null 2>&1

# bash __jk_script_dpa_find_pom.sh --project-path /tmp/aaa
show_usage="args: \
            [-p ] \
            [--project-path]"
#参数
PROJECT_PATH=""

GETOPT_ARGS=`getopt -o p: -al project-path: -- "$@"`

eval set -- "$GETOPT_ARGS"

#获取参数
while [ -n "$1" ]
do
	case "$1" in
		-p|--project-path) PROJECT_PATH=$2; shift 2;;
		--) break ;;
		*) echo $show_usage; break ;;
	esac
done



GetPom(){
    RES=`find $PROJECT_PATH -name pom.xml`

    local IFS=$'\n'
    local OLDIFS="$IFS"
    for line in $RES
        do
            echo $line
        done | sed '$!s/$/,/'
}

if [ ! $PROJECT_PATH ]; then
    echo 'miss args --project-path'
    exit 1
else
    pom_list=`GetPom`
    echo $pom_list | sed s/[[:space:]]//g
fi
