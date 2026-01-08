// ===== COMMUNITY COMMENTS SYSTEM =====

document.addEventListener('DOMContentLoaded', function() {
    console.log('Community Comments: Page loaded, initializing...');
    
    // Load comments on page load
    loadComments();
    
    // Post comment button
    const postBtn = document.getElementById('postCommentBtn');
    if (postBtn) {
        postBtn.addEventListener('click', function() {
            console.log('Community Comments: Post button clicked');
            postComment();
        });
    }
    
    // Character count for textarea
    const commentInput = document.getElementById('commentInput');
    if (commentInput) {
        commentInput.addEventListener('input', function() {
            updateCharCount();
        });
        
        // Auto-resize textarea
        commentInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }
    
    // Image upload handling
    const imageInput = document.getElementById('imageInput');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            handleImageUpload(e);
        });
    }
    
    // Enter key to post (Ctrl+Enter or Cmd+Enter)
    if (commentInput) {
        commentInput.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                postComment();
            }
        });
    }
    
    console.log('Community Comments: Initialization complete');
});

function loadComments() {
    console.log('Community Comments: Loading comments...');
    
    fetch('/api/comments/')
        .then(response => {
            console.log('Community Comments: API response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Community Comments: Comments data received:', data);
            const commentsList = document.getElementById('commentsList');
            const noComments = document.getElementById('noComments');
            const commentCount = document.getElementById('commentCount');
            
            if (!commentsList) {
                console.error('Community Comments: Comments list element not found!');
                return;
            }
            
            const comments = data.comments || [];
            console.log('Community Comments: Number of comments:', comments.length);
            
            // Update comment count
            if (commentCount) {
                commentCount.textContent = comments.length;
            }
            
            if (comments.length === 0) {
                commentsList.style.display = 'none';
                if (noComments) {
                    noComments.style.display = 'block';
                }
                return;
            }
            
            // Hide no comments message and show list
            if (noComments) {
                noComments.style.display = 'none';
            }
            commentsList.style.display = 'block';
            
            // Render comments
            commentsList.innerHTML = comments.map(comment => `
                <div class="comment-item">
                    <div class="comment-header">
                        <span class="comment-author">${comment.user_name}</span>
                        <span class="comment-time">${comment.time_ago}</span>
                    </div>
                    <div class="comment-message">${escapeHtml(comment.message)}</div>
                    ${comment.image_path ? `
                        <div class="comment-image" onclick="openImageModal('${comment.image_path}')">
                            <img src="/media/${comment.image_path}" alt="Comment image" loading="lazy">
                        </div>
                    ` : ''}
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Community Comments: Error loading comments:', error);
            const commentsList = document.getElementById('commentsList');
            if (commentsList) {
                commentsList.innerHTML = `
                    <div class="error-message">
                        <p>❌ Failed to load comments. Please refresh the page.</p>
                    </div>
                `;
            }
        });
}

function postComment() {
    console.log('Community Comments: postComment called');
    const commentInput = document.getElementById('commentInput');
    const postBtn = document.getElementById('postCommentBtn');
    const imageInput = document.getElementById('imageInput');
    
    if (!commentInput) {
        console.error('Community Comments: Comment input not found!');
        return;
    }
    
    const message = commentInput.value.trim();
    
    if (!message && !imageInput.files[0]) {
        showNotification('Please enter a comment or add an image', 'error');
        return;
    }
    
    if (message.length > 500) {
        showNotification('Comment is too long (max 500 characters)', 'error');
        return;
    }
    
    console.log('Community Comments: Posting comment:', message);
    
    // Disable button and show loading
    if (postBtn) {
        postBtn.disabled = true;
        postBtn.innerHTML = '<span class="btn-icon">⏳</span> Posting...';
    }
    
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('message', message);
    
    if (imageInput.files[0]) {
        formData.append('image', imageInput.files[0]);
    }
    
    fetch('/api/comments/post/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Community Comments: Post response:', data);
        if (data.success) {
            commentInput.value = '';
            updateCharCount();
            removeImage(); // Clear image preview
            loadComments(); // Reload comments to show the new one
            showNotification('Comment posted successfully! 🎉', 'success');
            
            // Reset textarea height
            commentInput.style.height = 'auto';
        } else {
            showNotification('Error posting comment: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Community Comments: Error posting comment:', error);
        showNotification('Failed to post comment. Please try again.', 'error');
    })
    .finally(() => {
        // Re-enable button
        if (postBtn) {
            postBtn.disabled = false;
            postBtn.innerHTML = '<span class="btn-icon">📝</span> Post Comment';
        }
    });
}

function updateCharCount() {
    const commentInput = document.getElementById('commentInput');
    const charCount = document.getElementById('charCount');
    
    if (!commentInput || !charCount) return;
    
    const currentLength = commentInput.value.length;
    
    charCount.textContent = `${currentLength}/500`;
    
    if (currentLength > 450) {
        charCount.style.color = '#f44336';
        charCount.style.fontWeight = '600';
    } else if (currentLength > 400) {
        charCount.style.color = '#ff9800';
        charCount.style.fontWeight = '600';
    } else {
        charCount.style.color = '#666';
        charCount.style.fontWeight = '500';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
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
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
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

// Auto-refresh comments every 30 seconds
setInterval(() => {
    console.log('Community Comments: Auto-refreshing comments...');
    loadComments();
}, 30000);

// ===== IMAGE HANDLING FUNCTIONS =====

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
        showNotification('Please select a valid image file', 'error');
        event.target.value = '';
        return;
    }
    
    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        showNotification('Image size must be less than 5MB', 'error');
        event.target.value = '';
        return;
    }
    
    // Create preview
    const reader = new FileReader();
    reader.onload = function(e) {
        const imagePreview = document.getElementById('imagePreview');
        const previewImg = document.getElementById('previewImg');
        const addImageBtn = document.getElementById('addImageBtn');
        
        if (imagePreview && previewImg && addImageBtn) {
            previewImg.src = e.target.result;
            imagePreview.style.display = 'block';
            addImageBtn.style.display = 'none';
        }
    };
    reader.readAsDataURL(file);
}

function removeImage() {
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const addImageBtn = document.getElementById('addImageBtn');
    
    if (imageInput) imageInput.value = '';
    if (imagePreview) imagePreview.style.display = 'none';
    if (addImageBtn) addImageBtn.style.display = 'flex';
}

function openImageModal(imagePath) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        cursor: pointer;
        animation: fadeIn 0.3s ease-out;
    `;
    
    // Create image
    const img = document.createElement('img');
    img.src = `/media/${imagePath}`;
    img.style.cssText = `
        max-width: 90%;
        max-height: 90%;
        object-fit: contain;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    `;
    
    // Create close button
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '✕';
    closeBtn.style.cssText = `
        position: absolute;
        top: 20px;
        right: 20px;
        background: rgba(255, 255, 255, 0.9);
        border: none;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        font-size: 20px;
        font-weight: bold;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    `;
    
    closeBtn.addEventListener('mouseenter', () => {
        closeBtn.style.background = 'rgba(255, 255, 255, 1)';
        closeBtn.style.transform = 'scale(1.1)';
    });
    
    closeBtn.addEventListener('mouseleave', () => {
        closeBtn.style.background = 'rgba(255, 255, 255, 0.9)';
        closeBtn.style.transform = 'scale(1)';
    });
    
    // Close modal function
    const closeModal = () => {
        modal.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            if (modal.parentElement) {
                modal.remove();
            }
        }, 300);
    };
    
    // Event listeners
    modal.addEventListener('click', closeModal);
    closeBtn.addEventListener('click', closeModal);
    img.addEventListener('click', (e) => e.stopPropagation());
    
    // Add fade animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    
    // Assemble modal
    modal.appendChild(img);
    modal.appendChild(closeBtn);
    document.body.appendChild(modal);
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
    
    // Restore body scroll when modal closes
    modal.addEventListener('animationend', (e) => {
        if (e.animationName === 'fadeOut') {
            document.body.style.overflow = 'auto';
        }
    });
}