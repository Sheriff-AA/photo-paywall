/* ===========================================
   DotNetLenses Photography - Main JavaScript
   =========================================== */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initMobileMenu();
    initHeroSlider();
    initScrollAnimations();
    initFilterButtons();
    initLightbox();
});

/* ===========================================
   Mobile Menu Toggle
   =========================================== */

function initMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            
            // Animate menu icon
            const icon = this.querySelector('svg');
            if (mobileMenu.classList.contains('hidden')) {
                icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>';
            } else {
                icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>';
            }
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!mobileMenuBtn.contains(event.target) && !mobileMenu.contains(event.target)) {
                mobileMenu.classList.add('hidden');
                const icon = mobileMenuBtn.querySelector('svg');
                icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>';
            }
        });
        
        // Close menu on link click
        const mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenu.classList.add('hidden');
                const icon = mobileMenuBtn.querySelector('svg');
                icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>';
            });
        });
    }
}

/* ===========================================
   Hero Image Slider
   =========================================== */

function initHeroSlider() {
    const heroSlides = document.querySelectorAll('.hero-slide');
    
    if (heroSlides.length > 1) {
        let currentSlide = 0;
        
        function showSlide(index) {
            heroSlides.forEach((slide, i) => {
                if (i === index) {
                    slide.style.opacity = '1';
                    slide.classList.add('active');
                } else {
                    slide.style.opacity = '0';
                    slide.classList.remove('active');
                }
            });
        }
        
        function nextSlide() {
            currentSlide = (currentSlide + 1) % heroSlides.length;
            showSlide(currentSlide);
        }
        
        // Auto-advance slides every 5 seconds
        setInterval(nextSlide, 5000);
    }
}

/* ===========================================
   Scroll Animations
   =========================================== */

function initScrollAnimations() {
    // Fade in elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe collection cards and sections
    const animatedElements = document.querySelectorAll('.collection-card, .collection-item, .section-title');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    // Navbar background on scroll
    const nav = document.querySelector('nav');
    if (nav) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 100) {
                nav.style.background = 'rgba(3, 7, 18, 0.95)';
            } else {
                nav.style.background = 'rgba(3, 7, 18, 0.8)';
            }
        });
    }
}

/* ===========================================
   Filter Buttons (Collections Page)
   =========================================== */

function initFilterButtons() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            filterButtons.forEach(btn => {
                btn.classList.remove('active', 'bg-amber-500', 'text-white');
                btn.classList.add('bg-gray-800', 'text-gray-300');
            });
            
            // Add active class to clicked button
            this.classList.add('active', 'bg-amber-500', 'text-white');
            this.classList.remove('bg-gray-800', 'text-gray-300');
            
            // Here you would typically filter the collections
            // For now, this is just visual feedback
            const category = this.textContent.trim().toLowerCase();
            filterCollections(category);
        });
    });
}

function filterCollections(category) {
    const collections = document.querySelectorAll('.collection-item');
    
    collections.forEach(collection => {
        if (category === 'all') {
            collection.style.display = 'block';
            setTimeout(() => {
                collection.style.opacity = '1';
                collection.style.transform = 'translateY(0)';
            }, 10);
        } else {
            // This would need to check against actual data attributes
            // For demo purposes, showing all
            collection.style.display = 'block';
            setTimeout(() => {
                collection.style.opacity = '1';
                collection.style.transform = 'translateY(0)';
            }, 10);
        }
    });
}

/* ===========================================
   Lightbox Gallery (Detail Page)
   =========================================== */

let currentImageIndex = 0;
let galleryImages = [];

function initLightbox() {
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    if (galleryItems.length > 0) {
        galleryImages = Array.from(galleryItems).map(item => item.dataset.image);
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            const lightbox = document.getElementById('lightbox');
            if (lightbox && lightbox.classList.contains('active')) {
                if (e.key === 'Escape') {
                    closeLightbox();
                } else if (e.key === 'ArrowLeft') {
                    previousImage();
                } else if (e.key === 'ArrowRight') {
                    nextImage();
                }
            }
        });
        
        // Close on background click
        const lightbox = document.getElementById('lightbox');
        if (lightbox) {
            lightbox.addEventListener('click', function(e) {
                if (e.target === lightbox) {
                    closeLightbox();
                }
            });
        }
    }
}

