# 部署指南

本文档提供 Spider Toolkit 项目的详细部署指南，涵盖开发、测试和生产环境的部署方案。

## 📋 部署概览

### 支持的部署方式
- 🖥️ **本地部署**: 直接在本地机器运行
- 🐳 **Docker 部署**: 使用容器化部署
- ☁️ **云平台部署**: AWS、阿里云、腾讯云等
- 🚀 **自动化部署**: 使用 GitHub Actions

## 🎯 环境要求

### 系统要求
- **操作系统**: Linux, macOS, Windows
- **Python**: 3.8+ (推荐 3.9+)
- **内存**: 最小 2GB，推荐 4GB+
- **存储**: 最小 5GB 可用空间
- **网络**: 稳定的网络连接

### 依赖服务 (可选)
- **数据库**: MySQL 5.7+, PostgreSQL 10+, SQLite 3+
- **缓存**: Redis 5.0+
- **消息队列**: RabbitMQ, Apache Kafka
- **监控**: Prometheus, Grafana

## 🛠️ 本地部署

### 1. 环境准备
```bash
# 创建项目目录
mkdir spider-toolkit-production
cd spider-toolkit-production

# 克隆项目
git clone https://github.com/shaojunying/Spider.git
cd Spider
```

### 2. Python 环境配置
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 升级 pip
pip install --upgrade pip
```

### 3. 依赖安装
```bash
# 安装生产依赖
make install

# 或手动安装
pip install -r requirements.txt
```

### 4. 配置文件设置
```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用其他编辑器
```

#### 关键配置项
```bash
# HTTP 配置
HTTP_TIMEOUT=30
HTTP_RETRIES=3
HTTP_DELAY_MIN=1.0
HTTP_DELAY_MAX=3.0

# 安全配置
SSL_VERIFY=true
MAX_FILE_SIZE=10485760

# 日志配置
LOG_LEVEL=INFO
LOG_FILE_ENABLED=true

# 输出目录
OUTPUT_DIR=/var/spider-data/output
LOGS_DIR=/var/spider-data/logs
```

### 5. 目录结构创建
```bash
# 创建数据目录
sudo mkdir -p /var/spider-data/{output,logs}
sudo chown -R $USER:$USER /var/spider-data

# 或使用相对路径
mkdir -p data/{output,logs}
```

### 6. 运行测试
```bash
# 运行测试套件
make test

# 快速功能验证
python -c "from core.common import get_logger; print('Import successful')"
```

### 7. 启动服务
```bash
# 运行示例爬虫
make run-house-scraper

# 或直接运行
python scrapers/house_price/anjuke_refactored.py
```

## 🐳 Docker 部署

### 1. Dockerfile 创建
```dockerfile
# /Users/shaojunying/WorkSpace/Spider/Dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    libpng-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据目录
RUN mkdir -p /app/data/{output,logs}

# 设置权限
RUN useradd -m spider && \
    chown -R spider:spider /app
USER spider

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from core.common import get_logger; get_logger('health')" || exit 1

# 默认命令
CMD ["python", "-m", "scrapers.house_price.main"]
```

### 2. Docker Compose 配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  spider-toolkit:
    build: .
    container_name: spider-toolkit
    restart: unless-stopped
    environment:
      - OUTPUT_DIR=/app/data/output
      - LOGS_DIR=/app/data/logs
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    networks:
      - spider-network
    depends_on:
      - redis
      - db

  redis:
    image: redis:6-alpine
    container_name: spider-redis
    restart: unless-stopped
    networks:
      - spider-network
    volumes:
      - redis-data:/data

  db:
    image: mysql:8.0
    container_name: spider-db
    restart: unless-stopped
    environment:
      - MYSQL_ROOT_PASSWORD=your_password
      - MYSQL_DATABASE=spider_db
      - MYSQL_USER=spider_user
      - MYSQL_PASSWORD=spider_pass
    volumes:
      - db-data:/var/lib/mysql
    networks:
      - spider-network

  prometheus:
    image: prom/prometheus
    container_name: spider-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - spider-network

  grafana:
    image: grafana/grafana
    container_name: spider-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - spider-network

volumes:
  redis-data:
  db-data:
  grafana-data:

networks:
  spider-network:
    driver: bridge
```

