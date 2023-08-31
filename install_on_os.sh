#!/bin/bash
TAR_PATH=$(cd `dirname $0`; pwd)

if [ $TAR_PATH != '/opt/jkexec/jksreExecEngine' ]; then
    echo -e "\033[31m 请将包放置/opt下解压执行.\033[0m"
    exit 1
fi

PKG_PATH=$TAR_PATH/require-on-os
JKSRE_CFG_HOME=~/.jkjk

Start_Exec(){
    if [ ! -L /usr/bin/supervisord ]; then
        ln -s $TAR_PATH/../venv/bin/supervisord /usr/bin/supervisord
        ln -s $TAR_PATH/../venv/bin/supervisorctl /usr/bin/supervisorctl
    fi
}

Install_Jkexec(){

    JKEXEC=/usr/lib/systemd/system/jkexec.service

    if [ ! -f "$JKEXEC" ]; then
      touch "$JKEXEC"
    fi
    cat $PKG_PATH/jkexec.service > "$JKEXEC"

    systemctl daemon-reload
    systemctl enable jkexec
    systemctl start jkexec

    echo -e "\e[1;32m 服务安装成功 [jkexec install success] \e[0m"
    echo -e "\e[1;32m systemctl status jkexec \e[0m"
}

Install_Service(){
    # 安装依赖
    # echo -e "\e[1;33m 安装依赖 [ dependent packages will install ] \e[0m"

    # yum install -y expect sshpass net-snmp-utils net-tools ipmitool
    
    if [ $? != 0 ]; then
        echo 'ERROR: dependent packages installed failed'
    fi

    COUNT_SNMP=$(rpm -qa | grep net-snmp-utils | wc -l)
    if [ $COUNT_SNMP -eq 0 ]; then
        echo -e "\033[31m 请安装net-snmp-utils [Please install net-snmp-utils ] \033[0m"
        exit 1
    fi
    COUNT_IPMI=$(rpm -qa | grep ipmitool | wc -l)
    if [ $COUNT_IPMI -eq 0 ]; then
        echo -e "\033[31m 请安装ipmitool [Please install ipmitool ] \033[0m"
        exit 1
    fi
    COUNT_expect=$(rpm -qa | grep expect | wc -l)
    if [ $COUNT_expect -eq 0 ]; then
        echo -e "\033[31m 请安装expect [Please install expect ] \033[0m"
        exit 1
    fi
    COUNT_sshpass=$(rpm -qa | grep sshpass | wc -l)
    if [ $COUNT_sshpass -eq 0 ]; then
        echo -e "\033[31m 请安装sshpass [Please install sshpass ] \033[0m"
        exit 1
    fi
    COUNT_net_tools=$(rpm -qa | grep net-tools | wc -l)
    if [ $COUNT_net_tools -eq 0 ]; then
        echo -e "\033[31m 请安装net-tools [Please install net_tools ] \033[0m"
        exit 1
    fi

    
    if [ ! -d "$PKG_PATH/python3" ]; then
        tar -zxvf $PKG_PATH/python3.tar.gz -C $PKG_PATH
    fi

    if [ ! -d "$JKSRE_CFG_HOME" ]; then
        mkdir $JKSRE_CFG_HOME
        cp -r $PKG_PATH/../sysconfig/ansible $JKSRE_CFG_HOME
        cp -r $PKG_PATH/../sysconfig/salt $JKSRE_CFG_HOME
        chmod -R 777 $JKSRE_CFG_HOME
    fi

    
    if [ -L /etc/ansible ]; then
        echo -e "\e[1;33m ansible配置已存在[Ansible configuration already exists] \e[0m"
    else
        echo -e "\e[1;33m 配置ansible[Configure ansible] \e[0m"
        ln -s $JKSRE_CFG_HOME/ansible/ /etc/ > /dev/null 2>&1
        cd ~
        SSH_KEY=`pwd`/.ssh/id_rsa.pub
        if [[ -f $SSH_KEY ]]; then
            echo -e "\e[1;32m 密钥已生成[Key already exists] \e[0m"
        else
            cd ~ && mkdir .ssh
            cp -a $PKG_PATH/../sysconfig/sshkey/* .ssh/
            chmod -R 600  .ssh/
        fi
        echo -e "\e[1;33m ansible配置完成[Configuration completed] \e[0m"
    fi

    if [ -L /etc/salt ]; then
        echo -e "\e[1;33m salt配置已存在[salt configuration already exists] \e[0m"
    else
        echo -e "\e[1;33m 配置salt[Configure salt] \e[0m"
        ln -s $JKSRE_CFG_HOME/salt/ /etc/ > /dev/null 2>&1
        echo -e "\e[1;33m salt配置完成[Configuration completed] \e[0m"
    fi
    chmod a+x $PKG_PATH/*.sh
    Start_Exec
    Install_Jkexec
}

Install_Service
