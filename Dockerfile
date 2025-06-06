# 神秘事件研究系统 - Docker镜像
# 基于Python 3.11的多阶段构建

# ================================
# 第一阶段：构建阶段
# ================================
FROM python:3.11-slim as builder

# 设置构建参数
ARG BUILD_ENV=production
ARG PYTHON_VERSION=3.11

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 创建工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .
COPY setup.py .
COPY __version__.py .

# 安装Python依赖
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ================================
# 第二阶段：运行阶段
# ================================
FROM python:3.11-slim as runtime

# 设置标签
LABEL maintainer="Mystery Research Team <team@mystery-research.com>" \
      version="1.0.0" \
      description="神秘事件研究系统 - AI驱动的神秘事件分析平台" \
      org.opencontainers.image.title="Mystery Event Research System" \
      org.opencontainers.image.description="AI-powered mystery event research and analysis platform" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="Mystery Research Team" \
      org.opencontainers.image.licenses="MIT"

# 创建非root用户
RUN groupadd -r mystery && useradd -r -g mystery mystery

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH=/app/.local/bin:$PATH \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO \
    MAX_WORKERS=4 \
    REQUEST_TIMEOUT=30

# 创建应用目录结构
WORKDIR /app
RUN mkdir -p \
    /app/logs \
    /app/data \
    /app/cache \
    /app/temp \
    /app/reports \
    /app/backups \
    && chown -R mystery:mystery /app

# 从构建阶段复制Python包
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY --chown=mystery:mystery . /app/

# 安装应用
RUN pip install -e .

# 创建配置文件
RUN if [ ! -f /app/.env ]; then \
        cp /app/.env.example /app/.env 2>/dev/null || \
        echo "# 请配置环境变量" > /app/.env; \
    fi

# 设置权限
RUN chmod +x /app/deploy.py /app/main.py && \
    chown -R mystery:mystery /app

# 切换到非root用户
USER mystery

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 设置卷
VOLUME ["/app/data", "/app/logs", "/app/cache"]

# 启动命令
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000"]