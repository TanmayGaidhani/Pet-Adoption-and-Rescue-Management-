// ===== SHARED FORM VALIDATION UTILITIES =====

function showError(input, message) {
    input.style.borderColor = '#f44336';
    let err = input.parentElement.querySelector('.val-error');
    if (!err) {
        err = document.createElement('small');
        err.className = 'val-error';
        err.style.cssText = 'color:#f44336;font-size:0.78rem;margin-top:3px;display:block';
        input.parentElement.appendChild(err);
    }
    err.textContent = message;
}

function clearError(input) {
    input.style.borderColor = '';
    const err = input.parentElement.querySelector('.val-error');
    if (err) err.remove();
}

// Only letters and spaces — no numbers
function validateName(input) {
    const val = input.value.trim();
    if (!val) { showError(input, 'This field is required'); return false; }
    if (!/^[a-zA-Z\s]+$/.test(val)) { showError(input, 'Name must contain only letters'); return false; }
    if (val.length < 2) { showError(input, 'Name must be at least 2 characters'); return false; }
    clearError(input); return true;
}

// Exactly 10 digits
function validatePhone(input) {
    const val = input.value.trim().replace(/\s/g, '');
    if (!val) { showError(input, 'Phone number is required'); return false; }
    if (!/^\d{10}$/.test(val)) { showError(input, 'Phone must be exactly 10 digits'); return false; }
    clearError(input); return true;
}

function validateEmail(input) {
    const val = input.value.trim();
    if (!val) { showError(input, 'Email is required'); return false; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) { showError(input, 'Enter a valid email address'); return false; }
    clearError(input); return true;
}

function validateRequired(input, label) {
    if (!input.value.trim()) { showError(input, `${label || 'This field'} is required`); return false; }
    clearError(input); return true;
}

function validatePassword(input) {
    const val = input.value;
    if (!val) { showError(input, 'Password is required'); return false; }
    if (val.length < 6) { showError(input, 'Password must be at least 6 characters'); return false; }
    clearError(input); return true;
}

// Block non-numeric input on phone fields live
function enforcePhoneInput(input) {
    input.addEventListener('input', function () {
        this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
    });
}

// Block numbers in name fields live
function enforceNameInput(input) {
    input.addEventListener('input', function () {
        this.value = this.value.replace(/[^a-zA-Z\s]/g, '');
    });
}
