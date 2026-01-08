document.addEventListener('DOMContentLoaded', function() {
    
    // Load found pets on page load
    loadFoundPets();

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
    const cityFilter = document.getElementById('cityFilter');
    
    animalTypeFilter.addEventListener('change', performSearch);
    cityFilter.addEventListener('change', performSearch);

    function loadFoundPets() {
        // Fetch real data from the API
        fetch('/api/found-pets/')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error:', data.error);
                    showError('Failed to load found pets');
                    return;
                }
                
                const pets = data.pets || [];
                displayPets(pets);
                populateCityFilter(pets);
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Failed to load found pets');
            });
    }

    function showError(message) {
        const petsGrid = document.getElementById('petsGrid');
        petsGrid.innerHTML = `
            <div class="loading-message">
                <p style="color: #f44336;">❌ ${message}</p>
            </div>
        `;
    }

    function displayPets(pets) {
        const petsGrid = document.getElementById('petsGrid');
        const noResults = document.getElementById('noResults');

        if (pets.length === 0) {
            petsGrid.innerHTML = '';
            noResults.style.display = 'block';
            return;
        }

        noResults.style.display = 'none';
        
        petsGrid.innerHTML = pets.map(pet => {
            const imageSrc = pet.image_path ? `/media/${pet.image_path}` : null;
            
            return `
                <div class="pet-card-compact">
                    <div class="pet-card-header">
                        <span class="pet-type-badge">${pet.animal_type || 'UNKNOWN'}</span>
                        <span class="pet-id">#${pet.id ? pet.id.substring(0, 6) : 'N/A'}</span>
                    </div>
                    
                    <div class="pet-image-container">
                        ${imageSrc 
                            ? `<img src="${imageSrc}" class="pet-image-compact" alt="${pet.breed || 'Pet'}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                               <div class="no-image-compact" style="display: none;">
                                   🔍<br><small>No Image</small>
                               </div>`
                            : `<div class="no-image-compact">
                                   🔍<br><small>No Image</small>
                               </div>`
                        }
                    </div>
                    
                    <div class="pet-content">
                        <h5 class="pet-title-compact">${pet.breed || 'Unknown Breed'}</h5>
                        <div class="pet-info-compact">
                            <div class="info-row-compact">
                                <span class="info-label-compact">Color:</span>
                                <span class="info-value-compact">${truncateText(pet.color || 'Unknown', 12)}</span>
                            </div>
                            <div class="info-row-compact">
                                <span class="info-label-compact">Gender:</span>
                                <span class="info-value-compact">${pet.gender || 'Unknown'}</span>
                            </div>
                            <div class="info-row-compact">
                                <span class="info-label-compact">Date:</span>
                                <span class="info-value-compact">${formatDate(pet.report_date)}</span>
                            </div>
                            <div class="info-row-compact">
                                <span class="info-label-compact">Condition:</span>
                                <span class="info-value-compact">${truncateText(pet.condition || 'Unknown', 10)}</span>
                            </div>
                            ${pet.special_marks ? `
                            <div class="info-row-compact">
                                <span class="info-label-compact">Marks:</span>
                                <span class="info-value-compact">${truncateText(pet.special_marks, 12)}</span>
                            </div>
                            ` : ''}
                        </div>
                        
                        <div class="pet-location-compact">
                            📍 ${truncateText(pet.location || 'Unknown', 15)}, ${truncateText(pet.city || 'Unknown', 10)}
                        </div>
                        
                        <div class="pet-actions-compact">
                            <button class="btn-contact-compact" onclick="contactFinder('${pet.contact_name}', '${pet.contact_phone}', '${pet.contact_email}')" title="Contact Finder">
                                📞 Contact
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

    function populateCityFilter(pets) {
        const cityFilter = document.getElementById('cityFilter');
        const cities = [...new Set(pets.map(pet => pet.city))];
        
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
        const city = cityFilter.value;

        // Show loading
        document.getElementById('petsGrid').innerHTML = `
            <div class="loading-message">
                <div class="loading-spinner"></div>
                <p>Searching...</p>
            </div>
        `;

        // Fetch and filter data
        fetch('/api/found-pets/')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError('Search failed');
                    return;
                }
                
                let pets = data.pets || [];
                
                // Apply filters
                if (searchTerm) {
                    pets = pets.filter(pet => 
                        (pet.breed && pet.breed.toLowerCase().includes(searchTerm)) ||
                        (pet.color && pet.color.toLowerCase().includes(searchTerm)) ||
                        (pet.location && pet.location.toLowerCase().includes(searchTerm)) ||
                        (pet.description && pet.description.toLowerCase().includes(searchTerm))
                    );
                }
                
                if (animalType) {
                    pets = pets.filter(pet => pet.animal_type === animalType);
                }
                
                if (city) {
                    pets = pets.filter(pet => pet.city === city);
                }
                
                displayPets(pets);
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Search failed');
            });
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    }

    // Make contactFinder function global
    window.contactFinder = function(name, phone, email) {
        const contactInfo = `Contact Information:\n\nName: ${name}\nPhone: ${phone}\nEmail: ${email || 'Not provided'}`;
        alert(contactInfo);
        // In real implementation, this could open a contact form or dial the number
    };

});