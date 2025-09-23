const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'https://law-agent-by-grok-1.onrender.com',
      changeOrigin: true,
      secure: true,
      pathRewrite: {
        '^/api': '/api' // Keep the /api prefix when forwarding to the target
      },
      on: {
        proxyReq: (proxyReq, req, res) => {
          console.log('Proxying request:', req.method, req.url, 'to target path:', proxyReq.path);
        },
        proxyRes: (proxyRes, req, res) => {
          console.log('Proxy response:', proxyRes.statusCode, 'for', req.method, req.url);
        },
        error: (err, req, res) => {
          console.error('Proxy error:', err);
        }
      }
    })
  );
};