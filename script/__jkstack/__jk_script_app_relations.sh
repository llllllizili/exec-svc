#!/bin/bash
source /etc/profile >/dev/null 2>&1
check_os_release()
{
  while true
  do
    os_release=$(grep "Red Hat Enterprise Linux Server release" /etc/issue 2>/dev/null)
    os_release_2=$(grep "Red Hat Enterprise Linux Server release" /etc/redhat-release 2>/dev/null)
    if [ "$os_release" ] && [ "$os_release_2" ]
    then
      if echo "$os_release"|grep "release 5" >/dev/null 2>&1
      then
        os_release=redhat5
        echo "$os_release"
      elif echo "$os_release"|grep "release 6" >/dev/null 2>&1
      then
        os_release=redhat6
        echo "$os_release"
      elif echo "$os_release"|grep "release 7" >/dev/null 2>&1
      then
        os_release=redhat7
        echo "$os_release"
      else
        os_release=""
        echo "$os_release"
      fi
      break
    fi
    os_release=$(grep "Aliyun Linux release" /etc/issue 2>/dev/null)
    os_release_2=$(grep "Aliyun Linux release" /etc/aliyun-release 2>/dev/null)
    if [ "$os_release" ] && [ "$os_release_2" ]
    then
      if echo "$os_release"|grep "release 5" >/dev/null 2>&1
      then
        os_release=aliyun5
        echo "$os_release"
      elif echo "$os_release"|grep "release 6" >/dev/null 2>&1
      then
        os_release=aliyun6
        echo "$os_release"
      elif echo "$os_release"|grep "release 7" >/dev/null 2>&1
      then
        os_release=aliyun7
        echo "$os_release"
      else
        os_release=""
        echo "$os_release"
      fi
      break
    fi
    os_release_2=$(grep "CentOS" /etc/*release 2>/dev/null)
    if [ "$os_release_2" ]
    then
      if echo "$os_release_2"|grep "release 5" >/dev/null 2>&1
      then
        os_release=centos5
        echo "$os_release"
      elif echo "$os_release_2"|grep "release 6" >/dev/null 2>&1
      then
        os_release=centos6
        echo "$os_release"
      elif echo "$os_release_2"|grep "release 7" >/dev/null 2>&1
      then
        os_release=centos7
        echo "$os_release"
      else
        os_release=""
        echo "$os_release"
      fi
      break
    fi
    os_release=$(grep -i "ubuntu" /etc/issue 2>/dev/null)
    os_release_2=$(grep -i "ubuntu" /etc/lsb-release 2>/dev/null)
    if [ "$os_release" ] && [ "$os_release_2" ]
    then
      if echo "$os_release"|grep "Ubuntu 10" >/dev/null 2>&1
      then
        os_release=ubuntu10
        echo "$os_release"
      elif echo "$os_release"|grep "Ubuntu 12.04" >/dev/null 2>&1
      then
        os_release=ubuntu1204
        echo "$os_release"
      elif echo "$os_release"|grep "Ubuntu 12.10" >/dev/null 2>&1
      then
        os_release=ubuntu1210
        echo "$os_release"
     elif echo "$os_release"|grep "Ubuntu 14.04" >/dev/null 2>&1
     then
        os_release=ubuntu1204
        echo "$os_release" 
      else
        os_release=""
        echo "$os_release"
      fi
      break
    fi
    os_release=$(grep -i "debian" /etc/issue 2>/dev/null)
    os_release_2=$(grep -i "debian" /proc/version 2>/dev/null)
    if [ "$os_release" ] && [ "$os_release_2" ]
    then
      if echo "$os_release"|grep "Linux 6" >/dev/null 2>&1
      then
        os_release=debian6
        echo "$os_release"
      elif echo "$os_release"|grep "Linux 7" >/dev/null 2>&1
      then
        os_release=debian7
        echo "$os_release"
      else
        os_release=""
        echo "$os_release"
      fi
      break
    fi
    break
    done
}

os_release=$(check_os_release)

getProcess(){
  local IFS=$'\n'
  local OLDIFS="$IFS"
  SERVER=`ss -npa  2>/dev/null | grep -E 'tcp|udp' |awk -F' ' '{print $1,$2,$5,$6,$7}'`
  echo -e "[\c"
  for line in $SERVER
    do
      protocol=`echo $line  | awk '{print $1}'`
      state=`echo $line | awk '{print $2}'`
      local_addr=`echo $line | awk '{print $3}'|awk -F: '{print $(NF-1)}'|awk -F] '{print $(NF-1)}' 2>/dev/null`
      local_port=`echo $line | awk '{print $3}'|awk -F: '{print $NF}'`
      foreign_addr=`echo $line | awk '{print $4}'|awk -F: '{print $(NF-1)}'|awk -F] '{print $(NF-1)}' 2>/dev/null`
      foreign_port=`echo $line | awk '{print $4}'|awk -F: '{print $NF}'`
      app=`echo $line | awk '{print $5}'| awk -F "[\"\"]" '{print $2}'`
      if [ "$state" = "LISTEN" ] || [ "$state" = "UNCONN" ]; then
          continue;
      else
        echo "{\"protocol\":\"$protocol\",\"state\":\"$state\",\"app\":\"$app\", \
          \"local_addr\":\"$local_addr\",\"local_port\":\"$local_port\", \
          \"foreign_addr\":\"$foreign_addr\",\"foreign_port\":\"$foreign_port\"}"
      fi
    done | sed '$!s/$/,/'
  echo -e "]\c"
}

echo $(getProcess)

