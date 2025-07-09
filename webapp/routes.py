"""
Routes for QI Digital Platform Flask Webapp
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import requests
import os

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# Service URLs
SERVICE_URLS = {
    'ai_rag': 'http://localhost:8000',
    'twin_registry': 'http://localhost:8001',
    'certificate_manager': 'http://localhost:3001',
    'qi_analytics': 'http://localhost:3002'
}

@main_bp.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    """Analytics dashboard"""
    try:
        # Get analytics data
        response = requests.get(f"{SERVICE_URLS['qi_analytics']}/api/analytics/overview", timeout=5)
        analytics_data = response.json() if response.status_code == 200 else {}
    except:
        analytics_data = {}
    
    return render_template('dashboard.html', analytics=analytics_data)

@main_bp.route('/certificates')
def certificates():
    """Certificate management"""
    try:
        # Get certificates data
        response = requests.get(f"{SERVICE_URLS['certificate_manager']}/api/certificates", timeout=5)
        certificates_data = response.json() if response.status_code == 200 else []
    except:
        certificates_data = []
    
    return render_template('certificates.html', certificates=certificates_data)

@main_bp.route('/twins')
def twins():
    """Digital twins view"""
    try:
        # Get twins data
        response = requests.get(f"{SERVICE_URLS['twin_registry']}/api/twins", timeout=5)
        twins_data = response.json() if response.status_code == 200 else []
    except:
        twins_data = []
    
    return render_template('twins.html', twins=twins_data)

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'qi-webapp',
        'timestamp': '2024-01-01T00:00:00Z'
    })

# API routes
@api_bp.route('/services/status')
def services_status():
    """Get status of all services"""
    status = {}
    
    for service_name, url in SERVICE_URLS.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            status[service_name] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'url': url
            }
        except:
            status[service_name] = {
                'status': 'unreachable',
                'url': url
            }
    
    return jsonify(status)

@api_bp.route('/query', methods=['POST'])
def query_ai():
    """Proxy AI query to AI/RAG service"""
    try:
        data = request.get_json()
        response = requests.post(f"{SERVICE_URLS['ai_rag']}/analyze", json=data, timeout=30)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500 