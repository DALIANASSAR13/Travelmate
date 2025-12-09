// DOM Elements
const confirmContinueBtn = document.getElementById('confirmContinueBtn');
const saveDraftBtn = document.getElementById('saveDraftBtn');
const goToPaymentBtn = document.getElementById('goToPaymentBtn');
const totalPriceElement = document.getElementById('totalPrice');
const travelInsuranceCheckbox = document.getElementById('travelInsurance');
const addTravellerCheckbox = document.getElementById('addTraveller');
const confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));

// Form elements
const traveller1Form = document.getElementById('traveller1');
const traveller2Form = document.getElementById('traveller2');

// Price calculation
let basePrice = 1080;
let insurancePerTraveller = 49;
let travellerCount = 2;

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners
    setupEventListeners();
    
    // Load saved data if available
    loadSavedData();
});

// Function to set up all event listeners
function setupEventListeners() {
    // Confirm & Continue button
    confirmContinueBtn.addEventListener('click', handleConfirmContinue);
    
    // Save Draft button
    saveDraftBtn.addEventListener('click', handleSaveDraft);
    
    // Go to Payment button in modal
    goToPaymentBtn.addEventListener('click', handleGoToPayment);
    
    // Travel insurance checkbox
    travelInsuranceCheckbox.addEventListener('change', updateTotalPrice);
    
    // Add traveller checkbox
    addTravellerCheckbox.addEventListener('change', handleAddTraveller);
    
    // Form validation on input
    setupFormValidation();
}

// Function to set up form validation
function setupFormValidation() {
    const requiredFields = document.querySelectorAll('input[required], select[required]');
    
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', clearValidation);
    });
}

// Function to validate a single field
function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    const fieldId = field.id;
    
    // Clear any previous validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    // Check if field is empty
    if (!value) {
        field.classList.add('is-invalid');
        showValidationMessage(fieldId, 'This field is required', false);
        return false;
    }
    
    // Field-specific validation
    let isValid = true;
    let message = '';
    
    switch(fieldId) {
        case 'fullName1':
        case 'fullName2':
            if (value.length < 2) {
                isValid = false;
                message = 'Full name must be at least 2 characters';
            } else if (!/^[a-zA-Z\s]+$/.test(value)) {
                isValid = false;
                message = 'Name can only contain letters and spaces';
            }
            break;
            
        case 'age1':
        case 'age2':
            const age = parseInt(value);
            if (age < 1 || age > 120) {
                isValid = false;
                message = 'Age must be between 1 and 120';
            }
            break;
            
        case 'passport1':
        case 'passport2':
            if (value.length < 5) {
                isValid = false;
                message = 'Passport/ID must be at least 5 characters';
            }
            break;
            
        case 'email1':
            if (!isValidEmail(value)) {
                isValid = false;
                message = 'Please enter a valid email address';
            }
            break;
            
        case 'phone1':
            if (!isValidPhone(value)) {
                isValid = false;
                message = 'Please enter a valid phone number';
            }
            break;
    }
    
    if (!isValid) {
        field.classList.add('is-invalid');
        showValidationMessage(fieldId, message, false);
        return false;
    } else {
        field.classList.add('is-valid');
        showValidationMessage(fieldId, 'Looks good!', true);
        return true;
    }
}

// Function to clear validation state
function clearValidation(e) {
    const field = e.target;
    field.classList.remove('is-valid', 'is-invalid');
    const messageElement = document.getElementById(`${field.id}-message`);
    if (messageElement) {
        messageElement.remove();
    }
}

// Function to show validation message
function showValidationMessage(fieldId, message, isValid) {
    // Remove existing message
    const existingMessage = document.getElementById(`${fieldId}-message`);
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create new message element
    const messageElement = document.createElement('div');
    messageElement.id = `${fieldId}-message`;
    messageElement.className = `validation-message ${isValid ? 'valid-feedback' : 'invalid-feedback'}`;
    messageElement.textContent = message;
    
    // Insert after the field
    const field = document.getElementById(fieldId);
    field.parentNode.appendChild(messageElement);
}

// Function to validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Function to validate phone format (basic validation)
function isValidPhone(phone) {
    // This is a simple validation - in a real app you'd use a more robust solution
    const phoneRegex = /^[\d\s\-\+\(\)]{10,}$/;
    return phoneRegex.test(phone);
}

// Function to validate all forms
function validateAllForms() {
    const requiredFields = document.querySelectorAll('input[required], select[required]');
    let allValid = true;
    
    requiredFields.forEach(field => {
        // Create a mock event for validation
        const event = { target: field };
        const isValid = validateField(event);
        if (!isValid) {
            allValid = false;
        }
    });
    
    return allValid;
}

