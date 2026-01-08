// ===== ADMIN ADOPTION MANAGEMENT JAVASCRIPT =====

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
    loadPets();
    loadAdoptionRequests();
});

// ===== TAB MANAGEMENT =====
function showTab(tabName) {
    // Remove active class from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab
    document.getElementById(tabName + 'TabBtn').classList.add('active');
    document.getElementById(tabName + 'Tab').classList.add('active');
    
    // Load data for the active tab
    if (tabName === 'pets') {
        loadPets();
    } else if (tabName === 'requests') {
        loadAdoptionRequests();
    }
}

// ===== MODAL MANAGEMENT =====
function showAddPetModal() {
    document.getElementById('addPetModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeAddPetModal() {
    document.getElementById('addPetModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    document.getElementById('addPetForm').reset();
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('addPetModal');
    if (event.target === modal) {
        closeAddPetModal();
    }
}

// ===== LOAD PETS =====
function loadPets() {
    const grid = document.getElementById('petsGrid');
    grid.innerHTML = '<div class="loading-message">Loading pets...</div>';
    
    fetch('/api/admin/adoption-pets/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                grid.innerHTML = '<div class="no-data">Error loading pets</div>';
                return;
            }
            
            displayPets(data.pets || []);
        })
        .catch(error => {
            console.error('Error loading pets:', error);
            grid.innerHTML = '<div class="no-data">Error loading pets</div>';
        });
}

function displayPets(pets) {
    const grid = document.getElementById('petsGrid');
    
    if (pets.length === 0) {
        grid.innerHTML = `
            <div class="no-data">
                <h3>No Pets Available</h3>
                <p>Click "Add New Pet for Adoption" to get started</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = pets.map(pet => {
        const imageSrc = pet.image_path 
            ? `/media/${pet.image_path}` 
            : null;
        
        const statusClass = `status-${pet.status.toLowerCase().replace(' ', '-')}`;
        
        return `
            <div class="pet-card-compact">
                <div class="pet-card-header">
                    <span class="pet-badge ${statusClass}">${pet.status}</span>
                    <span class="pet-id">#${pet.id.substring(0, 6)}</span>
                </div>
                
                <div class="pet-image-container">
                    ${imageSrc 
                        ? `<img src="${imageSrc}" class="pet-image-compact" alt="${pet.name}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                           <div class="no-image-compact" style="display: none;">
                               🐾<br><small>No Image</small>
                           </div>`
                        : `<div class="no-image-compact">
                               🐾<br><small>No Image</small>
                           </div>`
                    }
                </div>
                
                <div class="pet-content">
                    <h5 class="pet-title">${pet.name}</h5>
                    <div class="pet-info-compact">
                        <div class="info-row">
                            <span class="info-label">Type:</span>
                            <span class="info-value">${pet.animal_type}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Breed:</span>
                            <span class="info-value">${pet.breed || 'Mixed'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Age:</span>
                            <span class="info-value">${pet.age}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Gender:</span>
                            <span class="info-value">${pet.gender}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Fee:</span>
                            <span class="info-value">${pet.adoption_fee}</span>
                        </div>
                    </div>
                    
                    <div class="pet-actions-compact">
                        <button class="btn-edit-compact" onclick="editPet('${pet.id}')" title="Edit Pet">
                            ✏️
                        </button>
                        <button class="btn-delete-compact" onclick="deletePet('${pet.id}', '${pet.name}')" title="Delete Pet">
                            🗑️
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// ===== LOAD ADOPTION REQUESTS =====
function loadAdoptionRequests() {
    const grid = document.getElementById('requestsGrid');
    grid.innerHTML = '<div class="loading-message">Loading adoption requests...</div>';
    
    fetch('/api/admin/adoption-requests/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                grid.innerHTML = '<div class="no-data">Error loading requests</div>';
                return;
            }
            
            displayAdoptionRequests(data.requests || []);
        })
        .catch(error => {
            console.error('Error loading requests:', error);
            grid.innerHTML = '<div class="no-data">Error loading requests</div>';
        });
}

function displayAdoptionRequests(requests) {
    const grid = document.getElementById('requestsGrid');
    
    if (requests.length === 0) {
        grid.innerHTML = `
            <div class="no-data">
                <h3>No Pending Adoption Requests</h3>
                <p>All adoption requests have been processed</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = requests.map(request => {
        return `
            <div class="request-card">
                <div class="request-header">
                    <h3 class="request-title">Adoption Request</h3>
                    <span class="request-status status-${request.status}">${request.status}</span>
                </div>
                
                <div class="request-info">
                    <div class="info-row">
                        <span class="info-label">Pet:</span>
                        <span class="info-value">${request.pet_name}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Applicant:</span>
                        <span class="info-value">${request.applicant_name}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Email:</span>
                        <span class="info-value">${request.applicant_email}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Phone:</span>
                        <span class="info-value">${request.applicant_phone}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Housing:</span>
                        <span class="info-value">${request.housing_type}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Experience:</span>
                        <span class="info-value">${request.experience_with_pets}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Reason:</span>
                        <span class="info-value">${truncateText(request.reason_for_adoption, 50)}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Date:</span>
                        <span class="info-value">${request.created_at}</span>
                    </div>
                </div>
                
                <div class="request-actions">
                    <button class="btn-approve" onclick="approveAdoptionRequest('${request.id}')">
                        ✅ Approve
                    </button>
                    <button class="btn-reject" onclick="rejectAdoptionRequest('${request.id}')">
                        ❌ Reject
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// ===== ADD PET FORM SUBMISSION =====
document.getElementById('addPetForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const submitBtn = document.querySelector('.btn-submit');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.innerHTML = '<span class="btn-icon">⏳</span> Adding Pet...';
    submitBtn.disabled = true;
    
    fetch('/api/admin/add-adoption-pet/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Pet added for adoption successfully!');
            closeAddPetModal();
            loadPets(); // Reload pets list
        } else {
            alert('❌ Error: ' + (data.error || 'Failed to add pet'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('❌ Failed to add pet. Please try again.');
    })
    .finally(() => {
        // Reset button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
});

// ===== PET ACTIONS =====
function editPet(petId) {
    // TODO: Implement edit functionality
    alert('🚧 Edit functionality coming soon!');
}

function deletePet(petId, petName) {
    if (confirm(`Are you sure you want to delete "${petName}"? This action cannot be undone.`)) {
        // TODO: Implement delete functionality
        alert('🚧 Delete functionality coming soon!');
    }
}

// ===== ADOPTION REQUEST ACTIONS =====
function approveAdoptionRequest(requestId) {
    if (confirm('Are you sure you want to approve this adoption request?')) {
        processAdoptionRequest(requestId, 'approve');
    }
}

function rejectAdoptionRequest(requestId) {
    if (confirm('Are you sure you want to reject this adoption request?')) {
        processAdoptionRequest(requestId, 'reject');
    }
}

function processAdoptionRequest(requestId, action) {
    fetch('/api/admin/adoption-action/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            request_id: requestId,
            action: action
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`✅ ${data.message}`);
            loadAdoptionRequests(); // Reload requests
            loadPets(); // Reload pets (status might have changed)
        } else {
            alert('❌ Error: ' + (data.error || 'Failed to process request'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('❌ Failed to process request. Please try again.');
    });
}

// ===== UTILITY FUNCTIONS =====
function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
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