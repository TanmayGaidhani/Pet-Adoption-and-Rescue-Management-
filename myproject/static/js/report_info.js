document.addEventListener('DOMContentLoaded', function() {
    
    // Load rescue reports on page load
    loadRescueReports();

    // Search functionality
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.querySelector('.search-btn');
    
    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    // Filter functionality
    const animalTypeFilter = document.getElementById('animalTypeFilter');
    const urgencyFilter = document.getElementById('urgencyFilter');
    const cityFilter = document.getElementById('cityFilter');
    
    animalTypeFilter.addEventListener('change', performSearch);
    urgencyFilter.addEventListener('change', performSearch);
    cityFilter.addEventListener('change', performSearch);

    function loadRescueReports() {
        // Fetch real data from the API
        fetch('/api/rescue-reports/')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error:', data.error);
                    showError('Failed to load rescue reports');
                    return;
                }
                
                const reports = data.reports || [];
                displayReports(reports);
                populateCityFilter(reports);
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Failed to load rescue reports');
            });
    }

    function showError(message) {
        const reportsGrid = document.getElementById('reportsGrid');
        reportsGrid.innerHTML = `
            <div class="loading-message">
                <p style="color: #f44336;">❌ ${message}</p>
            </div>
        `;
    }

    function displayReports(reports) {
        const reportsGrid = document.getElementById('reportsGrid');
        const noResults = document.getElementById('noResults');

        if (reports.length === 0) {
            reportsGrid.innerHTML = '';
            noResults.style.display = 'block';
            return;
        }

        noResults.style.display = 'none';
        
        reportsGrid.innerHTML = reports.map(report => {
            const imageSrc = report.image_path ? `/media/${report.image_path}` : null;
            
            return `
                <div class="report-card-compact">
                    <div class="report-card-header">
                        <span class="animal-type-badge">${report.animal_type || 'UNKNOWN'}</span>
                        <span class="urgency-badge urgency-${report.urgency || 'low'}">${(report.urgency || 'low').toUpperCase()}</span>
                    </div>
                    
                    <div class="report-image-container">
                        ${imageSrc 
                            ? `<img src="${imageSrc}" class="report-image-compact" alt="${report.breed || 'Animal'}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                               <div class="no-image-compact" style="display: none;">
                                   🚨<br><small>No Image</small>
                               </div>`
                            : `<div class="no-image-compact">
                                   🚨<br><small>No Image</small>
                               </div>`
                        }
                    </div>
                    
                    <div class="report-content">
                        <h5 class="report-title-compact">${report.breed || 'Unknown Breed'}</h5>
                        <div class="report-info-compact">
                            <div class="info-row-compact">
                                <span class="info-label-compact">Color:</span>
                                <span class="info-value-compact">${truncateText(report.color || 'Unknown', 12)}</span>
                            </div>
                            <div class="info-row-compact">
                                <span class="info-label-compact">Gender:</span>
                                <span class="info-value-compact">${report.gender || 'Unknown'}</span>
                            </div>
                            <div class="info-row-compact">
                                <span class="info-label-compact">Condition:</span>
                                <span class="info-value-compact">${truncateText(report.condition || 'Unknown', 10)}</span>
                            </div>
                            <div class="info-row-compact">
                                <span class="info-label-compact">Date:</span>
                                <span class="info-value-compact">${formatDate(report.date_found)}</span>
                            </div>
                            ${report.special_marks ? `
                            <div class="info-row-compact">
                                <span class="info-label-compact">Marks:</span>
                                <span class="info-value-compact">${truncateText(report.special_marks, 12)}</span>
                            </div>
                            ` : ''}
                        </div>
                        
                        <div class="report-location-compact">
                            📍 ${truncateText(report.location || 'Unknown', 15)}, ${truncateText(report.city || 'Unknown', 10)}
                        </div>
                        
                        <div class="report-actions-compact">
                            <button class="btn-contact-compact" onclick="contactReporter('${report.contact_name}', '${report.contact_phone}', '${report.contact_email}')" title="Contact Reporter">
                                📞 Contact
                            </button>
                            <button class="btn-chat-compact" onclick="openPetChat('${report.id}', '${report.breed || 'Unknown Pet'}')" title="Chat about this pet">
                                💬 Chat
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

    function populateCityFilter(reports) {
        const cityFilter = document.getElementById('cityFilter');
        const cities = [...new Set(reports.map(report => report.city).filter(city => city))];
        
        // Clear existing options except the first one
        cityFilter.innerHTML = '<option value="">All Cities</option>';
        
        cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            cityFilter.appendChild(option);
        });
    }

    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase();
        const animalType = animalTypeFilter.value;
        const urgency = urgencyFilter.value;
        const city = cityFilter.value;

        // Show loading
        document.getElementById('reportsGrid').innerHTML = `
            <div class="loading-message">
                <div class="loading-spinner"></div>
                <p>Searching...</p>
            </div>
        `;

        // Fetch and filter data
        fetch('/api/rescue-reports/')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError('Search failed');
                    return;
                }
                
                let reports = data.reports || [];
                
                // Apply filters
                if (searchTerm) {
                    reports = reports.filter(report => 
                        (report.breed && report.breed.toLowerCase().includes(searchTerm)) ||
                        (report.color && report.color.toLowerCase().includes(searchTerm)) ||
                        (report.location && report.location.toLowerCase().includes(searchTerm)) ||
                        (report.description && report.description.toLowerCase().includes(searchTerm)) ||
                        (report.condition && report.condition.toLowerCase().includes(searchTerm))
                    );
                }
                
                if (animalType) {
                    reports = reports.filter(report => report.animal_type === animalType);
                }
                
                if (urgency) {
                    reports = reports.filter(report => report.urgency === urgency);
                }
                
                if (city) {
                    reports = reports.filter(report => report.city === city);
                }
                
                displayReports(reports);
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Search failed');
            });
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

    // Make contactReporter function global
    window.contactReporter = function(name, phone, email) {
        const contactInfo = `Contact Information:\n\nName: ${name}\nPhone: ${phone}\nEmail: ${email || 'Not provided'}\n\nPlease contact them to help with this rescue case.`;
        alert(contactInfo);
        // In real implementation, this could open a contact form or dial the number
    };

    // Chat functionality
    window.openPetChat = function(reportId, petName) {
        openChatModal(reportId, petName);
    };

    function openChatModal(reportId, petName) {
        // Create chat modal if it doesn't exist
        let chatModal = document.getElementById('petChatModal');
        if (!chatModal) {
            createChatModal();
            chatModal = document.getElementById('petChatModal');
        }

        // Set pet info
        document.getElementById('chatPetName').textContent = petName;
        document.getElementById('chatReportId').value = reportId;
        
        // Clear and load messages
        loadChatMessages(reportId);
        
        // Show modal
        chatModal.style.display = 'block';
    }

    function createChatModal() {
        const modalHTML = `
            <div id="petChatModal" class="chat-modal">
                <div class="chat-modal-content">
                    <div class="chat-header">
                        <h3>💬 Chat about <span id="chatPetName"></span></h3>
                        <span class="chat-close" onclick="closeChatModal()">&times;</span>
                    </div>
                    <div class="chat-messages" id="chatMessages">
                        <div class="loading-chat">Loading messages...</div>
                    </div>
                    <div class="chat-input-section">
                        <input type="hidden" id="chatReportId">
                        <div class="chat-input-container">
                            <input type="text" id="chatMessageInput" placeholder="Type your message about this pet..." maxlength="500">
                            <button id="sendChatMessage" onclick="sendMessage()">Send</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Add event listeners
        document.getElementById('chatMessageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    window.closeChatModal = function() {
        document.getElementById('petChatModal').style.display = 'none';
    };

    window.sendMessage = function() {
        const messageInput = document.getElementById('chatMessageInput');
        const reportId = document.getElementById('chatReportId').value;
        const message = messageInput.value.trim();

        if (!message) {
            alert('Please enter a message');
            return;
        }

        // Send message to server
        fetch('/api/pet-chat/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                report_id: reportId,
                message: message
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                messageInput.value = '';
                loadChatMessages(reportId);
            } else {
                alert('Failed to send message: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to send message');
        });
    };

    function loadChatMessages(reportId) {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '<div class="loading-chat">Loading messages...</div>';

        fetch(`/api/pet-chat/messages/${reportId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayChatMessages(data.messages);
                } else {
                    chatMessages.innerHTML = '<div class="no-messages">No messages yet. Start the conversation!</div>';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                chatMessages.innerHTML = '<div class="error-messages">Failed to load messages</div>';
            });
    }

    function displayChatMessages(messages) {
        const chatMessages = document.getElementById('chatMessages');
        
        if (messages.length === 0) {
            chatMessages.innerHTML = '<div class="no-messages">No messages yet. Start the conversation!</div>';
            return;
        }

        chatMessages.innerHTML = messages.map(msg => `
            <div class="chat-message ${msg.is_current_user ? 'own-message' : 'other-message'}">
                <div class="message-header">
                    <span class="message-user">${msg.user_name}</span>
                    <span class="message-time">${formatChatTime(msg.created_at)}</span>
                </div>
                <div class="message-text">${escapeHtml(msg.message)}</div>
            </div>
        `).join('');

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
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

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('petChatModal');
        if (event.target === modal) {
            closeChatModal();
        }
    });

});