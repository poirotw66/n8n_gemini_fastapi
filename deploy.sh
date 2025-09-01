#!/bin/bash

# Gemini API Cloudflare 部署脚本
# 使用方法: ./deploy.sh [域名]

set -e

DOMAIN=${1:-"itr-lab.cloud"}
PROJECT_DIR="/opt/gemini-api"

echo "🚀 开始部署 Gemini API 到 Cloudflare..."
echo "域名: $DOMAIN"

# 检查 Docker 和 Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 创建项目目录
echo "📁 创建项目目录..."
sudo mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "⚠️  .env 文件不存在"
    if [ -f example.env ]; then
        echo "📋 复制 example.env 到 .env..."
        cp example.env .env
    else
        echo "📝 创建 .env 文件..."
        cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key_here
EOF
    fi
    echo "❗ 请编辑 .env 文件，设置你的 GEMINI_API_KEY"
    echo "   nano .env"
    echo "   然后重新运行此脚本"
    exit 1
fi

# 检查 GEMINI_API_KEY 是否设置
if grep -q "your_gemini_api_key_here" .env; then
    echo "❗ 请先在 .env 文件中设置正确的 GEMINI_API_KEY"
    exit 1
fi

# 更新 nginx.conf 中的域名
echo "🔧 配置 Nginx..."
if [ -f nginx.conf ]; then
    sed -i "s/server_name _;/server_name api.$DOMAIN;/g" nginx.conf
    echo "✅ 已更新域名为: api.$DOMAIN"
else
    echo "❌ nginx.conf 文件不存在"
    exit 1
fi

# 构建并启动服务
echo "🏗️  构建并启动服务..."
docker-compose down 2>/dev/null || true
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ 服务启动成功！"
else
    echo "❌ 服务启动失败，检查日志:"
    docker-compose logs
    exit 1
fi

# 测试健康检查
echo "🩺 测试健康检查..."
if curl -f http://localhost/health &> /dev/null; then
    echo "✅ 健康检查通过！"
else
    echo "❌ 健康检查失败"
    docker-compose logs nginx
    docker-compose logs gemini-api
    exit 1
fi

# 显示后续步骤
echo ""
echo "🎉 本地部署完成！"
echo ""
echo "📋 后续步骤:"
echo "1. 确保服务器防火墙开放 80 和 443 端口"
echo "2. 在 Cloudflare 中添加你的域名 $DOMAIN"
echo "3. 添加 DNS 记录:"
echo "   类型: A, 名称: api, 内容: $(curl -s ifconfig.me), 代理状态: 已代理"
echo "4. 设置 SSL/TLS 模式为 'Full'"
echo ""
echo "🌐 本地测试地址:"
echo "   健康检查: http://localhost/health"
echo "   API 文档: http://localhost/docs"
echo ""
echo "🔗 Cloudflare 配置完成后的访问地址:"
echo "   https://api.$DOMAIN/health"
echo "   https://api.$DOMAIN/docs"
echo ""
echo "📚 详细配置指南请查看: CLOUDFLARE_SETUP.md"
echo ""
echo "🔍 查看服务日志:"
echo "   docker-compose logs -f"
echo ""
echo "⏹️  停止服务:"
echo "   docker-compose down"
