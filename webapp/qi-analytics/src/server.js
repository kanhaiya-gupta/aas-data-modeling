const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3002;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        service: 'qi-analytics',
        timestamp: new Date().toISOString()
    });
});

// API Routes
app.get('/api/analytics/overview', async (req, res) => {
    try {
        // Mock analytics data
        const overview = {
            totalDigitalTwins: 156,
            activeCertificates: 89,
            qualityScore: 94.2,
            complianceRate: 98.7,
            recentAlerts: 3,
            systemHealth: 'excellent'
        };
        
        res.json(overview);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/analytics/trends', async (req, res) => {
    try {
        // Mock trend data
        const trends = {
            qualityScores: [
                { date: '2024-01', score: 92.1 },
                { date: '2024-02', score: 93.5 },
                { date: '2024-03', score: 94.2 },
                { date: '2024-04', score: 94.8 },
                { date: '2024-05', score: 95.1 },
                { date: '2024-06', score: 94.2 }
            ],
            digitalTwins: [
                { date: '2024-01', count: 120 },
                { date: '2024-02', count: 135 },
                { date: '2024-03', count: 142 },
                { date: '2024-04', count: 148 },
                { date: '2024-05', count: 152 },
                { date: '2024-06', count: 156 }
            ]
        };
        
        res.json(trends);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/analytics/alerts', async (req, res) => {
    try {
        // Mock alerts data
        const alerts = [
            {
                id: 'alert-001',
                type: 'quality_threshold',
                severity: 'medium',
                message: 'Quality score dropped below threshold for Additive Manufacturing Unit #3',
                timestamp: '2024-06-15T10:30:00Z',
                status: 'active'
            },
            {
                id: 'alert-002',
                type: 'certificate_expiry',
                severity: 'high',
                message: 'Safety certificate expiring soon for Hydrogen Station #1',
                timestamp: '2024-06-14T15:45:00Z',
                status: 'pending'
            },
            {
                id: 'alert-003',
                type: 'system_health',
                severity: 'low',
                message: 'Minor performance degradation detected in AI/RAG system',
                timestamp: '2024-06-13T09:15:00Z',
                status: 'resolved'
            }
        ];
        
        res.json(alerts);
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
    console.log(`QI Analytics Dashboard running on http://localhost:${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/health`);
});

module.exports = app; 