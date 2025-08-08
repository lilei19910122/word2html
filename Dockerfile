# 定义构建参数
ARG DOCKER_REGISTRY_MIRROR

# 使用官方Python镜像（支持镜像源）
FROM ${DOCKER_REGISTRY_MIRROR:-python:3.11-slim}

# 设置工作目录
WORKDIR /app

# 配置pip使用国内镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖（优先使用预编译包）
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建uploads目录
RUN mkdir -p uploads

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5000

# 使用非root用户运行
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# 启动命令
CMD ["python", "app.py"]