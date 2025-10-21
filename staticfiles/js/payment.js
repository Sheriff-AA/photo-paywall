/* ===========================================
   PAYMENT PAGES JAVASCRIPT - payment.js
   Handles animations, interactions, and
   functionality for success, error, and
   cancel payment pages
   =========================================== */

document.addEventListener('DOMContentLoaded', function() {
    initPaymentPageAnimations();
    initPaymentInteractions();
    trackPaymentEvent();
    copyOrderIdToClipboard();
});

/* ===========================================
   Initialize Payment Page Animations
   =========================================== */

function initPaymentPageAnimations() {
    // Animate success checkmark
    const successCheckmark = document.querySelector('.success-checkmark');
    if (successCheckmark) {
        animateSuccessCheckmark();
    }
    
    // Animate error icon
    const errorIconContainer = document.querySelector('.error-icon-container');
    if (errorIconContainer) {
        animateErrorIcon();
    }
    
    // Animate cancel icon
    const cancelIconContainer = document.querySelector('.cancel-icon-container');
    if (cancelIconContainer) {
        animateCancelIcon();
    }
    
    // Fade in all content sections
    fadeInContent();
}

/* ===========================================
   Success Checkmark Animation
   =========================================== */

function animateSuccessCheckmark() {
    const checkmark = document.querySelector('.success-checkmark');
    
    // Add animation classes after delay
    setTimeout(() => {
        checkmark.style.animation = 'scaleIn 0.6s ease forwards';
    }, 100);
}

/* ===========================================
   Error Icon Animation
   =========================================== */

function animateErrorIcon() {
    const errorIcon = document.querySelector('.error-icon-container');
    
    setTimeout(() => {
        errorIcon.style.animation = 'scaleIn 0.6s ease forwards';
    }, 100);
}

/* ===========================================
   Cancel Icon Animation
   =========================================== */

function animateCancelIcon() {
    const cancelIcon = document.querySelector('.cancel-icon-container');
    
    setTimeout(() => {
        cancelIcon.style.animation = 'slideIn 0.6s ease forwards';
    }, 100);
}

/* ===========================================
   Fade In Content Sections
   =========================================== */

function fadeInContent() {
    const sections = document.querySelectorAll('section > div > div');
    
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(10px)';
        section.style.transition = 'all 0.6s ease';
        
        setTimeout(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, 200 + (index * 100));
    });
}

/* ===========================================
   Payment Page Interactions
   =========================================== */

