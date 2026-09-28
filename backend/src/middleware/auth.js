// Admin Authentication Middleware for Protecting Sensitive Records
const ADMIN_API_KEY = process.env.ADMIN_API_KEY || 'admin-cloudnexus-sec2026';

function requireAdminAuth(req, res, next) {
  const authHeader = req.headers['authorization'] || req.headers['x-admin-key'];
  
  if (!authHeader) {
    return res.status(401).json({
      success: false,
      error: '401 Unauthorized: Admin authentication required to access sensitive corporate records (Applications & Inquiries).'
    });
  }
  
  const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7).trim() : authHeader.trim();
  
  if (token !== ADMIN_API_KEY) {
    return res.status(403).json({
      success: false,
      error: '403 Forbidden: Invalid Admin Security Credentials.'
    });
  }
  
  next();
}

module.exports = { requireAdminAuth, ADMIN_API_KEY };
