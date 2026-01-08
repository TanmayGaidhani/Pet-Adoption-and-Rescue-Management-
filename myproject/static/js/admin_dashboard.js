// ===== ADMIN DASHBOARD JAVASCRIPT =====

// Prevent back button after logout
window.history.pushState(null, "", window.location.href);
window.onpopstate = function() {
    window.history.pushState(null, "", window.location.href);
};

// Check session on page load
window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        window.location.reload();
    }
});

// Load dashboard stats and reports
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
    loadReportRequests();
});

function loadDashboardStats() {
    fetch('/api/admin/stats/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }
            
            document.getElementById('totalUsers').textContent = data.total_users || 0;
            document.getElementById('foundPets').textContent = data.found_pets || 0;
            document.getElementById('rescueReports').textContent = data.rescue_reports || 0;
            document.getElementById('activeReports').textContent = data.active_reports || 0;
        })
        .catch(error => {
            console.error('Error loading stats:', error);
        });
}

function loadReportRequests() {
    // Load pending reports for admin review
    fetch('/api/admin/pending-reports/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }
            displayFoundRequests(data.found_pets || []);
            displayRescueRequests(data.rescue_reports || []);
        })
        .catch(error => {
            console.error('Error loading pending reports:', error);
        });
}

function displayFoundRequests(pets) {
    const grid = document.getElementById('foundRequestsGrid');

    if (pets.length === 0) {
        grid.innerHTML = '<div class="no-pending-requests"><div class="no-requests-icon">📋</div><h3>No Pending Found Pet Requests</h3><p>All found pet reports have been reviewed</p></div>';
        return;
    }

    grid.innerHTML = pets.slice(0, 6).map(pet => {
        return `
            <div class="report-card-compact found-pet-card" id="found-${pet.id}">
                <div class="report-card-header">
                    <span class="report-badge found-badge">FOUND</span>
                    <span class="report-id">#${pet.id.substring(0, 6)}</span>
                </div>
                
                <div class="report-image-container">
                    ${pet.image_path ? `
                        <img src="/media/${pet.image_path}" class="report-image-compact" alt="Found Pet" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                        <div class="no-image-compact" style="display: none;">
                            🔍<br><small>No Image</small>
                        </div>
                    ` : `
                        <div class="no-image-compact">
                            🔍<br><small>No Image</small>
                        </div>
                    `}
                </div>
                
                <div class="report-content">
                    <h5 class="report-title">${pet.breed || 'Unknown Breed'}</h5>
                    <div class="report-info-compact">
                        <div class="info-row">
                            <span class="info-label">Type:</span>
                            <span class="info-value">${pet.animal_type || 'Unknown'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Color:</span>
                            <span class="info-value">${pet.color || 'Unknown'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Location:</span>
                            <span class="info-value">${truncateText(pet.location || 'Unknown', 15)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Finder:</span>
                            <span class="info-value">${truncateText(pet.contact_name || 'Unknown', 12)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Date:</span>
                            <span class="info-value">${formatDate(pet.report_date)}</span>
                        </div>
                    </div>
                    
                    <div class="report-actions-compact">
                        <button class="btn-approve-compact" onclick="approveRequest('found','${pet.id}')" title="Approve Request">
                            ✓
                        </button>
                        <button class="btn-reject-compact" onclick="rejectRequest('found','${pet.id}')" title="Reject Request">
                            ✗
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Helper function to truncate text
function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}


function displayRescueRequests(reports) {
    const grid = document.getElementById('rescueRequestsGrid');
    
    if (reports.length === 0) {
        grid.innerHTML = '<div class="no-pending-requests"><div class="no-requests-icon">🚨</div><h3>No Pending Rescue Requests</h3><p>All rescue reports have been reviewed</p></div>';
        return;
    }

    grid.innerHTML = reports.slice(0, 6).map(report => {
        return `
            <div class="report-card-compact rescue-card" id="rescue-${report.id}">
                <div class="report-card-header">
                    <span class="report-badge rescue-badge">RESCUE</span>
                    <span class="report-id">#${report.id.substring(0, 6)}</span>
                    <span class="urgency-badge urgency-${report.urgency || 'low'}">${(report.urgency || 'low').toUpperCase()}</span>
                </div>
                
                <div class="report-image-container">
                    ${report.image_path ? `
                        <img src="/media/${report.image_path}" class="report-image-compact" alt="Rescue Animal" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                        <div class="no-image-compact" style="display: none;">
                            🚨<br><small>No Image</small>
                        </div>
                    ` : `
                        <div class="no-image-compact">
                            🚨<br><small>No Image</small>
                        </div>
                    `}
                </div>
                
                <div class="report-content">
                    <h5 class="report-title">${report.breed || 'Unknown Breed'}</h5>
                    <div class="report-info-compact">
                        <div class="info-row">
                            <span class="info-label">Type:</span>
                            <span class="info-value">${report.animal_type || 'Unknown'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Color:</span>
                            <span class="info-value">${report.color || 'Unknown'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Location:</span>
                            <span class="info-value">${truncateText(report.location || 'Unknown', 15)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Reporter:</span>
                            <span class="info-value">${truncateText(report.contact_name || 'Unknown', 12)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Date:</span>
                            <span class="info-value">${formatDate(report.report_date)}</span>
                        </div>
                    </div>
                    
                    <div class="report-actions-compact">
                        <button class="btn-approve-compact" onclick="approveRequest('rescue','${report.id}')" title="Approve Request">
                            ✓
                        </button>
                        <button class="btn-reject-compact" onclick="rejectRequest('rescue','${report.id}')" title="Reject Request">
                            ✗
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function showTab(tabName) {
    // Remove active class from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab
    event.target.classList.add('active');
    document.getElementById(tabName + 'Tab').classList.add('active');
}

function scrollToReports() {
    document.querySelector('.report-requests-section').scrollIntoView({ behavior: 'smooth' });
}

function approveRequest(type, id) {
    if (confirm(`Are you sure you want to approve this ${type} request?`)) {
        fetch('/api/admin/approve-report/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                report_id: id,
                report_type: type,
                action: 'approve'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`✅ ${type} request approved! It will now appear on the public pages.`);
                // Remove the card from the grid
                const card = document.getElementById(`${type}-${id}`);
                if (card) card.remove();
                loadReportRequests(); // Reload requests
            } else {
                alert(`❌ Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('❌ Failed to approve request');
        });
    }
}

function rejectRequest(type, id) {
    if (confirm(`Are you sure you want to reject this ${type} request?`)) {
        fetch('/api/admin/approve-report/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                report_id: id,
                report_type: type,
                action: 'reject'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`❌ ${type} request rejected.`);
                // Remove the card from the grid
                const card = document.getElementById(`${type}-${id}`);
                if (card) card.remove();
                loadReportRequests(); // Reload requests
            } else {
                alert(`❌ Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('❌ Failed to reject request');
        });
    }
}

function viewFullDetails(type, id) {
    // Find the report data
    let reportData = null;
    
    if (type === 'found') {
        // This would need to be stored globally or fetched again
        alert('📋 Full details view coming soon! For now, you can see all details in the card above.');
    } else if (type === 'rescue') {
        alert('📋 Full details view coming soon! For now, you can see all details in the card above.');
    }
}

// Helper function to get CSRF token
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

function formatDate(dateString) {
    if (!dateString) return 'Not specified';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}