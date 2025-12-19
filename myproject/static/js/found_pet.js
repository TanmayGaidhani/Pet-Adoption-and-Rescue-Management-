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
            // Handle image path - use placeholder if no image
            const imageSrc = pet.image_path ? `/media/${pet.image_path}` : 
                `https://via.placeholder.com/300x250/4facfe/FFFFFF?text=${encodeURIComponent(pet.animal_type || 'Pet')}`;
            
            return `
                <div class="pet-card">
                    <img src="${imageSrc}" alt="${pet.breed || 'Pet'}" class="pet-image" 
                         onerror="this.src='https://via.placeholder.com/300x250/4facfe/FFFFFF?text=Pet'">
                    <div class="pet-info">
                        <div class="pet-header">
                            <span class="pet-type">${pet.animal_type || 'Unknown'}</span>
                        </div>
                        <div class="pet-details">
                            <h3>${pet.breed || 'Unknown Breed'}</h3>
                            <p><strong>Color:</strong> ${pet.color || 'Not specified'}</p>
                            <p><strong>Gender:</strong> ${pet.gender || 'Unknown'}</p>
                            <p><strong>Report Date:</strong> ${formatDate(pet.repo)}</p>
                            ${pet.special_marks ? `<p><strong>Special Marks:</strong> ${pet.special_marks}</p>` : ''}
                            <p><strong>Condition:</strong> ${pet.condition || 'Not specified'}</p>
                            <p><strong>Description:</strong> ${pet.description || 'No description'}</p>
                            <div class="pet-location">
                                📍 ${pet.location || 'Unknown'}, ${pet.city || 'Unknown'}
                            </div>
                        </div>
                        <button class="contact-btn" onclick="contactFinder('${pet.contact_name}', '${pet.contact_phone}', '${pet.contact_email}')">
                            Contact Finder
                        </button>
                    </div>
                </div>
            `;
        }).join('');
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