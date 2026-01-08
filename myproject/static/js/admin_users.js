// ===== ADMIN USERS JAVASCRIPT =====

// Global variables
let currentUsers = [];
let filteredUsers = [];
let currentPage = 1;
let usersPerPage = 10;
let currentSort = { field: 'id', direction: 'asc' };

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

// Load users data and stats
document.addEventListener('DOMContentLoaded', function() {
    loadUsersStats();
    loadUsers();
    setupEventListeners();
});

function loadUsersStats() {
    fetch('/api/admin/users-stats/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }
            
            document.getElementById('totalUsersCount').textContent = data.total_users || 0;
            document.getElementById('activeUsersCount').textContent = data.active_users || 0;
            document.getElementById('newUsersCount').textContent = data.new_users || 0;
            document.getElementById('adminUsersCount').textContent = data.admin_users || 0;
        })
        .catch(error => {
            console.error('Error loading users stats:', error);
            // Show fallback data
            document.getElementById('totalUsersCount').textContent = '0';
            document.getElementById('activeUsersCount').textContent = '0';
            document.getElementById('newUsersCount').textContent = '0';
            document.getElementById('adminUsersCount').textContent = '0';
        });
}

function loadUsers() {
    fetch('/api/admin/users/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                showNoUsersMessage();
                return;
            }
            
            currentUsers = data.users || [];
            filteredUsers = [...currentUsers];
            displayUsers();
            updatePagination();
        })
        .catch(error => {
            console.error('Error loading users:', error);
            showNoUsersMessage();
        });
}

function showNoUsersMessage() {
    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = `
        <tr class="no-users-row">
            <td colspan="6" class="loading-cell">
                <div style="font-size: 48px; margin-bottom: 16px; opacity: 0.6;">👥</div>
                No users found
            </td>
        </tr>
    `;
}

function displayUsers() {
    const tbody = document.getElementById('usersTableBody');
    
    if (filteredUsers.length === 0) {
        showNoUsersMessage();
        return;
    }

    const startIndex = (currentPage - 1) * usersPerPage;
    const endIndex = startIndex + usersPerPage;
    const usersToShow = filteredUsers.slice(startIndex, endIndex);

    tbody.innerHTML = usersToShow.map(user => `
        <tr class="user-row" data-user-id="${user.id}">
            <td>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="
                        width: 32px;
                        height: 32px;
                        border-radius: 50%;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: 700;
                        font-size: 12px;
                    ">${user.username.charAt(0).toUpperCase()}</div>
                    <span style="font-weight: 600;">${user.username}</span>
                </div>
            </td>
            <td>${user.email}</td>
            <td>${user.first_name || 'N/A'} ${user.last_name || ''}</td>
            <td>${formatDate(user.date_joined)}</td>
            <td>
                <span class="status-badge ${getUserStatusClass(user)}">
                    ${getUserStatus(user)}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    ${!user.is_superuser ? `
                    <button class="action-btn btn-delete" onclick="deleteUser(${user.id})" title="Delete User">
                        🗑️ Delete
                    </button>` : ''}
                </div>
            </td>
        </tr>
    `).join('');
}

function getUserStatus(user) {
    if (user.is_superuser) return 'Admin';
    if (user.is_active) return 'Active';
    return 'Inactive';
}

function getUserStatusClass(user) {
    if (user.is_superuser) return 'status-admin';
    if (user.is_active) return 'status-active';
    return 'status-inactive';
}

