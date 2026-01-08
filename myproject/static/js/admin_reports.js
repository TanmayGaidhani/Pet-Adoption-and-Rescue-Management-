// ===== ADMIN REPORTS MANAGEMENT JAVASCRIPT =====

// Global variables
let currentReports = [];
let filteredReports = [];
let currentTab = 'all';

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

// Load data on page load
document.addEventListener('DOMContentLoaded', function() {
    loadReportsStats();
    loadReports();
    setupEventListeners();
});

function setupEventListeners() {
    // Refresh button
    const refreshBtn = document.getElementById('refreshReports');
    refreshBtn.addEventListener('click', function() {
        loadReportsStats();
        loadReports();
    });

    // Export button
    const exportBtn = document.getElementById('exportReports');
    exportBtn.addEventListener('click', exportReports);

    // Modal functionality
    setupModalListeners();
}

function loadReportsStats() {
    fetch('/api/admin/reports/stats/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }
            
            document.getElementById('totalReportsCount').textContent = data.total_reports || 0;
            document.getElementById('pendingReportsCount').textContent = data.pending_reports || 0;
            document.getElementById('approvedReportsCount').textContent = data.approved_reports || 0;
            document.getElementById('recentReportsCount').textContent = data.recent_reports || 0;
        })
        .catch(error => {
            console.error('Error loading reports stats:', error);
            // Show fallback data
            document.getElementById('totalReportsCount').textContent = '0';
            document.getElementById('pendingReportsCount').textContent = '0';
            document.getElementById('approvedReportsCount').textContent = '0';
            document.getElementById('recentReportsCount').textContent = '0';
        });
}

function loadReports() {
    fetch('/api/admin/reports/all/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                showNoReportsMessage();
                return;
            }
            
            currentReports = data.reports || [];
            filterReportsByTab(currentTab);
        })
        .catch(error => {
            console.error('Error loading reports:', error);
            showNoReportsMessage();
        });
}

function showNoReportsMessage() {
    const tbody = document.getElementById('reportsTableBody');
    tbody.innerHTML = `
        <tr class="no-reports-row">
            <td colspan="8" class="loading-cell">
                <div style="font-size: 48px; margin-bottom: 16px; opacity: 0.6;">📋</div>
                No reports found
            </td>
        </tr>
    `;
}

function showReportsTab(tab) {
    currentTab = tab;
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(tab + 'Tab').classList.add('active');
    
    // Filter and display reports
    filterReportsByTab(tab);
}

function filterReportsByTab(tab) {
    switch (tab) {
        case 'pending':
            filteredReports = currentReports.filter(report => report.status === 'pending');
            break;
        case 'approved':
            filteredReports = currentReports.filter(report => report.status === 'approved');
            break;
        case 'rescue':
            filteredReports = currentReports.filter(report => report.report_type === 'RESCUE');
            break;
        case 'found':
            filteredReports = currentReports.filter(report => report.report_type === 'FOUND');
            break;
        default:
            filteredReports = [...currentReports];
            break;
    }
    
    displayReports();
}

