// ===== ADMIN SETTINGS JAVASCRIPT =====

document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin Settings page loaded');
    
    // Load current settings
    loadCurrentSettings();
    
    // Add event listeners
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Save Settings button
    const saveBtn = document.getElementById('saveSettings');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveSettings);
    }
    
    // Reset Settings button
    const resetBtn = document.getElementById('resetSettings');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetSettings);
    }
    
    // Export Settings button
    const exportBtn = document.getElementById('exportSettings');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportSettings);
    }
    
    // Add change listeners to form elements
    const formElements = document.querySelectorAll('input, select');
    formElements.forEach(element => {
        element.addEventListener('change', markAsChanged);
    });
}

// Load current settings from server
async function loadCurrentSettings() {
    try {
        showLoading(true);
        
        const response = await fetch('/api/admin/settings/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            populateSettings(data.settings);
        } else {
            console.error('Failed to load settings');
            showMessage('Failed to load current settings', 'error');
        }
    } catch (error) {
        console.error('Error loading settings:', error);
        showMessage('Error loading settings', 'error');
    } finally {
        showLoading(false);
    }
}

// Populate form with settings data
function populateSettings(settings) {
    if (!settings) return;
    
    // Platform Settings
    if (settings.platformName) {
        document.getElementById('platformName').value = settings.platformName;
    }
    if (settings.platformVersion) {
        document.getElementById('platformVersion').value = settings.platformVersion;
    }
    if (settings.maintenanceMode !== undefined) {
        document.getElementById('maintenanceMode').value = settings.maintenanceMode.toString();
    }
    
    // Email Settings
    if (settings.emailNotifications !== undefined) {
        document.getElementById('emailNotifications').value = settings.emailNotifications.toString();
    }
    if (settings.adminEmail) {
        document.getElementById('adminEmail').value = settings.adminEmail;
    }
    if (settings.smtpServer) {
        document.getElementById('smtpServer').value = settings.smtpServer;
    }
    
    // Security Settings
    if (settings.sessionTimeout) {
        document.getElementById('sessionTimeout').value = settings.sessionTimeout;
    }
    if (settings.maxLoginAttempts) {
        document.getElementById('maxLoginAttempts').value = settings.maxLoginAttempts;
    }
    if (settings.requireEmailVerification !== undefined) {
        document.getElementById('requireEmailVerification').value = settings.requireEmailVerification.toString();
    }
    
    // Chat Settings
    if (settings.chatEnabled !== undefined) {
        document.getElementById('chatEnabled').value = settings.chatEnabled.toString();
    }
    if (settings.maxMessageLength) {
        document.getElementById('maxMessageLength').value = settings.maxMessageLength;
    }
    if (settings.chatModeration !== undefined) {
        document.getElementById('chatModeration').value = settings.chatModeration.toString();
    }
    
    // File Upload Settings
    if (settings.maxFileSize) {
        document.getElementById('maxFileSize').value = settings.maxFileSize;
    }
    if (settings.allowedFileTypes) {
        document.getElementById('allowedFileTypes').value = settings.allowedFileTypes;
    }
    if (settings.imageCompression !== undefined) {
        document.getElementById('imageCompression').value = settings.imageCompression.toString();
    }
    
    // Database Settings
    if (settings.dbStatus) {
        document.getElementById('dbStatus').value = settings.dbStatus;
    }
    if (settings.autoBackup !== undefined) {
        document.getElementById('autoBackup').value = settings.autoBackup.toString();
    }
    if (settings.backupFrequency) {
        document.getElementById('backupFrequency').value = settings.backupFrequency;
    }
}

// Collect all settings from form
function collectSettings() {
    return {
        // Platform Settings
        platformName: document.getElementById('platformName').value,
        platformVersion: document.getElementById('platformVersion').value,
        maintenanceMode: document.getElementById('maintenanceMode').value === 'true',
        
        // Email Settings
        emailNotifications: document.getElementById('emailNotifications').value === 'true',
        adminEmail: document.getElementById('adminEmail').value,
        smtpServer: document.getElementById('smtpServer').value,
        
        // Security Settings
        sessionTimeout: parseInt(document.getElementById('sessionTimeout').value),
        maxLoginAttempts: parseInt(document.getElementById('maxLoginAttempts').value),
        requireEmailVerification: document.getElementById('requireEmailVerification').value === 'true',
        
        // Chat Settings
        chatEnabled: document.getElementById('chatEnabled').value === 'true',
        maxMessageLength: parseInt(document.getElementById('maxMessageLength').value),
        chatModeration: document.getElementById('chatModeration').value === 'true',
        
        // File Upload Settings
        maxFileSize: parseInt(document.getElementById('maxFileSize').value),
        allowedFileTypes: document.getElementById('allowedFileTypes').value,
        imageCompression: document.getElementById('imageCompression').value === 'true',
        
        // Database Settings
        dbStatus: document.getElementById('dbStatus').value,
        autoBackup: document.getElementById('autoBackup').value === 'true',
        backupFrequency: document.getElementById('backupFrequency').value
    };
}

