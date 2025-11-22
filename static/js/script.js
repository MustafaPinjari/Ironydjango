// JavaScript for order form

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Toggle address sections based on delivery type
    const deliveryTypeSelect = document.getElementById('id_delivery_type');
    const pickupSection = document.getElementById('pickupAddressSection');
    const deliverySection = document.getElementById('deliveryAddressSection');

    function toggleAddressSections() {
        if (deliveryTypeSelect && pickupSection && deliverySection) {
            if (deliveryTypeSelect.value === 'delivery') {
                pickupSection.style.display = 'block';
                deliverySection.style.display = 'block';
            } else {
                pickupSection.style.display = 'block';
                deliverySection.style.display = 'none';
            }
        }
    }

    // Initialize sections
    if (deliveryTypeSelect) {
        deliveryTypeSelect.addEventListener('change', toggleAddressSections);
        toggleAddressSections();
    }

    // Form validation
    const form = document.getElementById('orderForm');
    if (form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    }
});
