#!/bin/ksh
source /etc/profile >/dev/null 2>&1
:<< 'PlutoChan'
if [ $# != 2 ] ; then
  echo "USAGE: $0 NGINX_IP LOCAL_IP"
  echo "Example: $0 10.192.56.9 10.192.85.132"
  exit 1;
fi
PlutoChan

check_os_release()
{
  while true
  do
    os_release=$(oslevel -r)
    if [ "$os_release" ]
    then
      if echo "$os_release"|grep "5300" >/dev/null 2>&1
      then
        os_release=aix53
        echo "$os_release"
      elif echo "$os_release"|grep "6100" >/dev/null 2>&1
      then
        os_release=aix61
        echo "$os_release"
      elif echo "$os_release"|grep "7100" >/dev/null 2>&1
      then
        os_release=aix71
        echo "$os_release"
      elif echo "$os_release"|grep "7200" >/dev/null 2>&1
      then
        os_release=aix72
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


get_net(){
  echo  "[\c"
  DEV=`ifconfig -a |awk -F: '{print $1}'|grep '^[ebp]'`
  for I in $DEV
  do
    speed=`entstat -d $I | grep "^Media Speed Running" |awk -F: '{print $2}'`
    link=`entstat -d $I | egrep "^(Link Status|Port Operational State)" |awk -F: '{print $2}'`
    hwaddr=`entstat -d $I | grep "^Hardware Address" |awk -F" " '{print $3}'`
    ip=`ifconfig $I | grep -w "inet" |awk -F" " '{print $2}'|head -1`
    subnet=`netstat -rn |egrep $ip| egrep '/' |cut -d" " -f1 | awk -F'/' '{print $2}'`
    gateway=`netstat -rn | grep default | awk '{print $2}'`
    #gateway=`prtconf | grep Gateway | awk -F: '{print $2}'`
    echo  "{\"name\":\"$I\",\"speed\":\"$speed\",\"link\":\"$link\",\"mac\":\"$hwaddr\",\"ip\":\"$ip\",\"subnet\":\"$subnet\",\"gateway\":\"$gateway\"}"
  done | sed '$!s/$/,/'
  echo  "]\c"
}


get_cpu(){
    num=`pmcycles -m | wc -l`

    echo  "[\c"
    model=`prtconf | grep '^Processor Type' |awk -F: '{print $2}'`
    #for ((i=0; i<=$num; i+=1)); do
    i=0
    while [ "$i" -lt "$num" ]
    do
        if [ "$i" -eq "$(($num-1))" ]
        then
            echo  "{\"id\":\"CPU$i\",\"name\":\"$model\"}"
        else
            echo  "{\"id\":\"CPU$i\",\"name\":\"$model\"},"
        fi
        #$((i++))
        i=$(($i+1))
    done
    echo  "]\c"
}


get_disk(){
  echo "[\c"
    DEV=`df -g| grep '^/dev/*' | cut -d' ' -f1 | sort`
    #DEV=`df -hPl| grep '^/dev/*' | cut -d' ' -f1 | sort`
    for I in $DEV
    do
      dev=`df -gI| grep $I | awk '{print $1}'`
      lv=`echo $I |sed 's!/dev/!!'`
      dev_type=`lsvg -l rootvg | grep -w $lv | awk '{print $2}'`
      size=`df -gI | grep $I | awk '{print $2}'`
      used=`df -gI 2>/dev/null| grep $I | awk '{print $3}'`
      free=`df -gI 2>/dev/null| grep $I | awk '{print $4}'`
      use_per=`df -gI 2>/dev/null| grep $I | awk '{print $5}'`
      mount=`df -gI 2>/dev/null| grep $I | awk '{print $6}'`
      echo  "{\"name\":\"$I\",\"dev_type\":\"$dev_type\",\"size\":\"$size\",\"used\":\"$used\",\"free\":\"$free\",\"free_space\":\"$use_per\",\"filesystem\":\"$mount\"}"
    done | sed '$!s/$/,/'
  echo "]\c"
}


get_info(){
  os_sys=`uname -s`
  host_name=`hostname`
  product_id=`uname -u | awk -F, '{print $2}'`

  if [[ ! -n $product_id ]];then
    product_id='Permission denied'
  fi
  #if [[ $os_release =~ 'aix' ]];then
  if echo "$os_release"|grep "aix" >/dev/null 2>&1
  then
    os_version=`oslevel -s`
  fi
  os_kernel=$os_version
  cpu_num=`prtconf | grep '^Number Of Processors' | awk -F: '{print $2}'`
  #cpu_core=`grep 'cpu cores' /proc/cpuinfo |uniq |awk -F : '{print $2}'`
  logic_cpu=`pmcycles -m | wc -l`
  #cpu_load=`cat /proc/loadavg | awk '{print $1}'`
  #svmon -G
  #mem_total=$(cat /proc/meminfo | awk -F ' ' 'NR==1{print $2}')
  mem_total=$(svmon -G | grep ^memory |awk '{print $2}')
  #disks=`lspv|cut -d' ' -f1`
  #disk_total=0
  #for d in `lspv | cut -d' ' -f1`
  #disks=`lspv | awk '{print $1}'`
  #for d in $disks
  #do
  #  cap=`lspv $d | egrep '^TOTAL PPs'| awk '{print $4}'|sed 's/(//'`
  #  disk_total=$(($disk_total+$cap))
  #done
  #echo "disk total: " $disk_total
  #disk_total=`cat /proc/partitions | grep -w "0" |grep -E -i -w 'sd[[:alpha:]]|vd[[:alpha:]]' | awk '{print $3}'|awk '{sum+=$1} END {print sum}'`
  net_detail=$(get_net)
  cpu_detail=$(get_cpu)
  disk_detail=$(get_disk)
  install_date=`lslpp -h bos.mp* |egrep '[0-9]/[0-9]' | awk '{print $4,$5}'|head -1`
  #install_date=`ls -lact --full-time /etc/ | awk 'END {print $6,$7,$8}'`
  echo "{
    \"system_type\":\"$os_sys\",\
    \"hostname\":\"$host_name\",
    \"system_version\":\"$os_version\",\
    \"os_kernel\":\"$os_kernel\",\
    \"cpu_num\":\"$cpu_num\",
    \"logic_cpu\":\"$logic_cpu\",\
    \"mem_total\":\"$mem_total\",\
    \"product_id\":\"$product_id\",\
    \"disk_total\":\"no permission\",\
    \"install_date\":\"$install_date\",\
    \"network\":$net_detail,\
    \"cpu_model\":$cpu_detail,\
    \"logicdisk\":$disk_detail
  }"
  #\"cpu_core\":\"$cpu_core\",\
}



get_status(){
  #cpu_load=`cat /proc/loadavg 2>/dev/null| awk '{print $3}'` #前三个表示1,5,15min
  #MemTotal - MemFree - MemBuffers - MemCache
  os_release=aix53
  if echo "$os_release"|grep "aix" >/dev/null 2>&1;then
    mem_used=`svmon -G |grep -i mem |awk '{print $3/$2*100,"%"}'`
  fi
  disk_detail=$(get_disk)
  net_detail=$(get_net)

  echo "{
    \"mem_used\":\"$mem_used\",
    \"disk_detail\":$disk_detail,
    \"net_detail\":$net_detail
  }"
#\"cpu_load\":\"$cpu_load\",
}



