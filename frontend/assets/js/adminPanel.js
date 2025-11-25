const API_BASE = 'http://127.0.0.1:5000/api';

function showResult(title, content, isSuccess = true) {
    const resultBox = document.getElementById('result-box');
    const resultTitle = document.getElementById('result-title');
    const resultContent = document.getElementById('result-content');
    
    resultTitle.textContent = title;
    resultContent.innerHTML = content;
    
    resultBox.className = 'result-box show ' + (isSuccess ? 'success' : 'error');
}

function formatJSON(data) {
    return JSON.stringify(data, null, 2);
}

async function checkDatabaseConnection() {
    try {
        const response = await fetch(`${API_BASE}/admin/database-status`);
        const data = await response.json();
        
        if (data.status === 'success' && data.connected) {
            let content = `
                <div class="info-item">
                    <span class="status-indicator success"></span>
                    <strong>Status:</strong> ${data.message}
                </div>
                <div class="info-item">
                    <span class="info-label">Database Path:</span> ${data.database_path}
                </div>
                <div class="info-item">
                    <span class="info-label">Database Size:</span> ${data.database_size_mb} MB
                </div>
                <div class="info-item">
                    <span class="info-label">Tables Found:</span> ${data.tables.length}
                </div>
                <h4 style="color: #DCAB6B; margin-top: 20px;">Table Information:</h4>
                <ul>
            `;
            
            for (const [table, count] of Object.entries(data.table_counts)) {
                content += `<li><strong>${table}:</strong> ${count} rows</li>`;
            }
            
            content += `</ul><pre>${formatJSON(data)}</pre>`;
            
            showResult('Database Connection Status - SUCCESS', content, true);
        } else {
            showResult('Database Connection Status - FAILED', 
                `<div class="info-item">
                    <span class="status-indicator error"></span>
                    <strong>Error:</strong> ${data.message || data.error}
                </div>
                <div class="info-item">
                    <span class="info-label">Database Path:</span> ${data.database_path}
                </div>
                <div class="info-item">
                    <span class="info-label">Database Exists:</span> ${data.database_exists ? 'Yes' : 'No'}
                </div>
                <pre>${formatJSON(data)}</pre>`, false);
        }
    } catch (error) {
        showResult('Database Connection Status - ERROR', 
            `<div class="info-item">
                <span class="status-indicator error"></span>
                <strong>Connection Error:</strong> ${error.message}
            </div>
            <p>Make sure the Flask server is running on port 5000.</p>`, false);
    }
}

async function showApiDetails() {
    try {
        const response = await fetch(`${API_BASE}/admin/api-details`);
        const data = await response.json();
        
        if (data.status === 'success') {
            let content = `
                <div class="info-item">
                    <span class="info-label">API Base URL:</span> ${data.api_base_url}
                </div>
                <div class="info-item">
                    <span class="info-label">Total Endpoints:</span> ${data.total_endpoints}
                </div>
                <h4 style="color: #DCAB6B; margin-top: 20px;">Available Endpoints:</h4>
                <ul>
            `;
            
            data.endpoints.forEach(endpoint => {
                content += `<li><strong>${endpoint.method} ${endpoint.path}</strong> - ${endpoint.description}</li>`;
            });
            
            content += `</ul>`;
            
            // News API Status
            const newsStatusClass = data.news_api.status === 'connected' ? 'success' : 
                                   data.news_api.status === 'error' ? 'error' : 'warning';
            content += `
                <h4 style="color: #DCAB6B; margin-top: 20px;">News API Status:</h4>
                <div class="info-item">
                    <span class="status-indicator ${newsStatusClass}"></span>
                    <strong>Status:</strong> ${data.news_api.status.toUpperCase()}
                </div>
                <div class="info-item">
                    <span class="info-label">Message:</span> ${data.news_api.message}
                </div>
                <div class="info-item">
                    <span class="info-label">API Key Configured:</span> ${data.news_api.key_configured ? 'Yes' : 'No'}
                </div>
                <div class="info-item">
                    <span class="info-label">API URL:</span> ${data.news_api.url}
                </div>
                <h4 style="color: #DCAB6B; margin-top: 20px;">Server Information:</h4>
                <div class="info-item">
                    <span class="info-label">Flask Version:</span> ${data.server_info.flask_version}
                </div>
                <div class="info-item">
                    <span class="info-label">CORS Enabled:</span> ${data.server_info.cors_enabled ? 'Yes' : 'No'}
                </div>
                <pre>${formatJSON(data)}</pre>
            `;
            
            showResult('API Details', content, true);
        } else {
            showResult('API Details - ERROR', 
                `<div class="info-item">
                    <span class="status-indicator error"></span>
                    <strong>Error:</strong> ${data.message || data.error}
                </div>
                <pre>${formatJSON(data)}</pre>`, false);
        }
    } catch (error) {
        showResult('API Details - ERROR', 
            `<div class="info-item">
                <span class="status-indicator error"></span>
                <strong>Connection Error:</strong> ${error.message}
            </div>
            <p>Make sure the Flask server is running on port 5000.</p>`, false);
    }
}

