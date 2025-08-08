#!/bin/bash

# Docker镜像导出和部署脚本
set -e

echo "=========================================="
echo "   Docker镜像导出和部署脚本"
echo "=========================================="
echo

# 设置变量
IMAGE_NAME="word2html-word2html"
IMAGE_TAG="latest"
EXPORT_FILE="${IMAGE_NAME}_${IMAGE_TAG}.tar"

echo "设置镜像名称: $IMAGE_NAME"
echo "设置镜像标签: $IMAGE_TAG"
echo "导出文件名: $EXPORT_FILE"
echo

# 检查Docker是否运行
echo "检查Docker服务状态..."
if ! docker version >/dev/null 2>&1; then
    echo "错误: Docker未运行或未安装！"
    echo "请先启动Docker服务"
    exit 1
fi
echo "Docker服务运行正常"
echo

# 构建Docker镜像
echo "开始构建Docker镜像..."
docker-compose build
echo "Docker镜像构建完成"
echo

# 导出Docker镜像
echo "开始导出Docker镜像到当前目录..."
docker save -o "$EXPORT_FILE" "$IMAGE_NAME:$IMAGE_TAG"
echo "Docker镜像导出完成: $EXPORT_FILE"
echo

# 显示文件信息
echo "导出文件信息:"
ls -lh "$EXPORT_FILE"
echo

echo "=========================================="
echo "   Ubuntu服务器部署命令"
echo "=========================================="
echo
echo "1. 将文件 $EXPORT_FILE 传输到Ubuntu服务器:"
echo "   scp $EXPORT_FILE username@server_ip:/path/to/destination/"
echo
echo "2. 在Ubuntu服务器上导入Docker镜像:"
echo "   docker load -i $EXPORT_FILE"
echo
echo "3. 运行Docker容器:"
echo "   docker run -d --name $IMAGE_NAME -p 5000:5000 -v /path/to/uploads:/app/uploads $IMAGE_NAME:$IMAGE_TAG"
echo
echo "4. 或者使用docker-compose运行（如果有docker-compose.yml文件）:"
echo "   docker-compose up -d"
echo
echo "5. 查看运行状态:"
echo "   docker ps"
echo
echo "6. 查看日志:"
echo "   docker logs $IMAGE_NAME"
echo
echo "7. 停止容器:"
echo "   docker stop $IMAGE_NAME"
echo
echo "8. 删除容器:"
echo "   docker rm $IMAGE_NAME"
echo
echo "=========================================="
echo "   脚本执行完成！"
echo "=========================================="
echo
echo "镜像文件已导出到: $(pwd)/$EXPORT_FILE"
echo "请按照上述Ubuntu服务器部署命令进行部署"