# Cloudflare 反向代理 Gemini API 配置指南

## 概述
这个配置将让你通过 Cloudflare 反向代理访问你的 Gemini API，提供以下好处：
- SSL/TLS 加密
- DDoS 防护
- 全球 CDN 加速
- 流量分析
- 隐藏真实服务器 IP

## 前置条件
1. 一个可以通过公网访问的服务器 (VPS/云服务器)
2. 一个域名
3. Cloudflare 账户

## 部署步骤

### 1. 服务器部署

#### 1.1 上传代码到服务器
```bash
# 将项目文件上传到服务器
scp -r /home/justin/n8n-compose/gemini-api/ user@your-server-ip:/opt/
```

#### 1.2 配置环境变量
```bash
# 在服务器上创建 .env 文件
cd /opt/gemini-api
cp example.env .env
# 编辑 .env 文件，设置你的 GEMINI_API_KEY
nano .env
```

#### 1.3 启动服务
```bash
# 构建并启动服务
docker-compose up -d
```

#### 1.4 验证服务运行
```bash
# 检查服务状态
docker-compose ps
# 测试 API
curl http://localhost/health
```

### 2. Cloudflare 配置

#### 2.1 添加域名到 Cloudflare
1. 登录 Cloudflare 控制台
2. 点击 "Add a Site"
3. 输入你的域名 (例如: yourdomain.com)
4. 选择免费计划
5. 按照指示更新你的 DNS 服务器到 Cloudflare

#### 2.2 DNS 配置
在 Cloudflare DNS 设置中添加以下记录：

| Type | Name | Content | Proxy Status |
|------|------|---------|--------------|
| A | api | your-server-ip | ✅ Proxied |
| A | @ | your-server-ip | ✅ Proxied (可选) |

#### 2.3 SSL/TLS 配置
1. 进入 SSL/TLS → Overview
2. 选择 "Full" 或 "Full (strict)" 模式
3. 等待证书生成完成

#### 2.4 页面规则 (可选)
在 Rules → Page Rules 中可以添加：
```
api.yourdomain.com/*
设置：
- Cache Level: Bypass
- Browser Integrity Check: On
```

### 3. 安全配置 (推荐)

#### 3.1 Cloudflare 防火墙规则
在 Security → WAF → Custom Rules 中添加：
```
规则名称: Block non-API requests
表达式: (http.request.uri.path does not start with "/health" and http.request.uri.path does not start with "/docs" and http.request.uri.path does not start with "/summarize" and http.request.uri.path does not start with "/grounding" and http.request.uri.path does not start with "/doc" and http.request.uri.path does not start with "/image")
操作: Block
```

#### 3.2 速率限制
在 Security → WAF → Rate limiting rules 中添加：
```
规则名称: API Rate Limit
匹配: hostname eq "api.yourdomain.com"
速率: 100 requests per 1 minute per IP
操作: Block for 1 hour
```

### 4. 本地 Nginx 配置优化

#### 4.1 更新 nginx.conf 中的 server_name
```nginx
server_name api.yourdomain.com;  # 替换为你的实际域名
```

#### 4.2 添加 Cloudflare IP 限制 (可选)
在 nginx.conf 中添加：
```nginx
# 只允许 Cloudflare IP 访问
include /etc/nginx/conf.d/cloudflare.conf;
```

创建 cloudflare.conf：
```nginx
# Cloudflare IP 范围 (定期更新)
allow 173.245.48.0/20;
allow 103.21.244.0/22;
allow 103.22.200.0/22;
# ... 添加所有 Cloudflare IP 范围
deny all;
```

## 测试配置

### 1. 基本连接测试
```bash
curl -H "Host: api.yourdomain.com" http://your-server-ip/health
```

### 2. 通过 Cloudflare 测试
```bash
curl https://api.yourdomain.com/health
```

### 3. API 功能测试
```bash
# 测试摘要功能
curl -X POST "https://api.yourdomain.com/summarize" \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=example", "prompt": "简要总结这个视频"}'

# 测试查询功能
curl -X POST "https://api.yourdomain.com/grounding" \
  -H "Content-Type: application/json" \
  -d '{"query": "今天的天气如何？", "use_google_search": true}'
```

## 监控和维护

### 1. Cloudflare 分析
- 访问 Analytics → Traffic 查看流量统计
- 查看 Security → Events 了解安全事件

### 2. 服务器监控
```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs -f gemini-api
docker-compose logs -f nginx

# 查看资源使用情况
docker stats
```

### 3. 性能优化建议
1. **缓存配置**: 对静态资源启用 Cloudflare 缓存
2. **压缩**: 启用 Cloudflare 的 Auto Minify 功能
3. **图像优化**: 启用 Cloudflare 的 Polish 功能
4. **HTTP/2**: 确保启用 HTTP/2 和 HTTP/3

## 故障排除

### 常见问题

1. **522 错误**: 检查服务器防火墙，确保 80/443 端口开放
2. **SSL 错误**: 检查 Cloudflare SSL 模式设置
3. **超时错误**: 增加 nginx 的 proxy_read_timeout 值
4. **上传文件失败**: 检查 client_max_body_size 设置

### 调试命令
```bash
# 检查端口是否监听
netstat -tulpn | grep :80
netstat -tulpn | grep :443

# 检查 Docker 网络
docker network ls
docker network inspect firecrawl-net

# 测试容器间连接
docker exec gemini-nginx-proxy ping gemini-api-standalone
```

## 域名示例配置

假设你的域名是 `example.com`，最终访问地址将是：
- 主 API: `https://api.example.com/`
- 健康检查: `https://api.example.com/health`
- API 文档: `https://api.example.com/docs`
- 摘要接口: `https://api.example.com/summarize`
- 查询接口: `https://api.example.com/grounding`
- 文档理解: `https://api.example.com/doc`
- 图像生成: `https://api.example.com/image/generate`

## 安全提醒

1. 定期更新 Cloudflare IP 白名单
2. 启用 Cloudflare 的 Bot Fight Mode
3. 考虑启用 DDoS 保护
4. 定期监控 API 使用情况
5. 设置适当的速率限制
6. 保护好你的 GEMINI_API_KEY

## 成本估算

- Cloudflare: 免费计划足够使用
- 服务器: 根据流量需求选择合适的 VPS 配置
- 域名: 年费约 $10-15
- SSL 证书: Cloudflare 提供免费 SSL