// Save settings to server
async function saveSettings() {
    try {
        showLoading(true);
        
        const settings = collectSettings();
        
        // Validate settings
        if (!validateSettings(settings)) {
            return;
        }
        
        const response = await fetch('/api/admin/settings/save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ settings: settings })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showMessage('Settings saved successfully! 💾', 'success');
            markAsUnchanged();
        } else {
            showMessage(data.error || 'Failed to save settings', 'error');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showMessage('Error saving settings', 'error');
    } finally {
        showLoading(false);
    }
}

// Validate settings before saving
function validateSettings(settings) {
    // Email validation
    if (settings.adminEmail && !isValidEmail(settings.adminEmail)) {
        showMessage('Please enter a valid admin email address', 'error');
        return false;
    }
    
    // Session timeout validation
    if (settings.sessionTimeout < 15 || settings.sessionTimeout > 480) {
        showMessage('Session timeout must be between 15 and 480 minutes', 'error');
        return false;
    }
    
    // Max login attempts validation
    if (settings.maxLoginAttempts < 3 || settings.maxLoginAttempts > 10) {
        showMessage('Max login attempts must be between 3 and 10', 'error');
        return false;
    }
    
    // Message length validation
    if (settings.maxMessageLength < 100 || settings.maxMessageLength > 1000) {
        showMessage('Max message length must be between 100 and 1000 characters', 'error');
        return false;
    }
    
    // File size validation
    if (settings.maxFileSize < 1 || settings.maxFileSize > 50) {
        showMessage('Max file size must be between 1 and 50 MB', 'error');
        return false;
    }
    
    return true;
}

// Reset settings to default
async function resetSettings() {
    if (!confirm('Are you sure you want to reset all settings to default values? This action cannot be undone.')) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/admin/settings/reset/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showMessage('Settings reset to default values! 🔄', 'success');
            // Reload the page to show default values
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showMessage(data.error || 'Failed to reset settings', 'error');
        }
    } catch (error) {
        console.error('Error resetting settings:', error);
        showMessage('Error resetting settings', 'error');
    } finally {
        showLoading(false);
    }
}

// Export settings configuration
async function exportSettings() {
    try {
        showLoading(true);
        
        const response = await fetch('/api/admin/settings/export/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `rescuemate-settings-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showMessage('Settings exported successfully! 📊', 'success');
        } else {
            showMessage('Failed to export settings', 'error');
        }
    } catch (error) {
        console.error('Error exporting settings:', error);
        showMessage('Error exporting settings', 'error');
    } finally {
        showLoading(false);
    }
}

// Mark form as changed
function markAsChanged() {
    const saveBtn = document.getElementById('saveSettings');
    if (saveBtn) {
        saveBtn.style.background = 'linear-gradient(135deg, #e74c3c, #c0392b)';
        saveBtn.innerHTML = '💾 Save Changes *';
    }
}

// Mark form as unchanged
function markAsUnchanged() {
    const saveBtn = document.getElementById('saveSettings');
    if (saveBtn) {
        saveBtn.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
        saveBtn.innerHTML = '💾 Save Settings';
    }
}

// Show loading state
function showLoading(isLoading) {
    const cards = document.querySelectorAll('.settings-card');
    const buttons = document.querySelectorAll('.settings-actions button');
    
    if (isLoading) {
        cards.forEach(card => card.classList.add('loading'));
        buttons.forEach(btn => btn.disabled = true);
    } else {
        cards.forEach(card => card.classList.remove('loading'));
        buttons.forEach(btn => btn.disabled = false);
    }
}

// Show message to user
function showMessage(message, type = 'info') {
    const container = document.getElementById('messageContainer');
    const content = document.getElementById('messageContent');
    
    if (container && content) {
        content.textContent = message;
        content.className = `message-content ${type}`;
        container.style.display = 'block';
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            container.style.display = 'none';
        }, 5000);
    }
}

// Email validation helper
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Handle page visibility change
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // Page became visible, refresh settings
        loadCurrentSettings();
    }
});

// Handle beforeunload to warn about unsaved changes
window.addEventListener('beforeunload', function(e) {
    const saveBtn = document.getElementById('saveSettings');
    if (saveBtn && saveBtn.innerHTML.includes('*')) {
        e.preventDefault();
        e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
        return e.returnValue;
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+S to save
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        saveSettings();
    }
    
    // Ctrl+R to reset (with confirmation)
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        resetSettings();
    }
});

console.log('Admin Settings JavaScript loaded successfully');