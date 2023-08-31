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
    os_release=$(grep -i "SUSE" /etc/issue 2>/dev/null)
    if [ "$os_release" ]
    then
      if echo "$os_release"|grep "10" >/dev/null 2>&1
      then
        os_release=suse10
        echo "$os_release"
      elif echo "$os_release"|grep "11" >/dev/null 2>&1
      then
        os_release=suse11
        echo "$os_release"
      else
        os_release=suse
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
    # 中标麒麟
    os_release=$(grep -i "NeoKylin" /etc/issue 2>/dev/null)
    if [ "$os_release" ]
    then
      if echo "$os_release"|grep "6.0" >/dev/null 2>&1
      then
        os_release=NeoKylin
        echo "$os_release"
      elif echo "$os_release"|grep "7.0" >/dev/null 2>&1
      then
        os_release=NeoKylin
        echo "$os_release"
      else
        os_release=NeoKylin
        echo "$os_release"
      fi
      break
    fi
    # 银河麒麟
    os_release=$(grep -i "Kylin" /etc/os-release  2>/dev/null)
    if [ "$os_release" ]
    then
      if echo "$os_release"|grep "V10" >/dev/null 2>&1
      then
        os_release=Kylin
        echo "$os_release"
      elif echo "$os_release"|grep "V11" >/dev/null 2>&1
      then
        os_release=Kylin
        echo "$os_release"
      else
        os_release=Kylin
        echo "$os_release"
      fi
      break
    fi
    break
  done
}

os_release=$(check_os_release)

#网卡信息
get_net(){
  echo -e "[\c"
  DEV=`ip address 2>/dev/null|grep ^[0-9] |awk -F: '{print $2}' |sed "s/ //g" |grep '^[ebp]'`
  for I in $DEV
  do
    speed=`ethtool $I 2>/dev/null| grep "Speed" |awk -F: '{print $2}'`
    link=`ip address show $I 2>/dev/null| grep -E "UP|DOWN" | awk -F" " '{print $9}'`
    hwaddr=`ip address show $I 2>/dev/null| grep "link/" | sed 's/^[ \t]*//;s/[ \t]*$//' | awk -F" " '{print $2}'`
    ip=`ip address show $I 2>/dev/null| grep -w "inet" |sed "s/^[ \t]*//g" |awk -F" " '{print $2}'`
    subnet=`echo $ip | awk -F'/' '{print $2}'`
    gateway=`ip route show 2>/dev/null | grep default | awk '{print $3}'`
    echo -e "{\"name\":\"$I\",\"speed\":\"$speed\",\"link\":\"$link\",\"mac\":\"$hwaddr\",\"ip\":\"$ip\",\"subnet\":\"$subnet\",\"gateway\":\"$gateway\"}"
  done | sed '$!s/$/,/'
  echo -e "]\c"
}

get_cpu(){
    i=0
    for id in `grep 'processor' /proc/cpuinfo |awk -F: '{print $2}'`;do
        i=$((i+1))
    done

    ii=0
    echo -e "[\c"
    cpu=`grep 'model name' /proc/cpuinfo |awk -F: '{print $2}'`
    echo "$cpu" | while read line;do
        ii=$((ii+1))
        if [ "$ii" == $i ];
        then
            echo -e "{\"id\":\"CPU$((ii-1))\",\"name\":\"$line\"}"
        else
            echo -e "{\"id\":\"CPU$((ii-1))\",\"name\":\"$line\"},"
        fi
    done
    echo -e "]\c"
}

#磁盘使用情况
get_disk(){
  echo -e "[\c"
    DEV=`df -hPl 2>/dev/null | grep '^/dev/*' | cut -d' ' -f1 | sort`
    for I in $DEV
    do 
      dev=`df -TPl 2>/dev/null | grep $I | awk '{print $1}'`
      dev_type=`df -TPl 2>/dev/null | grep $I | awk '{print $2}'`
      size=`df -TPl 2>/dev/null | grep $I | awk '{print $3}'`
      used=`df -TPl 2>/dev/null | grep $I | awk '{print $4}'`
      free=`df -TPl 2>/dev/null | grep $I | awk '{print $5}'`
      use_per=`df -TPl 2>/dev/null | grep $I | awk '{print $6}'`
      mount=`df -TPl 2>/dev/null | grep $I | awk '{print $7}'`
      #echo -e "{\"name\":\"$I\",\"dev_type\":\"$dev_type\",\"size\":\"$size\",\"used\":\"$used\",\"freespace\":\"$free\",\"use_per\":\"$use_per\",\"filesystem\":\"$mount\"}"
      echo -e "{\"dev_type\":\"$dev_type\",\"size\":\"$size\",\"used\":\"$used\",\"freespace\":\"$free\", \"filesystem\":\"$mount\"}"
    done | sed '$!s/$/,/'
  echo -e "]\c"
}

