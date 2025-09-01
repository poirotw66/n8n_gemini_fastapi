// Cloudflare Workers 脚本，用于高级代理和缓存控制
// 部署到 Cloudflare Workers 可以提供更精细的控制

export default {
  async fetch(request, env, ctx) {
    // 获取原始 URL
    const url = new URL(request.url);
    
    // 配置你的后端服务器 IP 或域名
    const BACKEND_HOST = 'your-server-ip'; // 替换为你的服务器 IP
    const BACKEND_PORT = '80'; // 如果使用 HTTPS 则改为 443
    const BACKEND_PROTOCOL = 'http'; // 如果使用 HTTPS 则改为 https
    
    // 构建后端 URL
    const backendUrl = `${BACKEND_PROTOCOL}://${BACKEND_HOST}:${BACKEND_PORT}${url.pathname}${url.search}`;
    
    // 克隆请求
    const modifiedRequest = new Request(backendUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body,
    });
    
    // 添加真实 IP 头部
    modifiedRequest.headers.set('X-Real-IP', request.headers.get('CF-Connecting-IP'));
    modifiedRequest.headers.set('X-Forwarded-For', request.headers.get('CF-Connecting-IP'));
    modifiedRequest.headers.set('X-Forwarded-Proto', url.protocol.slice(0, -1));
    
    try {
      // 发送请求到后端
      const response = await fetch(modifiedRequest);
      
      // 克隆响应
      const modifiedResponse = new Response(response.body, response);
      
      // 添加 CORS 头部
      modifiedResponse.headers.set('Access-Control-Allow-Origin', '*');
      modifiedResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      modifiedResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
      
      // 添加安全头部
      modifiedResponse.headers.set('X-Frame-Options', 'SAMEORIGIN');
      modifiedResponse.headers.set('X-Content-Type-Options', 'nosniff');
      modifiedResponse.headers.set('X-XSS-Protection', '1; mode=block');
      modifiedResponse.headers.set('Referrer-Policy', 'no-referrer-when-downgrade');
      
      // 缓存控制
      if (url.pathname === '/health') {
        // 健康检查端点短缓存
        modifiedResponse.headers.set('Cache-Control', 'public, max-age=30');
      } else if (url.pathname.startsWith('/image/')) {
        // 图片文件长缓存
        modifiedResponse.headers.set('Cache-Control', 'public, max-age=86400');
      } else {
        // API 请求不缓存
        modifiedResponse.headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
      }
      
      return modifiedResponse;
    } catch (error) {
      return new Response(JSON.stringify({
        error: 'Backend service unavailable',
        message: error.message
      }), {
        status: 502,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
  },
};

// 使用方法:
// 1. 在 Cloudflare Dashboard 中创建一个新的 Worker
// 2. 将此代码粘贴到 Worker 编辑器中
// 3. 修改 BACKEND_HOST 为你的服务器 IP
// 4. 保存并部署
// 5. 在域名的 DNS 设置中，将 api 子域名指向这个 Worker:
//    类型: AAAA, 名称: api, 内容: 100::, 代理状态: 已代理
//    然后在 Workers 路由中添加: api.yourdomain.com/*