get_relations(){
  #IFS=$'\n'
  #IFS='\n'
  OLDIFS="$IFS"
  IFS='
'
  SERVER=`netstat -an 2>/dev/null | grep ^tcp | grep 'ESTAB' |awk -F' ' '{print $1,$4,$5,$6}'`
  echo  "[\c"
  for line in $SERVER
  do
    protocol=`echo $line  | awk '{print $1}'`
    localAddr=`echo $line | awk '{print $2}'|awk -F. '{print $1"."$2"."$3"."$4}'`
    localPort=`echo $line | awk '{print $2}'|awk -F. '{print $NF}'`
    foreignAddr=`echo $line | awk '{print $3}'|awk -F. '{print $1"."$2"."$3"."$4}'`
    foreignPort=`echo $line | awk '{print $3}'|awk -F. '{print $NF}'`
    state=`echo $line | awk '{print $4}'`
    #app=`echo $line | awk '{print $5}'| awk -F'/' '{print $2}'`
    echo "{\"protocol\":\"$protocol\",\"local_addr\":\"$localAddr\",\"local_port\":\"$localPort\",\"foreign_addr\":\"$foreignAddr\",\"foreign_port\":\"$foreignPort\",\"state\":\"$state\"}"
  done | sed '$!s/$/,/'
  echo  "]\c"
  IFS="$OLDIFS"
}


