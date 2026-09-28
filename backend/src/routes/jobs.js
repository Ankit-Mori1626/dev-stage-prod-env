const express = require('express');
const router = express.Router();
const { pool } = require('../db');

// GET all active job openings
router.get('/jobs', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM job_openings WHERE is_active = true ORDER BY id ASC');
    res.status(200).json({
      success: true,
      data: result.rows,
      count: result.rowCount
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// POST submit a job application
router.post('/applications', async (req, res) => {
  const { job_id, job_title, candidate_name, email, phone, experience_years, portfolio_url, cover_note } = req.body;
  
  if (!candidate_name || !email || !job_title) {
    return res.status(400).json({ success: false, error: 'candidate_name, email, and job_title are required' });
  }

  try {
    const query = `
      INSERT INTO job_applications (job_id, job_title, candidate_name, email, phone, experience_years, portfolio_url, cover_note)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      RETURNING *;
    `;
    const values = [job_id || null, job_title, candidate_name, email, phone || '', experience_years || '', portfolio_url || '', cover_note || ''];
    const result = await pool.query(query, values);

    res.status(201).json({
      success: true,
      message: 'Application submitted successfully!',
      data: result.rows[0]
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

const { requireAdminAuth } = require('../middleware/auth');

// GET all job applications (Protected: for HR / Talent management only)
router.get('/applications', requireAdminAuth, async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM job_applications ORDER BY created_at DESC');
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