function openLightbox(index) {
    currentImageIndex = index;
    const lightbox = document.getElementById('lightbox');
    const lightboxImage = document.getElementById('lightboxImage');
    const lightboxCounter = document.getElementById('lightboxCounter');
    
    if (lightbox && lightboxImage && galleryImages.length > 0) {
        lightboxImage.src = galleryImages[index];
        lightboxCounter.textContent = `${index + 1} / ${galleryImages.length}`;
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeLightbox() {
    const lightbox = document.getElementById('lightbox');
    if (lightbox) {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function nextImage() {
    currentImageIndex = (currentImageIndex + 1) % galleryImages.length;
    updateLightboxImage();
}

function previousImage() {
    currentImageIndex = (currentImageIndex - 1 + galleryImages.length) % galleryImages.length;
    updateLightboxImage();
}

function updateLightboxImage() {
    const lightboxImage = document.getElementById('lightboxImage');
    const lightboxCounter = document.getElementById('lightboxCounter');
    
    if (lightboxImage && lightboxCounter) {
        // Fade out
        lightboxImage.style.opacity = '0';
        
        setTimeout(() => {
            lightboxImage.src = galleryImages[currentImageIndex];
            lightboxCounter.textContent = `${currentImageIndex + 1} / ${galleryImages.length}`;
            
            // Fade in
            lightboxImage.style.opacity = '1';
        }, 150);
    }
}

/* ===========================================
   Smooth Scroll for Anchor Links
   =========================================== */

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#' && href !== '') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

/* ===========================================
   Image Lazy Loading Helper
   =========================================== */

function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading if needed
if (document.querySelectorAll('img[data-src]').length > 0) {
    lazyLoadImages();
}

/* ===========================================
   Form Validation (Newsletter, Contact)
   =========================================== */

function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const emailInput = this.querySelector('input[type="email"]');
            
            if (emailInput && !validateEmail(emailInput.value)) {
                e.preventDefault();
                showFormError(emailInput, 'Please enter a valid email address');
            }
        });
    });
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showFormError(input, message) {
    // Remove any existing error
    const existingError = input.parentElement.querySelector('.form-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error text-red-500 text-sm mt-2';
    errorDiv.textContent = message;
    input.parentElement.appendChild(errorDiv);
    
    // Add error styling to input
    input.classList.add('border-red-500');
    
    // Remove error on input
    input.addEventListener('input', function() {
        this.classList.remove('border-red-500');
        const error = this.parentElement.querySelector('.form-error');
        if (error) {
            error.remove();
        }
    }, { once: true });
}

// Initialize form validation
initFormValidation();

/* ===========================================
   Search Functionality (Collections Page)
   =========================================== */

function initSearch() {
    const searchInput = document.querySelector('input[type="text"][placeholder*="Search"]');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const searchTerm = this.value.toLowerCase();
            
            searchTimeout = setTimeout(() => {
                searchCollections(searchTerm);
            }, 300); // Debounce search
        });
    }
}

function searchCollections(term) {
    const collections = document.querySelectorAll('.collection-item');
    let visibleCount = 0;
    
    collections.forEach(collection => {
        const title = collection.querySelector('h3');
        if (title) {
            const titleText = title.textContent.toLowerCase();
            
            if (titleText.includes(term) || term === '') {
                collection.style.display = 'block';
                setTimeout(() => {
                    collection.style.opacity = '1';
                    collection.style.transform = 'translateY(0)';
                }, 10);
                visibleCount++;
            } else {
                collection.style.opacity = '0';
                collection.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    collection.style.display = 'none';
                }, 300);
            }
        }
    });
    
    // Update results count if exists
    const resultsCount = document.querySelector('.text-gray-400 .text-amber-400');
    if (resultsCount) {
        resultsCount.textContent = visibleCount;
    }
}

// Initialize search
initSearch();

/* ===========================================
   Touch Swipe for Mobile Gallery
   =========================================== */

function initTouchSwipe() {
    const lightbox = document.getElementById('lightbox');
    
    if (lightbox) {
        let touchStartX = 0;
        let touchEndX = 0;
        
        lightbox.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        lightbox.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });
        
        function handleSwipe() {
            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;
            
            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
                    // Swipe left - next image
                    nextImage();
                } else {
                    // Swipe right - previous image
                    previousImage();
                }
            }
        }
    }
}