async function readDatabase() {
    try {
        const response = await fetch(`${API_BASE}/admin/read-database`);
        const data = await response.json();
        
        if (data.status === 'success') {
            let content = `
                <div class="info-item">
                    <span class="status-indicator success"></span>
                    <strong>Status:</strong> ${data.message}
                </div>
                <div class="info-item">
                    <span class="info-label">Tables Found:</span> ${data.tables.length}
                </div>
            `;
            
            // Display each table's data
            for (const [tableName, tableData] of Object.entries(data.data)) {
                content += `
                    <h4 style="color: #DCAB6B; margin-top: 20px; border-top: 1px solid #26408B; padding-top: 15px;">
                        Table: ${tableName}
                    </h4>
                    <div class="info-item">
                        <span class="info-label">Total Rows:</span> ${tableData.total_rows}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Showing:</span> ${tableData.showing_rows} ${tableData.showing_rows < tableData.total_rows ? '(limited to first 100 rows)' : ''}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Columns:</span> ${tableData.columns.map(c => `${c.name} (${c.type})`).join(', ')}
                    </div>
                `;
                
                if (tableData.sample_data.length > 0) {
                    // Create a simple table display
                    content += `
                        <div style="overflow-x: auto; margin-top: 10px;">
                            <table style="width: 100%; border-collapse: collapse; background: #0D0221; font-size: 0.85em;">
                                <thead>
                                    <tr style="background: #26408B;">
                    `;
                    
                    // Table headers
                    const columnNames = tableData.columns.map(c => c.name);
                    columnNames.forEach(col => {
                        content += `<th style="padding: 8px; border: 1px solid #26408B; text-align: left; color: #DCAB6B;">${col}</th>`;
                    });
                    
                    content += `
                                    </tr>
                                </thead>
                                <tbody>
                    `;
                    
                    // Table rows (limit display to first 20 rows for readability)
                    const displayRows = tableData.sample_data.slice(0, 20);
                    displayRows.forEach(row => {
                        content += `<tr>`;
                        columnNames.forEach(col => {
                            const value = row[col] !== null && row[col] !== undefined ? row[col] : 'NULL';
                            content += `<td style="padding: 6px; border: 1px solid #26408B; color: #f0f0f0;">${value}</td>`;
                        });
                        content += `</tr>`;
                    });
                    
                    content += `
                                </tbody>
                            </table>
                        </div>
                    `;
                    
                    if (tableData.sample_data.length > 20) {
                        content += `<p style="color: #888; font-size: 0.85em; margin-top: 5px;">Showing first 20 of ${tableData.sample_data.length} rows</p>`;
                    }
                } else {
                    content += `<p style="color: #888; margin-top: 10px;">No data in this table.</p>`;
                }
            }
            
            // Add full JSON at the bottom
            content += `
                <details style="margin-top: 20px;">
                    <summary style="color: #DCAB6B; cursor: pointer; margin-bottom: 10px;">View Full JSON Data</summary>
                    <pre>${formatJSON(data)}</pre>
                </details>
            `;
            
            showResult('Database Contents', content, true);
        } else {
            showResult('Read Database - ERROR', 
                `<div class="info-item">
                    <span class="status-indicator error"></span>
                    <strong>Error:</strong> ${data.message || data.error}
                </div>
                <pre>${formatJSON(data)}</pre>`, false);
        }
    } catch (error) {
        showResult('Read Database - ERROR', 
            `<div class="info-item">
                <span class="status-indicator error"></span>
                <strong>Connection Error:</strong> ${error.message}
            </div>
            <p>Make sure the Flask server is running on port 5000.</p>`, false);
    }
}

function showSiteDetails() {
    // This can be implemented to show site information
    showResult('Site Details', 
        '<p>Climate Change Dashboard v1.0<br>Built with Flask backend and Chart.js frontend.</p>', true);
}
