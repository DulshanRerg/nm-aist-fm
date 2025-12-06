// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    console.log('Nelson Mandela Radio - Hapa ni Nyumbani');
    
    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenuContent = document.querySelector('.ast-mobile-header-content');
    
    if (mobileMenuToggle && mobileMenuContent) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenuContent.classList.toggle('active');
            const icon = this.querySelector('i');
            if (icon) {
                if (mobileMenuContent.classList.contains('active')) {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-times');
                } else {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!mobileMenuToggle.contains(event.target) && !mobileMenuContent.contains(event.target)) {
                mobileMenuContent.classList.remove('active');
                const icon = mobileMenuToggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        });
    }
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#' || href.startsWith('#!')) return;
            
            e.preventDefault();
            const targetElement = document.querySelector(href);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                if (mobileMenuContent && mobileMenuContent.classList.contains('active')) {
                    mobileMenuContent.classList.remove('active');
                    const icon = mobileMenuToggle.querySelector('i');
                    if (icon) {
                        icon.classList.remove('fa-times');
                        icon.classList.add('fa-bars');
                    }
                }
            }
        });
    });
    
    // Form validation
    const contactForm = document.querySelector('.contact-form form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            let isValid = true;
            const inputs = this.querySelectorAll('input[required], textarea[required]');
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = 'red';
                } else {
                    input.style.borderColor = '';
                }
                
                if (input.type === 'email') {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(input.value)) {
                        isValid = false;
                        input.style.borderColor = 'red';
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields correctly.');
            }
        });
    }
    
    // Add active class to current menu item
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll('.main-header-menu .menu-item a');
    
    menuItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentPath || 
            (href !== '/' && currentPath.startsWith(href)) ||
            (currentPath === '/' && href === '/')) {
            item.parentElement.classList.add('current-menu-item');
        }
    });
    
    // Lazy loading images
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    }
    
    // Sticky header
    window.addEventListener('scroll', function() {
        const header = document.querySelector('.site-header');
        if (window.scrollY > 100) {
            header.classList.add('sticky');
            header.style.background = 'var(--ast-global-color-5)';
            header.style.padding = '15px 0';
            header.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
        } else {
            header.classList.remove('sticky');
            header.style.background = 'transparent';
            header.style.padding = '25px 0';
            header.style.boxShadow = 'none';
        }
    });
    
    // Social media share buttons
    document.querySelectorAll('.social-icon').forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.1)';
        });
        
        icon.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Initialize animations
    initAnimations();
});

function initAnimations() {
    // Simple scroll animations
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.elementor-invisible');
        const windowHeight = window.innerHeight;
        
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < windowHeight - elementVisible) {
                element.classList.add('animated');
            }
        });
    };
    
    // Initial check
    animateOnScroll();
    
    // Check on scroll
    window.addEventListener('scroll', animateOnScroll);
}

// Radio player functionality (if needed)
class RadioPlayer {
    constructor() {
        this.audio = null;
        this.isPlaying = false;
    }
    
    play(streamUrl) {
        if (!this.audio) {
            this.audio = new Audio(streamUrl);
        }
        
        if (this.isPlaying) {
            this.pause();
        } else {
            this.audio.play();
            this.isPlaying = true;
        }
    }
    
    pause() {
        if (this.audio) {
            this.audio.pause();
            this.isPlaying = false;
        }
    }
}

// Global radio player instance
window.radioPlayer = new RadioPlayer();