// Initialize touch swipe
initTouchSwipe();

/* ===========================================
   Performance Optimization - Image Preloading
   =========================================== */

function preloadAdjacentImages() {
    if (galleryImages.length > 0 && currentImageIndex >= 0) {
        const nextIndex = (currentImageIndex + 1) % galleryImages.length;
        const prevIndex = (currentImageIndex - 1 + galleryImages.length) % galleryImages.length;
        
        // Preload next and previous images
        [nextIndex, prevIndex].forEach(index => {
            const img = new Image();
            img.src = galleryImages[index];
        });
    }
}

/* ===========================================
   Loading State Management
   =========================================== */

function showLoadingState(element) {
    if (element) {
        element.classList.add('loading-skeleton');
    }
}

function hideLoadingState(element) {
    if (element) {
        element.classList.remove('loading-skeleton');
    }
}

// /* ===========================================
//    Add to Cart Functionality (Basic)
//    =========================================== */

// function initAddToCart() {
//     const addToCartButtons = document.querySelectorAll('button:contains("Add to Cart")');
    
//     addToCartButtons.forEach(button => {
//         button.addEventListener('click', function(e) {
//             e.preventDefault();
            
//             // Show feedback
//             const originalText = this.textContent;
//             this.textContent = 'Added! ✓';
//             this.classList.add('bg-green-500');
            
//             setTimeout(() => {
//                 this.textContent = originalText;
//                 this.classList.remove('bg-green-500');
//             }, 2000);
            
//             // Here you would typically send data to backend
//             console.log('Item added to cart');
//         });
//     });
// }

// // Initialize add to cart
// initAddToCart();

/* ===========================================
   Sort Functionality (Collections Page)
   =========================================== */

function initSort() {
    const sortSelect = document.querySelector('select');
    
    if (sortSelect && sortSelect.options[0] && sortSelect.options[0].text.includes('Latest')) {
        sortSelect.addEventListener('change', function() {
            const sortValue = this.value;
            sortCollections(sortValue);
        });
    }
}

function sortCollections(sortBy) {
    const container = document.querySelector('.grid.grid-cols-1');
    if (!container) return;
    
    const collections = Array.from(container.querySelectorAll('.collection-item'));
    
    collections.sort((a, b) => {
        // This is a basic example - you'd need actual data attributes
        // to sort properly in a real implementation
        switch(sortBy) {
            case 'Latest First':
                return 0; // Keep original order
            case 'Oldest First':
                return 0; // Would reverse
            default:
                return 0;
        }
    });
    
    // Re-append in new order
    collections.forEach(collection => {
        container.appendChild(collection);
    });
}

// Initialize sort
initSort();

/* ===========================================
   Analytics Tracking (Placeholder)
   =========================================== */

function trackEvent(eventName, eventData) {
    // This is where you'd integrate with analytics
    // e.g., Google Analytics, Mixpanel, etc.
    console.log('Event tracked:', eventName, eventData);
}

// Track page views
trackEvent('page_view', {
    page: window.location.pathname
});

// Track collection views
const collectionCards = document.querySelectorAll('.collection-item');
collectionCards.forEach(card => {
    card.addEventListener('click', function() {
        const title = this.querySelector('h3');
        if (title) {
            trackEvent('collection_viewed', {
                collection_name: title.textContent
            });
        }
    });
});

/* ===========================================
   Utility Functions
   =========================================== */

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function for scroll events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/* ===========================================
   Error Handling
   =========================================== */

window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.message);
    // You could send this to your error tracking service
});

/* ===========================================
   Console Welcome Message
   =========================================== */

console.log('%c🎨 DotNetLenses Photography', 'color: #fbbf24; font-size: 24px; font-weight: bold;');
console.log('%cBuilt with Django + Tailwind CSS', 'color: #9ca3af; font-size: 14px;');
console.log('%cCapturing moments, creating memories ✨', 'color: #f97316; font-size: 14px;');


/* ===========================================
   Purchase Modal Functions
   =========================================== */