function setupEventListeners() {
    // Search functionality
    const searchInput = document.getElementById('userSearch');
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        filterUsers(searchTerm);
    });

    // Filter functionality
    const filterSelect = document.getElementById('userFilter');
    filterSelect.addEventListener('change', function() {
        applyFilter(this.value);
    });

    // Refresh button
    const refreshBtn = document.getElementById('refreshUsers');
    refreshBtn.addEventListener('click', function() {
        loadUsers();
        loadUsersStats();
    });

    // Export button
    const exportBtn = document.getElementById('exportUsers');
    exportBtn.addEventListener('click', exportUsers);

    // Sorting functionality
    const sortableHeaders = document.querySelectorAll('.sortable');
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const field = this.dataset.sort;
            sortUsers(field);
        });
    });

    // Pagination
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    
    prevBtn.addEventListener('click', function() {
        if (currentPage > 1) {
            currentPage--;
            displayUsers();
            updatePagination();
        }
    });

    nextBtn.addEventListener('click', function() {
        const totalPages = Math.ceil(filteredUsers.length / usersPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            displayUsers();
            updatePagination();
        }
    });

    // Modal functionality
    const modal = document.getElementById('userModal');
    const closeModal = document.getElementById('closeModal');
    const modalClose = document.querySelector('.modal-close');

    closeModal.addEventListener('click', function() {
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

function filterUsers(searchTerm) {
    filteredUsers = currentUsers.filter(user => {
        return user.username.toLowerCase().includes(searchTerm) ||
               user.email.toLowerCase().includes(searchTerm) ||
               (user.first_name && user.first_name.toLowerCase().includes(searchTerm)) ||
               (user.last_name && user.last_name.toLowerCase().includes(searchTerm));
    });
    
    currentPage = 1;
    displayUsers();
    updatePagination();
}

function applyFilter(filterType) {
    const searchTerm = document.getElementById('userSearch').value.toLowerCase();
    
    let filtered = currentUsers;
    
    // Apply search filter first
    if (searchTerm) {
        filtered = filtered.filter(user => {
            return user.username.toLowerCase().includes(searchTerm) ||
                   user.email.toLowerCase().includes(searchTerm) ||
                   (user.first_name && user.first_name.toLowerCase().includes(searchTerm)) ||
                   (user.last_name && user.last_name.toLowerCase().includes(searchTerm));
        });
    }
    
    // Apply status filter
    switch (filterType) {
        case 'active':
            filtered = filtered.filter(user => user.is_active && !user.is_superuser);
            break;
        case 'inactive':
            filtered = filtered.filter(user => !user.is_active);
            break;
        case 'admin':
            filtered = filtered.filter(user => user.is_superuser);
            break;
        case 'recent':
            const oneWeekAgo = new Date();
            oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
            filtered = filtered.filter(user => new Date(user.date_joined) > oneWeekAgo);
            break;
        default:
            // 'all' - no additional filtering
            break;
    }
    
    filteredUsers = filtered;
    currentPage = 1;
    displayUsers();
    updatePagination();
}

function sortUsers(field) {
    if (currentSort.field === field) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.field = field;
        currentSort.direction = 'asc';
    }

    filteredUsers.sort((a, b) => {
        let aValue = a[field];
        let bValue = b[field];

        // Handle null/undefined values
        if (aValue == null) aValue = '';
        if (bValue == null) bValue = '';

        // Handle dates
        if (field === 'date_joined' || field === 'last_login') {
            aValue = new Date(aValue);
            bValue = new Date(bValue);
        }

        // Handle strings
        if (typeof aValue === 'string') {
            aValue = aValue.toLowerCase();
            bValue = bValue.toLowerCase();
        }

        if (currentSort.direction === 'asc') {
            return aValue > bValue ? 1 : -1;
        } else {
            return aValue < bValue ? 1 : -1;
        }
    });

    displayUsers();
    updateSortArrows();
}

function updateSortArrows() {
    // Reset all headers
    document.querySelectorAll('.sortable .th-content').forEach(header => {
        const text = header.textContent.replace(' ↑', '').replace(' ↓', '');
        header.textContent = text;
    });

    // Update current sort header
    const currentHeader = document.querySelector(`[data-sort="${currentSort.field}"] .th-content`);
    if (currentHeader) {
        const text = currentHeader.textContent;
        const arrow = currentSort.direction === 'asc' ? ' ↑' : ' ↓';
        currentHeader.textContent = text + arrow;
    }
}

function updatePagination() {
    const totalUsers = filteredUsers.length;
    const totalPages = Math.ceil(totalUsers / usersPerPage);
    const startIndex = (currentPage - 1) * usersPerPage + 1;
    const endIndex = Math.min(currentPage * usersPerPage, totalUsers);

    // Update pagination info
    const paginationInfo = document.getElementById('paginationInfo');
    paginationInfo.textContent = `Showing ${startIndex}-${endIndex} of ${totalUsers} users`;

    // Update pagination buttons
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages || totalPages === 0;

    // Update page numbers
    const pageNumbers = document.getElementById('pageNumbers');
    pageNumbers.innerHTML = '';

    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.className = `page-number ${i === currentPage ? 'active' : ''}`;
        pageBtn.textContent = i;
        pageBtn.addEventListener('click', function() {
            currentPage = i;
            displayUsers();
            updatePagination();
        });
        pageNumbers.appendChild(pageBtn);
    }
}

