document.addEventListener('DOMContentLoaded', function () {

    // Max date = today
    const reportDateInput = document.getElementById('reportDate');
    if (reportDateInput) {
        reportDateInput.setAttribute('max', new Date().toISOString().split('T')[0]);
    }

    // Image preview
    const fileInput = document.getElementById('animalImage');
    const imagePreview = document.getElementById('imagePreview');
    const uploadDisplay = document.querySelector('.file-upload-display');

    fileInput.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (!file) return;
        if (file.size > 5 * 1024 * 1024) { alert('File size must be less than 5MB'); fileInput.value = ''; return; }
        if (!file.type.match('image.*')) { alert('Please upload an image file'); fileInput.value = ''; return; }
        const reader = new FileReader();
        reader.onload = function (e) {
            imagePreview.innerHTML = `<img src="${e.target.result}" alt="Animal Preview">`;
            imagePreview.classList.add('active');
            uploadDisplay.style.display = 'none';
        };
        reader.readAsDataURL(file);
    });

    // Enforce text-only on city/location/breed/color
    ['breed', 'color', 'city'].forEach(id => {
        const el = document.getElementById(id);
        if (el) enforceNameInput(el);
    });

    // Form submit validation
    document.getElementById('rescueForm').addEventListener('submit', function (e) {
        let valid = true;

        // Required selects & inputs
        ['reportType', 'animalType', 'ageEstimate', 'gender', 'condition', 'urgency'].forEach(id => {
            const el = document.getElementById(id);
            if (el && !validateRequired(el, el.previousElementSibling?.textContent)) valid = false;
        });

        ['color', 'location', 'city', 'description'].forEach(id => {
            const el = document.getElementById(id);
            if (el && !validateRequired(el, id)) valid = false;
        });

        // Date not in future
        const dateVal = document.getElementById('reportDate').value;
        if (!dateVal) {
            showError(document.getElementById('reportDate'), 'Report date is required');
            valid = false;
        } else if (new Date(dateVal) > new Date()) {
            showError(document.getElementById('reportDate'), 'Date cannot be in the future');
            valid = false;
        } else {
            clearError(document.getElementById('reportDate'));
        }

        if (!valid) {
            e.preventDefault();
            alert('Please fill in all required fields correctly');
        }
    });
});