function openPurchaseModal() {
    const modal = document.getElementById('purchaseModal');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closePurchaseModal() {
    const modal = document.getElementById('purchaseModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Close modal on background click
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('purchaseModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closePurchaseModal();
            }
        });
    }
    
    // Close modal on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closePurchaseModal();
        }
    });
    
    // Form submission handling
    const purchaseForm = document.getElementById('purchaseForm');
    if (purchaseForm) {
        purchaseForm.addEventListener('submit', function(e) {
            // Add loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<svg class="animate-spin h-5 w-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';
            }
        });
    }
});

/* ===========================================
   Carousel Functions
   =========================================== */

let currentSlideIndex = 0;
let carouselInterval;
const CAROUSEL_AUTO_PLAY_INTERVAL = 5000;

function initCarousel() {
    const carousel = document.getElementById('workCarousel');
    if (!carousel) return;
    
    const slides = carousel.querySelectorAll('.carousel-slide');
    if (slides.length === 0) return;
    
    const dotsContainer = document.getElementById('carouselDots');
    const prevBtn = document.getElementById('prevSlide');
    const nextBtn = document.getElementById('nextSlide');
    
    // Create dots
    if (dotsContainer) {
        slides.forEach((_, index) => {
            const dot = document.createElement('button');
            dot.className = `carousel-dot ${index === 0 ? 'active' : ''}`;
            dot.addEventListener('click', () => goToSlide(index));
            dotsContainer.appendChild(dot);
        });
    }
    
    // Navigation buttons
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            changeSlide(-1);
            resetAutoPlay();
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            changeSlide(1);
            resetAutoPlay();
        });
    }
    
    // Start auto-play
    startAutoPlay();
    
    // Pause on hover
    carousel.addEventListener('mouseenter', stopAutoPlay);
    carousel.addEventListener('mouseleave', startAutoPlay);
}

function changeSlide(direction) {
    const carousel = document.getElementById('workCarousel');
    if (!carousel) return;
    
    const slides = carousel.querySelectorAll('.carousel-slide');
    currentSlideIndex = (currentSlideIndex + direction + slides.length) % slides.length;
    updateCarousel();
}

function goToSlide(index) {
    currentSlideIndex = index;
    updateCarousel();
    resetAutoPlay();
}

function updateCarousel() {
    const carousel = document.getElementById('workCarousel');
    if (!carousel) return;
    
    const slides = carousel.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.carousel-dot');
    
    carousel.style.transform = `translateX(-${currentSlideIndex * 100}%)`;
    
    // Update dots
    dots.forEach((dot, index) => {
        if (index === currentSlideIndex) {
            dot.classList.add('active');
        } else {
            dot.classList.remove('active');
        }
    });
}

function startAutoPlay() {
    stopAutoPlay();
    carouselInterval = setInterval(() => {
        changeSlide(1);
    }, CAROUSEL_AUTO_PLAY_INTERVAL);
}

function stopAutoPlay() {
    if (carouselInterval) {
        clearInterval(carouselInterval);
    }
}

function resetAutoPlay() {
    stopAutoPlay();
    startAutoPlay();
}

// Initialize carousel when DOM is ready
document.addEventListener('DOMContentLoaded', initCarousel);

/* ===========================================
   Gallery Filter Functions
   =========================================== */

function initGalleryFilters() {
    const filterButtons = document.querySelectorAll('.gallery-filter-btn');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.dataset.filter;
            
            // Update active button
            filterButtons.forEach(btn => {
                btn.classList.remove('active', 'bg-amber-500', 'text-white');
                btn.classList.add('bg-gray-800', 'text-gray-300');
            });
            this.classList.add('active', 'bg-amber-500', 'text-white');
            this.classList.remove('bg-gray-800', 'text-gray-300');
            
            // Filter gallery items
            filterGallery(filter);
        });
    });
}

function filterGallery(category) {
    const items = document.querySelectorAll('.gallery-grid-item');
    
    items.forEach(item => {
        const itemCategory = item.dataset.category;
        
        if (category === 'all' || itemCategory === category) {
            item.classList.remove('hiding');
            item.classList.add('showing');
            setTimeout(() => {
                item.style.display = 'block';
                item.classList.remove('showing');
            }, 300);
        } else {
            item.classList.add('hiding');
            setTimeout(() => {
                item.style.display = 'none';
                item.classList.remove('hiding');
            }, 300);
        }
    });
}

