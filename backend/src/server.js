const express = require('express');
const cors = require('cors');
const client = require('prom-client');
const { pool, initDB } = require('./db');
const taskRoutes = require('./routes/tasks');
const jobRoutes = require('./routes/jobs');
const inquiryRoutes = require('./routes/inquiries');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Prometheus Metrics Setup
const collectDefaultMetrics = client.collectDefaultMetrics;
collectDefaultMetrics({ register: client.register });

const httpRequestDurationMicroseconds = new client.Histogram({
  name: 'http_request_duration_ms',
  help: 'Duration of HTTP requests in ms',
  labelNames: ['method', 'route', 'code'],
  buckets: [0.1, 5, 15, 50, 100, 200, 500, 1000]
});

app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    httpRequestDurationMicroseconds
      .labels(req.method, req.route ? req.route.path : req.path, res.statusCode)
      .observe(duration);
  });
  next();
});

// Corporate & Operational REST Routes
app.use('/api/tasks', taskRoutes);
app.use('/api', jobRoutes);
app.use('/api', inquiryRoutes);

// Liveness Probe Endpoint
app.get('/healthz', (req, res) => {
  res.status(200).json({ status: 'UP', timestamp: new Date().toISOString() });
});

// Readiness Probe Endpoint (checks DB connectivity)
app.get('/ready', async (req, res) => {
  try {
    await pool.query('SELECT 1');
    res.status(200).json({ 
      status: 'READY',
      environment: process.env.APP_ENV || 'development',
      pod: process.env.POD_NAME || 'standalone',
      database: 'CONNECTED'
    });
  } catch (err) {
    res.status(503).json({ status: 'NOT_READY', error: err.message });
  }
});

// Metrics Endpoint for Prometheus Scraping
app.get('/metrics', async (req, res) => {
  res.setHeader('Content-Type', client.register.contentType);
  res.send(await client.register.metrics());
});

// Ingress & ALB Route Telemetry Endpoint
app.get('/api/ingress-info', (req, res) => {
  res.status(200).json({
    status: 'SUCCESS',
    timestamp: new Date().toISOString(),
    pod_name: process.env.POD_NAME || 'standalone-backend-pod',
    node_name: process.env.NODE_NAME || 'local-node',
    environment: process.env.APP_ENV || 'development',
    client_ip: req.ip || req.connection.remoteAddress,
    headers: {
      host: req.headers['host'],
      'x-forwarded-for': req.headers['x-forwarded-for'] || null,
      'x-forwarded-proto': req.headers['x-forwarded-proto'] || null,
      'x-forwarded-port': req.headers['x-forwarded-port'] || null,
      'x-real-ip': req.headers['x-real-ip'] || null,
      'x-amzn-trace-id': req.headers['x-amzn-trace-id'] || null,
      'user-agent': req.headers['user-agent']
    },
    ingress_type_detected: req.headers['x-amzn-trace-id'] ? 'AWS Application Load Balancer (ALB)' : (req.headers['x-forwarded-for'] ? 'NGINX Ingress / Reverse Proxy' : 'Direct / Local Access')
  });
});

// Server Start & DB Init
app.listen(PORT, async () => {
  console.log(`=============================================`);
  console.log(`🚀 3-Tier Backend API running on port ${PORT}`);
  console.log(`🌍 Environment: ${process.env.APP_ENV || 'development'}`);
  console.log(`📦 Node: ${process.env.NODE_NAME || 'local'} | Pod: ${process.env.POD_NAME || 'local'}`);
  console.log(`=============================================`);
  await initDB();
});

// Graceful Shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received. Closing HTTP server and DB pool...');
  await pool.end();
  process.exit(0);
});
