要在此目录的上上级使用,即 /opt/jkexec 下



基础镜像构建，当venv 或 os依赖变化时，更改
docker build -f Dockerfile-base-image -t harbor.jkstack.com/sre/base_image:v1 .


服务镜像构建

docker build -t harbor.jkstack.com/jkstack/sre/exec_engine:v1.16.1 .