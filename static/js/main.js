/**
 * Ironyy - Main JavaScript File
 * Handles common functionality across the application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Handle file input preview
    document.querySelectorAll('.custom-file-input').forEach(input => {
        input.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name || 'Choose file';
            const label = this.nextElementSibling;
            label.textContent = fileName;
            
            // Image preview if it's an image
            if (this.getAttribute('data-preview')) {
                const preview = document.querySelector(this.getAttribute('data-preview'));
                if (preview && e.target.files && e.target.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    }
                    reader.readAsDataURL(e.target.files[0]);
                }
            }
        });
    });

    // Handle order status updates
    document.querySelectorAll('.status-update-form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.innerHTML;
            
            try {
                // Show loading state
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
                
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Show success message
                    showToast('Status updated successfully', 'success');
                    // Reload the page or update the UI as needed
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                    } else {
                        window.location.reload();
                    }
                } else {
                    throw new Error(data.message || 'Failed to update status');
                }
            } catch (error) {
                console.error('Error:', error);
                showToast(error.message || 'An error occurred', 'danger');
            } finally {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            }
        });
    });

    // Handle dynamic formset additions
    document.querySelectorAll('.add-form-row').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const formsetContainer = document.getElementById(this.dataset.formsetId);
            const totalForms = document.getElementById(`id_${this.dataset.prefix}-TOTAL_FORMS`);
            const formCount = parseInt(totalForms.value);
            
            // Clone the first form row and update its attributes
            const newForm = formsetContainer.querySelector('.form-row').cloneNode(true);
            const formRegex = new RegExp(`(${this.dataset.prefix}-\\d+)`, 'g');
            
            // Update form field names and IDs
            newForm.innerHTML = newForm.innerHTML.replace(formRegex, `${this.dataset.prefix}-${formCount}`);
            
            // Clear input values
            newForm.querySelectorAll('input, select, textarea').forEach(input => {
                if (input.type !== 'hidden') {
                    input.value = '';
                }
            });
            
            // Add delete button
            const deleteButton = document.createElement('button');
            deleteButton.type = 'button';
            deleteButton.className = 'btn btn-sm btn-outline-danger delete-form-row';
            deleteButton.innerHTML = '<i class="bi-trash"></i>';
            deleteButton.addEventListener('click', function() {
                this.closest('.form-row').remove();
                updateFormIndices(formsetContainer, this.dataset.prefix);
            });
            
            newForm.querySelector('.form-group').appendChild(deleteButton);
            formsetContainer.appendChild(newForm);
            
            // Update the total form count
            totalForms.value = formCount + 1;
            
            // Initialize any new select2 or other plugins
            if (typeof initSelect2 === 'function') {
                initSelect2();
            }
        });
    });

    // Handle formset row deletion
    document.addEventListener('click', function(e) {
        if (e.target.closest('.delete-form-row')) {
            e.preventDefault();
            const row = e.target.closest('.form-row');
            const formsetContainer = row.closest('.formset-container');
            const prefix = e.target.closest('.delete-form-row').dataset.prefix;
            
            // If this is not the last row, remove it
            if (formsetContainer.querySelectorAll('.form-row').length > 1) {
                row.remove();
                updateFormIndices(formsetContainer, prefix);
            }
        }
    });

    // Function to update form indices after row deletion
    function updateFormIndices(container, prefix) {
        const rows = container.querySelectorAll('.form-row');
        const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
        
        rows.forEach((row, index) => {
            // Update form field names and IDs
            row.querySelectorAll('input, select, textarea').forEach(input => {
                const name = input.name.replace(/\d+/, index);
                const id = input.id.replace(/\d+/, index);
                input.name = name;
                input.id = id;
                
                // Update any labels pointing to this input
                if (input.id) {
                    const label = document.querySelector(`label[for="${input.id.replace(/\d+/, index - 1)}"]`);
                    if (label) {
                        label.setAttribute('for', input.id);
                    }
                }
            });
        });
        
        // Update the total form count
        totalForms.value = rows.length;
    }

    // Show toast notification
    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;
        
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        
        // Remove the toast after it's hidden
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastEl.remove();
        });
    }

    // Initialize any datepickers
    if (typeof $ !== 'undefined' && $.fn.datepicker) {
        $('.datepicker').datepicker({
            format: 'yyyy-mm-dd',
            autoclose: true,
            todayHighlight: true
        });
    }

    // Initialize any timepickers
    if (typeof $ !== 'undefined' && $.fn.timepicker) {
        $('.timepicker').timepicker({
            showMeridian: false,
            minuteStep: 15
        });
    }
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Set up AJAX CSRF token
const csrftoken = getCookie('csrftoken');
if (csrftoken) {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}

// Initialize Select2 if available
function initSelect2() {
    if (typeof $ !== 'undefined' && $.fn.select2) {
        $('.select2').select2({
            theme: 'bootstrap-5',
            width: '100%',
            placeholder: 'Select an option',
            allowClear: true
        });
    }
}

// Call initSelect2 on document ready
if (document.readyState !== 'loading') {
    initSelect2();
} else {
    document.addEventListener('DOMContentLoaded', initSelect2);
}
