/**
 * AASX ETL Pipeline JavaScript
 * 
 * Handles the frontend functionality for the AASX ETL pipeline including:
 * - ETL pipeline execution
 * - Progress tracking
 * - Results display
 * - RAG search functionality
 * - Configuration management
 */

class AASXETLPipeline {
    constructor() {
        this.isProcessing = false;
        this.currentProgress = {
            extract: 0,
            transform: 0,
            load: 0,
            overall: 0
        };
        this.initializeEventListeners();
        this.initializeProgressCircles();
    }

    initializeEventListeners() {
        // ETL Pipeline Controls
        document.getElementById('runETLPipeline')?.addEventListener('click', () => this.runETLPipeline());
        document.getElementById('processAllFiles')?.addEventListener('click', () => this.processAllFiles());
        document.getElementById('exportRAGDataset')?.addEventListener('click', () => this.exportRAGDataset());
        document.getElementById('viewPipelineStats')?.addEventListener('click', () => this.viewPipelineStats());

        // Individual file processing
        document.querySelectorAll('.process-file').forEach(button => {
            button.addEventListener('click', (e) => {
                const filename = e.target.closest('button').dataset.filename;
                this.processSingleFile(filename);
            });
        });

        // File actions
        document.querySelectorAll('.open-file').forEach(button => {
            button.addEventListener('click', (e) => {
                const filename = e.target.closest('button').dataset.filename;
                this.openFile(filename);
            });
        });

        document.querySelectorAll('.view-results').forEach(button => {
            button.addEventListener('click', (e) => {
                const filename = e.target.closest('button').dataset.filename;
                this.viewFileResults(filename);
            });
        });

        // RAG Search
        document.getElementById('searchRAG')?.addEventListener('click', () => this.performRAGSearch());
        document.getElementById('ragQuery')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.performRAGSearch();
        });

        // Launch Explorer
        document.getElementById('launchExplorer')?.addEventListener('click', () => {
            const modal = new bootstrap.Modal(document.getElementById('launchExplorerModal'));
            modal.show();
        });

        // Refresh files
        document.getElementById('refreshFiles')?.addEventListener('click', () => this.refreshFiles());

        // Export results
        document.getElementById('exportResults')?.addEventListener('click', () => this.exportResults());
    }

    initializeProgressCircles() {
        // Initialize progress circles with CSS
        const style = document.createElement('style');
        style.textContent = `
            .progress-circle {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: conic-gradient(#007bff 0deg, #e9ecef 0deg);
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto;
                position: relative;
            }
            .progress-circle::before {
                content: '';
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: white;
                position: absolute;
            }
            .progress-text {
                position: relative;
                z-index: 1;
                font-weight: bold;
                color: #007bff;
            }
        `;
        document.head.appendChild(style);
    }

    async runETLPipeline() {
        if (this.isProcessing) {
            this.showAlert('ETL pipeline is already running', 'warning');
            return;
        }

        this.isProcessing = true;
        this.showETLProgress();
        this.updateETLStatus('Starting ETL pipeline...');

        try {
            // Get configuration
            const config = this.getETLConfiguration();
            
            // Start ETL processing
            const response = await fetch('/api/aasx/etl/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.updateETLProgress(100, 100, 100, 100);
                this.updateETLStatus('ETL pipeline completed successfully!');
                this.showETLResults(result);
                this.updateFileStatuses(result.processed_files);
            } else {
                throw new Error(result.error || 'ETL pipeline failed');
            }

        } catch (error) {
            console.error('ETL Pipeline Error:', error);
            this.updateETLStatus(`Error: ${error.message}`, 'error');
            this.showAlert(`ETL pipeline failed: ${error.message}`, 'danger');
        } finally {
            this.isProcessing = false;
        }
    }

    async processSingleFile(filename) {
        if (this.isProcessing) {
            this.showAlert('ETL pipeline is already running', 'warning');
            return;
        }

        this.isProcessing = true;
        this.updateFileStatus(filename, 'processing');
        this.showETLProgress();

        try {
            const config = this.getETLConfiguration();
            config.files = [filename];

            const response = await fetch('/api/aasx/etl/process-file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.updateFileStatus(filename, 'completed');
                this.updateETLProgress(100, 100, 100, 100);
                this.updateETLStatus('File processed successfully!');
                this.showFileResults(filename, result);
            } else {
                this.updateFileStatus(filename, 'failed');
                throw new Error(result.error || 'File processing failed');
            }

        } catch (error) {
            console.error('File Processing Error:', error);
            this.updateFileStatus(filename, 'failed');
            this.updateETLStatus(`Error: ${error.message}`, 'error');
            this.showAlert(`File processing failed: ${error.message}`, 'danger');
        } finally {
            this.isProcessing = false;
        }
    }

    async processAllFiles() {
        const files = Array.from(document.querySelectorAll('#aasxFilesTable tbody tr'))
            .map(row => row.dataset.filename);

        if (files.length === 0) {
            this.showAlert('No files to process', 'warning');
            return;
        }

        this.isProcessing = true;
        this.showETLProgress();
        this.updateETLStatus('Processing all files...');

        try {
            const config = this.getETLConfiguration();
            config.files = files;

            const response = await fetch('/api/aasx/etl/process-batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.updateETLProgress(100, 100, 100, 100);
                this.updateETLStatus('All files processed successfully!');
                this.showETLResults(result);
                this.updateFileStatuses(result.processed_files);
            } else {
                throw new Error(result.error || 'Batch processing failed');
            }

        } catch (error) {
            console.error('Batch Processing Error:', error);
            this.updateETLStatus(`Error: ${error.message}`, 'error');
            this.showAlert(`Batch processing failed: ${error.message}`, 'danger');
        } finally {
            this.isProcessing = false;
        }
    }

    async performRAGSearch() {
        const query = document.getElementById('ragQuery').value.trim();
        const entityType = document.getElementById('searchEntityType').value;

        if (!query) {
            this.showAlert('Please enter a search query', 'warning');
            return;
        }

        const resultsContainer = document.getElementById('searchResults');
        resultsContainer.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Searching...</div>';

        try {
            const response = await fetch('/api/aasx/rag/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    entity_type: entityType,
                    top_k: 10
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.displayRAGResults(result.results, query);
            } else {
                throw new Error(result.error || 'Search failed');
            }

        } catch (error) {
            console.error('RAG Search Error:', error);
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    Search failed: ${error.message}
                </div>
            `;
        }
    }

    displayRAGResults(results, query) {
        const resultsContainer = document.getElementById('searchResults');
        
        if (results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i>
                    No results found for "${query}"
                </div>
            `;
            return;
        }

        let html = `
            <h6>Search Results for "${query}" (${results.length} results)</h6>
            <div class="list-group">
        `;

        results.forEach((result, index) => {
            const similarity = (1 - result.similarity) * 100; // Convert distance to similarity
            const badgeClass = similarity > 80 ? 'bg-success' : similarity > 60 ? 'bg-warning' : 'bg-secondary';
            
            html += `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-1">
                                <span class="badge ${badgeClass} me-2">${result.metadata.entity_type}</span>
                                ${result.metadata.entity_id || 'Unknown ID'}
                            </h6>
                            <p class="mb-1">${result.document}</p>
                            <small class="text-muted">
                                Quality: ${result.metadata.quality_level || 'N/A'} | 
                                Compliance: ${result.metadata.compliance_status || 'N/A'}
                            </small>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-primary">${similarity.toFixed(1)}%</span>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        resultsContainer.innerHTML = html;
    }

    async exportRAGDataset() {
        try {
            const response = await fetch('/api/aasx/rag/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.showAlert('RAG dataset exported successfully!', 'success');
                // Trigger download
                const link = document.createElement('a');
                link.href = result.download_url;
                link.download = 'rag_dataset.json';
                link.click();
            } else {
                throw new Error(result.error || 'Export failed');
            }

        } catch (error) {
            console.error('RAG Export Error:', error);
            this.showAlert(`RAG export failed: ${error.message}`, 'danger');
        }
    }

    async viewPipelineStats() {
        try {
            const response = await fetch('/api/aasx/etl/stats');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const stats = await response.json();
            this.showPipelineStats(stats);

        } catch (error) {
            console.error('Stats Error:', error);
            this.showAlert(`Failed to load pipeline stats: ${error.message}`, 'danger');
        }
    }

    showPipelineStats(stats) {
        const modal = new bootstrap.Modal(document.getElementById('etlResultsModal'));
        const content = document.getElementById('etlResultsContent');
        
        content.innerHTML = `
            <h6>Pipeline Statistics</h6>
            <div class="row">
                <div class="col-md-6">
                    <table class="table table-sm">
                        <tbody>
                            <tr><td>Files Processed:</td><td>${stats.files_processed || 0}</td></tr>
                            <tr><td>Files Failed:</td><td>${stats.files_failed || 0}</td></tr>
                            <tr><td>Total Processing Time:</td><td>${(stats.total_processing_time || 0).toFixed(2)}s</td></tr>
                            <tr><td>Extract Time:</td><td>${(stats.extract_time || 0).toFixed(2)}s</td></tr>
                            <tr><td>Transform Time:</td><td>${(stats.transform_time || 0).toFixed(2)}s</td></tr>
                            <tr><td>Load Time:</td><td>${(stats.load_time || 0).toFixed(2)}s</td></tr>
                        </tbody>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Component Statistics</h6>
                    <div class="mb-3">
                        <strong>Processor:</strong>
                        <ul class="list-unstyled ms-3">
                            <li>Files processed: ${stats.component_stats?.processor?.files_processed || 0}</li>
                            <li>Success rate: ${((stats.component_stats?.processor?.success_rate || 0) * 100).toFixed(1)}%</li>
                        </ul>
                    </div>
                    <div class="mb-3">
                        <strong>Transformer:</strong>
                        <ul class="list-unstyled ms-3">
                            <li>Transformations applied: ${stats.component_stats?.transformer?.transformations_applied || 0}</li>
                            <li>Output formats: ${stats.component_stats?.transformer?.output_formats || 0}</li>
                        </ul>
                    </div>
                    <div class="mb-3">
                        <strong>Loader:</strong>
                        <ul class="list-unstyled ms-3">
                            <li>Database records: ${stats.component_stats?.loader?.database_records || 0}</li>
                            <li>Vector embeddings: ${stats.component_stats?.loader?.vector_embeddings || 0}</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
        
        modal.show();
    }

    getETLConfiguration() {
        return {
            extract: {
                enable_hybrid_processing: document.getElementById('enableHybridProcessing')?.checked || false,
                enable_validation: document.getElementById('enableValidation')?.checked || false
            },
            transform: {
                enable_quality_checks: document.getElementById('enableQualityChecks')?.checked || false,
                enable_enrichment: document.getElementById('enableEnrichment')?.checked || false,
                output_formats: this.getSelectedOutputFormats(),
                include_metadata: true
            },
            load: {
                enable_vector_db: document.getElementById('enableVectorDB')?.checked || false,
                enable_rag_export: document.getElementById('enableRAGExport')?.checked || false,
                vector_db_type: document.getElementById('vectorDBType')?.value || 'chromadb',
                output_directory: 'output',
                database_path: 'aasx_data.db',
                vector_db_path: 'vector_db'
            },
            parallel_processing: false,
            max_workers: 4
        };
    }

    getSelectedOutputFormats() {
        const formats = [];
        if (document.getElementById('formatJson')?.checked) formats.push('json');
        if (document.getElementById('formatCsv')?.checked) formats.push('csv');
        if (document.getElementById('formatGraph')?.checked) formats.push('graph');
        return formats.length > 0 ? formats : ['json'];
    }

    showETLProgress() {
        document.getElementById('etlProgress').style.display = 'block';
        this.updateETLProgress(0, 0, 0, 0);
    }

    updateETLProgress(extract, transform, load, overall) {
        this.currentProgress = { extract, transform, load, overall };
        
        // Update progress circles
        this.updateProgressCircle('extractProgress', extract);
        this.updateProgressCircle('transformProgress', transform);
        this.updateProgressCircle('loadProgress', load);
        this.updateProgressCircle('overallProgress', overall);
        
        // Update progress bar
        const progressBar = document.getElementById('overallProgressBar');
        if (progressBar) {
            progressBar.style.width = `${overall}%`;
            progressBar.setAttribute('aria-valuenow', overall);
        }
    }

    updateProgressCircle(elementId, progress) {
        const element = document.getElementById(elementId);
        if (element) {
            const degrees = (progress / 100) * 360;
            element.style.background = `conic-gradient(#007bff ${degrees}deg, #e9ecef ${degrees}deg)`;
            element.querySelector('.progress-text').textContent = `${progress}%`;
        }
    }

    updateETLStatus(message, type = 'info') {
        const statusElement = document.getElementById('etlStatusText');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `text-${type === 'error' ? 'danger' : type}`;
        }
    }

    updateFileStatus(filename, status) {
        const statusElement = document.getElementById(`status-${filename}`);
        if (statusElement) {
            const statusClasses = {
                'pending': 'bg-secondary',
                'processing': 'bg-warning',
                'completed': 'bg-success',
                'failed': 'bg-danger'
            };
            
            statusElement.className = `badge ${statusClasses[status] || 'bg-secondary'}`;
            statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        }
    }

    updateFileStatuses(processedFiles) {
        if (processedFiles) {
            Object.entries(processedFiles).forEach(([filename, status]) => {
                this.updateFileStatus(filename, status);
            });
        }
    }

    showETLResults(result) {
        document.getElementById('etlResults').style.display = 'block';
        
        // Update statistics
        document.getElementById('statsFilesProcessed').textContent = result.files_processed || 0;
        document.getElementById('statsFilesFailed').textContent = result.files_failed || 0;
        document.getElementById('statsTotalTime').textContent = `${(result.total_time || 0).toFixed(2)}s`;
        document.getElementById('statsDBRecords').textContent = result.database_records || 0;
        document.getElementById('statsVectorEmbeddings').textContent = result.vector_embeddings || 0;
        
        // Update output files
        const outputFilesList = document.getElementById('outputFilesList');
        if (result.files_exported && result.files_exported.length > 0) {
            let html = '<ul class="list-unstyled">';
            result.files_exported.forEach(file => {
                html += `<li><i class="fas fa-file text-primary me-2"></i>${file}</li>`;
            });
            html += '</ul>';
            outputFilesList.innerHTML = html;
        } else {
            outputFilesList.innerHTML = '<p class="text-muted">No output files generated.</p>';
        }
    }

    showFileResults(filename, result) {
        const modal = new bootstrap.Modal(document.getElementById('etlResultsModal'));
        const content = document.getElementById('etlResultsContent');
        
        content.innerHTML = `
            <h6>Processing Results for ${filename}</h6>
            <div class="row">
                <div class="col-md-6">
                    <h6>Processing Status</h6>
                    <p><strong>Status:</strong> <span class="badge bg-success">Completed</span></p>
                    <p><strong>Processing Time:</strong> ${(result.processing_time || 0).toFixed(2)}s</p>
                    
                    <h6 class="mt-3">Phase Results</h6>
                    <ul class="list-unstyled">
                        <li><strong>Extract:</strong> ${result.extract_result?.success ? 'Success' : 'Failed'}</li>
                        <li><strong>Transform:</strong> ${result.transform_result?.success ? 'Success' : 'Failed'}</li>
                        <li><strong>Load:</strong> ${result.load_result?.success ? 'Success' : 'Failed'}</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Output Details</h6>
                    <p><strong>Files Exported:</strong> ${result.load_result?.files_exported?.length || 0}</p>
                    <p><strong>Database Records:</strong> ${result.load_result?.database_records || 0}</p>
                    <p><strong>Vector Embeddings:</strong> ${result.load_result?.vector_embeddings || 0}</p>
                </div>
            </div>
        `;
        
        modal.show();
    }

    async openFile(filename) {
        try {
            const response = await fetch(`/api/aasx/open/${encodeURIComponent(filename)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('File opened successfully!', 'success');
            } else {
                throw new Error(result.error || 'Failed to open file');
            }
        } catch (error) {
            console.error('Open File Error:', error);
            this.showAlert(`Failed to open file: ${error.message}`, 'danger');
        }
    }

    async viewFileResults(filename) {
        try {
            const response = await fetch(`/api/aasx/results/${encodeURIComponent(filename)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            
            if (result.success) {
                this.showFileResults(filename, result.data);
            } else {
                throw new Error(result.error || 'Failed to load results');
            }
        } catch (error) {
            console.error('View Results Error:', error);
            this.showAlert(`Failed to load results: ${error.message}`, 'danger');
        }
    }

    async refreshFiles() {
        try {
            const response = await fetch('/api/aasx/refresh');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // Reload the page to show updated files
            window.location.reload();
        } catch (error) {
            console.error('Refresh Error:', error);
            this.showAlert(`Failed to refresh files: ${error.message}`, 'danger');
        }
    }

    async exportResults() {
        try {
            const response = await fetch('/api/aasx/etl/export-results', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                // Trigger download
                const link = document.createElement('a');
                link.href = result.download_url;
                link.download = 'etl_results.json';
                link.click();
                this.showAlert('Results exported successfully!', 'success');
            } else {
                throw new Error(result.error || 'Export failed');
            }

        } catch (error) {
            console.error('Export Error:', error);
            this.showAlert(`Export failed: ${error.message}`, 'danger');
        }
    }

    showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Global function for launching explorer
function launchExplorer(method) {
    const modal = bootstrap.Modal.getInstance(document.getElementById('launchExplorerModal'));
    modal.hide();
    
    switch (method) {
        case 'direct':
            window.open('/api/aasx/launch', '_blank');
            break;
        case 'script':
            window.open('/api/aasx/launch-script', '_blank');
            break;
        case 'manual':
            alert('Manual Launch Instructions:\n\n1. Navigate to the AasxPackageExplorer directory\n2. Run AasxPackageExplorer.exe\n3. Open your AASX file from the application');
            break;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.aasxETL = new AASXETLPipeline();
}); 