function initPaymentInteractions() {
    // Add hover effects to buttons
    const buttons = document.querySelectorAll('a[href*="collections"], a[href*="home"], a[href*="contact"]');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Add click animation to buttons
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            ripple.style.width = ripple.style.height = '20px';
            ripple.style.left = x - 10 + 'px';
            ripple.style.top = y - 10 + 'px';
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(255, 255, 255, 0.5)';
            ripple.style.pointerEvents = 'none';
            ripple.style.animation = 'ripple-animation 0.6s ease-out';
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

/* ===========================================
   Track Payment Event (Analytics)
   =========================================== */

// function trackPaymentEvent() {
//     const pageTitle = document.title;
//     let eventType = 'payment_unknown';
    
//     if (pageTitle.includes('Successful')) {
//         eventType = 'payment_success';
//     } else if (pageTitle.includes('Failed')) {
//         eventType = 'payment_error';
//     } else if (pageTitle.includes('Cancelled')) {
//         eventType = 'payment_cancel';
//     }
    
//     // Send analytics event
//     if (typeof gtag !== 'undefined') {
//         gtag('event', eventType, {
//             'page_title': pageTitle,
//             'timestamp': new Date().toISOString()
//         });
//     }
    
//     // Console log for debugging
//     console.log(`Payment Event: ${eventType}`);
// }

/* ===========================================
   Copy Order ID to Clipboard
   =========================================== */

function copyOrderIdToClipboard() {
    const orderIdElements = document.querySelectorAll('dl dt, dl dd');
    
    // Find and add click handler to order ID
    orderIdElements.forEach((element, index) => {
        if (element.textContent.includes('Order ID') || element.textContent.includes('ID:')) {
            const nextElement = orderIdElements[index + 1];
            
            if (nextElement) {
                nextElement.style.cursor = 'pointer';
                nextElement.title = 'Click to copy order ID';
                nextElement.style.transition = 'all 0.2s ease';
                
                nextElement.addEventListener('click', function() {
                    const text = this.textContent.trim();
                    
                    navigator.clipboard.writeText(text).then(() => {
                        // Show feedback
                        const originalText = this.textContent;
                        this.textContent = '✓ Copied!';
                        this.style.color = '#4ade80';
                        
                        setTimeout(() => {
                            this.textContent = originalText;
                            this.style.color = '';
                        }, 2000);
                    }).catch(err => {
                        console.error('Failed to copy:', err);
                    });
                });
                
                nextElement.addEventListener('mouseover', function() {
                    this.style.color = '#fbbf24';
                });
                
                nextElement.addEventListener('mouseout', function() {
                    this.style.color = '';
                });
            }
        }
    });
}

/* ===========================================
   Ripple Animation Keyframes (CSS via JS)
   =========================================== */

function injectRippleStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple-animation {
            from {
                opacity: 1;
                transform: scale(0);
            }
            to {
                opacity: 0;
                transform: scale(4);
            }
        }
    `;
    document.head.appendChild(style);
}

injectRippleStyles();

/* ===========================================
   Animated Counter for Order Summary
   =========================================== */

function animateCounter(element, targetValue, duration = 1000) {
    const start = 0;
    const increment = targetValue / (duration / 16);
    let current = start;
    
    const interval = setInterval(() => {
        current += increment;
        
        if (current >= targetValue) {
            element.textContent = targetValue;
            clearInterval(interval);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Animate photo count if present
document.addEventListener('DOMContentLoaded', function() {
    const photoCountElements = document.querySelectorAll('div:has(svg) span');
    
    photoCountElements.forEach(element => {
        if (element.textContent.includes('photo')) {
            const match = element.textContent.match(/(\d+)/);
            if (match) {
                const count = parseInt(match[1]);
                animateCounter(element, count, 800);
            }
        }
    });
});

/* ===========================================
   Scroll to Section Animation
   =========================================== */

function smoothScrollToSection(selectorOrId) {
    const element = document.querySelector(selectorOrId);
    
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/* ===========================================
   Back Button Handler
   =========================================== */

document.querySelectorAll('a[href="javascript:history.back()"]').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Fade out effect before navigation
        document.body.style.transition = 'opacity 0.3s ease';
        document.body.style.opacity = '0';
        
        setTimeout(() => {
            window.history.back();
        }, 300);
    });
});

/* ===========================================
   Print Order Function
   =========================================== */

function printOrderDetails() {
    const printWindow = window.open('', '', 'height=400,width=600');
    const content = document.querySelector('.payment-success-card') || document.querySelector('.payment-details-card');
    
    if (content) {
        printWindow.document.write('<html><head><title>Order Details</title>');
        printWindow.document.write('<style>body { font-family: Arial; margin: 20px; }');
        printWindow.document.write('table { width: 100%; border-collapse: collapse; }');
        printWindow.document.write('th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }');
        printWindow.document.write('</style></head><body>');
        printWindow.document.write(content.innerHTML);
        printWindow.document.write('</body></html>');
        printWindow.document.close();
        printWindow.print();
    }
}

// Make print function available globally
window.printOrderDetails = printOrderDetails;

/* ===========================================
   Download Receipt Function
   =========================================== */

function downloadReceipt() {
    const content = document.querySelector('.payment-success-card') || document.querySelector('.payment-details-card');
    
    if (content) {
        const element = document.createElement('a');
        const file = new Blob([content.innerText], { type: 'text/plain' });
        element.href = URL.createObjectURL(file);
        element.download = `receipt-${new Date().getTime()}.txt`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }
}

// Make download function available globally
window.downloadReceipt = downloadReceipt;

/* ===========================================
   Retry Payment Function
   =========================================== */

function retryPayment() {
    // Fade out and redirect back
    document.body.style.transition = 'opacity 0.3s ease';
    document.body.style.opacity = '0';
    
    setTimeout(() => {
        window.history.back();
    }, 300);
}

// Make retry function available globally
window.retryPayment = retryPayment;

/* ===========================================
   Page Visibility Handler
   =========================================== */

document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        console.log('Payment page hidden');
    } else {
        console.log('Payment page visible');
        // Refresh page state if needed
        location.reload();
    }
});

// /* ===========================================
//    Error Reporting Function
//    =========================================== */

// function reportPaymentError(errorMessage) {
//     const errorContainer = document.querySelector('.error-message-container');
    
//     if (errorContainer) {
//         const alert = document.createElement('div');
//         alert.className = 'bg-red-500/20 border border-red-500/50 rounded-lg p-4 mb-4';
//         alert.innerHTML = `
//             <div class="flex items-center space-x-2">
//                 <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
//                 </svg>
//                 <span class="text-red-300">${errorMessage}</span>
//             </div>
//         `;
        
//         errorContainer.appendChild(alert);
        
//         // Auto-remove after 5 seconds
//         setTimeout(() => {
//             alert.remove();
//         }, 5000);
//     }
// }

// // Make error function available globally
// window.reportPaymentError = reportPaymentError;

// /* ===========================================
//    Performance Monitoring
//    =========================================== */

// function logPagePerformance() {
//     if (window.performance && window.performance.timing) {
//         const perfData = window.performance.timing;
//         const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        
//         console.log(`Payment page load time: ${pageLoadTime}ms`);
        
//         if (window.gtag) {
//             gtag('event', 'page_view', {
//                 'page_load_time': pageLoadTime
//             });
//         }
//     }
// }

// window.addEventListener('load', logPagePerformance);

/* ===========================================
   Accessibility Enhancements
   =========================================== */

function improveAccessibility() {
    // Add aria labels to icons
    const icons = document.querySelectorAll('svg');
    icons.forEach(icon => {
        if (!icon.getAttribute('aria-label')) {
            const parent = icon.closest('[class*="icon"]') || icon.closest('button') || icon.closest('a');
            if (parent) {
                const label = parent.textContent.trim() || 'Icon';
                icon.setAttribute('aria-label', label);
                icon.setAttribute('role', 'img');
            }
        }
    });
    
    // Ensure all interactive elements are keyboard accessible
    const buttons = document.querySelectorAll('a, button');
    buttons.forEach(btn => {
        if (btn.tabIndex === -1) {
            btn.tabIndex = 0;
        }
    });
}

improveAccessibility();

/* ===========================================
   Console Welcome Message
   =========================================== */

console.log(`
%c🎨 DotNetLenses Photography - Payment Page
%cSuccessfully loaded payment processing
%cHaving issues? Contact support@lensstory.com

`, 'color: #fbbf24; font-weight: bold;', 'color: #9ca3af;', 'color: #f97316;');

