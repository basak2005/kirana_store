// Custom JavaScript for Kirana Store Management

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert.querySelector('.btn-close')) {
                alert.querySelector('.btn-close').click();
            }
        }, 5000);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete, .delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Format currency inputs
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^\d.]/g, '');
            let parts = value.split('.');
            if (parts.length > 2) {
                value = parts[0] + '.' + parts.slice(1).join('');
            }
            if (parts[1] && parts[1].length > 2) {
                value = parts[0] + '.' + parts[1].substring(0, 2);
            }
            e.target.value = value;
        });
    });

    // Phone number formatting
    const phoneInputs = document.querySelectorAll('.phone-input');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 10) {
                value = value.substring(0, 10);
            }
            e.target.value = value;
        });
    });

    // Search functionality
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const tableRows = document.querySelectorAll('.searchable-table tbody tr');
            
            tableRows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });

    // Auto-calculate totals in forms
    function calculateTotal() {
        let subtotal = 0;
        const itemRows = document.querySelectorAll('.item-row');
        
        itemRows.forEach(function(row) {
            const quantity = parseFloat(row.querySelector('.quantity-input')?.value || 0);
            const price = parseFloat(row.querySelector('.price-input')?.value || 0);
            const total = quantity * price;
            
            const totalCell = row.querySelector('.total-cell');
            if (totalCell) {
                totalCell.textContent = '₹' + total.toFixed(2);
            }
            
            subtotal += total;
        });
        
        const subtotalElement = document.querySelector('.subtotal');
        if (subtotalElement) {
            subtotalElement.textContent = '₹' + subtotal.toFixed(2);
        }
        
        // Calculate GST and grand total
        const gstRate = parseFloat(document.querySelector('.gst-rate')?.value || 0);
        const gstAmount = (subtotal * gstRate) / 100;
        const grandTotal = subtotal + gstAmount;
        
        const gstElement = document.querySelector('.gst-amount');
        if (gstElement) {
            gstElement.textContent = '₹' + gstAmount.toFixed(2);
        }
        
        const totalElement = document.querySelector('.grand-total');
        if (totalElement) {
            totalElement.textContent = '₹' + grandTotal.toFixed(2);
        }
    }

    // Attach event listeners for calculation
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('quantity-input') || 
            e.target.classList.contains('price-input') || 
            e.target.classList.contains('gst-rate')) {
            calculateTotal();
        }
    });

    // Add new item row in forms
    const addItemButtons = document.querySelectorAll('.add-item-btn');
    addItemButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const template = document.querySelector('.item-row-template');
            if (template) {
                const newRow = template.cloneNode(true);
                newRow.classList.remove('item-row-template', 'd-none');
                newRow.classList.add('item-row');
                
                const tbody = document.querySelector('.items-table tbody');
                if (tbody) {
                    tbody.appendChild(newRow);
                }
            }
        });
    });

    // Remove item row
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-item-btn')) {
            e.preventDefault();
            const row = e.target.closest('.item-row');
            if (row) {
                row.remove();
                calculateTotal();
            }
        }
    });

    // Print functionality
    const printButtons = document.querySelectorAll('.print-btn');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });

    // Loading state for forms
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                
                // Re-enable after 10 seconds as fallback
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Submit';
                }, 10000);
            }
        });
    });

    // Initialize Charts (if Chart.js is loaded)
    if (typeof Chart !== 'undefined') {
        // Sales Chart
        const salesChartCanvas = document.getElementById('salesChart');
        if (salesChartCanvas) {
            const ctx = salesChartCanvas.getContext('2d');
            // Chart configuration would go here
        }
    }

    // Real-time clock for dashboard
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-IN');
        const dateString = now.toLocaleDateString('en-IN');
        
        const clockElement = document.querySelector('.live-clock');
        if (clockElement) {
            clockElement.textContent = timeString;
        }
        
        const dateElement = document.querySelector('.live-date');
        if (dateElement) {
            dateElement.textContent = dateString;
        }
    }

    // Update clock every second
    setInterval(updateClock, 1000);
    updateClock(); // Initial call

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl + N for new sale
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            const newSaleLink = document.querySelector('a[href*="new_sale"]');
            if (newSaleLink) {
                newSaleLink.click();
            }
        }
        
        // Ctrl + D for dashboard
        if (e.ctrlKey && e.key === 'd') {
            e.preventDefault();
            const dashboardLink = document.querySelector('a[href*="dashboard"]');
            if (dashboardLink) {
                dashboardLink.click();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(function(modal) {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
    });

    console.log('Kirana Store Management System initialized');
});
