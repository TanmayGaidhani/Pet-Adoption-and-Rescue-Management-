// ===== USER PROFILE JAVASCRIPT =====

document.addEventListener('DOMContentLoaded', function() {
    console.log('User Profile: Page loaded, initializing...');
    
    // Load user data and activity
    loadUserStats();
    loadUserActivity();
    loadMemberSince();
    
    // Profile form submission
    const profileForm = document.getElementById('profileUpdateForm');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            updateProfile();
        });
    }
    
    // Settings change handlers
    const emailNotifications = document.getElementById('emailNotifications');
    const communityNotifications = document.getElementById('communityNotifications');
    const privacyLevel = document.getElementById('privacyLevel');
    
    if (emailNotifications) {
        emailNotifications.addEventListener('change', function() {
            updateSetting('email_notifications', this.checked);
        });
    }
    
    if (communityNotifications) {
        communityNotifications.addEventListener('change', function() {
            updateSetting('community_notifications', this.checked);
        });
    }
    
    if (privacyLevel) {
        privacyLevel.addEventListener('change', function() {
            updateSetting('privacy_level', this.value);
        });
    }
    
    console.log('User Profile: Initialization complete');
});

// ===== PROFILE MANAGEMENT =====

function toggleEditMode() {
    const editForm = document.getElementById('editProfileForm');
    const editBtn = document.querySelector('.edit-profile-btn');
    
    if (!editForm || !editBtn) return;
    
    if (editForm.style.display === 'none' || editForm.style.display === '') {
        editForm.style.display = 'block';
        editBtn.innerHTML = '<span class="btn-icon">❌</span> Cancel Edit';
        editBtn.style.background = 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)';
    } else {
        editForm.style.display = 'none';
        editBtn.innerHTML = '<span class="btn-icon">✏️</span> Edit Profile';
        editBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }
}

function updateProfile() {
    const form = document.getElementById('profileUpdateForm');
    if (!form) return;
    
    const formData = new FormData(form);
    const data = {};
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    console.log('Updating profile:', data);
    
    // Show loading state
    const saveBtn = form.querySelector('.btn-save');
    const originalText = saveBtn.innerHTML;
    saveBtn.innerHTML = '<span class="btn-icon">⏳</span> Saving...';
    saveBtn.disabled = true;
    
    fetch('/api/profile/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Profile updated successfully! 🎉', 'success');
            toggleEditMode();
            // Update displayed information
            updateDisplayedProfile(data.user);
        } else {
            showNotification('Error updating profile: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Error updating profile:', error);
        showNotification('Failed to update profile. Please try again.', 'error');
    })
    .finally(() => {
        saveBtn.innerHTML = originalText;
        saveBtn.disabled = false;
    });
}

function updateDisplayedProfile(userData) {
    const profileName = document.querySelector('.profile-name');
    const profileEmail = document.querySelector('.profile-email');
    
    if (profileName && userData.name) {
        profileName.textContent = userData.name;
    }
    
    if (profileEmail && userData.email) {
        profileEmail.textContent = userData.email;
    }
}

// ===== USER STATS AND ACTIVITY =====

function loadUserStats() {
    console.log('Loading user stats...');
    
    fetch('/api/profile/stats/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading stats:', data.error);
                return;
            }
            
            // Update stat numbers
            const stats = data.stats || {};
            updateStatElement('adoptionRequests', stats.adoption_requests || 0);
            updateStatElement('rescueReports', stats.rescue_reports || 0);
            updateStatElement('foundPetReports', stats.found_pet_reports || 0);
            updateStatElement('communityComments', stats.community_comments || 0);
        })
        .catch(error => {
            console.error('Error loading user stats:', error);
        });
}

function updateStatElement(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        // Animate number counting
        animateNumber(element, 0, value, 1000);
    }
}

function animateNumber(element, start, end, duration) {
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + (end - start) * progress);
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

function loadUserActivity() {
    console.log('Loading user activity...');
    
    fetch('/api/profile/activity/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading activity:', data.error);
                return;
            }
            
            const activities = data.activities || [];
            displayActivity(activities);
        })
        .catch(error => {
            console.error('Error loading user activity:', error);
            showActivityError();
        });
}

