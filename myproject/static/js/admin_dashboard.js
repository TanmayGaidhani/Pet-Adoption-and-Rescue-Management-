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
        const imageSrc = pet.image_path
            ? `/media/${pet.image_path}`
            : 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRUVGMkZGIi8+CjxjaXJjbGUgY3g9IjUwIiBjeT0iNDAiIHI9IjE1IiBmaWxsPSIjNjY3RUVBIi8+CjxwYXRoIGQ9Ik0zNSA2NUg2NVY3NUgzNVY2NVoiIGZpbGw9IiM2NjdFRUEiLz4KPHN2Zz4K';

        return `
            <div class="responsive-admin-card found-pet-card" id="found-${pet.id}">
                <div class="card-header">
                    <span class="report-badge found-badge">FOUND</span>
                    <span class="report-id">#${pet.id}</span>
                </div>

                <div class="card-body">
                    <div class="card-image">
                        <img src="${imageSrc}" alt="Found Pet" 
                             onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRUVGMkZGIi8+CjxjaXJjbGUgY3g9IjUwIiBjeT0iNDAiIHI9IjE1IiBmaWxsPSIjNjY3RUVBIi8+CjxwYXRoIGQ9Ik0zNSA2NUg2NVY3NUgzNVY2NVoiIGZpbGw9IiM2NjdFRUEiLz4KPHN2Zz4K'">
                    </div>
                    
                    <div class="card-info">
                        <h3 class="pet-title">${pet.breed || 'Unknown Breed'}</h3>
                        <p class="pet-details">${pet.animal_type || 'Unknown'} • ${pet.color || 'Unknown'}</p>
                        
                        <div class="info-compact">
                            <div class="info-row">
                                <span class="info-icon">📍</span>
                                <span class="info-text">${truncateText(pet.location || "Unknown location", 20)}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-icon">👤</span>
                                <span class="info-text">${truncateText(pet.contact_name || "Unknown", 15)}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-icon">📞</span>
                                <span class="info-text">${pet.contact_phone || "No phone"}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-icon">📅</span>
                                <span class="info-text">${formatDate(pet.report_date)}</span>
                            </div>
                        </div>

                        ${pet.special_marks ? `
                        <div class="special-compact">
                            <span class="special-icon">⭐</span>
                            <span class="special-text">${truncateText(pet.special_marks, 30)}</span>
                        </div>` : ''}
                    </div>
                </div>

                <div class="card-actions">
                    <button class="btn-approve" onclick="approveRequest('found','${pet.id}')">
                        <span class="btn-icon">✓</span>
                        <span class="btn-text">Approve</span>
                    </button>
                    <button class="btn-reject" onclick="rejectRequest('found','${pet.id}')">
                        <span class="btn-icon">✗</span>
                        <span class="btn-text">Reject</span>
                    </button>
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
        const imageSrc = report.image_path ? `/media/${report.image_path}` : 
            'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRkVGM0M3Ii8+CjxjaXJjbGUgY3g9IjUwIiBjeT0iNDAiIHI9IjE1IiBmaWxsPSIjRjU5NTZDIi8+CjxwYXRoIGQ9Ik0zNSA2NUg2NVY3NUgzNVY2NVoiIGZpbGw9IiNGNTk1NkMiLz4KPHN2Zz4K';
        
        return `
            <div class="responsive-admin-card rescue-card" id="rescue-${report.id}">
                <div class="card-header">
                    <span class="report-badge rescue-badge">RESCUE</span>
                    <span class="report-id">#${report.id}</span>
                    <span class="urgency-badge urgency-${report.urgency || 'low'}">${(report.urgency || 'low').toUpperCase()}</span>
                </div>
                
                <div class="card-body">
                    <div class="card-image">
                        <img src="${imageSrc}" alt="Rescue Animal" 
                             onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjRkVGM0M3Ii8+CjxjaXJjbGUgY3g9IjUwIiBjeT0iNDAiIHI9IjE1IiBmaWxsPSIjRjU5NTZDIi8+CjxwYXRoIGQ9Ik0zNSA2NUg2NVY3NUgzNVY2NVoiIGZpbGw9IiNGNTk1NkMiLz4KPHN2Zz4K'">
                    </div>
                    
                    <div class="card-info">
                        <h3 class="pet-title">${report.breed || 'Unknown Breed'}</h3>
                        <p class="pet-details">${report.animal_type || 'Unknown'} • ${report.color || 'Unknown'}</p>
                        
                        <div class="info-compact">
                            <div class="info-row">
                                <span class="info-icon">📍</span>
                                <span class="info-text">${truncateText(report.location || "Unknown location", 20)}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-icon">👤</span>
                                <span class="info-text">${truncateText(report.contact_name || "Unknown", 15)}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-icon">📞</span>
                                <span class="info-text">${report.contact_phone || "No phone"}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-icon">📅</span>
                                <span class="info-text">${formatDate(report.report_date)}</span>
                            </div>
                        </div>
                        
                        ${report.special_marks ? `
                        <div class="special-compact">
                            <span class="special-icon">⭐</span>
                            <span class="special-text">${truncateText(report.special_marks, 30)}</span>
                        </div>` : ''}
                    </div>
                </div>
                
                <div class="card-actions">
                    <button class="btn-approve" onclick="approveRequest('rescue', '${report.id}')">
                        <span class="btn-icon">✓</span>
                        <span class="btn-text">Approve</span>
                    </button>
                    <button class="btn-reject" onclick="rejectRequest('rescue', '${report.id}')">
                        <span class="btn-icon">✗</span>
                        <span class="btn-text">Reject</span>
                    </button>
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