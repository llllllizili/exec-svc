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
      elif echo "$os_release"|grep "Ubuntu 16.04" >/dev/null 2>&1
      then
        os_release=ubuntu1604
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




# 进程,应用详情
get_app(){
  local IFS=$'\n'
  local OLDIFS="$IFS"
  SERVER=`ps -e -o 'pid,ppid,user,pcpu,rsz,lstart,comm,args' 2>/dev/null| grep -v __jk_ |awk -F' ' '{print $0}'| sed '1d'`
  # NETSTAT=`netstat -ntulpa 2>/dev/null| grep -E 'tcp|udp'`
  SS=`ss -ntulpa  2>/dev/null | grep -E 'tcp|udp' |awk '{print $1,$2,$5,$6,$7}'`
  echo -e "[\c"
  for line in $SERVER
    do
      #echo $line
      PID=`echo $line | awk '{print $1}'`
      P_PID=`echo $line | awk '{print $2}'`
      USER=`echo $line | awk '{print $3}'`
      CPU_USE=`echo $line | awk '{print $4}'`
      MEM_USE=`echo $line | awk '{print $5}'`
      START_TIME=`echo $line | awk '{print $6,$7,$8,$9,$10}'`
      COMMAND=`echo $line | awk '{print $11}'`

      INSTALL_DIR=`pwdx $PID 2>/dev/null| awk -F: '{print $2}'  2>/dev/null`
      if [[ $INSTALL_DIR == ' /' ]]; then
        INSTALL_DIR=`whereis ${COMMAND%*d} 2>/dev/null | awk '{print $NF}'`
        if [[ $INSTALL_DIR =~ '.gz' ]]; then
          INSTALL_DIR=`whereis  ${COMMAND%*d} 2>/dev/null | awk '{print $(NF-1)}'`
          if [[ $INSTALL_DIR =~ ':' ]]; then
            INSTALL_DIR=`whereis  $COMMAND 2>/dev/null | awk '{print $(NF-1)}'`
          fi
        fi
      fi
      ARGS=$(echo $line | awk '{for(i=1;i<11;i++)$i="";print}' | sed "s/\"//g" |sed "s/'//g" | sed "s/\\\//g")
      APP_PORT=`echo "$SS" | grep $PID | awk '{print $3}' | awk 'END{print $1}'|awk -F: '{print $(NF)}'`
      STATE=`echo "$SS" | grep $PID | awk '{print $2,$5}' | awk 'END{print $1}'`
      NUM=`echo "$SS" | grep $PID | wc -l`
      if [[ $P_PID -eq '0' ]] || [[ $P_PID -eq '2' ]]; then
      # if [[ $P_PID -eq '0' ]] || [[ $P_PID -eq '1' ]] || [[ $P_PID -eq '2' ]] || [[ $NUM -eq '0' ]]; then
        continue
      else
        echo -e "{\"pid\":\"$PID\",\"ppid\":\"$P_PID\", \"install_dir\":\"$INSTALL_DIR\", \
                  \"user\":\"$USER\",\"cpu_use\":\"$CPU_USE\", \
                  \"mem_use\":\"$MEM_USE\",\"start_time\":\"$START_TIME\", \
                  \"command\":\"$COMMAND\",\"args\":\"${ARGS}\", \
                  \"port\":\"$APP_PORT\",\"state\":\"$STATE\",\"num\":\"$NUM\"}"
      fi
  done | sed '$!s/$/,/'
  echo -e "]\c"
}

echo $(get_app)
