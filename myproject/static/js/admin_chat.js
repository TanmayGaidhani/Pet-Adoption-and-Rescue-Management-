// ===== ADMIN CHAT MANAGEMENT JAVASCRIPT =====

// Global variables
let currentChatId = null;
let currentPetName = '';
let chatRefreshInterval = null;

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
    loadChatStats();
    loadChatList();
    setupEventListeners();
    
    // Auto-refresh every 30 seconds
    chatRefreshInterval = setInterval(() => {
        loadChatStats();
        loadChatList();
        if (currentChatId) {
            loadChatMessages(currentChatId);
        }
    }, 30000);
});

function setupEventListeners() {
    // Refresh button
    const refreshBtn = document.getElementById('refreshChats');
    refreshBtn.addEventListener('click', function() {
        loadChatStats();
        loadChatList();
        if (currentChatId) {
            loadChatMessages(currentChatId);
        }
    });

    // Search functionality
    const searchInput = document.getElementById('chatSearch');
    searchInput.addEventListener('input', function() {
        filterChatList(this.value);
    });

    // Send admin message
    const sendBtn = document.getElementById('sendAdminMessage');
    const messageInput = document.getElementById('adminMessageText');
    
    sendBtn.addEventListener('click', sendAdminMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendAdminMessage();
        }
    });

    // Moderation actions
    document.getElementById('moderateChat').addEventListener('click', openModerationModal);
    document.getElementById('closeChat').addEventListener('click', closeChatDiscussion);

    // Modal functionality
    setupModalListeners();
}

function loadChatStats() {
    fetch('/api/admin/chat-stats/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }
            
            document.getElementById('totalChatsCount').textContent = data.total_chats || 0;
            document.getElementById('recentMessagesCount').textContent = data.recent_messages || 0;
            document.getElementById('activeUsersCount').textContent = data.active_users || 0;
            document.getElementById('flaggedMessagesCount').textContent = data.flagged_messages || 0;
        })
        .catch(error => {
            console.error('Error loading chat stats:', error);
            // Show fallback data
            document.getElementById('totalChatsCount').textContent = '0';
            document.getElementById('recentMessagesCount').textContent = '0';
            document.getElementById('activeUsersCount').textContent = '0';
            document.getElementById('flaggedMessagesCount').textContent = '0';
        });
}

function loadChatList() {
    fetch('/api/admin/chat-list/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                showNoChatMessage();
                return;
            }
            
            displayChatList(data.chats || []);
        })
        .catch(error => {
            console.error('Error loading chat list:', error);
            showNoChatMessage();
        });
}

function showNoChatMessage() {
    const chatList = document.getElementById('chatList');
    chatList.innerHTML = `
        <div class="loading-chats">
            <div style="font-size: 48px; margin-bottom: 16px; opacity: 0.6;">💬</div>
            No active pet discussions found
        </div>
    `;
}

function displayChatList(chats) {
    const chatList = document.getElementById('chatList');
    
    if (chats.length === 0) {
        showNoChatMessage();
        return;
    }

    chatList.innerHTML = chats.map(chat => `
        <div class="chat-item" data-chat-id="${chat.report_id}" onclick="selectChat('${chat.report_id}', '${chat.pet_name}')">
            <div class="chat-item-header">
                <span class="chat-pet-name">${chat.pet_name}</span>
                <span class="chat-message-count">${chat.message_count}</span>
            </div>
            <div class="chat-last-message">${chat.last_message || 'No messages yet'}</div>
        </div>
    `).join('');
}

function selectChat(chatId, petName) {
    // Update active chat
    currentChatId = chatId;
    currentPetName = petName;
    
    // Update UI
    document.querySelectorAll('.chat-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-chat-id="${chatId}"]`).classList.add('active');
    
    // Update header - show user name and pet info
    const headerInfo = document.querySelector('.selected-chat-info');
    headerInfo.innerHTML = `
        <h3>💬 ${petName}</h3>
        <p>Report ID: ${chatId} • Admin monitoring active</p>
    `;
    
    // Load messages
    loadChatMessages(chatId);
    
    // Show admin input
    document.getElementById('adminMessageInput').style.display = 'block';
}

function loadChatMessages(chatId) {
    const container = document.getElementById('chatMessagesContainer');
    container.innerHTML = '<div class="loading-chats">Loading messages...</div>';

    fetch(`/api/admin/chat-messages/${chatId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayChatMessages(data.messages);
            } else {
                container.innerHTML = '<div class="loading-chats">No messages found</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = '<div class="loading-chats" style="color: #ef4444;">Failed to load messages</div>';
        });
}

function displayChatMessages(messages) {
    const container = document.getElementById('chatMessagesContainer');
    
    if (messages.length === 0) {
        container.innerHTML = `
            <div class="no-chat-selected">
                <div class="no-chat-icon">💬</div>
                <h3>No Messages Yet</h3>
                <p>This pet discussion hasn't started yet. Users can start chatting about this pet.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = messages.map(msg => `
        <div class="admin-chat-message ${msg.is_admin ? 'admin-message' : 'user-message'}">
            <div class="admin-message-header">
                <span class="admin-message-user ${msg.is_admin ? 'is-admin' : ''}">${msg.user_name}${msg.is_admin ? ' (Admin)' : ''}</span>
                <span class="admin-message-time">${formatChatTime(msg.created_at)}</span>
            </div>
            <div class="admin-message-text">${escapeHtml(msg.message)}</div>
        </div>
    `).join('');

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function sendAdminMessage() {
    const messageInput = document.getElementById('adminMessageText');
    const message = messageInput.value.trim();

    if (!message) {
        alert('Please enter a message');
        return;
    }

    if (!currentChatId) {
        alert('Please select a chat first');
        return;
    }

    // Send message
    fetch('/api/admin/send-chat-message/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            report_id: currentChatId,
            message: message,
            is_admin: true
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            messageInput.value = '';
            loadChatMessages(currentChatId);
            loadChatList(); // Refresh chat list to update message counts
        } else {
            alert('Failed to send message: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to send message');
    });
}

function filterChatList(searchTerm) {
    const chatItems = document.querySelectorAll('.chat-item');
    const term = searchTerm.toLowerCase();

    chatItems.forEach(item => {
        const petName = item.querySelector('.chat-pet-name').textContent.toLowerCase();
        const chatId = item.dataset.chatId.toLowerCase();
        
        if (petName.includes(term) || chatId.includes(term)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

function openModerationModal() {
    document.getElementById('moderationModal').style.display = 'block';
}

function closeChatDiscussion() {
    if (!currentChatId) {
        alert('Please select a chat first');
        return;
    }

    if (confirm(`Are you sure you want to close the discussion for ${currentPetName}? This will prevent new messages.`)) {
        // Implement chat closing logic
        fetch('/api/admin/close-chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                report_id: currentChatId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Chat discussion closed successfully');
                loadChatList();
            } else {
                alert('Failed to close chat: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to close chat');
        });
    }
}

function setupModalListeners() {
    const modal = document.getElementById('moderationModal');
    const closeBtn = document.querySelector('.modal-close');
    const cancelBtn = document.getElementById('cancelModeration');
    const applyBtn = document.getElementById('applyModeration');

    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    cancelBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    applyBtn.addEventListener('click', function() {
        // Implement moderation action
        const reason = document.getElementById('moderationReason').value;
        if (!reason.trim()) {
            alert('Please provide a reason for moderation');
            return;
        }
        
        alert('Moderation feature coming soon!');
        modal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

function formatChatTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
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

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (chatRefreshInterval) {
        clearInterval(chatRefreshInterval);
    }
});