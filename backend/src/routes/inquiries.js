const express = require('express');
const router = express.Router();
const { pool } = require('../db');

// POST submit a client service inquiry
router.post('/inquiries', async (req, res) => {
  const { client_name, email, company_name, service_required, budget, message } = req.body;
  
  if (!client_name || !email || !service_required || !message) {
    return res.status(400).json({ success: false, error: 'client_name, email, service_required, and message are required' });
  }

  try {
    const query = `
      INSERT INTO service_inquiries (client_name, email, company_name, service_required, budget, message)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *;
    `;
    const values = [client_name, email, company_name || '', service_required, budget || '', message];
    const result = await pool.query(query, values);

    res.status(201).json({
      success: true,
      message: 'Inquiry received. Our Cloud Architect team will contact you shortly.',
      data: result.rows[0]
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

const { requireAdminAuth } = require('../middleware/auth');

// GET all client service inquiries (Protected: for CRM / Sales / Leadership only)
router.get('/inquiries', requireAdminAuth, async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM service_inquiries ORDER BY created_at DESC');
    res.status(200).json({
      success: true,
      data: result.rows,
      count: result.rowCount
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;