get_app_details(){
  OLDIFS="$IFS"
  IFS='
'
  #抓进程的详情，pid,ppid,user,pcpu,rss,stime,comm,args，不支持rss
  #SERVER=`ps -e -o 'pid,ppid,user,pcpu,rsz,stime,comm,args' 2>/dev/null| awk -F' ' '{print $0}'| sed '1d'`
  SERVER=`ps -e -o 'pid,ppid,user,pcpu,stime,comm,args' 2>/dev/null| awk -F' ' '{print $0}'| sed '1d'`
  #NETSTAT=`netstat -ntlpa 2>/dev/null`
  echo  "[\c"
  for line in $SERVER
    do
      #echo $line
      PID=`echo $line | awk '{print $1}'`
      P_PID=`echo $line | awk '{print $2}'`
      USER=`echo $line | awk '{print $3}'`
      CPU_USE=`echo $line | awk '{print $4}'`
      #MEM_USE=`echo $line | awk '{print $5}'`
      START_TIME=`echo $line | awk '{print $5}'`
      COMMAND=`echo $line | awk '{print $6}'`

      #抓程序的安装目录，pwdx不能使用，whereis 可以使用
      #INSTALL_DIR=`pwdx $PID 2>/dev/null| awk -F: '{print $2}'  2>/dev/null`
      #if [[ $INSTALL_DIR == ' /' ]]; then
      #此段，用which命令似乎更方便
      INSTALL_DIR=`whereis ${COMMAND%*d} 2>/dev/null | awk '{print $NF}'`
      #if [[ $INSTALL_DIR =~ '.gz' ]]; then
      if echo $INSTALL_DIR |grep '.gz' ; then
        INSTALL_DIR=`whereis  ${COMMAND%*d} 2>/dev/null | awk '{print $(NF-1)}'`
        #if [[ $INSTALL_DIR =~ ':' ]]; then
        if echo $INSTALL_DIR |grep ':' ; then
          INSTALL_DIR=`whereis  $COMMAND 2>/dev/null | awk '{print $(NF-1)}'`
        fi
      fi
      #fi

      ARGS=`echo $line | awk '{for(i=1;i<8;i++)$i="";print}'`
      if echo $ARGS | grep '\\' ; then
        ARGS=''
      fi
      #APP_PORT=`echo "$NETSTAT" |awk '{print $4,$7}' | grep "\<$PID/"| awk 'END{print $1}'|awk -F: '{print $2}'`
      #STATE=`echo "$NETSTAT" |awk '{print $6,$7}' | grep "\<$PID/"| awk 'END{print $1}'`
      #NUM=`echo "$NETSTAT" | grep "\<$PID/"| wc -l`
      if [[ $P_PID -eq '0' ]] || [[ $P_PID -eq '2' ]]; then
        continue
      else
        echo  "{\"pid\":\"$PID\",\"ppid\":\"$P_PID\", \"install_dir\":\"$INSTALL_DIR\", \
                  \"user\":\"$USER\",\"cpu_use\":\"$CPU_USE\", \
                  \"start_time\":\"$START_TIME\", \
                  \"command\":\"$COMMAND\",\"args\":\"$ARGS\"}"
      fi
  done | sed '$!s/$/,/'
  echo  "]\c"
  IFS="$OLDIFS"
}



get_user_list(){
  OLDIFS="$IFS"
  IFS='
'
  USERLIST=`cat /etc/passwd 2>/dev/null | awk  -F ':' '{print $1,$3,$4}'`
  echo  "[\c"
  for line in $USERLIST
    do
      user=`echo $line  | awk '{print $1}'`
      uid=`echo $line | awk '{print $2}'`
      gid=`echo $line | awk '{print $3}'`
      echo "{\"user\":\"$user\",\"UID\":\"$uid\",\"GID\":\"$gid\"}"
    done | sed '$!s/$/,/'
  echo  "]\c"
  IFS="$OLDIFS"
}



verify_net(){
  echo  "\c"
  #与前面抓取网络相同，也是用ifconfig
  #DEV=`ip address |grep ^[0-9] |awk -F: '{print $2}' |sed "s/ //g" |grep '^[ebp]'`
  DEV=`ifconfig -a |awk -F: '{print $1}'|grep '^[ebp]'`
  for I in $DEV
  do
    hwaddr=`entstat -d $I | grep "^Hardware Address" |awk -F" " '{print $3}'`
    ip=`ifconfig $I | grep -w "inet" |awk -F" " '{print $2}'|head -1`
    echo "\"$I\":[\"$ip\",\"$hwaddr\"]"
  done | sed '$!s/$/,/'
  echo  "\c"
}


verify_info(){
  host_name=`hostname`
  sn=`uname -u | awk -F, '{print $2}'`
  #sn=`dmidecode -t 1 2>/dev/null| grep Serial | awk -F: '{ print $2 }'`
  if [[ ! -n $sn ]];then
    sn=':Permission denied'
  fi
  if echo "$os_release"|grep "aix" >/dev/null 2>&1
  then
    os_version=`oslevel -s`
  fi

  echo "{\"osfinger\":\"$os_version\",\"ip_interfaces\":{$(verify_net) }}" | tr '\n' ' '
}

echo "$(verify_info)"