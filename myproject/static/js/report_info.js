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
            // Handle image path - use placeholder if no image
            const imageSrc = report.image_path ? `/media/${report.image_path}` : 
                `https://via.placeholder.com/350x250/f5576c/FFFFFF?text=${encodeURIComponent(report.animal_type || 'Animal')}`;
            
            return `
                <div class="report-card">
                    <img src="${imageSrc}" alt="${report.breed || 'Animal'}" class="report-image" 
                         onerror="this.src='https://via.placeholder.com/350x250/f5576c/FFFFFF?text=Animal'">
                    <div class="report-info">
                        <div class="report-header">
                            <span class="animal-type">${report.animal_type || 'Unknown'}</span>
                            <span class="urgency-badge urgency-${report.urgency || 'low'}">${(report.urgency || 'low').toUpperCase()}</span>
                        </div>
                        <div class="report-details">
                            <h3>${report.breed || 'Unknown Breed'}</h3>
                            <p><strong>Color:</strong> ${report.color || 'Not specified'}</p>
                            <p><strong>Gender:</strong> ${report.gender || 'Unknown'}</p>
                            <p><strong>Condition:</strong> ${report.condition || 'Not specified'}</p>
                            <p><strong>Date Found:</strong> ${formatDate(report.date_found)}</p>
                            ${report.special_marks ? `<p><strong>Special Marks:</strong> ${report.special_marks}</p>` : ''}
                            <p><strong>Description:</strong> ${report.description || 'No description'}</p>
                            <div class="report-location">
                                📍 ${report.location || 'Unknown'}, ${report.city || 'Unknown'}
                            </div>
                        </div>
                        <button class="contact-btn" onclick="contactReporter('${report.contact_name}', '${report.contact_phone}', '${report.contact_email}')">
                            Contact Reporter
                        </button>
                    </div>
                </div>
            `;
        }).join('');
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

});