# suse grep -i "SUSE" /etc/SuSE-release
#获取centos信息
get_info(){
  os_sys=`uname -o`
  host_name=`hostname`
  product_id=`dmidecode -t 1 2>/dev/null| grep Serial | awk -F: '{ print $2 }'`
  if [[ ! -n $product_id ]];then
    product_id='Permission denied'
  fi
  if [[ $os_release =~ 'ubuntu' ]];then
    os_version=`grep -i "ubuntu" /etc/issue | awk -F' ' '{print $1$2$3}' 2>/dev/null`
    # mem_used=`free -m |grep -i mem |awk '{print $3/$2*100,"%"}'`
    mem_used=`free -m |grep -i mem | awk '{printf "%0.2f",$3/$2*100}'`%
  elif [[ $os_release =~ 'centos' ]];then
    os_version=`cat /etc/redhat-release 2>/dev/null`
    # mem_used=`free -m |grep -i mem |awk '{print $3/$2*100,"%"}'`
    mem_used=`free -m |grep -i mem | awk '{printf "%0.2f",$3/$2*100}'`%
  elif [[ $os_release =~ 'redhat' ]];then
    os_version=`cat /etc/redhat-release 2>/dev/null`
    # mem_used=`free -m |grep -i mem |awk '{print $3/$2*100,"%"}'`
    mem_used=`free -m |grep -i mem | awk '{printf "%0.2f",$3/$2*100}'`%
  elif [[ $os_release =~ 'suse' ]];then
    os_version=`lsb_release -a 2>/dev/null | grep Description | awk -F: '{ print $2 }'`
    # mem_used=`free -m |grep -i mem |awk '{print $3/$2*100,"%"}'`
    mem_used=`free -m |grep -i mem | awk '{printf "%0.2f",$3/$2*100}'`%
  else
    os_version=`cat /etc/os-release  2>/dev/null | grep PRETTY_NAME | awk -F '"' '{print $2}'`
    if test -z "$os_version"; then
      os_version=`lsb_release -a 2>/dev/null | grep Description | awk -F: '{ print $2 }'`
    elif  test -z "$os_version"; then
      os_version='Not supported'
    fi
    # mem_used=`free -m |grep -i mem |awk '{print $3/$2*100,"%"}'`
    mem_used=`free -m |grep -i mem | awk '{printf "%0.2f",$3/$2*100}'`%
  fi
  os_kernel=`uname -r`

  cpu_core=`cat /proc/cpuinfo| grep 'physical id'| sort| uniq| wc -l`
  cpu_num=`grep 'cpu cores' /proc/cpuinfo |uniq |awk -F : '{print $2}'`
  logic_cpu=`cat /proc/cpuinfo| grep 'processor' | wc -l`
  cpu_load=`cat /proc/loadavg | awk '{print $1}'`
  mem_total=$(cat /proc/meminfo | awk -F ' ' 'NR==1{print $2}')
  disk_total=`cat /proc/partitions | grep -w "0" |grep -E -i -w 'sd[[:alpha:]]|vd[[:alpha:]]' | awk '{print $3}'|awk '{sum+=$1} END {print sum}'`

  # SUSE lsblk -m | grep -E -i 'disk|磁盘' | grep -E -i 'sd|vd'  | awk 'NR==1{ print $2 }'
  net_detial=$(get_net)
  cpu_detial=$(get_cpu)
  disk_detial=$(get_disk)
  install_date=`ls -lact --full-time /etc/ | awk 'END {print $6,$7,$8}'`
  # uptime=`uptime -s`
  uptime=`date -d "$(awk -F. '{print $1}' /proc/uptime) second ago" +"%Y-%m-%d %H:%M:%S"`

  echo "{\
    \"system_type\":\"$os_sys\",\
    \"hostname\":\"$host_name\",
    \"system_version\":\"$os_version\",\
    \"os_kernel\":\"$os_kernel\",\
    \"cpu_num\":\"$cpu_num\",\
    \"cpu_core\":\"$cpu_core\",\
    \"logic_cpu\":\"$logic_cpu\",\
    \"mem_total\":\"$mem_total\",\
    \"cpu_load\":\"$cpu_load\",
    \"mem_used\":\"$mem_used\",
    \"product_id\":\"$product_id\",\
    \"disk_total\":\"$disk_total\",\
    \"install_date\":\"$install_date\",\
    \"uptime\":\"$uptime\",\
    \"network\":$net_detial,\
    \"cpu_model\":$cpu_detial,\
    \"logicdisk\":$disk_detial
  }"
}

echo $(get_info)

