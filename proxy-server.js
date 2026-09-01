#!/usr/bin/env node
/**
 * Simple reverse proxy for ngrok
 * Routes /lti/* to backend (port 8000)
 * Routes everything else to frontend (port 3000)
 */

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = 4000;
const API_UPSTREAM_URL =
  process.env.API_UPSTREAM_URL ||
  'http://localhost:8080';

// Health check
app.get('/proxy-health', (req, res) => {
  res.json({ status: 'ok', message: 'Proxy server running' });
});

// Proxy /api/v1/* requests to the local backend API to avoid CORS.
app.use('/api/v1', createProxyMiddleware({
  target: API_UPSTREAM_URL,
  changeOrigin: true,
  secure: true,
  logLevel: 'info',
  onProxyReq: (proxyReq, req, res) => {
    console.log(`[API] ${req.method} ${req.path}`);
  }
}));

// Proxy /lti/* requests to backend (port 8000)
app.use('/lti', createProxyMiddleware({
  target: 'http://localhost:8000',
  changeOrigin: true,
  logLevel: 'info',
  onProxyReq: (proxyReq, req, res) => {
    console.log(`[LTI Backend] ${req.method} ${req.path}`);
  }
}));

// Proxy /health to backend
app.use('/health', createProxyMiddleware({
  target: 'http://localhost:8000',
  changeOrigin: true,
  logLevel: 'info'
}));

// Proxy /docs to backend (FastAPI docs)
app.use('/docs', createProxyMiddleware({
  target: 'http://localhost:8000',
  changeOrigin: true,
  logLevel: 'info'
}));

// Proxy everything else to frontend (port 3000)
app.use('/', createProxyMiddleware({
  target: 'http://localhost:3000',
  changeOrigin: true,
  ws: true, // Enable WebSocket support for React hot reload
  logLevel: 'info',
  onProxyReq: (proxyReq, req, res) => {
    if (!req.path.startsWith('/static') && !req.path.startsWith('/sockjs-node')) {
      console.log(`[Frontend] ${req.method} ${req.path}`);
    }
  }
}));

app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║         Reverse Proxy Server Running on Port ${PORT}         ║
╚════════════════════════════════════════════════════════════╝

Routing:
  • /api/v1/* → ${API_UPSTREAM_URL} (Backend API)
  • /lti/*    → http://localhost:8000 (LTI Backend)
  • /health   → http://localhost:8000 (Backend Health)
  • /docs     → http://localhost:8000 (API Docs)
  • /*        → http://localhost:3000 (React Frontend)

Point ngrok to this port:
  ngrok http ${PORT} --domain=your-domain.ngrok-free.app

Then update .env:
  TOOL_URL=https://your-domain.ngrok-free.app
  FRONTEND_URL=https://your-domain.ngrok-free.app
`);
});
