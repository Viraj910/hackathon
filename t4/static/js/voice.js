// Voice Recognition JavaScript for Hospital Form

// Global variables
let recognition;
let isListening = false;
let currentFieldId = null;

// Initialize speech recognition when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeSpeechRecognition();
    addVoiceButtonListeners();
    addFormValidation();
});

// Initialize speech recognition
function initializeSpeechRecognition() {
    // Check if browser supports speech recognition
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        
        // Configure recognition settings
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US'; // You can change this to 'en-IN' for Indian English
        recognition.maxAlternatives = 1;
        
        // Event handlers
        recognition.onstart = function() {
            console.log('Voice recognition started');
            isListening = true;
            showVoiceModal();
            updateVoiceButtonState(currentFieldId, true);
        };
        
        recognition.onresult = function(event) {
            console.log('Voice recognition result received');
            const transcript = event.results[0][0].transcript;
            
            if (currentFieldId) {
                const field = document.getElementById(currentFieldId);
                if (field) {
                    // Handle different field types
                    if (field.type === 'number' || field.name === 'age') {
                        // Extract numbers from speech for age/number fields
                        const numbers = transcript.match(/\d+/);
                        if (numbers) {
                            field.value = numbers[0];
                        } else {
                            // Try to convert word numbers to digits
                            field.value = convertWordToNumber(transcript);
                        }
                    } else if (field.name === 'gender') {
                        // Handle gender selection
                        const gender = detectGender(transcript);
                        if (gender) {
                            field.value = gender;
                        }
                    } else if (field.name === 'blood_group') {
                        // Handle blood group selection
                        const bloodGroup = detectBloodGroup(transcript);
                        if (bloodGroup) {
                            field.value = bloodGroup;
                        }
                    } else {
                        // For text fields, use the transcript directly
                        field.value = transcript;
                    }
                    
                    // Add visual feedback
                    field.classList.add('border-success');
                    setTimeout(() => {
                        field.classList.remove('border-success');
                    }, 2000);
                    
                    // Trigger change event for form validation
                    field.dispatchEvent(new Event('change'));
                }
            }
            
            hideVoiceModal();
            isListening = false;
            updateVoiceButtonState(currentFieldId, false);
        };
        
        recognition.onerror = function(event) {
            console.error('Voice recognition error:', event.error);
            hideVoiceModal();
            isListening = false;
            updateVoiceButtonState(currentFieldId, false);
            
            // Show user-friendly error messages
            let errorMessage = 'Sorry, there was an error with voice recognition.';
            switch(event.error) {
                case 'network':
                    errorMessage = 'Network error. Please check your internet connection.';
                    break;
                case 'not-allowed':
                    errorMessage = 'Microphone access denied. Please allow microphone access and try again.';
                    break;
                case 'no-speech':
                    errorMessage = 'No speech detected. Please try speaking again.';
                    break;
                case 'audio-capture':
                    errorMessage = 'No microphone found. Please connect a microphone and try again.';
                    break;
            }
            showToast(errorMessage, 'error');
        };
        
        recognition.onend = function() {
            console.log('Voice recognition ended');
            hideVoiceModal();
            isListening = false;
            updateVoiceButtonState(currentFieldId, false);
        };
        
    } else {
        console.warn('Speech recognition not supported in this browser');
        // Hide all voice buttons if not supported
        const voiceButtons = document.querySelectorAll('.btn[onclick*="startDictation"]');
        voiceButtons.forEach(button => {
            button.style.display = 'none';
        });
        showToast('Voice recognition is not supported in this browser. Please use Chrome or Edge.', 'warning');
    }
}

// Main function called by voice buttons
function startDictation(fieldId) {
    if (!recognition) {
        showToast('Voice recognition is not available in this browser.', 'error');
        return;
    }
    
    if (isListening) {
        // Stop current recognition
        recognition.stop();
        return;
    }
    
    currentFieldId = fieldId;
    
    try {
        recognition.start();
    } catch (error) {
        console.error('Error starting recognition:', error);
        showToast('Could not start voice recognition. Please try again.', 'error');
    }
}

// Add click listeners to voice buttons
function addVoiceButtonListeners() {
    // Add click listener to modal to stop recording
    const voiceModal = document.getElementById('voiceModal');
    if (voiceModal) {
        voiceModal.addEventListener('click', function() {
            if (isListening && recognition) {
                recognition.stop();
            }
        });
    }
}