### 3. 构建和运行
```bash
# 构建镜像
make docker-build

# 使用 docker-compose 启动
docker-compose up -d

# 查看日志
docker-compose logs -f spider-toolkit

# 停止服务
docker-compose down
```

## ☁️ 云平台部署

### AWS 部署

#### 使用 EC2
```bash
# 1. 启动 EC2 实例 (Ubuntu 20.04)
# 2. 连接到实例
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. 安装 Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu

# 4. 部署项目
git clone https://github.com/shaojunying/Spider.git
cd Spider
docker-compose up -d
```

#### 使用 ECS
```yaml
# ecs-task-definition.json
{
  "family": "spider-toolkit",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "spider-toolkit",
      "image": "your-account.dkr.ecr.region.amazonaws.com/spider-toolkit:latest",
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/spider-toolkit",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### 阿里云部署

#### 使用容器服务 ACK
```bash
# 1. 创建 ACK 集群
# 2. 配置 kubectl
# 3. 部署应用
kubectl apply -f k8s/
```

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spider-toolkit
spec:
  replicas: 3
  selector:
    matchLabels:
      app: spider-toolkit
  template:
    metadata:
      labels:
        app: spider-toolkit
    spec:
      containers:
      - name: spider-toolkit
        image: registry.cn-hangzhou.aliyuncs.com/your-namespace/spider-toolkit:latest
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        env:
        - name: LOG_LEVEL
          value: "INFO"
```

## 🚀 自动化部署

### GitHub Actions 部署流程
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /opt/spider-toolkit
          git pull origin main
          docker-compose down
          docker-compose build
          docker-compose up -d
```

### 部署脚本
```bash
#!/bin/bash
# deploy.sh

set -e

echo "开始部署 Spider Toolkit..."

# 备份当前版本
if [ -d "/opt/spider-toolkit-backup" ]; then
    rm -rf /opt/spider-toolkit-backup
fi
cp -r /opt/spider-toolkit /opt/spider-toolkit-backup

# 拉取最新代码
cd /opt/spider-toolkit
git pull origin main

# 构建并重启服务
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 等待服务启动
sleep 30

# 健康检查
if curl -f http://localhost:8080/health; then
    echo "部署成功！"
else
    echo "部署失败，回滚..."
    docker-compose down
    rm -rf /opt/spider-toolkit
    mv /opt/spider-toolkit-backup /opt/spider-toolkit
    cd /opt/spider-toolkit
    docker-compose up -d
    exit 1
fi
```

## 🔧 生产环境配置

### 性能优化
```bash
# 系统级优化
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65535' >> /etc/sysctl.conf
sysctl -p

# 文件描述符限制
echo '* soft nofile 65535' >> /etc/security/limits.conf
echo '* hard nofile 65535' >> /etc/security/limits.conf
```

### 监控配置
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'spider-toolkit'
    static_configs:
      - targets: ['spider-toolkit:8080']
```

### 日志管理
```yaml
# logging/logrotate.conf
/var/spider-data/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 spider spider
    postrotate
        systemctl reload spider-toolkit
    endscript
}
```

## 🛡️ 安全配置

### 防火墙设置
```bash
# Ubuntu/Debian
ufw allow ssh
ufw allow 80
ufw allow 443
ufw enable

# CentOS/RHEL
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

### SSL/TLS 配置
```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 监控和故障排除

### 健康检查
```bash
# 检查服务状态
systemctl status spider-toolkit

# 检查日志
tail -f /var/spider-data/logs/spider.log

# 检查资源使用
htop
df -h
```

### 常见问题

1. **内存不足**
   ```bash
   # 增加交换空间
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

2. **网络连接问题**
   ```bash
   # 检查网络连接
   ping google.com
   nslookup target-website.com
   ```

3. **权限问题**
   ```bash
   # 修复文件权限
   sudo chown -R spider:spider /opt/spider-toolkit
   sudo chmod -R 755 /opt/spider-toolkit
   ```

## 📚 运维最佳实践

### 备份策略
- 每日自动备份配置文件
- 每周备份完整数据
- 异地备份重要数据

### 更新策略
- 定期更新依赖包
- 测试环境先行验证
- 灰度发布新版本

### 监控指标
- CPU 使用率
- 内存使用率
- 磁盘空间
- 网络吞吐量
- 爬虫成功率
- 响应时间

---

**注意**: 生产环境部署需要仔细规划和测试。建议先在测试环境验证所有配置后再部署到生产环境。