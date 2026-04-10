// ===== ADOPTION PAGE JAVASCRIPT =====

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

// Global variables
let allPets = [];
let filteredPets = [];

// Load pets on page load
document.addEventListener('DOMContentLoaded', function() {
    loadAvailablePets();
});

// ===== LOAD AVAILABLE PETS =====
function loadAvailablePets() {
    const grid = document.getElementById('petsGrid');
    grid.innerHTML = '<div class="loading-message">Loading available pets...</div>';
    
    fetch('/api/adoption-pets/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                grid.innerHTML = '<div class="no-pets">Error loading pets</div>';
                return;
            }
            
            allPets = data.pets || [];
            filteredPets = [...allPets];
            displayPets(filteredPets);
        })
        .catch(error => {
            console.error('Error loading pets:', error);
            grid.innerHTML = '<div class="no-pets">Error loading pets</div>';
        });
}

// ===== DISPLAY PETS =====
function displayPets(pets) {
    const grid = document.getElementById('petsGrid');
    
    if (pets.length === 0) {
        grid.innerHTML = `
            <div class="no-pets">
                <h3>No Pets Available</h3>
                <p>Check back soon for new pets looking for homes!</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = pets.map(pet => {
        const imageSrc = pet.image_path 
            ? `/media/${pet.image_path}` 
            : null;
        
        // Create traits array
        const traits = [];
        if (pet.good_with_kids === 'Yes') traits.push('Good with Kids');
        if (pet.good_with_pets === 'Yes') traits.push('Good with Pets');
        if (pet.spayed_neutered === 'Yes') traits.push('Spayed/Neutered');
        if (pet.vaccination_status === 'Up to Date') traits.push('Vaccinated');
        
        return `
            <div class="pet-card-compact" data-type="${pet.animal_type}" data-size="${pet.size}" data-age="${pet.age}">
                <div class="pet-card-header">
                    <span class="pet-type-badge">${pet.animal_type.toUpperCase()}</span>
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
                    <h5 class="pet-title-compact">${pet.name}</h5>
                    <div class="pet-info-compact">
                        <div class="info-row-compact">
                            <span class="info-label-compact">Breed:</span>
                            <span class="info-value-compact">${truncateText(pet.breed || 'Mixed', 12)}</span>
                        </div>
                        <div class="info-row-compact">
                            <span class="info-label-compact">Age:</span>
                            <span class="info-value-compact">${pet.age}</span>
                        </div>
                        <div class="info-row-compact">
                            <span class="info-label-compact">Gender:</span>
                            <span class="info-value-compact">${pet.gender}</span>
                        </div>
                        <div class="info-row-compact">
                            <span class="info-label-compact">Size:</span>
                            <span class="info-value-compact">${pet.size}</span>
                        </div>
                        <div class="info-row-compact">
                            <span class="info-label-compact">Energy:</span>
                            <span class="info-value-compact">${pet.energy_level}</span>
                        </div>
                        <div class="info-row-compact">
                            <span class="info-label-compact">Fee:</span>
                            <span class="info-value-compact">${pet.adoption_fee}</span>
                        </div>
                    </div>
                    
                    ${traits.length > 0 ? `
                    <div class="pet-traits-compact">
                        ${traits.slice(0, 2).map(trait => `<span class="trait-badge-compact">${trait}</span>`).join('')}
                    </div>
                    ` : ''}
                    
                    <div class="pet-actions-compact">
                        <button class="btn-adopt-compact" onclick="openAdoptionModal('${pet.id}')" title="Adopt ${pet.name}">
                            adopt
                        </button>
                        <button class="btn-details-compact" onclick="showPetDetails('${pet.id}')" title="View Details">
                            Infoℹ️
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// ===== FILTERING FUNCTIONS =====
function filterPets() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const typeFilter = document.getElementById('typeFilter').value;
    const sizeFilter = document.getElementById('sizeFilter').value;
    const ageFilter = document.getElementById('ageFilter').value;
    
    filteredPets = allPets.filter(pet => {
        // Search filter
        const matchesSearch = !searchTerm || 
            pet.name.toLowerCase().includes(searchTerm) ||
            pet.breed.toLowerCase().includes(searchTerm) ||
            pet.animal_type.toLowerCase().includes(searchTerm) ||
            pet.description.toLowerCase().includes(searchTerm);
        
        // Type filter
        const matchesType = !typeFilter || pet.animal_type === typeFilter;
        
        // Size filter
        const matchesSize = !sizeFilter || pet.size === sizeFilter;
        
        // Age filter (simplified)
        let matchesAge = true;
        if (ageFilter) {
            const age = pet.age.toLowerCase();
            switch (ageFilter) {
                case 'puppy':
                    matchesAge = age.includes('puppy') || age.includes('kitten') || age.includes('young');
                    break;
                case 'young':
                    matchesAge = age.includes('young') || age.includes('1') || age.includes('2');
                    break;
                case 'adult':
                    matchesAge = age.includes('adult') || age.includes('3') || age.includes('4') || age.includes('5');
                    break;
                case 'senior':
                    matchesAge = age.includes('senior') || age.includes('6') || age.includes('7') || age.includes('8');
                    break;
            }
        }
        
        return matchesSearch && matchesType && matchesSize && matchesAge;
    });
    
    displayPets(filteredPets);
}

function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('sizeFilter').value = '';
    document.getElementById('ageFilter').value = '';
    
    filteredPets = [...allPets];
    displayPets(filteredPets);
}