function displayReports() {
    const tbody = document.getElementById('reportsTableBody');
    
    if (filteredReports.length === 0) {
        showNoReportsMessage();
        return;
    }

    tbody.innerHTML = filteredReports.map(report => `
        <tr class="report-row" data-report-id="${report.id}">
            <td>
                <span class="report-type-badge type-${report.report_type.toLowerCase()}">
                    ${report.report_type}
                </span>
            </td>
            <td>${report.animal_type || 'Unknown'}</td>
            <td>${report.breed || 'Unknown'}</td>
            <td>${report.location || 'Unknown'}, ${report.city || ''}</td>
            <td>${report.user_name || report.contact_name || 'Unknown'}</td>
            <td>${formatDate(report.report_date)}</td>
            <td>
                <span class="status-badge status-${report.status}">
                    ${report.status.toUpperCase()}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn btn-view" onclick="viewReport('${report.id}')" title="View Details">
                        👁️ View
                    </button>
                    ${report.status === 'pending' ? `
                    <button class="action-btn btn-approve" onclick="approveReport('${report.id}')" title="Approve Report">
                        ✅ Approve
                    </button>
                    <button class="action-btn btn-reject" onclick="rejectReport('${report.id}')" title="Reject Report">
                        ❌ Reject
                    </button>` : ''}
                    <button class="action-btn btn-delete" onclick="deleteReport('${report.id}')" title="Delete Report">
                        🗑️ Delete
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function viewReport(reportId) {
    const report = currentReports.find(r => r.id === reportId);
    if (!report) return;

    const modal = document.getElementById('reportModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    modalTitle.textContent = `📋 ${report.report_type} Report - ${report.breed || 'Unknown Pet'}`;
    
    modalBody.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
            <div>
                <h4 style="color: #374151; margin-bottom: 10px; font-size: 14px; font-weight: 600;">Pet Information</h4>
                <div style="background: #f9fafb; padding: 15px; border-radius: 8px;">
                    <p><strong>Type:</strong> ${report.animal_type || 'Unknown'}</p>
                    <p><strong>Breed:</strong> ${report.breed || 'Unknown'}</p>
                    <p><strong>Color:</strong> ${report.color || 'Unknown'}</p>
                    <p><strong>Gender:</strong> ${report.gender || 'Unknown'}</p>
                    <p><strong>Condition:</strong> ${report.condition || 'Unknown'}</p>
                </div>
            </div>
            <div>
                <h4 style="color: #374151; margin-bottom: 10px; font-size: 14px; font-weight: 600;">Report Details</h4>
                <div style="background: #f9fafb; padding: 15px; border-radius: 8px;">
                    <p><strong>Status:</strong> <span class="status-badge status-${report.status}">${report.status.toUpperCase()}</span></p>
                    <p><strong>Date:</strong> ${formatDate(report.report_date)}</p>
                    <p><strong>Location:</strong> ${report.location || 'Unknown'}</p>
                    <p><strong>City:</strong> ${report.city || 'Unknown'}</p>
                </div>
            </div>
        </div>
        <div>
            <h4 style="color: #374151; margin-bottom: 10px; font-size: 14px; font-weight: 600;">Contact Information</h4>
            <div style="background: #f9fafb; padding: 15px; border-radius: 8px;">
                <p><strong>Reporter:</strong> ${report.user_name || report.contact_name || 'Unknown'}</p>
                <p><strong>Phone:</strong> ${report.contact_phone || 'Not provided'}</p>
                <p><strong>Email:</strong> ${report.contact_email || 'Not provided'}</p>
            </div>
        </div>
        ${report.description ? `
        <div style="margin-top: 20px;">
            <h4 style="color: #374151; margin-bottom: 10px; font-size: 14px; font-weight: 600;">Description</h4>
            <div style="background: #f9fafb; padding: 15px; border-radius: 8px;">
                <p>${report.description}</p>
            </div>
        </div>` : ''}
        ${report.image_path ? `
        <div style="margin-top: 20px;">
            <h4 style="color: #374151; margin-bottom: 10px; font-size: 14px; font-weight: 600;">Pet Image</h4>
            <div style="text-align: center;">
                <img src="/media/${report.image_path}" alt="Pet Image" style="max-width: 300px; max-height: 300px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            </div>
        </div>` : ''}
    `;

    // Show/hide action buttons based on status
    const approveBtn = document.getElementById('approveReport');
    const rejectBtn = document.getElementById('rejectReport');
    const deleteBtn = document.getElementById('deleteReport');
    
    if (report.status === 'pending') {
        approveBtn.style.display = 'inline-block';
        rejectBtn.style.display = 'inline-block';
        approveBtn.onclick = () => approveReportFromModal(reportId);
        rejectBtn.onclick = () => rejectReportFromModal(reportId);
    } else {
        approveBtn.style.display = 'none';
        rejectBtn.style.display = 'none';
    }

    // Always show delete button
    deleteBtn.style.display = 'inline-block';
    deleteBtn.onclick = () => deleteReportFromModal(reportId);

    modal.style.display = 'block';
}

function approveReport(reportId) {
    if (confirm('Are you sure you want to approve this report?')) {
        performReportAction(reportId, 'approve');
    }
}

function rejectReport(reportId) {
    if (confirm('Are you sure you want to reject this report? This will delete it permanently.')) {
        performReportAction(reportId, 'reject');
    }
}

function approveReportFromModal(reportId) {
    if (confirm('Are you sure you want to approve this report?')) {
        performReportAction(reportId, 'approve');
        document.getElementById('reportModal').style.display = 'none';
    }
}

function rejectReportFromModal(reportId) {
    if (confirm('Are you sure you want to reject this report? This will delete it permanently.')) {
        performReportAction(reportId, 'reject');
        document.getElementById('reportModal').style.display = 'none';
    }
}

function deleteReport(reportId) {
    const report = currentReports.find(r => r.id === reportId);
    if (!report) return;

    const confirmMessage = `Are you sure you want to delete this ${report.report_type.toLowerCase()} report?\n\nReport Details:\n- Animal: ${report.animal_type || 'Unknown'} (${report.breed || 'Unknown'})\n- Reporter: ${report.user_name || report.contact_name || 'Unknown'}\n- Date: ${formatDate(report.report_date)}\n\nThis action cannot be undone and the user will be notified.`;
    
    if (confirm(confirmMessage)) {
        performDeleteAction(reportId);
    }
}

function deleteReportFromModal(reportId) {
    const report = currentReports.find(r => r.id === reportId);
    if (!report) return;

    const confirmMessage = `Are you sure you want to delete this ${report.report_type.toLowerCase()} report?\n\nThis action cannot be undone and the user will be notified.`;
    
    if (confirm(confirmMessage)) {
        performDeleteAction(reportId);
        document.getElementById('reportModal').style.display = 'none';
    }
}

function performDeleteAction(reportId) {
    fetch('/api/admin/reports/delete/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            report_id: reportId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Report deleted successfully! User has been notified.');
            loadReports();
            loadReportsStats();
        } else {
            alert(`Failed to delete report: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to delete report');
    });
}

function performReportAction(reportId, action) {
    const report = currentReports.find(r => r.id === reportId);
    if (!report) return;

    fetch('/api/admin/approve-report/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            report_id: reportId,
            report_type: report.report_type.toLowerCase(),
            action: action
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Report ${action}d successfully!`);
            loadReports();
            loadReportsStats();
        } else {
            alert(`Failed to ${action} report: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Failed to ${action} report`);
    });
}

