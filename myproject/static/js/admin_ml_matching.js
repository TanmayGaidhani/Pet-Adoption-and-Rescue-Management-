// Admin ML Matching JavaScript

let selectedLostReport = null;
let selectedFoundReport = null;
let currentMatchResult = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    loadReports();
    loadMatchResults();
});

// Tab Management
function showTab(tabName, event) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    // Load content based on tab
    if (tabName === 'results') {
        loadMatchResults();
    } else if (tabName === 'batch') {
        // Batch tab content is loaded on demand
    }
}

// Load Lost and Found Reports
async function loadReports() {
    try {
        showLoading('Loading reports...');
        
        // Add cache-busting parameter
        const timestamp = new Date().getTime();
        const response = await fetch(`/api/admin/reports-for-matching/?t=${timestamp}`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayLostReports(data.lost_reports);
        displayFoundReports(data.found_reports);
        updateStats(data.lost_reports.length, data.found_reports.length);
        
        hideLoading();
        
    } catch (error) {
        console.error('Error loading reports:', error);
        hideLoading();
        showError('Failed to load reports: ' + error.message);
    }
}

// Display Lost Reports
function displayLostReports(reports) {
    const grid = document.getElementById('lostReportsGrid');
    
    if (reports.length === 0) {
        grid.innerHTML = '<div class="loading-message">No approved lost pet reports found</div>';
        return;
    }
    
    grid.innerHTML = reports.map(report => `
        <div class="report-card compact-card" onclick="selectLostReport('${report.id}', event)">
            <div class="card-header">
                <span class="card-badge lost-badge">LOST</span>
                <span class="card-id">#${report.id.substring(0, 6)}</span>
            </div>
            <div class="card-image-container">
                ${report.image_path ? `
                    <img src="/media/${report.image_path}" class="card-image" alt="Lost Pet" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="no-image-placeholder" style="display: none;">
                        📷<br><small>No Image</small>
                    </div>
                ` : `
                    <div class="no-image-placeholder">
                        📷<br><small>No Image</small>
                    </div>
                `}
            </div>
            <div class="card-content">
                <h5 class="card-title">${report.animal_type} - ${report.breed}</h5>
                <div class="card-details">
                    <div class="detail-row">
                        <span class="detail-label">Color:</span>
                        <span class="detail-value">${report.color || 'N/A'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Location:</span>
                        <span class="detail-value">${report.location || 'N/A'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Owner:</span>
                        <span class="detail-value">${report.owner_name || 'N/A'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Date:</span>
                        <span class="detail-value">${formatDate(report.report_date)}</span>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Display Found Reports
function displayFoundReports(reports) {
    const grid = document.getElementById('foundReportsGrid');
    
    if (reports.length === 0) {
        grid.innerHTML = '<div class="loading-message">No approved found pet reports found</div>';
        return;
    }
    
    grid.innerHTML = reports.map(report => `
        <div class="report-card compact-card" onclick="selectFoundReport('${report.id}', event)">
            <div class="card-header">
                <span class="card-badge found-badge">FOUND</span>
                <span class="card-id">#${report.id.substring(0, 6)}</span>
            </div>
            <div class="card-image-container">
                ${report.image_path ? `
                    <img src="/media/${report.image_path}" class="card-image" alt="Found Pet" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="no-image-placeholder" style="display: none;">
                        📷<br><small>No Image</small>
                    </div>
                ` : `
                    <div class="no-image-placeholder">
                        📷<br><small>No Image</small>
                    </div>
                `}
            </div>
            <div class="card-content">
                <h5 class="card-title">${report.animal_type} - ${report.breed}</h5>
                <div class="card-details">
                    <div class="detail-row">
                        <span class="detail-label">Color:</span>
                        <span class="detail-value">${report.color || 'N/A'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Location:</span>
                        <span class="detail-value">${report.location || 'N/A'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Finder:</span>
                        <span class="detail-value">${report.finder_name || 'N/A'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Date:</span>
                        <span class="detail-value">${formatDate(report.report_date)}</span>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Select Lost Report
function selectLostReport(reportId, event) {
    // Remove previous selection
    document.querySelectorAll('#lostReportsGrid .compact-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Select current card
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('selected');
    }
    selectedLostReport = reportId;
    
    updateMatchButton();
}

// Select Found Report
function selectFoundReport(reportId, event) {
    // Remove previous selection
    document.querySelectorAll('#foundReportsGrid .compact-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Select current card
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('selected');
    }
    selectedFoundReport = reportId;
    
    updateMatchButton();
}

// Update Match Button State
function updateMatchButton() {
    const matchBtn = document.getElementById('runMatchBtn');
    
    if (selectedLostReport && selectedFoundReport) {
        matchBtn.disabled = false;
        matchBtn.innerHTML = '<span class="btn-icon">🤖</span>Run ML Match';
    } else {
        matchBtn.disabled = true;
        matchBtn.innerHTML = '<span class="btn-icon">🤖</span>Select Reports First';
    }
}

// Run ML Match
async function runMLMatch() {
    if (!selectedLostReport || !selectedFoundReport) {
        showError('Please select both a lost report and a found report');
        return;
    }
    
    try {
        showLoading('Running ML analysis...');
        
        const response = await fetch('/api/admin/run-ml-match/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                lost_report_id: selectedLostReport,
                found_report_id: selectedFoundReport
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        currentMatchResult = data;
        showMatchResult(data);
        hideLoading();
        
    } catch (error) {
        console.error('Error running ML match:', error);
        hideLoading();
        showError('Failed to run ML match: ' + error.message);
    }
}

// Show Match Result Modal
function showMatchResult(result) {
    const modal = document.getElementById('matchModal');
    const modalBody = document.getElementById('matchModalBody');
    
    modalBody.innerHTML = `
        <div class="probability-display">
            <div class="probability-number">${(result.probability * 100).toFixed(1)}%</div>
            <div class="probability-label">Match Probability</div>
            <div class="match-strength ${result.match_strength}">${result.match_strength} MATCH</div>
        </div>
        
        <div class="match-result">
            <div class="pet-info">
                <h3>📋 Lost Pet</h3>
                ${result.lost_report.image_path ? 
                    `<img src="/media/${result.lost_report.image_path}" class="pet-image-modal" alt="Lost Pet" onclick="openImageModal('/media/${result.lost_report.image_path}', 'Lost Pet')" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                     <div class="no-image-modal" style="display: none;">📷 No Image Available</div>` : 
                    `<div class="no-image-modal">📷 No Image Available</div>`
                }
                <p><strong>Type:</strong> ${result.lost_report.animal_type}</p>
                <p><strong>Breed:</strong> ${result.lost_report.breed}</p>
                <p><strong>Color:</strong> ${result.lost_report.color}</p>
                <p><strong>Location:</strong> ${result.lost_report.location}</p>
                <p><strong>Owner:</strong> ${result.lost_report.owner_name}</p>
                <p><strong>Email:</strong> ${result.lost_report.owner_email}</p>
            </div>
            
            <div class="pet-info">
                <h3>🔍 Found Pet</h3>
                ${result.found_report.image_path ? 
                    `<img src="/media/${result.found_report.image_path}" class="pet-image-modal" alt="Found Pet" onclick="openImageModal('/media/${result.found_report.image_path}', 'Found Pet')" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                     <div class="no-image-modal" style="display: none;">📷 No Image Available</div>` : 
                    `<div class="no-image-modal">📷 No Image Available</div>`
                }
                <p><strong>Type:</strong> ${result.found_report.animal_type}</p>
                <p><strong>Breed:</strong> ${result.found_report.breed}</p>
                <p><strong>Color:</strong> ${result.found_report.color}</p>
                <p><strong>Location:</strong> ${result.found_report.location}</p>
                <p><strong>Finder:</strong> ${result.found_report.finder_name}</p>
                <p><strong>Email:</strong> ${result.found_report.finder_email}</p>
            </div>
        </div>
        
        <div class="feature-analysis">
            <h4>🔍 Feature Analysis</h4>
            ${Object.entries(result.feature_analysis).map(([key, feature]) => `
                <div class="feature-item">
                    <span>${feature.description}</span>
                    <span class="feature-value">${typeof feature.value === 'number' ? feature.value.toFixed(3) : feature.value}</span>
                </div>
            `).join('')}
        </div>
        
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
            <strong>🤖 AI Recommendation:</strong> ${result.recommendation}
        </div>
    `;
    
    modal.style.display = 'block';
}

// Close Match Modal
function closeMatchModal() {
    document.getElementById('matchModal').style.display = 'none';
    currentMatchResult = null;
}

// Approve Match
async function approveMatch() {
    if (!currentMatchResult) return;
    
    try {
        showLoading('Approving match and sending notifications...');
        
        const response = await fetch('/api/admin/match-action/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                match_id: currentMatchResult.match_id,
                action: 'approve',
                admin_notes: 'Match approved by admin after ML analysis'
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        hideLoading();
        closeMatchModal();
        showSuccess(data.message);
        loadMatchResults(); // Refresh results
        
    } catch (error) {
        console.error('Error approving match:', error);
        hideLoading();
        showError('Failed to approve match: ' + error.message);
    }
}

// Reject Match
async function rejectMatch() {
    if (!currentMatchResult) return;
    
    try {
        showLoading('Rejecting match...');
        
        const response = await fetch('/api/admin/match-action/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                match_id: currentMatchResult.match_id,
                action: 'reject',
                admin_notes: 'Match rejected by admin after review'
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        hideLoading();
        closeMatchModal();
        showSuccess(data.message);
        loadMatchResults(); // Refresh results
        
    } catch (error) {
        console.error('Error rejecting match:', error);
        hideLoading();
        showError('Failed to reject match: ' + error.message);
    }
}

// Load Match Results
async function loadMatchResults() {
    try {
        const response = await fetch('/api/admin/match-results/');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayMatchResults(data.match_results);
        
    } catch (error) {
        console.error('Error loading match results:', error);
        showError('Failed to load match results: ' + error.message);
    }
}

// Display Match Results
function displayMatchResults(results) {
    const grid = document.getElementById('matchResultsGrid');
    
    if (results.length === 0) {
        grid.innerHTML = '<div class="loading-message">No match results found</div>';
        return;
    }
    
    grid.innerHTML = results.map(result => `
        <div class="result-card">
            <div class="result-header">
                <div class="result-probability">${(result.probability * 100).toFixed(1)}%</div>
                <div class="result-status ${result.status}">${result.status.toUpperCase()}</div>
            </div>
            <div class="result-details">
                <p><strong>Lost Pet:</strong> ${result.lost_pet_info}</p>
                <p><strong>Found Pet:</strong> ${result.found_pet_info}</p>
                <p><strong>Match Strength:</strong> ${result.match_strength}</p>
                <p><strong>Admin:</strong> ${result.admin_name}</p>
                <p><strong>Date:</strong> ${result.created_at}</p>
                <p><strong>Recommendation:</strong> ${result.recommendation}</p>
            </div>
        </div>
    `).join('');
}

// Run Batch Analysis
async function runBatchAnalysis() {
    try {
        showLoading('Running batch ML analysis...');
        
        const response = await fetch('/api/admin/batch-ml-analysis/');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayBatchResults(data);
        
        // Switch to batch tab
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Remove active class from all tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Show batch tab
        document.getElementById('batch-tab').classList.add('active');
        document.querySelector('[onclick*="batch"]').classList.add('active');
        
        hideLoading();
        
    } catch (error) {
        console.error('Error running batch analysis:', error);
        hideLoading();
        showError('Failed to run batch analysis: ' + error.message);
    }
}

// Display Batch Results
function displayBatchResults(data) {
    const statsDiv = document.getElementById('batchStats');
    const resultsDiv = document.getElementById('batchResults');
    
    // Update stats
    statsDiv.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: #667eea;">${data.total_lost_reports}</div>
                <div>Lost Reports</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: #667eea;">${data.total_found_reports}</div>
                <div>Found Reports</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: #28a745;">${data.high_probability_matches}</div>
                <div>High Matches (≥80%)</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: #ffc107;">${data.medium_probability_matches}</div>
                <div>Medium Matches (50-79%)</div>
            </div>
        </div>
    `;
    
    // Display potential matches
    if (data.potential_matches.length === 0) {
        resultsDiv.innerHTML = '<div class="loading-message">No potential matches found with probability ≥ 50%</div>';
        return;
    }
    
    resultsDiv.innerHTML = data.potential_matches.map(match => `
        <div class="batch-match-card">
            <div class="batch-match-header">
                <div class="batch-probability">${(match.probability * 100).toFixed(1)}%</div>
                <div class="match-strength ${match.match_strength}">${match.match_strength}</div>
            </div>
            <div class="batch-match-details">
                <div>
                    <strong>Lost Pet:</strong> ${match.lost_pet_info}<br>
                    <small>ID: ${match.lost_report_id.substring(0, 8)}</small>
                </div>
                <div>
                    <strong>Found Pet:</strong> ${match.found_pet_info}<br>
                    <small>ID: ${match.found_report_id.substring(0, 8)}</small>
                </div>
            </div>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e9ecef;">
                <strong>Recommendation:</strong> ${match.recommendation}
            </div>
        </div>
    `).join('');
}

// Show Match History
function showMatchHistory() {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show results tab
    document.getElementById('results-tab').classList.add('active');
    document.querySelector('[onclick*="results"]').classList.add('active');
    
    loadMatchResults();
}

// Update Stats
function updateStats(lostCount, foundCount) {
    document.getElementById('lostReportsCount').textContent = lostCount;
    document.getElementById('foundReportsCount').textContent = foundCount;
    
    // Update other stats from match results
    fetch('/api/admin/match-results/')
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                const totalMatches = data.match_results.length;
                const approvedMatches = data.match_results.filter(r => r.status === 'approved').length;
                
                document.getElementById('totalMatchesCount').textContent = totalMatches;
                document.getElementById('approvedMatchesCount').textContent = approvedMatches;
            }
        })
        .catch(error => console.error('Error updating stats:', error));
}

// Utility Functions
function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loadingOverlay');
    overlay.querySelector('p').textContent = message;
    overlay.style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function showError(message) {
    alert('Error: ' + message);
}

function showSuccess(message) {
    alert('Success: ' + message);
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('matchModal');
    const imageModal = document.getElementById('imageModal');
    if (event.target === modal) {
        closeMatchModal();
    }
    if (event.target === imageModal) {
        closeImageModal();
    }
}

// Image Modal Functions
function openImageModal(imageSrc, title) {
    const imageModal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const imageTitle = document.getElementById('imageTitle');
    
    if (imageModal && modalImage && imageTitle) {
        modalImage.src = imageSrc;
        imageTitle.textContent = title;
        imageModal.style.display = 'block';
    }
}

function closeImageModal() {
    const imageModal = document.getElementById('imageModal');
    if (imageModal) {
        imageModal.style.display = 'none';
    }
}