function displayActivity(activities) {
    const activityList = document.getElementById('activityList');
    const noActivity = document.getElementById('noActivity');
    
    if (!activityList) return;
    
    if (activities.length === 0) {
        activityList.style.display = 'none';
        if (noActivity) noActivity.style.display = 'block';
        return;
    }
    
    if (noActivity) noActivity.style.display = 'none';
    activityList.style.display = 'block';
    
    activityList.innerHTML = activities.map(activity => `
        <div class="activity-item" data-type="${activity.type}">
            <div class="activity-icon ${activity.type}">
                ${getActivityIcon(activity.type)}
            </div>
            <div class="activity-content">
                <div class="activity-title">${activity.title}</div>
                <div class="activity-description">${activity.description}</div>
                <div class="activity-time">${activity.time_ago}</div>
            </div>
        </div>
    `).join('');
}

function getActivityIcon(type) {
    const icons = {
        'adoption': '🐾',
        'rescue': '🚨',
        'found': '🔍',
        'comment': '💬'
    };
    return icons[type] || '📝';
}

function showActivityError() {
    const activityList = document.getElementById('activityList');
    if (activityList) {
        activityList.innerHTML = `
            <div class="error-message">
                <p>❌ Failed to load activity. Please refresh the page.</p>
            </div>
        `;
    }
}

function loadMemberSince() {
    fetch('/api/profile/member-since/')
        .then(response => response.json())
        .then(data => {
            const memberSinceElement = document.getElementById('memberSince');
            if (memberSinceElement && data.member_since) {
                memberSinceElement.textContent = data.member_since;
            }
        })
        .catch(error => {
            console.error('Error loading member since:', error);
        });
}

// ===== ACTIVITY FILTERING =====

function filterActivity(type) {
    console.log('Filtering activity by:', type);
    
    // Update active filter button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Filter activity items
    const activityItems = document.querySelectorAll('.activity-item');
    activityItems.forEach(item => {
        if (type === 'all' || item.dataset.type === type) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// ===== SETTINGS MANAGEMENT =====

function updateSetting(settingName, value) {
    console.log('Updating setting:', settingName, value);
    
    fetch('/api/profile/settings/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            setting: settingName,
            value: value
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Setting updated successfully', 'success');
        } else {
            showNotification('Error updating setting: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Error updating setting:', error);
        showNotification('Failed to update setting. Please try again.', 'error');
    });
}

// ===== ACCOUNT DELETION =====

function confirmAccountDeletion() {
    const confirmed = confirm(
        '⚠️ WARNING: This action cannot be undone!\n\n' +
        'Deleting your account will:\n' +
        '• Remove all your reports and adoption requests\n' +
        '• Delete all your community comments\n' +
        '• Permanently erase your profile data\n\n' +
        'Are you absolutely sure you want to delete your account?'
    );
    
    if (confirmed) {
        const doubleConfirm = prompt(
            'To confirm account deletion, please type "DELETE MY ACCOUNT" (without quotes):'
        );
        
        if (doubleConfirm === 'DELETE MY ACCOUNT') {
            deleteAccount();
        } else {
            showNotification('Account deletion cancelled - incorrect confirmation text', 'info');
        }
    }
}

function deleteAccount() {
    console.log('Deleting user account...');
    
    fetch('/api/profile/delete/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Your account has been successfully deleted. You will now be redirected to the homepage.');
            window.location.href = '/';
        } else {
            showNotification('Error deleting account: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting account:', error);
        showNotification('Failed to delete account. Please try again.', 'error');
    });
}

// ===== UTILITY FUNCTIONS =====

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

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">✕</button>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#dc2626' : '#3b82f6'};
        color: white;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
        max-width: 400px;
        word-wrap: break-word;
    `;
    
    notification.querySelector('.notification-content').style.cssText = `
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 15px;
    `;
    
    notification.querySelector('.notification-close').style.cssText = `
        background: none;
        border: none;
        color: white;
        font-size: 16px;
        cursor: pointer;
        padding: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background-color 0.3s;
    `;
    
    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideInRight 0.3s ease-out reverse';
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}