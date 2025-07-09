const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises;

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        service: 'certificate-manager',
        timestamp: new Date().toISOString()
    });
});

// API Routes
app.get('/api/certificates', async (req, res) => {
    try {
        // Mock data for now
        const certificates = [
            {
                id: 'cert-001',
                name: 'Quality Certificate - Additive Manufacturing',
                type: 'quality_certificate',
                status: 'active',
                issuedDate: '2024-01-15',
                expiryDate: '2025-01-15',
                issuer: 'QI Authority',
                digitalTwinId: 'dt-001'
            },
            {
                id: 'cert-002',
                name: 'Safety Certificate - Hydrogen Station',
                type: 'safety_certificate',
                status: 'active',
                issuedDate: '2024-02-20',
                expiryDate: '2025-02-20',
                issuer: 'Safety Authority',
                digitalTwinId: 'dt-002'
            }
        ];
        
        res.json(certificates);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/certificates', async (req, res) => {
    try {
        const certificate = {
            id: `cert-${Date.now()}`,
            ...req.body,
            createdAt: new Date().toISOString()
        };
        
        // Mock: save certificate
        res.status(201).json(certificate);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/certificates/:id', async (req, res) => {
    try {
        const { id } = req.params;
        
        // Mock: get certificate by ID
        const certificate = {
            id,
            name: 'Sample Certificate',
            type: 'quality_certificate',
            status: 'active',
            issuedDate: '2024-01-15',
            expiryDate: '2025-01-15',
            issuer: 'QI Authority',
            digitalTwinId: 'dt-001'
        };
        
        res.json(certificate);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`Certificate Manager running on http://localhost:${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/health`);
});

module.exports = app; 