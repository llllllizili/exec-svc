# README


![](./images/架构图.png)


![](./images/调用关系.png)


[测试报告](https://github.com/llllllizili/zbx-wechat/blob/main/images/ExecutionEnginePerformanceTestReport.pdf)

# 安转

## CentOS 7

yum install -y  openssl-devel wget expect  sshpass net-snmp-utils net-tools openssh-clients ipmitool

sh install_on_os.sh
## docker cli

```shell
docker run --rm -it -p 8093:8093 -p 9001:9001 --name exec \
-e EXEC_ENGINE_NAME="SH-WG-A8-Zone01" \
-e EXEC_ENGINE_IP="127.0.0.1" \
-e DPA_ADDRESS="127.0.0.1" \
-e EXEC_WORKER_CONCURRENCY='4' \
-e EXEC_WORKER_TASK_TIMEOUT='1200' \
-e ELASTICSEARCH_ADDR='http://127.0.0.1:9200/' \
-e EXEC_RABBITMQ_ADDR='amqp://admin:admin@127.0.0.1:5672/zone01' \
-e PUBLIC_RABBITMQ_ADDR='amqp://admin:admin@127.0.0.1:5672/' \
-e SMART_AGENT_SERVER_ADDR='127.0.0.1' \
-e SMART_AGENT_SERVER_PORT='13081' \
harbor.jkstack.com/sre/exec_engine:v1.16.1
```

9001 可选，supervisor服务端口