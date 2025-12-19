document.addEventListener('DOMContentLoaded', function() {
    
    // Set max date to today for report date
    const reportDateInput = document.getElementById('reportDate');
    if (reportDateInput) {
        const today = new Date().toISOString().split('T')[0];
        reportDateInput.setAttribute('max', today);
    }

    // Image preview functionality
    const fileInput = document.getElementById('animalImage');
    const imagePreview = document.getElementById('imagePreview');
    const uploadDisplay = document.querySelector('.file-upload-display');

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        
        if (file) {
            // Check file size (5MB max)
            if (file.size > 5 * 1024 * 1024) {
                alert('❌ File size must be less than 5MB');
                fileInput.value = '';
                return;
            }

            // Check file type
            if (!file.type.match('image.*')) {
                alert('❌ Please upload an image file');
                fileInput.value = '';
                return;
            }

            // Show preview
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.innerHTML = `<img src="${e.target.result}" alt="Animal Preview">`;
                imagePreview.classList.add('active');
                uploadDisplay.style.display = 'none';
            };
            reader.readAsDataURL(file);
        }
    });

    // Form validation
    const form = document.getElementById('rescueForm');
    
    form.addEventListener('submit', function(e) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.style.borderColor = '#f44336';
            } else {
                field.style.borderColor = '#e0e0e0';
            }
        });

        if (!isValid) {
            e.preventDefault();
            alert('❌ Please fill in all required fields');
            return;
        }

        // Phone validation
        const phone = document.getElementById('contactPhone').value;
        const phonePattern = /^[\d\s\+\-\(\)]+$/;
        if (!phonePattern.test(phone)) {
            e.preventDefault();
            alert('❌ Please enter a valid phone number');
            document.getElementById('contactPhone').focus();
            return;
        }

        // Email validation
        const email = document.getElementById('contactEmail').value;
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(email)) {
            e.preventDefault();
            alert('❌ Please enter a valid email address');
            document.getElementById('contactEmail').focus();
            return;
        }

        // Date validation
        const reportDate = new Date(document.getElementById('reportDate').value);
        const currentDate = new Date();
        if (reportDate > currentDate) {
            e.preventDefault();
            alert('❌ Report date cannot be in the future');
            document.getElementById('reportDate').focus();
            return;
        }
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });

    // Prevent autofill
    const allInputs = document.querySelectorAll('input, select, textarea');
    allInputs.forEach(input => {
        input.setAttribute('readonly', 'readonly');
        setTimeout(() => {
            input.removeAttribute('readonly');
        }, 500);
    });

});