// ===== ADOPTION MODAL =====
function openAdoptionModal(petId) {
    const pet = allPets.find(p => p.id === petId);
    if (!pet) return;
    
    // Set pet ID in form
    document.getElementById('petId').value = petId;
    
    // Update pet preview
    const preview = document.getElementById('petPreview');
    preview.innerHTML = `
        <h3>🐾 ${pet.name}</h3>
        <p><strong>${pet.animal_type}</strong> • ${pet.breed || 'Mixed'} • ${pet.age} • ${pet.gender}</p>
        <p><strong>Adoption Fee:</strong> ${pet.adoption_fee}</p>
        <p>${pet.description}</p>
    `;
    
    // Show modal
    document.getElementById('adoptionModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeAdoptionModal() {
    document.getElementById('adoptionModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    document.getElementById('adoptionForm').reset();
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('adoptionModal');
    if (event.target === modal) {
        closeAdoptionModal();
    }
}

// ===== PET DETAILS =====
function showPetDetails(petId) {
    const pet = allPets.find(p => p.id === petId);
    if (!pet) return;
    
    let details = `🐾 ${pet.name} - Detailed Information\n\n`;
    details += `Type: ${pet.animal_type}\n`;
    details += `Breed: ${pet.breed || 'Mixed'}\n`;
    details += `Age: ${pet.age}\n`;
    details += `Gender: ${pet.gender}\n`;
    details += `Size: ${pet.size}\n`;
    details += `Color: ${pet.color || 'Not specified'}\n\n`;
    
    details += `Health & Behavior:\n`;
    details += `Health Status: ${pet.health_status}\n`;
    details += `Vaccination Status: ${pet.vaccination_status}\n`;
    details += `Spayed/Neutered: ${pet.spayed_neutered}\n`;
    details += `Good with Kids: ${pet.good_with_kids}\n`;
    details += `Good with Other Pets: ${pet.good_with_pets}\n`;
    details += `Energy Level: ${pet.energy_level}\n\n`;
    
    if (pet.personality) {
        details += `Personality: ${pet.personality}\n\n`;
    }
    
    details += `Description: ${pet.description}\n\n`;
    
    if (pet.special_needs) {
        details += `Special Needs: ${pet.special_needs}\n\n`;
    }
    
    details += `Adoption Fee: ${pet.adoption_fee}\n`;
    details += `Contact: ${pet.contact_info}`;
    
    alert(details);
}

// ===== ADOPTION FORM SUBMISSION =====
document.getElementById('adoptionForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // Validate address
    const address = document.getElementById('address');
    if (!validateRequired(address, 'Address')) { address.focus(); return; }

    // Validate reason
    const reason = document.getElementById('reasonForAdoption');
    if (!validateRequired(reason, 'Reason for adoption')) { reason.focus(); return; }

    const formData = new FormData(this);
    const submitBtn = document.querySelector('.btn-submit');
    const originalText = submitBtn.innerHTML;
    
    // Convert FormData to JSON
    const data = {};
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    // Show loading state
    submitBtn.innerHTML = '<span class="btn-icon">⏳</span> Submitting Application...';
    submitBtn.disabled = true;
    
    fetch('/api/adoption-request/', {
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
            alert('🎉 ' + data.message);
            closeAdoptionModal();
        } else {
            alert('❌ Error: ' + (data.error || 'Failed to submit application'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('❌ Failed to submit application. Please try again.');
    })
    .finally(() => {
        // Reset button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
});

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