function deleteUser(userId) {
    const user = currentUsers.find(u => u.id === userId);
    if (!user) return;

    // Create a custom confirmation dialog
    const confirmDelete = confirm(
        `⚠️ DELETE USER CONFIRMATION\n\n` +
        `Are you sure you want to permanently delete user "${user.username}"?\n\n` +
        `This will also delete:\n` +
        `• All their pet reports\n` +
        `• All their comments\n` +
        `• All their chat messages\n` +
        `• All associated data\n\n` +
        `⚠️ THIS ACTION CANNOT BE UNDONE!\n\n` +
        `Click OK to proceed or Cancel to abort.`
    );

    if (!confirmDelete) return;

    // Show loading state
    const deleteBtn = document.querySelector(`[onclick="deleteUser(${userId})"]`);
    const originalText = deleteBtn.innerHTML;
    deleteBtn.innerHTML = '⏳ Deleting...';
    deleteBtn.disabled = true;

    // Make API call to delete user
    fetch('/api/admin/delete-user/', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            user_id: userId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            alert(`✅ User "${user.username}" has been successfully deleted.`);
            
            // Remove user from current data
            currentUsers = currentUsers.filter(u => u.id !== userId);
            filteredUsers = filteredUsers.filter(u => u.id !== userId);
            
            // Refresh the display
            displayUsers();
            updatePagination();
            loadUsersStats(); // Refresh stats
        } else {
            // Show error message
            alert(`❌ Error deleting user: ${data.error}`);
            
            // Restore button
            deleteBtn.innerHTML = originalText;
            deleteBtn.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error deleting user:', error);
        alert(`❌ Network error occurred while deleting user. Please try again.`);
        
        // Restore button
        deleteBtn.innerHTML = originalText;
        deleteBtn.disabled = false;
    });
}

function exportUsers() {
    const csvContent = generateCSV(filteredUsers);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `users_export_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

function generateCSV(users) {
    const headers = ['ID', 'Username', 'Email', 'First Name', 'Last Name', 'Status', 'Active', 'Staff', 'Superuser', 'Date Joined', 'Last Login'];
    const csvRows = [headers.join(',')];

    users.forEach(user => {
        const row = [
            user.id,
            `"${user.username}"`,
            `"${user.email}"`,
            `"${user.first_name || ''}"`,
            `"${user.last_name || ''}"`,
            `"${getUserStatus(user)}"`,
            user.is_active ? 'Yes' : 'No',
            user.is_staff ? 'Yes' : 'No',
            user.is_superuser ? 'Yes' : 'No',
            `"${formatDate(user.date_joined)}"`,
            `"${user.last_login ? formatDate(user.last_login) : 'Never'}"`
        ];
        csvRows.push(row.join(','));
    });

    return csvRows.join('\n');
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getAccountAge(dateJoined) {
    const joinDate = new Date(dateJoined);
    const now = new Date();
    const diffTime = Math.abs(now - joinDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 30) {
        return `${diffDays} days`;
    } else if (diffDays < 365) {
        const months = Math.floor(diffDays / 30);
        return `${months} month${months > 1 ? 's' : ''}`;
    } else {
        const years = Math.floor(diffDays / 365);
        return `${years} year${years > 1 ? 's' : ''}`;
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