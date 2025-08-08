#!/bin/bash

# Word转HTML转换器启动脚本

echo "正在启动Word转HTML转换器..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建uploads目录（如果不存在）
if [ ! -d "uploads" ]; then
    mkdir -p uploads
    echo "已创建uploads目录"
fi

# 停止现有容器（如果有）
echo "停止现有容器..."
docker-compose down

# 构建并启动服务
echo "构建Docker镜像..."
docker-compose build --no-cache

echo "启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 15

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 测试健康检查接口
echo "测试服务健康状态..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ 服务启动成功！"
    echo "🌐 服务地址: http://localhost:5000"
    echo "📖 API文档: http://localhost:5000/"
    echo "💚 健康检查: http://localhost:5000/health"
else
    echo "❌ 服务启动失败，请检查日志"
    echo "查看日志: docker-compose logs"
fi

echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  进入容器: docker-compose exec word2html bash"