// Show voice recognition modal
function showVoiceModal() {
    const modal = document.getElementById('voiceModal');
    if (modal) {
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
}

// Hide voice recognition modal
function hideVoiceModal() {
    const modal = document.getElementById('voiceModal');
    if (modal) {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
    }
}

// Update voice button appearance
function updateVoiceButtonState(fieldId, listening) {
    if (!fieldId) return;
    
    const button = document.querySelector(`button[onclick="startDictation('${fieldId}')"]`);
    if (button) {
        const icon = button.querySelector('i');
        if (listening) {
            button.classList.add('btn-danger');
            button.classList.remove('btn-outline-secondary');
            if (icon) {
                icon.classList.add('fa-stop');
                icon.classList.remove('fa-microphone');
            }
            button.title = 'Stop Recording';
        } else {
            button.classList.remove('btn-danger');
            button.classList.add('btn-outline-secondary');
            if (icon) {
                icon.classList.remove('fa-stop');
                icon.classList.add('fa-microphone');
            }
            button.title = 'Voice Input';
        }
    }
}

// Helper function to detect gender from speech
function detectGender(transcript) {
    const text = transcript.toLowerCase();
    if (text.includes('male') && !text.includes('female')) {
        return 'Male';
    } else if (text.includes('female')) {
        return 'Female';
    } else if (text.includes('other') || text.includes('prefer not') || text.includes('non-binary')) {
        return 'Other';
    }
    return null;
}

// Helper function to detect blood group from speech
function detectBloodGroup(transcript) {
    const text = transcript.toLowerCase().replace(/\s+/g, '');
    
    const bloodGroups = {
        'apositive': 'A+', 'aplus': 'A+', 'a+': 'A+',
        'anegative': 'A-', 'aminus': 'A-', 'a-': 'A-',
        'bpositive': 'B+', 'bplus': 'B+', 'b+': 'B+',
        'bnegative': 'B-', 'bminus': 'B-', 'b-': 'B-',
        'abpositive': 'AB+', 'abplus': 'AB+', 'ab+': 'AB+',
        'abnegative': 'AB-', 'abminus': 'AB-', 'ab-': 'AB-',
        'opositive': 'O+', 'oplus': 'O+', 'o+': 'O+',
        'onegative': 'O-', 'ominus': 'O-', 'o-': 'O-'
    };
    
    for (const [key, value] of Object.entries(bloodGroups)) {
        if (text.includes(key)) {
            return value;
        }
    }
    
    return null;
}

// Helper function to convert word numbers to digits
function convertWordToNumber(transcript) {
    const text = transcript.toLowerCase();
    const numberWords = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
        'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
        'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
        'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
        'eighteen': '18', 'nineteen': '19', 'twenty': '20', 'thirty': '30',
        'forty': '40', 'fifty': '50', 'sixty': '60', 'seventy': '70',
        'eighty': '80', 'ninety': '90'
    };
    
    for (const [word, number] of Object.entries(numberWords)) {
        if (text.includes(word)) {
            return number;
        }
    }
    
    return transcript; // Return original if no number words found
}

// Add form validation
function addFormValidation() {
    const form = document.getElementById('patientForm');
    if (form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showToast('Please fill in all required fields.', 'error');
            }
            form.classList.add('was-validated');
        });
        
        // Add real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.hasAttribute('required') && !this.value.trim()) {
                    this.classList.add('is-invalid');
                } else {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid') && this.value.trim()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
        });
    }
}

// Toast notification function
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert">
            <div class="toast-header">
                <i class="fas fa-${getToastIcon(type)} text-${type} me-2"></i>
                <strong class="me-auto">Hospital Form</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000
    });
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Get appropriate icon for toast type
function getToastIcon(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Alt + V to start voice input for focused field
    if (event.altKey && event.key === 'v') {
        event.preventDefault();
        const focused = document.activeElement;
        if (focused && focused.id) {
            startDictation(focused.id);
        } else {
            showToast('Please focus on an input field first, then press Alt+V for voice input.', 'info');
        }
    }
    
    // Escape to stop voice recognition
    if (event.key === 'Escape' && isListening) {
        if (recognition) {
            recognition.stop();
        }
    }
});

// Add accessibility features
document.addEventListener('DOMContentLoaded', function() {
    // Add aria-labels to voice buttons
    const voiceButtons = document.querySelectorAll('button[onclick*="startDictation"]');
    voiceButtons.forEach(button => {
        button.setAttribute('aria-label', 'Start voice input for this field');
        button.setAttribute('tabindex', '0');
    });
    
    // Add keyboard navigation for voice buttons
    voiceButtons.forEach(button => {
        button.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                this.click();
            }
        });
    });
});