// Initialize gallery filters
document.addEventListener('DOMContentLoaded', initGalleryFilters);

/* ===========================================
   Gallery Lightbox Functions
   =========================================== */

let currentGalleryImageIndex = 0;
let galleryLightboxImages = [];

function initGalleryLightbox() {
    const galleryItems = document.querySelectorAll('.gallery-grid-item');
    
    if (galleryItems.length > 0) {
        galleryLightboxImages = Array.from(galleryItems).map(item => {
            const img = item.querySelector('img');
            return img ? img.src : '';
        }).filter(src => src !== '');
        
        // Keyboard navigation for gallery lightbox
        document.addEventListener('keydown', function(e) {
            const lightbox = document.getElementById('galleryLightbox');
            if (lightbox && lightbox.classList.contains('active')) {
                if (e.key === 'Escape') {
                    closeGalleryLightbox();
                } else if (e.key === 'ArrowLeft') {
                    previousGalleryImage();
                } else if (e.key === 'ArrowRight') {
                    nextGalleryImage();
                }
            }
        });
        
        // Close on background click
        const galleryLightbox = document.getElementById('galleryLightbox');
        if (galleryLightbox) {
            galleryLightbox.addEventListener('click', function(e) {
                if (e.target === galleryLightbox) {
                    closeGalleryLightbox();
                }
            });
        }
    }
}

function openGalleryLightbox(index) {
    currentGalleryImageIndex = index;
    const lightbox = document.getElementById('galleryLightbox');
    const lightboxImage = document.getElementById('galleryLightboxImage');
    const lightboxCounter = document.getElementById('galleryLightboxCounter');
    
    if (lightbox && lightboxImage && galleryLightboxImages.length > 0) {
        lightboxImage.src = galleryLightboxImages[index];
        lightboxCounter.textContent = `${index + 1} / ${galleryLightboxImages.length}`;
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeGalleryLightbox() {
    const lightbox = document.getElementById('galleryLightbox');
    if (lightbox) {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function nextGalleryImage() {
    currentGalleryImageIndex = (currentGalleryImageIndex + 1) % galleryLightboxImages.length;
    updateGalleryLightboxImage();
}

function previousGalleryImage() {
    currentGalleryImageIndex = (currentGalleryImageIndex - 1 + galleryLightboxImages.length) % galleryLightboxImages.length;
    updateGalleryLightboxImage();
}

function updateGalleryLightboxImage() {
    const lightboxImage = document.getElementById('galleryLightboxImage');
    const lightboxCounter = document.getElementById('galleryLightboxCounter');
    
    if (lightboxImage && lightboxCounter) {
        lightboxImage.style.opacity = '0';
        
        setTimeout(() => {
            lightboxImage.src = galleryLightboxImages[currentGalleryImageIndex];
            lightboxCounter.textContent = `${currentGalleryImageIndex + 1} / ${galleryLightboxImages.length}`;
            lightboxImage.style.opacity = '1';
        }, 150);
    }
}

// Initialize gallery lightbox
document.addEventListener('DOMContentLoaded', initGalleryLightbox);

/* ===========================================
   Downloads Page Functions
   =========================================== */

function selectAll() {
    const checkboxes = document.querySelectorAll('.photo-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
}

function deselectAll() {
    const checkboxes = document.querySelectorAll('.photo-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
}

function downloadSelected() {
    const checkboxes = document.querySelectorAll('.photo-checkbox:checked');
    
    if (checkboxes.length === 0) {
        alert('Please select at least one photo to download');
        return;
    }
    
    // Create download links for each selected photo
    checkboxes.forEach((checkbox, index) => {
        const url = checkbox.dataset.photoUrl;
        if (url) {
            setTimeout(() => {
                const link = document.createElement('a');
                link.href = url;
                link.download = '';
                link.click();
            }, index * 500); // Stagger downloads
        }
    });
}

/* ===========================================
   Contact Form Functions
   =========================================== */

function initContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic validation
            const email = this.querySelector('input[type="email"]');
            const message = this.querySelector('textarea[name="message"]');
            
            if (!email.value || !message.value) {
                alert('Please fill in all required fields');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Sending...';
            
            // Simulate form submission (replace with actual AJAX call)
            setTimeout(() => {
                // Show success message
                const successMessage = document.getElementById('formSuccessMessage');
                if (successMessage) {
                    successMessage.classList.remove('hidden');
                }
                
                // Reset form
                this.reset();
                
                // Reset button
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
                
                // Hide success message after 5 seconds
                setTimeout(() => {
                    if (successMessage) {
                        successMessage.classList.add('hidden');
                    }
                }, 5000);
            }, 1500);
        });
    }
}

// Initialize contact form
document.addEventListener('DOMContentLoaded', initContactForm);

/* ===========================================
   FAQ Accordion Functions
   =========================================== */

function initFAQAccordion() {
    const faqQuestions = document.querySelectorAll('.faq-question');
    
    faqQuestions.forEach(question => {
        question.addEventListener('click', function() {
            const answer = this.nextElementSibling;
            const isActive = this.classList.contains('active');
            
            // Close all other FAQs
            faqQuestions.forEach(q => {
                q.classList.remove('active');
                const a = q.nextElementSibling;
                if (a) {
                    a.classList.remove('active');
                }
            });
            
            // Toggle current FAQ
            if (!isActive) {
                this.classList.add('active');
                if (answer) {
                    answer.classList.add('active');
                }
            }
        });
    });
}

// Initialize FAQ accordion
document.addEventListener('DOMContentLoaded', initFAQAccordion);

/* ===========================================
   Touch Swipe for Carousel (Mobile)
   =========================================== */

function initCarouselTouchSwipe() {
    const carousel = document.getElementById('workCarousel');
    
    if (carousel) {
        let touchStartX = 0;
        let touchEndX = 0;
        
        carousel.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        carousel.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            handleCarouselSwipe();
        }, { passive: true });
        
        function handleCarouselSwipe() {
            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;
            
            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
                    // Swipe left - next slide
                    changeSlide(1);
                } else {
                    // Swipe right - previous slide
                    changeSlide(-1);
                }
                resetAutoPlay();
            }
        }
    }
}

