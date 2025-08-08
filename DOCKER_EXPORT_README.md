# Docker镜像导出和部署脚本

本项目提供了两个脚本来帮助您将Docker服务打包成镜像并导出到当前目录，同时提供在Ubuntu服务器上的导入和启动命令。

## 文件说明

### 1. export_docker_image.bat
Windows批处理脚本，用于在Windows环境下导出Docker镜像。

### 2. export_docker_image.sh
Linux Shell脚本，用于在Linux环境下导出Docker镜像。

## 使用方法

### Windows环境

1. 确保Docker Desktop已安装并正在运行
2. 双击运行 `export_docker_image.bat` 或在命令行中执行：
   ```cmd
   export_docker_image.bat
   ```

### Linux环境

1. 确保Docker和Docker Compose已安装并正在运行
2. 为脚本添加执行权限：
   ```bash
   chmod +x export_docker_image.sh
   ```
3. 运行脚本：
   ```bash
   ./export_docker_image.sh
   ```

## 脚本功能

脚本会自动执行以下操作：

1. **检查Docker服务状态** - 确保Docker正在运行
2. **构建Docker镜像** - 使用docker-compose构建镜像
3. **导出Docker镜像** - 将镜像保存为.tar文件到当前目录
4. **显示部署命令** - 提供Ubuntu服务器上的完整部署命令

## 输出文件

脚本会在当前目录生成一个导出文件：
- `word2html-word2html_latest.tar`

## Ubuntu服务器部署步骤

### 1. 传输镜像文件
将导出的.tar文件传输到Ubuntu服务器：
```bash
scp word2html-word2html_latest.tar username@server_ip:/path/to/destination/
```

### 2. 导入Docker镜像
在Ubuntu服务器上导入镜像：
```bash
docker load -i word2html-word2html_latest.tar
```

### 3. 运行容器
#### 方式一：直接运行
```bash
docker run -d --name word2html-word2html -p 5000:5000 -v /path/to/uploads:/app/uploads word2html-word2html:latest
```

#### 方式二：使用docker-compose（推荐）
1. 将docker-compose.yml文件传输到服务器
2. 运行：
   ```bash
   docker-compose up -d
   ```

### 4. 验证服务
```bash
# 查看运行状态
docker ps
```bash
# 查看容器日志
docker logs word2html-word2html

# 测试健康检查
curl http://localhost:5000/health
```

## 常用管理命令

```bash
# 查看容器状态
docker ps

# 查看容器日志
docker logs word2html-converter

# 停止容器
docker stop word2html-converter

# 启动容器
docker start word2html-converter

# 重启容器
docker restart word2html-converter

# 删除容器
docker rm word2html-converter

# 删除镜像
docker rmi word2html-converter:latest
```

## 注意事项

1. **Docker服务**：确保在运行脚本前Docker服务已启动
2. **端口冲突**：确保Ubuntu服务器的5000端口未被占用
3. **目录权限**：确保uploads目录有正确的读写权限
4. **防火墙设置**：确保Ubuntu服务器的防火墙允许5000端口访问
5. **存储空间**：确保有足够的磁盘空间存储导出的镜像文件

## 故障排除

### 常见问题

1. **Docker未运行**
   - Windows: 启动Docker Desktop
   - Linux: 启动Docker服务 `sudo systemctl start docker`

2. **构建失败**
   - 检查Dockerfile和docker-compose.yml配置
   - 确保网络连接正常，能够下载依赖

3. **导出失败**
   - 确保磁盘空间充足
   - 检查文件写入权限

4. **容器启动失败**
   - 检查端口是否被占用
   - 查看容器日志获取详细错误信息

### 日志查看
```bash
# 查看容器日志
docker logs word2html-word2html

# 查看最后100行日志
docker logs --tail 100 word2html-word2html
```

## 支持的服务

导出的镜像包含以下服务：
- **Word转HTML转换服务** - 基于Flask的Web服务
- **文件上传功能** - 支持Word文档上传
- **健康检查** - 提供健康检查端点
- **生产环境配置** - 优化的生产环境设置

服务默认运行在5000端口，提供RESTful API接口。