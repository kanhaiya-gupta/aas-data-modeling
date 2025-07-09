/**
 * Neo4j Knowledge Graph Frontend JavaScript
 * Handles graph visualization, queries, analytics, and data import
 */

// Global variables
let graphData = null;
let simulation = null;
let charts = {};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeNeo4jInterface();
});

/**
 * Initialize the Neo4j interface
 */
function initializeNeo4jInterface() {
    console.log('Initializing Neo4j Knowledge Graph Interface...');
    
    // Check connection status
    checkConnectionStatus();
    
    // Load initial data
    loadDatabaseStats();
    
    // Initialize charts
    initializeCharts();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load graph data if on graph tab
    if (document.getElementById('graph-tab').classList.contains('active')) {
        loadGraphData();
    }
}

/**
 * Check Neo4j connection status
 */
async function checkConnectionStatus() {
    try {
        const response = await fetch('/api/kg-neo4j/status');
        const data = await response.json();
        
        const statusIndicator = document.getElementById('connectionStatus');
        const statusText = document.getElementById('connectionText');
        
        if (data.connected) {
            statusIndicator.className = 'status-indicator status-connected';
            statusText.textContent = 'Connected';
        } else {
            statusIndicator.className = 'status-indicator status-disconnected';
            statusText.textContent = 'Disconnected';
        }
    } catch (error) {
        console.error('Error checking connection status:', error);
        const statusIndicator = document.getElementById('connectionStatus');
        const statusText = document.getElementById('connectionText');
        statusIndicator.className = 'status-indicator status-disconnected';
        statusText.textContent = 'Error';
    }
}

/**
 * Load database statistics
 */
async function loadDatabaseStats() {
    try {
        const response = await fetch('/api/kg-neo4j/stats');
        const data = await response.json();
        
        // Update stats cards
        document.getElementById('nodeCount').textContent = data.total_nodes || 0;
        document.getElementById('relationshipCount').textContent = data.total_relationships || 0;
        document.getElementById('assetCount').textContent = data.asset_count || 0;
        document.getElementById('submodelCount').textContent = data.submodel_count || 0;
        
    } catch (error) {
        console.error('Error loading database stats:', error);
        // Set default values
        document.getElementById('nodeCount').textContent = '-';
        document.getElementById('relationshipCount').textContent = '-';
        document.getElementById('assetCount').textContent = '-';
        document.getElementById('submodelCount').textContent = '-';
    }
}

/**
 * Load graph data for visualization
 */
async function loadGraphData() {
    try {
        const response = await fetch('/api/kg-neo4j/graph-data');
        const data = await response.json();
        
        if (data.success) {
            graphData = data.data;
            renderGraph();
        } else {
            console.error('Failed to load graph data:', data.error);
            showNotification('Failed to load graph data', 'error');
        }
    } catch (error) {
        console.error('Error loading graph data:', error);
        showNotification('Error loading graph data', 'error');
    }
}

/**
 * Render the graph visualization using D3.js
 */