// Initialize carousel touch swipe
document.addEventListener('DOMContentLoaded', initCarouselTouchSwipe);

/* ===========================================
   Lazy Load Images (Performance)
   =========================================== */

function initLazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
                
                // Add fade-in effect
                img.style.opacity = '0';
                img.addEventListener('load', function() {
                    this.style.transition = 'opacity 0.3s ease';
                    this.style.opacity = '1';
                });
            }
        });
    }, {
        rootMargin: '50px'
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading
document.addEventListener('DOMContentLoaded', initLazyLoadImages);

/* ===========================================
   Page Transition Effects
   =========================================== */

function initPageTransitions() {
    // Fade in page content on load
    document.body.style.opacity = '0';
    
    window.addEventListener('load', function() {
        document.body.style.transition = 'opacity 0.3s ease';
        document.body.style.opacity = '1';
    });
    
    // Smooth transitions for internal links
    document.querySelectorAll('a[href^="/"]').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Skip if it's just a hash or external
            if (href === '#' || href.startsWith('http')) {
                return;
            }
            
            e.preventDefault();
            
            document.body.style.transition = 'opacity 0.2s ease';
            document.body.style.opacity = '0';
            
            setTimeout(() => {
                window.location.href = href;
            }, 200);
        });
    });
}

// Initialize page transitions
initPageTransitions();

/* ===========================================
   Console Art (Easter Egg)
   =========================================== */

console.log(`
%c
   __                 _____ __                
  / /   ___  ____  _/ ___// /_____  _______  __
 / /   / _ \\/ __ \\/ \\__ \\/ __/ __ \\/ ___/ / / /
/ /___/  __/ / / /___/ / /_/ /_/ / /  / /_/ / 
/_____/\\___/_/ /_//____/\\__/\\____/_/   \\__, /  
                                      /____/   
%cCapturing Moments, Creating Memories ✨
%cInterested in our code? We're hiring! hello@lensstory.com

`, 'color: #fbbf24; font-family: monospace;', 'color: #9ca3af;', 'color: #f97316;');


