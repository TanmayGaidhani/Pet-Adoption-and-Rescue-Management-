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

// Auto-fill demo credentials if coming from Try Demo button
window.addEventListener('DOMContentLoaded', function() {
    const demoEmail = sessionStorage.getItem('demo_email');
    const demoPass = sessionStorage.getItem('demo_password');
    if (demoEmail && demoPass) {
        setTimeout(() => {
            fillField('email', demoEmail);
            fillField('password', demoPass);
            sessionStorage.removeItem('demo_email');
            sessionStorage.removeItem('demo_password');
        }, 600);
    }
});

// ===== DEMO CREDENTIALS FUNCTIONS =====

function fillField(fieldId, value, cardElement) {
  const input = document.getElementById(fieldId);
  if (!input) return;

  input.removeAttribute('readonly');
  input.value = value;
  input.style.borderColor = '#4CAF50';
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));

  // Animation pulse effect on input
  input.classList.remove('highlight-pulse');
  void input.offsetWidth; // Force DOM reflow to re-trigger CSS keyframe
  input.classList.add('highlight-pulse');
  setTimeout(() => input.classList.remove('highlight-pulse'), 800);

  // Button feedback on the clicked card
  if (cardElement) {
    const btn = cardElement.querySelector('.demo-copy-btn');
    if (btn) {
      const originalText = btn.textContent;
      btn.textContent = '✓ Filled';
      btn.classList.add('filled');
      setTimeout(() => {
        btn.textContent = originalText;
        btn.classList.remove('filled');
      }, 1200);
    }
  }
}

function copyValue(event, text, btn) {
  if (event) {
    event.stopPropagation();
  }
  const originalText = btn.textContent;

  function onCopied() {
    btn.textContent = '✓ Copied';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = originalText;
      btn.classList.remove('copied');
    }, 1500);
  }

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(onCopied).catch(() => {
      fallbackCopy(text);
      onCopied();
    });
  } else {
    fallbackCopy(text);
    onCopied();
  }
}

function fallbackCopy(text) {
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.select();
  try {
    document.execCommand('copy');
  } catch (err) {}
  document.body.removeChild(ta);
}

function quickFillAll(emailVal, passVal, btn) {
  fillField('email', emailVal);
  fillField('password', passVal);

  if (btn) {
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span>✓ Applied!</span>';
    btn.classList.add('quick-filled');
    setTimeout(() => {
      btn.innerHTML = originalText;
      btn.classList.remove('quick-filled');
    }, 1400);
  }
}

