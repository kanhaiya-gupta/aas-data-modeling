/**
 * Digital Certificate Management System
 * Manages digital certificates and product passports for Quality Infrastructure
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { Pool } = require('pg');
const redis = require('redis');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const Joi = require('joi');
const multer = require('multer');
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');
const moment = require('moment');
const winston = require('winston');
const QRCode = require('qrcode');
const { PDFDocument, rgb } = require('pdf-lib');
const { createCanvas } = require('canvas');
require('dotenv').config();

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3001;

// Configure logging
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

// Database configuration
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://aasx_user:aasx_password@localhost:5432/aasx_data',
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Redis configuration
const redisClient = redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379'
});

redisClient.on('error', (err) => logger.error('Redis Client Error', err));
redisClient.connect();

// Security middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// File upload configuration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, process.env.CERTIFICATE_STORAGE_PATH || './certificates');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + '.pdf');
  }
});

const upload = multer({ 
  storage: storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'), false);
    }
  }
});

// Validation schemas
const certificateSchema = Joi.object({
  certificate_id: Joi.string().required(),
  certificate_type: Joi.string().valid('conformity', 'origin', 'sustainability', 'quality').required(),
  certificate_name: Joi.string().required(),
  issuer_id: Joi.string().required(),
  issuer_name: Joi.string().required(),
  subject_id: Joi.string().required(),
  subject_type: Joi.string().valid('aas', 'twin', 'product').required(),
  certificate_data: Joi.object().required(),
  validity_start: Joi.date().required(),
  validity_end: Joi.date().optional(),
  status: Joi.string().valid('active', 'expired', 'revoked', 'suspended').default('active')
});

const productPassportSchema = Joi.object({
  passport_id: Joi.string().required(),
  product_id: Joi.string().required(),
  aas_id: Joi.string().optional(),
  twin_id: Joi.string().optional(),
  passport_type: Joi.string().valid('sustainability', 'circularity', 'compliance').required(),
  passport_data: Joi.object().required(),
  lifecycle_phase: Joi.string().valid('design', 'manufacturing', 'use', 'end_of_life').optional()
});

// Authentication middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key', (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.user = user;
    next();
  });
};

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    services: {
      database: 'connected',
      redis: redisClient.isReady ? 'connected' : 'disconnected'
    }
  });
});

// Certificate endpoints
app.post('/certificates', authenticateToken, async (req, res) => {
  try {
    // Validate input
    const { error, value } = certificateSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const client = await pool.connect();
    
    try {
      // Check if certificate already exists
      const existing = await client.query(
        'SELECT certificate_id FROM certificates.digital_certificates WHERE certificate_id = $1',
        [value.certificate_id]
      );

      if (existing.rows.length > 0) {
        return res.status(400).json({ error: 'Certificate already exists' });
      }

      // Generate signature hash
      const signatureData = JSON.stringify(value.certificate_data) + value.validity_start + value.subject_id;
      const signatureHash = crypto.createHash('sha256').update(signatureData).digest('hex');

      // Insert certificate
      const result = await client.query(
        `
        INSERT INTO certificates.digital_certificates 
        (certificate_id, certificate_type, certificate_name, issuer_id, issuer_name, 
         subject_id, subject_type, certificate_data, validity_start, validity_end, 
         status, signature_hash, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW(), NOW())
        RETURNING *
        `,
        [
          value.certificate_id,
          value.certificate_type,
          value.certificate_name,
          value.issuer_id,
          value.issuer_name,
          value.subject_id,
          value.subject_type,
          JSON.stringify(value.certificate_data),
          value.validity_start,
          value.validity_end,
          value.status,
          signatureHash
        ]
      );

      // Cache certificate
      await redisClient.setEx(
        `cert:${value.certificate_id}`,
        3600, // 1 hour
        JSON.stringify(result.rows[0])
      );

      logger.info(`Certificate created: ${value.certificate_id}`);
      res.status(201).json(result.rows[0]);

    } finally {
      client.release();
    }

  } catch (error) {
    logger.error('Error creating certificate:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/certificates', authenticateToken, async (req, res) => {
  try {
    const { 
      certificate_type, 
      subject_id, 
      subject_type, 
      status, 
      limit = 50, 
      offset = 0 
    } = req.query;

    const client = await pool.connect();
    
    try {
      let query = 'SELECT * FROM certificates.digital_certificates WHERE 1=1';
      const params = [];
      let paramCount = 0;

      if (certificate_type) {
        paramCount++;
        query += ` AND certificate_type = $${paramCount}`;
        params.push(certificate_type);
      }

      if (subject_id) {
        paramCount++;
        query += ` AND subject_id = $${paramCount}`;
        params.push(subject_id);
      }

      if (subject_type) {
        paramCount++;
        query += ` AND subject_type = $${paramCount}`;
        params.push(subject_type);
      }

      if (status) {
        paramCount++;
        query += ` AND status = $${paramCount}`;
        params.push(status);
      }

      paramCount++;
      query += ` ORDER BY created_at DESC LIMIT $${paramCount}`;
      params.push(parseInt(limit));

      paramCount++;
      query += ` OFFSET $${paramCount}`;
      params.push(parseInt(offset));

      const result = await client.query(query, params);
      res.json(result.rows);

    } finally {
      client.release();
    }

  } catch (error) {
    logger.error('Error fetching certificates:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/certificates/:certificateId', authenticateToken, async (req, res) => {
  try {
    const { certificateId } = req.params;

    // Check cache first
    const cached = await redisClient.get(`cert:${certificateId}`);
    if (cached) {
      return res.json(JSON.parse(cached));
    }

    const client = await pool.connect();
    
    try {
      const result = await client.query(
        'SELECT * FROM certificates.digital_certificates WHERE certificate_id = $1',
        [certificateId]
      );

      if (result.rows.length === 0) {
        return res.status(404).json({ error: 'Certificate not found' });
      }

      // Cache result
      await redisClient.setEx(
        `cert:${certificateId}`,
        3600,
        JSON.stringify(result.rows[0])
      );

      res.json(result.rows[0]);

    } finally {
      client.release();
    }

  } catch (error) {
    logger.error('Error fetching certificate:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.put('/certificates/:certificateId', authenticateToken, async (req, res) => {
  try {
    const { certificateId } = req.params;
    const updates = req.body;

    const client = await pool.connect();
    
    try {
      // Check if certificate exists
      const existing = await client.query(
        'SELECT * FROM certificates.digital_certificates WHERE certificate_id = $1',
        [certificateId]
      );

      if (existing.rows.length === 0) {
        return res.status(404).json({ error: 'Certificate not found' });
      }

      // Build update query
      const updateFields = [];
      const params = [certificateId];
      let paramCount = 1;

      if (updates.status) {
        paramCount++;
        updateFields.push(`status = $${paramCount}`);
        params.push(updates.status);
      }

      if (updates.validity_end) {
        paramCount++;
        updateFields.push(`validity_end = $${paramCount}`);
        params.push(updates.validity_end);
      }

      if (updates.certificate_data) {
        paramCount++;
        updateFields.push(`certificate_data = $${paramCount}`);
        params.push(JSON.stringify(updates.certificate_data));
      }

      if (updateFields.length === 0) {
        return res.status(400).json({ error: 'No valid fields to update' });
      }

      paramCount++;
      updateFields.push(`updated_at = $${paramCount}`);
      params.push(new Date());

      const query = `
        UPDATE certificates.digital_certificates 
        SET ${updateFields.join(', ')}
        WHERE certificate_id = $1
        RETURNING *
      `;

      const result = await client.query(query, params);

      // Clear cache
      await redisClient.del(`cert:${certificateId}`);

      logger.info(`Certificate updated: ${certificateId}`);
      res.json(result.rows[0]);

    } finally {
      client.release();
    }

  } catch (error) {
    logger.error('Error updating certificate:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/certificates/:certificateId/revoke', authenticateToken, async (req, res) => {
  try {
    const { certificateId } = req.params;
    const { reason } = req.body;

    const client = await pool.connect();
    
    try {
      const result = await client.query(
        `
        UPDATE certificates.digital_certificates 
        SET status = 'revoked', revocation_reason = $1, revocation_date = NOW(), updated_at = NOW()
        WHERE certificate_id = $2
        RETURNING *
        `,
        [reason, certificateId]
      );

      if (result.rows.length === 0) {
        return res.status(404).json({ error: 'Certificate not found' });
      }

      // Clear cache
      await redisClient.del(`cert:${certificateId}`);

      logger.info(`Certificate revoked: ${certificateId}`);
      res.json(result.rows[0]);

    } finally {
      client.release();
    }

  } catch (error) {
    logger.error('Error revoking certificate:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Product Passport endpoints
app.post('/passports', authenticateToken, async (req, res) => {
  try {
    // Validate input
    const { error, value } = productPassportSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const client = await pool.connect();
    
    try {
      // Check if passport already exists
      const existing = await client.query(
        'SELECT passport_id FROM certificates.product_passports WHERE passport_id = $1',
        [value.passport_id]
      );

      if (existing.rows.length > 0) {
        return res.status(400).json({ error: 'Product passport already exists' });
      }

      // Calculate scores
      const sustainabilityScore = calculateSustainabilityScore(value.passport_data);
      const circularityScore = calculateCircularityScore(value.passport_data);
      const complianceScore = calculateComplianceScore(value.passport_data);

      // Insert passport
      const result = await client.query(
        `
        INSERT INTO certificates.product_passports 
        (passport_id, product_id, aas_id, twin_id, passport_type, passport_data, 
         lifecycle_phase, sustainability_score, circularity_score, compliance_score, 
         created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
        RETURNING *
        `,
        [
          value.passport_id,
          value.product_id,
          value.aas_id,
          value.twin_id,
          value.passport_type,
          JSON.stringify(value.passport_data),
          value.lifecycle_phase,
          sustainabilityScore,
          circularityScore,
          complianceScore
        ]
      );

      logger.info(`Product passport created: ${value.passport_id}`);
      res.status(201).json(result.rows[0]);

    } finally {
      client.release();
    }

  } catch (error) {
    logger.error('Error creating product passport:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/passports', authenticateToken, async (req, res) => {
  try {
    const { 
      passport_type, 
      product_id, 
      lifecycle_phase, 
      limit = 50, 
      offset = 0 
    } = req.query;

    const client = await pool.connect();
    
    try {
      let query = 'SELECT * FROM certificates.product_passports WHERE 1=1';
      const params = [];
      let paramCount = 0;

      if (passport_type) {
        paramCount++;
        query += ` AND passport_type = $${paramCount}`;
        params.push(passport_type);
      }

      if (product_id) {
        paramCount++;
        query += ` AND product_id = $${paramCount}`;
        params.push(product_id);
      }

      if (lifecycle_phase) {
        paramCount++;
        query += ` AND lifecycle_phase = $${paramCount}`;
        params.push(lifecycle_phase);
      }

      paramCount++;
      query += ` ORDER BY created_at DESC LIMIT $${paramCount}`;
      params.push(parseInt(limit));

      paramCount++;
      query += ` OFFSET $${paramCount}`;
      params.push(parseInt(offset));

      const result = await client.query(query, params);
      res.json(result.rows);

    } finally {
      client.release();
    }

  } catch (error) {
    logger.error('Error fetching passports:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Certificate template endpoints
app.get('/templates', authenticateToken, async (req, res) => {
  try {
    const { template_type, is_active } = req.query;

    const client = await pool.connect();
    
    try {
      let query = 'SELECT * FROM certificates.certificate_templates WHERE 1=1';
      const params = [];
      let paramCount = 0;

      if (template_type) {
        paramCount++;
        query += ` AND template_type = $${paramCount}`;
        params.push(template_type);
      }

      if (is_active !== undefined) {
        paramCount++;
        query += ` AND is_active = $${paramCount}`;
        params.push(is_active === 'true');
      }

      query += ' ORDER BY template_name';

      const result = await client.query(query, params);
      res.json(result.rows);

    } finally {
      client.release();
    }

  } catch (error) {
    logger.error('Error fetching templates:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Certificate generation endpoints
app.post('/certificates/:certificateId/generate-pdf', authenticateToken, async (req, res) => {
  try {
    const { certificateId } = req.params;

    const client = await pool.connect();
    
    try {
      const result = await client.query(
        'SELECT * FROM certificates.digital_certificates WHERE certificate_id = $1',
        [certificateId]
      );

      if (result.rows.length === 0) {
        return res.status(404).json({ error: 'Certificate not found' });
      }

      const certificate = result.rows[0];
      const pdfBuffer = await generateCertificatePDF(certificate);

      res.setHeader('Content-Type', 'application/pdf');
      res.setHeader('Content-Disposition', `attachment; filename="certificate-${certificateId}.pdf"`);
      res.send(pdfBuffer);

    } finally {
      client.release();
    }

  } catch (error) {
    logger.error('Error generating PDF:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/certificates/:certificateId/generate-qr', authenticateToken, async (req, res) => {
  try {
    const { certificateId } = req.params;

    const client = await pool.connect();
    
    try {
      const result = await client.query(
        'SELECT * FROM certificates.digital_certificates WHERE certificate_id = $1',
        [certificateId]
      );

      if (result.rows.length === 0) {
        return res.status(404).json({ error: 'Certificate not found' });
      }

      const certificate = result.rows[0];
      const qrCodeDataURL = await QRCode.toDataURL(JSON.stringify({
        certificate_id: certificate.certificate_id,
        signature_hash: certificate.signature_hash,
        validity_start: certificate.validity_start,
        status: certificate.status
      }));

      res.json({ qr_code: qrCodeDataURL });

    } finally {
      client.release();
    }

  } catch (error) {
    logger.error('Error generating QR code:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Validation endpoints
app.post('/certificates/validate', authenticateToken, async (req, res) => {
  try {
    const { certificate_id, signature_hash } = req.body;

    const client = await pool.connect();
    
    try {
      const result = await client.query(
        'SELECT * FROM certificates.digital_certificates WHERE certificate_id = $1',
        [certificate_id]
      );

      if (result.rows.length === 0) {
        return res.json({ valid: false, reason: 'Certificate not found' });
      }

      const certificate = result.rows[0];

      // Check signature
      if (certificate.signature_hash !== signature_hash) {
        return res.json({ valid: false, reason: 'Invalid signature' });
      }

      // Check validity
      const now = new Date();
      if (certificate.validity_end && new Date(certificate.validity_end) < now) {
        return res.json({ valid: false, reason: 'Certificate expired' });
      }

      // Check status
      if (certificate.status !== 'active') {
        return res.json({ valid: false, reason: `Certificate ${certificate.status}` });
      }

      res.json({ valid: true, certificate });

    } finally {
      client.release();
    }

  } catch (error) {
    logger.error('Error validating certificate:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Statistics endpoints
app.get('/statistics', authenticateToken, async (req, res) => {
  try {
    const client = await pool.connect();
    
    try {
      // Certificate statistics
      const certStats = await client.query(`
        SELECT 
          certificate_type,
          status,
          COUNT(*) as count
        FROM certificates.digital_certificates 
        GROUP BY certificate_type, status
      `);

      // Passport statistics
      const passportStats = await client.query(`
        SELECT 
          passport_type,
          lifecycle_phase,
          COUNT(*) as count
        FROM certificates.product_passports 
        GROUP BY passport_type, lifecycle_phase
      `);

      // Template statistics
      const templateStats = await client.query(`
        SELECT 
          template_type,
          is_active,
          COUNT(*) as count
        FROM certificates.certificate_templates 
        GROUP BY template_type, is_active
      `);

      res.json({
        certificates: certStats.rows,
        passports: passportStats.rows,
        templates: templateStats.rows
      });

    } finally {
      client.release();
    }

  } catch (error) {
    logger.error('Error fetching statistics:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Helper functions
function calculateSustainabilityScore(passportData) {
  // Implement sustainability scoring logic
  const factors = {
    material_efficiency: passportData.material_efficiency || 0,
    energy_efficiency: passportData.energy_efficiency || 0,
    carbon_footprint: passportData.carbon_footprint || 0,
    recyclability: passportData.recyclability || 0
  };

  const weights = { 0.25, 0.25, 0.25, 0.25 };
  const score = Object.values(factors).reduce((sum, value, index) => {
    return sum + (value * weights[index]);
  }, 0);

  return Math.min(Math.max(score, 0), 100);
}

function calculateCircularityScore(passportData) {
  // Implement circularity scoring logic
  const factors = {
    reuse_potential: passportData.reuse_potential || 0,
    repair_ability: passportData.repair_ability || 0,
    disassembly_ease: passportData.disassembly_ease || 0,
    material_recovery: passportData.material_recovery || 0
  };

  const weights = { 0.25, 0.25, 0.25, 0.25 };
  const score = Object.values(factors).reduce((sum, value, index) => {
    return sum + (value * weights[index]);
  }, 0);

  return Math.min(Math.max(score, 0), 100);
}

function calculateComplianceScore(passportData) {
  // Implement compliance scoring logic
  const standards = passportData.compliance_standards || [];
  const compliance_levels = passportData.compliance_levels || {};

  if (standards.length === 0) return 0;

  const totalScore = standards.reduce((sum, standard) => {
    const level = compliance_levels[standard] || 0;
    return sum + level;
  }, 0);

  return Math.min(Math.max((totalScore / standards.length) * 100, 0), 100);
}

async function generateCertificatePDF(certificate) {
  try {
    const pdfDoc = await PDFDocument.create();
    const page = pdfDoc.addPage([595.28, 841.89]); // A4 size
    const { width, height } = page.getSize();

    // Add certificate content
    page.drawText('Digital Certificate', {
      x: 50,
      y: height - 100,
      size: 24,
      color: rgb(0, 0, 0)
    });

    page.drawText(`Certificate ID: ${certificate.certificate_id}`, {
      x: 50,
      y: height - 150,
      size: 12,
      color: rgb(0, 0, 0)
    });

    page.drawText(`Type: ${certificate.certificate_type}`, {
      x: 50,
      y: height - 170,
      size: 12,
      color: rgb(0, 0, 0)
    });

    page.drawText(`Issuer: ${certificate.issuer_name}`, {
      x: 50,
      y: height - 190,
      size: 12,
      color: rgb(0, 0, 0)
    });

    page.drawText(`Valid from: ${new Date(certificate.validity_start).toLocaleDateString()}`, {
      x: 50,
      y: height - 210,
      size: 12,
      color: rgb(0, 0, 0)
    });

    if (certificate.validity_end) {
      page.drawText(`Valid until: ${new Date(certificate.validity_end).toLocaleDateString()}`, {
        x: 50,
        y: height - 230,
        size: 12,
        color: rgb(0, 0, 0)
      });
    }

    page.drawText(`Status: ${certificate.status}`, {
      x: 50,
      y: height - 250,
      size: 12,
      color: rgb(0, 0, 0)
    });

    page.drawText(`Signature: ${certificate.signature_hash}`, {
      x: 50,
      y: height - 270,
      size: 8,
      color: rgb(0.5, 0.5, 0.5)
    });

    return await pdfDoc.save();
  } catch (error) {
    logger.error('Error generating PDF:', error);
    throw error;
  }
}

// Error handling middleware
app.use((error, req, res, next) => {
  logger.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  logger.info(`Certificate Manager running on port ${PORT}`);
  console.log(`Certificate Manager running on port ${PORT}`);
});

module.exports = app; 