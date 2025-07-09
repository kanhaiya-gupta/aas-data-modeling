# QI Digital Platform

Quality Infrastructure Digital Twin Management & Analytics Platform

## 🏗️ Project Structure

```
aas-data-modeling/
├── backend/                    # Backend services
│   ├── ai-rag/                # AI/RAG System (FastAPI)
│   ├── twin-registry/         # Digital Twin Registry (FastAPI)
│   ├── certificate-manager/   # Certificate Manager (Node.js)
│   ├── qi-analytics/          # Analytics Dashboard (Node.js)
│   └── shared/                # Shared utilities and models
├── webapp/                    # Frontend application (Flask)
│   ├── static/               # CSS, JS, images
│   ├── templates/            # HTML templates
│   ├── config/               # Configuration files
│   └── app.py               # Flask web application
├── docs/                     # Documentation
│   ├── API.md               # API documentation
│   ├── ARCHITECTURE.md      # System architecture
│   ├── DEVELOPMENT.md       # Development guide
│   └── DEPLOYMENT.md        # Deployment guide
├── AasxPackageExplorer/      # AASX Explorer (Windows)
├── main.py                   # Main orchestrator
├── requirements.txt          # Backend dependencies
└── docker-compose.yml        # Docker orchestration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Conda (recommended)

### Setup

1. **Create conda environment:**
   ```bash
   conda create -n qi-digital-platform python=3.11 -y
   conda activate qi-digital-platform
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r webapp/requirements.txt
   ```

3. **Start the platform:**
   ```bash
   python main.py start
   ```

4. **Access the application:**
   - Web Interface: http://localhost:5000
   - AI/RAG API: http://localhost:8000
   - Twin Registry: http://localhost:8001
   - Certificate Manager: http://localhost:3001
   - Analytics Dashboard: http://localhost:3002

## 🎯 Features

- **Digital Twin Management**: Create and manage digital twins for quality infrastructure
- **AI/RAG System**: Intelligent analysis and retrieval of quality data
- **Certificate Management**: Digital certificates and product passports
- **Analytics Dashboard**: Real-time analytics and insights
- **AAS Integration**: Asset Administrative Shell support

## 🛠️ Development

### Backend Services

- **AI/RAG System**: FastAPI-based AI and retrieval system
- **Twin Registry**: Digital twin registration and management
- **Certificate Manager**: Node.js certificate management
- **Analytics Dashboard**: Node.js analytics and visualization

### Frontend

- **Flask Webapp**: Modern web interface with Bootstrap
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Live data updates and notifications

## 📚 Documentation

- [API Documentation](docs/API.md) - Complete API reference
- [Architecture Guide](docs/ARCHITECTURE.md) - System architecture and design
- [Development Guide](docs/DEVELOPMENT.md) - Development setup and guidelines
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the [documentation](docs/)
- Review the [development guide](docs/DEVELOPMENT.md)
