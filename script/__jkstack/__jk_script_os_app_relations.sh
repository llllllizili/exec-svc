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
# tcp ESTAB 192.168.3.210:37567 192.168.3.130:5673 users:(("celery",pid=2094,fd=123))
# get_relations(){
#   echo -e "[\c"
#     local IFS=$'\n'
#     local OLDIFS=$IFS
#     SERVER=`ss -4pn 2>/dev/null |awk 'NR!=1 {print $1,$2,$5,$6,$7}'`
#     for line in $SERVER
#       do
#         protocol=`echo $line  | awk '{print $1}'`
#         state=`echo $line | awk '{print $2}'`
#         localAddr=`echo $line | awk '{print $3}'|awk -F: '{print $(NF-1)}'`
#         localPort=`echo $line | awk '{print $3}'|awk -F: '{print $NF}'`
#         foreignAddr=`echo $line | awk '{print $4}'|awk -F: '{print $(NF-1)}'`
#         foreignPort=`echo $line | awk '{print $4}'|awk -F: '{print $NF}'`
#         app=`echo $line | awk '{print $5}'| awk -F'"' '{print $2}'`
#         echo -e "{\"protocol\":\"$protocol\",\"app\":\"$app\",\"local_addr\":\"$localAddr\",\"local_port\":\"$localPort\",\"foreign_addr\":\"$foreignAddr\",\"foreign_port\":\"$foreignPort\",\"state\":\"$state\"}"
#       done | sed '$!s/$/,/'
#   echo -e "]\c"
# }

# ESTAB 172.17.0.1:39752 172.17.0.3:5672 users:(("docker-proxy",pid=3583,fd=5))
get_relations(){
  echo -e "[\c"
    local IFS=$'\n'
    local OLDIFS=$IFS
   # SERVER=`ss -tpn 2>/dev/null |awk 'NR!=1 {print $1,$4,$5,$6}'`
    SERVER=`ss -tpna 2>/dev/null |awk 'NR!=1 {print $1,$4,$5,$6}'`

    for line in $SERVER
      do
        protocol='tcp'
        state=`echo $line | awk '{print $1}'`
        if [[ "$line" =~ ':ffff:' ]]; then
          localAddr=`echo $line | awk '{print $2}'|awk -F: '{print $(NF-1)}'|awk -F']' '{print $1}'`
          foreignAddr=`echo $line | awk '{print $3}'|awk -F: '{print $(NF-1)}'|awk -F']' '{print $1}'`
        elif [[ "$state" == 'LISTEN' ]]; then
          #localAddr=`echo $line | awk '{print $2}'|awk -F: '{print $(NF-1)}'|awk -F']' '{print $1}'`
          localAddr=`echo $line | awk '{print $2}'|awk -F : '{print $(NF-1)}'`
          foreignAddr=`echo $line | awk '{print $3}'|awk -F: '{print $(NF-1)}'`
          if [[ "$localAddr" =~ ']' ]]; then
            localAddr='[::'$localAddr
          fi
          if [[ "$foreignAddr" =~ ']' ]]; then
            foreignAddr='[::'$foreignAddr
          fi
        else
          localAddr=`echo $line | awk '{print $2}'|awk -F: '{print $(NF-1)}'`
          foreignAddr=`echo $line | awk '{print $3}'|awk -F: '{print $(NF-1)}'`
        fi


        localPort=`echo $line | awk '{print $2}'|awk -F: '{print $NF}'`
        foreignPort=`echo $line | awk '{print $3}'|awk -F: '{print $NF}'`
        app=`echo $line | awk '{print $4}'| awk -F'"' '{print $2}'`
        pid=`echo $line | awk '{print $4}'| awk -F',' '{print $2}' | awk -F'=' '{print $2}'`
        if [[ "$os_release" == 'centos6' ]]; then
          pid=`echo $line | awk '{print $4}'| awk -F',' '{print $2}' `
        fi
        echo -e "{\"protocol\":\"$protocol\",\"app\":\"$app\",\"local_addr\":\"$localAddr\",\"local_port\":\"$localPort\",\"foreign_addr\":\"$foreignAddr\",\"foreign_port\":\"$foreignPort\",\"state\":\"$state\",\"pid\":\"$pid\"}"
      done | sed '$!s/$/,/'
  echo -e "]\c"
}

echo $(get_relations)
