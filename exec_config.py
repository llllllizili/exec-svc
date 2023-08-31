#!/usr/bin python
# -*- encoding: utf-8 -*-

# 执行引擎名字定义: 如华东01 IP地址 等有意义的定义
EXEC_ENGINE_NAME = "ShangHaiWanGU-A8"
# 执行引擎IP
EXEC_ENGINE_IP = "127.0.0.1"   
# 若未部署DPA则: DPA_ADDRESS = None  
DPA_ADDRESS = "127.0.0.1"  

# 集群则填多个es地址,逗号分隔
ELASTIC_SEARCH = {
    'hosts': ['http://192.168.3.183:9200/']
    # 'hosts': ['http://username:password@192.168.3.183:9200/'] # basic认证开启时填写格式
}
#异步队列mq集群
# MQ集群SSL认证， True: 启用MQ-SSL  ， False: 禁用MQ-SSL
ENABLE_CELERY_MQ_CLUSTER_SSL = False
# 不同区域zone不同 , 若SSL则格式为 ['amqps://admin:admin@127.0.0.1:5671/zone01']
CELERY_MQ_CLUSTER = [
    'amqp://admin:admin@192.168.3.130:5672/zone01',
    # 'amqps://admin:admin@127.0.0.1:5671/zone01',  
]

#其他产品mq集群
# MQ集群SSL认证， True: 启用MQ-SSL  ， False关闭MQ-SSL
ENABLE_OTHER_MQ_CLUSTER_SSL = False
# 不同区域zone不同 , 若SSL则格式为 ['amqps://admin:admin@127.0.0.1:5671/zone01']
OTHER_MQ_CLUSTER = [
    'amqp://admin:admin@192.168.3.130:5672/',
    # 'amqps://admin:admin@192.168.6.71:5671/',
]

# SmartAgent config
SMART_AGENT_SERVER = {
    'host': '192.168.3.147',
    'port': 13080
}

# 异步任务设置
WORKER_EXEC_CONCURRENCY = 8         # WORKER进程数,通常为CPU数, 或 *2
WORKER_PREFETCH_MULTIPLIER = 20     # WORKER预取任务数量
WORKER_TASK_TIMEOUT = 7200          # 任务超时时间, 默认 1200秒