function exportReports() {
    const csvContent = generateReportsCSV(filteredReports);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `reports_export_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

function generateReportsCSV(reports) {
    const headers = ['Type', 'Animal Type', 'Breed', 'Color', 'Location', 'City', 'Reporter', 'Contact Phone', 'Contact Email', 'Date', 'Status', 'Description'];
    const csvRows = [headers.join(',')];

    reports.forEach(report => {
        const row = [
            `"${report.report_type}"`,
            `"${report.animal_type || ''}"`,
            `"${report.breed || ''}"`,
            `"${report.color || ''}"`,
            `"${report.location || ''}"`,
            `"${report.city || ''}"`,
            `"${report.user_name || report.contact_name || ''}"`,
            `"${report.contact_phone || ''}"`,
            `"${report.contact_email || ''}"`,
            `"${formatDate(report.report_date)}"`,
            `"${report.status}"`,
            `"${(report.description || '').replace(/"/g, '""')}"`
        ];
        csvRows.push(row.join(','));
    });

    return csvRows.join('\n');
}

function setupModalListeners() {
    const modal = document.getElementById('reportModal');
    const closeBtn = document.getElementById('closeModal');
    const modalClose = document.querySelector('.modal-close');

    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    modalClose.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
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

// Make functions global
window.showReportsTab = showReportsTab;
window.viewReport = viewReport;
window.approveReport = approveReport;
window.rejectReport = rejectReport;
window.deleteReport = deleteReport;