// Function to handle Confirm & Continue button click
function handleConfirmContinue() {
    if (validateAllForms()) {
        // Save form data
        saveFormData();
        
        // Show confirmation modal
        confirmationModal.show();
    } else {
        alert('Please fill in all required fields correctly before proceeding.');
        // Scroll to first invalid field
        const firstInvalid = document.querySelector('.is-invalid');
        if (firstInvalid) {
            firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}

// Function to handle Save Draft button click
function handleSaveDraft() {
    saveFormData();
    
    // Show success message
    alert('Traveller details have been saved. You can return later to complete your booking.');
    
    // Update button text temporarily
    const originalText = saveDraftBtn.innerHTML;
    saveDraftBtn.innerHTML = '<i class="fas fa-check me-1"></i>Saved!';
    saveDraftBtn.classList.remove('btn-outline-secondary');
    saveDraftBtn.classList.add('btn-success');
    
    // Revert after 2 seconds
    setTimeout(() => {
        saveDraftBtn.innerHTML = originalText;
        saveDraftBtn.classList.remove('btn-success');
        saveDraftBtn.classList.add('btn-outline-secondary');
    }, 2000);
}

// Function to handle Go to Payment button click
function handleGoToPayment() {
    // In a real application, this would redirect to a payment page
    // For this demo, we'll show an alert and reset the form
    confirmationModal.hide();
    
    alert('Redirecting to secure payment page... In a real application, this would take you to payment processing.');
    
    // Reset form (in a real app, you wouldn't do this)
    // document.querySelector('form').reset();
}

// Function to save form data to localStorage
function saveFormData() {
    const formData = {
        traveller1: {
            fullName: document.getElementById('fullName1').value,
            age: document.getElementById('age1').value,
            gender: document.getElementById('gender1').value,
            passport: document.getElementById('passport1').value,
            nationality: document.getElementById('nationality1').value,
            email: document.getElementById('email1').value,
            phone: document.getElementById('phone1').value
        },
        traveller2: {
            fullName: document.getElementById('fullName2').value,
            age: document.getElementById('age2').value,
            gender: document.getElementById('gender2').value,
            passport: document.getElementById('passport2').value,
            nationality: document.getElementById('nationality2').value,
            email: document.getElementById('email2').value,
            phone: document.getElementById('phone2').value
        },
        options: {
            travelInsurance: travelInsuranceCheckbox.checked,
            specialAssistance: document.getElementById('specialAssistance').checked
        },
        timestamp: new Date().toISOString()
    };
    
    localStorage.setItem('flightBookingTravellerDetails', JSON.stringify(formData));
    console.log('Form data saved to localStorage');
}

// Function to load saved data from localStorage
function loadSavedData() {
    const savedData = localStorage.getItem('flightBookingTravellerDetails');
    
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            
            // Load traveller 1 data
            if (data.traveller1) {
                document.getElementById('fullName1').value = data.traveller1.fullName || '';
                document.getElementById('age1').value = data.traveller1.age || '';
                document.getElementById('gender1').value = data.traveller1.gender || '';
                document.getElementById('passport1').value = data.traveller1.passport || '';
                document.getElementById('nationality1').value = data.traveller1.nationality || '';
                document.getElementById('email1').value = data.traveller1.email || '';
                document.getElementById('phone1').value = data.traveller1.phone || '';
            }
            
            // Load traveller 2 data
            if (data.traveller2) {
                document.getElementById('fullName2').value = data.traveller2.fullName || '';
                document.getElementById('age2').value = data.traveller2.age || '';
                document.getElementById('gender2').value = data.traveller2.gender || '';
                document.getElementById('passport2').value = data.traveller2.passport || '';
                document.getElementById('nationality2').value = data.traveller2.nationality || '';
                document.getElementById('email2').value = data.traveller2.email || '';
                document.getElementById('phone2').value = data.traveller2.phone || '';
            }
            
            // Load options
            if (data.options) {
                travelInsuranceCheckbox.checked = data.options.travelInsurance || false;
                document.getElementById('specialAssistance').checked = data.options.specialAssistance || false;
            }
            
            // Update price if insurance was selected
            updateTotalPrice();
            
            console.log('Saved data loaded from localStorage');
        } catch (error) {
            console.error('Error loading saved data:', error);
        }
    }
}

// Function to update total price based on selections
function updateTotalPrice() {
    let total = basePrice;
    
    // Add insurance if selected
    if (travelInsuranceCheckbox.checked) {
        total += (insurancePerTraveller * travellerCount);
    }
    
    // Update display
    totalPriceElement.textContent = `$${total}`;
}

// Function to handle adding another traveller
function handleAddTraveller() {
    if (addTravellerCheckbox.checked) {
        alert('Adding another traveller would show an additional form. In a real application, this would dynamically generate another traveller form.');
        // In a real app, you would dynamically create another traveller form here
        // and update the travellerCount and price accordingly
    }
}

// Auto-save form data periodically
setInterval(saveFormData, 30000); // Every 30 seconds