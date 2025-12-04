// Login form functionality
document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.getElementById('loginForm');
  const email = document.getElementById('email');
  const password = document.getElementById('password');
  const togglePassword = document.getElementById('togglePassword');
  const rememberMe = document.getElementById('remember');

  // Prevent autofill
  const allInputs = document.querySelectorAll('input[type="email"], input[type="password"]');
  allInputs.forEach(input => {
    input.setAttribute('readonly', 'readonly');
    setTimeout(() => {
      input.removeAttribute('readonly');
    }, 500);
  });

  // Toggle password visibility
  togglePassword.addEventListener('click', function() {
    const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
    password.setAttribute('type', type);
    
    // Change icon
    this.textContent = type === 'password' ? '👁️' : '🙈';
  });

  // Email validation
  email.addEventListener('blur', function() {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(this.value)) {
      this.style.borderColor = '#ff4444';
    } else {
      this.style.borderColor = '#4CAF50';
    }
  });

  // Form submission - let Django handle it
  loginForm.addEventListener('submit', function(e) {
    // Basic validation only
    if (!email.value || !password.value) {
      e.preventDefault();
      alert('❌ Please fill in all fields!');
      return;
    }

    // Email validation
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email.value)) {
      e.preventDefault();
      alert('❌ Please enter a valid email address!');
      email.focus();
      return;
    }

    // Let the form submit normally to Django
  });



  // Add animation to inputs
  const inputs = document.querySelectorAll('.input-wrapper input');
  inputs.forEach(input => {
    input.addEventListener('focus', function() {
      this.parentElement.parentElement.style.transform = 'scale(1.02)';
      this.parentElement.parentElement.style.transition = 'transform 0.2s ease';
    });

    input.addEventListener('blur', function() {
      this.parentElement.parentElement.style.transform = 'scale(1)';
    });
  });

  // Forgot password link
  const forgotPassword = document.querySelector('.forgot-password');
  forgotPassword.addEventListener('click', function(e) {
    e.preventDefault();
    alert('🔑 Password reset link will be sent to your email!');
  });
});