function renderGraph() {
    if (!graphData || !graphData.nodes) {
        console.warn('No graph data available');
        return;
    }
    
    const container = document.getElementById('graphVisualization');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // Clear previous visualization
    container.innerHTML = '';
    
    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Create zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 10])
        .on('zoom', (event) => {
            svg.select('g').attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    // Create main group
    const g = svg.append('g');
    
    // Create force simulation
    simulation = d3.forceSimulation(graphData.nodes)
        .force('link', d3.forceLink(graphData.links || []).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(30));
    
    // Create links
    const links = g.append('g')
        .selectAll('line')
        .data(graphData.links || [])
        .enter()
        .append('line')
        .attr('class', 'link')
        .attr('stroke-width', 2);
    
    // Create nodes
    const nodes = g.append('g')
        .selectAll('circle')
        .data(graphData.nodes)
        .enter()
        .append('circle')
        .attr('class', 'node')
        .attr('r', d => getNodeRadius(d))
        .attr('fill', d => getNodeColor(d))
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Add node labels
    const labels = g.append('g')
        .selectAll('text')
        .data(graphData.nodes)
        .enter()
        .append('text')
        .attr('class', 'node-label')
        .text(d => d.id_short || d.id)
        .attr('dy', '.35em');
    
    // Add tooltips
    nodes.on('mouseover', function(event, d) {
        showTooltip(event, d);
    })
    .on('mouseout', function() {
        hideTooltip();
    });
    
    // Update positions on simulation tick
    simulation.on('tick', () => {
        links
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        nodes
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        labels
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
}

/**
 * Get node radius based on type
 */
function getNodeRadius(node) {
    switch (node.type) {
        case 'asset': return 15;
        case 'submodel': return 12;
        default: return 10;
    }
}

/**
 * Get node color based on type
 */
function getNodeColor(node) {
    switch (node.type) {
        case 'asset': return '#4CAF50';
        case 'submodel': return '#2196F3';
        default: return '#9E9E9E';
    }
}

/**
 * Drag functions for interactive nodes
 */
function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

/**
 * Show tooltip for nodes
 */
function showTooltip(event, node) {
    const tooltip = document.getElementById('tooltip');
    tooltip.style.display = 'block';
    tooltip.style.left = event.pageX + 10 + 'px';
    tooltip.style.top = event.pageY - 10 + 'px';
    
    tooltip.innerHTML = `
        <strong>${node.type.toUpperCase()}</strong><br>
        ID: ${node.id}<br>
        ${node.id_short ? `Short ID: ${node.id_short}<br>` : ''}
        ${node.properties?.description ? `Description: ${node.properties.description}<br>` : ''}
        ${node.properties?.quality_level ? `Quality: ${node.properties.quality_level}` : ''}
    `;
}

/**
 * Hide tooltip
 */
function hideTooltip() {
    document.getElementById('tooltip').style.display = 'none';
}

/**
 * Execute Cypher query
 */
async function executeQuery() {
    const query = document.getElementById('cypherQuery').value.trim();
    if (!query) {
        showNotification('Please enter a query', 'warning');
        return;
    }
    
    const resultsDiv = document.getElementById('queryResults');
    resultsDiv.innerHTML = '<p class="text-muted">Executing query...</p>';
    
    try {
        const response = await fetch('/api/kg-neo4j/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayQueryResults(data.results);
        } else {
            resultsDiv.innerHTML = `<p class="text-danger">Error: ${data.error}</p>`;
        }
    } catch (error) {
        console.error('Error executing query:', error);
        resultsDiv.innerHTML = '<p class="text-danger">Error executing query</p>';
    }
}

/**
 * Display query results
 */
function displayQueryResults(results) {
    const resultsDiv = document.getElementById('queryResults');
    
    if (!results || results.length === 0) {
        resultsDiv.innerHTML = '<p class="text-muted">No results found</p>';
        return;
    }
    
    let html = '<div class="table-responsive"><table class="table table-sm">';
    
    // Create header
    const keys = Object.keys(results[0]);
    html += '<thead><tr>';
    keys.forEach(key => {
        html += `<th>${key}</th>`;
    });
    html += '</tr></thead>';
    
    // Create rows
    html += '<tbody>';
    results.forEach(row => {
        html += '<tr>';
        keys.forEach(key => {
            const value = row[key];
            if (typeof value === 'object') {
                html += `<td><code>${JSON.stringify(value)}</code></td>`;
            } else {
                html += `<td>${value}</td>`;
            }
        });
        html += '</tr>';
    });
    html += '</tbody></table></div>';
    
    resultsDiv.innerHTML = html;
}

/**
 * Load pre-built queries
 */
function loadQuery(type) {
    const queries = {
        'basic-stats': 'MATCH (n) RETURN labels(n) as labels, count(n) as count ORDER BY count DESC',
        'quality-distribution': 'MATCH (n) WHERE n.quality_level IS NOT NULL RETURN n.quality_level as quality, count(n) as count ORDER BY count DESC',
        'compliance-summary': 'MATCH (n) WHERE n.compliance_status IS NOT NULL RETURN n.compliance_status as status, count(n) as count ORDER BY count DESC',
        'isolated-nodes': 'MATCH (n) WHERE NOT (n)--() RETURN n.id as id, labels(n) as labels LIMIT 10'
    };
    
    document.getElementById('cypherQuery').value = queries[type] || '';
}

/**
 * Clear query editor
 */
function clearQuery() {
    document.getElementById('cypherQuery').value = '';
    document.getElementById('queryResults').innerHTML = '<p class="text-muted">Execute a query to see results here...</p>';
}

/**
 * Initialize charts for analytics
 */
function initializeCharts() {
    // Quality distribution chart
    const qualityCtx = document.getElementById('qualityChart');
    if (qualityCtx) {
        charts.quality = new Chart(qualityCtx, {
            type: 'doughnut',
            data: {
                labels: ['HIGH', 'MEDIUM', 'LOW'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Entity types chart
    const entityCtx = document.getElementById('entityChart');
    if (entityCtx) {
        charts.entity = new Chart(entityCtx, {
            type: 'bar',
            data: {
                labels: ['Assets', 'Submodels'],
                datasets: [{
                    label: 'Count',
                    data: [0, 0],
                    backgroundColor: ['#4CAF50', '#2196F3']
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

/**
 * Load analytics data
 */
async function loadAnalytics() {
    try {
        const response = await fetch('/api/kg-neo4j/analytics');
        const data = await response.json();
        
        if (data.success) {
            updateCharts(data.analytics);
            displayAnalyticsResults(data.analytics);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

/**
 * Update charts with analytics data
 */
function updateCharts(analytics) {
    // Update quality distribution chart
    if (charts.quality && analytics.quality_distribution) {
        charts.quality.data.datasets[0].data = [
            analytics.quality_distribution.HIGH || 0,
            analytics.quality_distribution.MEDIUM || 0,
            analytics.quality_distribution.LOW || 0
        ];
        charts.quality.update();
    }
    
    // Update entity types chart
    if (charts.entity && analytics.entity_distribution) {
        charts.entity.data.datasets[0].data = [
            analytics.entity_distribution.asset || 0,
            analytics.entity_distribution.submodel || 0
        ];
        charts.entity.update();
    }
}

/**
 * Display detailed analytics results
 */
function displayAnalyticsResults(analytics) {
    const resultsDiv = document.getElementById('analyticsResults');
    
    let html = '<div class="row">';
    
    // Quality metrics
    if (analytics.quality_metrics) {
        html += `
            <div class="col-md-6">
                <h6>Quality Metrics</h6>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Average Quality Score:</span>
                        <span class="badge bg-primary">${analytics.quality_metrics.average_score || 'N/A'}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                        <span>High Quality Items:</span>
                        <span class="badge bg-success">${analytics.quality_metrics.high_quality_count || 0}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Compliance Rate:</span>
                        <span class="badge bg-info">${analytics.quality_metrics.compliance_rate || 'N/A'}%</span>
                    </li>
                </ul>
            </div>
        `;
    }
    
    // Graph metrics
    if (analytics.graph_metrics) {
        html += `
            <div class="col-md-6">
                <h6>Graph Metrics</h6>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Total Nodes:</span>
                        <span class="badge bg-secondary">${analytics.graph_metrics.total_nodes || 0}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Total Relationships:</span>
                        <span class="badge bg-secondary">${analytics.graph_metrics.total_relationships || 0}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Isolated Nodes:</span>
                        <span class="badge bg-warning">${analytics.graph_metrics.isolated_nodes || 0}</span>
                    </li>
                </ul>
            </div>
        `;
    }
    
    html += '</div>';
    resultsDiv.innerHTML = html;
}

/**
 * Import data from ETL output
 */
async function importData() {
    const directory = document.getElementById('importDirectory').value;
    const clearDatabase = document.getElementById('clearDatabase').checked;
    
    const statusDiv = document.getElementById('importStatus');
    statusDiv.innerHTML = '<p class="text-info">Importing data...</p>';
    
    try {
        const response = await fetch('/api/kg-neo4j/import', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                directory: directory,
                clear_database: clearDatabase
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6>Import Successful!</h6>
                    <p>Imported ${data.imported_files} files</p>
                    <p>Nodes: ${data.nodes_imported}</p>
                    <p>Relationships: ${data.relationships_imported}</p>
                </div>
            `;
            
            // Refresh stats and data
            loadDatabaseStats();
            if (document.getElementById('graph-tab').classList.contains('active')) {
                loadGraphData();
            }
        } else {
            statusDiv.innerHTML = `<div class="alert alert-danger">Import failed: ${data.error}</div>`;
        }
    } catch (error) {
        console.error('Error importing data:', error);
        statusDiv.innerHTML = '<div class="alert alert-danger">Error importing data</div>';
    }
}

/**
 * Utility functions
 */
function refreshConnection() {
    checkConnectionStatus();
    loadDatabaseStats();
}

function resetZoom() {
    if (simulation) {
        simulation.alpha(1).restart();
    }
}

function exportGraph() {
    if (graphData) {
        const dataStr = JSON.stringify(graphData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'neo4j-graph-data.json';
        link.click();
        URL.revokeObjectURL(url);
    }
}

function showNotification(message, type = 'info') {
    // Create a simple notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Import form submission
    const importForm = document.getElementById('importForm');
    if (importForm) {
        importForm.addEventListener('submit', function(e) {
            e.preventDefault();
            importData();
        });
    }
    
    // Tab change events
    const tabs = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            if (e.target.id === 'graph-tab') {
                loadGraphData();
            } else if (e.target.id === 'analytics-tab') {
                loadAnalytics();
            }
        });
    });
}

// Make functions globally available
window.loadGraphData = loadGraphData;
window.executeQuery = executeQuery;
window.loadQuery = loadQuery;
window.clearQuery = clearQuery;
window.refreshConnection = refreshConnection;
window.resetZoom = resetZoom;
window.exportGraph = exportGraph; 