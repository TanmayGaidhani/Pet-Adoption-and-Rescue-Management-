// Feature card interactions
document.addEventListener('DOMContentLoaded', function() {
  const featureCards = document.querySelectorAll('.feature-card');
  const featureBtns = document.querySelectorAll('.feature-btn');

  // Add hover sound effect simulation (visual feedback)
  featureCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.animation = 'none';
      setTimeout(() => {
        this.style.animation = '';
      }, 10);
    });
  });

  // Button click actions
  featureBtns.forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      const card = this.closest('.feature-card');
      const feature = card.getAttribute('data-feature');
      
      // Create ripple effect
      const ripple = document.createElement('span');
      ripple.classList.add('ripple');
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = e.clientX - rect.left - size/2 + 'px';
      ripple.style.top = e.clientY - rect.top - size/2 + 'px';
      this.appendChild(ripple);
      
      setTimeout(() => ripple.remove(), 600);
      
      // Show alert based on feature
      const messages = {
        'match': '🏠 Instant Match: Find your perfect pet companion now!',
        'community': '💝 Community Hub: Join our network of animal lovers!',
        'secure': '🔒 Trusted Network: Explore verified shelters near you!',
        'mobile': '📱 Always Connected: Download our mobile app!'
      };
      
      alert(messages[feature] || 'Feature coming soon!');
    });
  });

  // Smooth scroll for navigation
  document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href.startsWith('#')) {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });
});
