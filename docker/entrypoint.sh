#!/bin/bash

TAR_PATH='/opt/jkexec/jksreExecEngine'

JKSRE_CFG_HOME=~/.jkjk

OS_Env_Check(){
    if [ ! -d "$JKSRE_CFG_HOME" ]; then
        mkdir $JKSRE_CFG_HOME
        cp -r $TAR_PATH/sysconfig/ansible $JKSRE_CFG_HOME
        cp -r $TAR_PATH/sysconfig/salt $JKSRE_CFG_HOME
        chmod -R 777 $JKSRE_CFG_HOME
    fi
    
    if [ ! -d "$TAR_PATH/require-on-os/python3" ]; then
        tar -zxvf $TAR_PATH/require-on-os/python3.tar.gz -C $TAR_PATH/require-on-os/
        echo -e "\e[1;33m Python3环境初始化完成[Configuration completed] \e[0m"
    fi
    
    if [ -L /etc/ansible ]; then
        echo -e "\e[1;33m ansible配置已存在[Ansible configuration already exists] \e[0m"
    else
        ln -s $JKSRE_CFG_HOME/ansible/ /etc/ > /dev/null 2>&1
        cd ~
        SSH_KEY=`pwd`/.ssh/id_rsa.pub
        if [[ -f $SSH_KEY ]]; then
            echo -e "\e[1;32m 密钥已生成[Key already exists] \e[0m"
        else
            cd ~ && mkdir .ssh
            cp -a $TAR_PATH/sysconfig/sshkey/* .ssh/
            chmod -R 600  .ssh/
        fi
        echo -e "\e[1;33m ansible配置完成[Configuration completed] \e[0m"
    fi

    if [ -L /etc/salt ]; then
        echo -e "\e[1;33m salt配置已存在[salt configuration already exists] \e[0m"
    else
        ln -s $JKSRE_CFG_HOME/salt/ /etc/ > /dev/null 2>&1
        echo -e "\e[1;33m salt配置完成[Configuration completed] \e[0m"
    fi
    chmod a+x /opt/jkexec/jksreExecEngine/require-on-os/on-docker/*.sh
    touch /var/log/jkexec.log
}

App_Config(){
    cd $TAR_PATH
    cp -a exec_config_template.py exec_config_env.py
    sed -i "/^EXEC_ENGINE_NAME/c EXEC_ENGINE_NAME = \"$EXEC_ENGINE_NAME\"" exec_config_env.py
    sed -i "/^EXEC_ENGINE_IP/c EXEC_ENGINE_IP = \"$EXEC_ENGINE_IP\"" exec_config_env.py
    sed -i "/^DPA_ADDRESS/c DPA_ADDRESS = \"$DPA_ADDRESS\"" exec_config_env.py
    # celery
    sed -i "/^WORKER_EXEC_CONCURRENCY/c WORKER_EXEC_CONCURRENCY = $EXEC_WORKER_CONCURRENCY" exec_config_env.py
    sed -i "/^WORKER_TASK_TIMEOUT/c WORKER_TASK_TIMEOUT = $EXEC_WORKER_TASK_TIMEOUT" exec_config_env.py
    # MQ
    sed -i "s*EXEC_MQ_CLUSTER_ADDR*$EXEC_RABBITMQ_ADDR*g" exec_config_env.py
    sed -i "s*PUBLIC_MQ_CLUSTER_ADDR*$PUBLIC_RABBITMQ_ADDR*g" exec_config_env.py
    # es
    sed -i "s*ELASTIC_SEARCH_ADDR*$ELASTICSEARCH_ADDR*g" exec_config_env.py
    # smartagaent
    sed -i "s*SMART_AGENT_SERVER_ADDR*$SMART_AGENT_SERVER_ADDR*g" exec_config_env.py
    sed -i "s/SMART_AGENT_SERVER_PORT/$SMART_AGENT_SERVER_PORT/g" exec_config_env.py
    cat exec_config_env.py > exec_config.py

    # 如果设置了BUG变量，日志基本改为DEBUG
    if [ $DEBUG_TASK ];then
        sed -i "s/DEBUG = False/DEBUG = True/g" jksreExecEngine/settings.py # Django 开启debug
        sed -i "s/ERROR/DEBUG/g" jksreExecEngine/settings.py # 日志开启debug
    fi

}

OS_Env_Check

App_Config

/opt/jkexec/venv/bin/supervisord -c /opt/jkexec/jksreExecEngine/require-on-os/on-docker/supervisord.conf && tail -f /var/log/jkexec.log