// AI Hospital Assistant - Advanced Voice Interface
class AIHospitalAssistant {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.isActive = false;
        this.currentStep = 0;
        this.conversationContext = {};
        this.chatContainer = document.getElementById('chatContainer');
        this.aiAvatar = document.getElementById('aiAvatar');
        this.statusIndicator = document.getElementById('listeningStatus');
        
        // Initialize speech recognition
        this.initializeSpeechRecognition();
        
        // Bind methods to preserve 'this' context
        this.start = this.start.bind(this);
        this.stop = this.stop.bind(this);
        this.processUserInput = this.processUserInput.bind(this);
    }
    
    initializeSpeechRecognition() {
        console.log('Initializing speech recognition...');
        
        // Check for speech recognition support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.error('Speech recognition not supported');
            this.addMessage('ai', 'Sorry, your browser doesn\'t support voice recognition. Please use Chrome, Edge, or Safari for the best experience.');
            return;
        }
        
        // Use the available recognition API
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        // Configure recognition settings
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';
        this.recognition.maxAlternatives = 1;
        
        // Event handlers
        this.recognition.onstart = () => {
            console.log('Speech recognition started');
            this.isListening = true;
            this.showListeningIndicator('Listening... Speak now!');
            this.animateAvatar(true);
        };
        
        this.recognition.onresult = (event) => {
            console.log('Speech recognition result received');
            const transcript = event.results[0][0].transcript;
            console.log('User said:', transcript);
            this.processUserInput(transcript);
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.hideListeningIndicator();
            this.animateAvatar(false);
            
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
                case 'aborted':
                    console.log('Speech recognition aborted');
                    return; // Don't show error for intentional aborts
            }
            
            this.addMessage('ai', errorMessage);
            this.speak(errorMessage);
        };
        
        this.recognition.onend = () => {
            console.log('Speech recognition ended');
            this.isListening = false;
            this.hideListeningIndicator();
            this.animateAvatar(false);
            
            // Auto-restart if assistant is still active and not in an error state
            if (this.isActive && this.currentStep < 4) {
                setTimeout(() => {
                    if (this.isActive && !this.isListening) {
                        this.startListening();
                    }
                }, 2000);
            }
        };
        
        console.log('Speech recognition initialized successfully');
    }
    
    start() {
        console.log('Starting AI Assistant...');
        this.isActive = true;
        this.currentStep = 0;
        this.updateProgressStep(1);
        
        // Update UI
        document.getElementById('startAssistant').disabled = true;
        document.getElementById('stopAssistant').disabled = false;
        
        const welcomeMessage = "Hello! I'm AI Assistant, your virtual medical assistant. I'll help you complete your hospital registration by having a conversation with you. Let's start with some basic information. What is your full name?";
        
        this.addMessage('ai', welcomeMessage);
        this.speak(welcomeMessage, () => {
            setTimeout(() => {
                this.startListening();
            }, 1000);
        });
    }
    
    stop() {
        console.log('Stopping AI Assistant...');
        this.isActive = false;
        this.isListening = false;
        
        if (this.recognition) {
            this.recognition.abort();
        }
        
        if (this.synthesis) {
            this.synthesis.cancel();
        }
        
        // Update UI
        document.getElementById('startAssistant').disabled = false;
        document.getElementById('stopAssistant').disabled = true;
        
        this.hideListeningIndicator();
        this.animateAvatar(false);
        
        this.addMessage('ai', 'Registration paused. Click "Start Registration" to continue.');
    }
    
    startListening() {
        if (!this.recognition) {
            console.error('Speech recognition not available');
            this.addMessage('ai', 'Voice recognition is not available. Please check your browser settings.');
            return;
        }
        
        if (this.isActive && !this.isListening) {
            try {
                console.log('Starting to listen...');
                this.recognition.start();
            } catch (e) {
                console.error('Error starting recognition:', e);
                this.addMessage('ai', 'Error starting voice recognition. Please try again.');
            }
        }
    }
    
    speak(text, callback) {
        console.log('AI speaking:', text);
        
        if (!this.synthesis) {
            console.error('Speech synthesis not available');
            if (callback) callback();
            return;
        }
        
        // Cancel any ongoing speech
        this.synthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 0.8;
        
        utterance.onstart = () => {
            console.log('Speech synthesis started');
            this.animateAvatar(true);
        };
        
        utterance.onend = () => {
            console.log('Speech synthesis ended');
            this.animateAvatar(false);
            if (callback) callback();
        };
        
        utterance.onerror = (event) => {
            console.error('Speech synthesis error:', event);
            this.animateAvatar(false);
            if (callback) callback();
        };
        
        this.synthesis.speak(utterance);
    }
    
    processUserInput(userInput) {
        console.log('Processing user input:', userInput);
        this.addMessage('user', userInput);
        
        // Extract information from user input
        this.extractAndFillData(userInput);
        
        // Determine next step based on current conversation state
        this.handleConversationFlow(userInput);
    }
    
    extractAndFillData(input) {
        const lowercaseInput = input.toLowerCase();
        console.log('Extracting data from:', input);
        
        // Extract name information
        const nameMatch = this.extractName(input);
        if (nameMatch) {
            console.log('Found name:', nameMatch);
            if (nameMatch.firstName) this.fillField('firstName', nameMatch.firstName);
            if (nameMatch.lastName) this.fillField('lastName', nameMatch.lastName);
        }
        
        // Extract age
        const ageMatch = input.match(/\b(\d{1,3})\s*(?:years?\s*old|age)\b/i) || 
                        input.match(/\bage\s*(?:is\s*)?(\d{1,3})\b/i) ||
                        input.match(/\bi\s*am\s*(\d{1,3})\b/i) ||
                        input.match(/(\d{1,3})\s*years?\s*old/i);
        if (ageMatch) {
            console.log('Found age:', ageMatch[1]);
            this.fillField('age', ageMatch[1]);
        }
        
        // Extract gender with voice recognition corrections
        if (lowercaseInput.includes('male') && !lowercaseInput.includes('female')) {
            this.fillField('gender', 'male');
        } else if (lowercaseInput.includes('mail') && !lowercaseInput.includes('email')) {
            // Voice recognition often mistakes "male" for "mail"
            console.log('Voice correction: "mail" interpreted as "male"');
            this.fillField('gender', 'male');
        } else if (lowercaseInput.includes('female')) {
            this.fillField('gender', 'female');
        } else if (lowercaseInput.includes('other') || lowercaseInput.includes('non-binary')) {
            this.fillField('gender', 'other');
        }
        
        // Extract phone number
        const phoneMatch = input.match(/\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b/) ||
                          input.match(/\b\d{10}\b/) ||
                          input.match(/\(\d{3}\)\s*\d{3}[-.\s]?\d{4}/);
        if (phoneMatch) {
            console.log('Found phone:', phoneMatch[0]);
            this.fillField('phone', phoneMatch[0]);
        }
        
        // Extract email
        const emailMatch = input.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/);
        if (emailMatch) {
            console.log('Found email:', emailMatch[0]);
            this.fillField('email', emailMatch[0]);
        }
        
        // Extract symptoms (when discussing medical information)
        if (this.currentStep >= 1 && (
            lowercaseInput.includes('pain') || lowercaseInput.includes('hurt') || 
            lowercaseInput.includes('ache') || lowercaseInput.includes('sick') ||
            lowercaseInput.includes('symptom') || lowercaseInput.includes('feel'))) {
            this.fillField('symptoms', input);
        }
        
        // Extract allergies
        if (lowercaseInput.includes('allergic') || lowercaseInput.includes('allergy') ||
            lowercaseInput.includes('reaction')) {
            this.fillField('allergies', input);
        }
        
        // Extract medications
        if (lowercaseInput.includes('medication') || lowercaseInput.includes('medicine') ||
            lowercaseInput.includes('pill') || lowercaseInput.includes('drug') ||
            lowercaseInput.includes('taking')) {
            this.fillField('medications', input);
        }
    }
    
    extractName(input) {
        // Remove common phrases and clean the input
        let cleanInput = input.replace(/(?:my\s+name\s+is\s+|i\s+am\s+|i'm\s+|call\s+me\s+|this\s+is\s+)/gi, '').trim();
        
        // Split by spaces and filter out common words
        const words = cleanInput.split(/\s+/).filter(word => 
            word.length > 1 && 
            !/^(the|and|or|but|a|an)$/i.test(word) &&
            /^[a-zA-Z]+$/.test(word)
        );
        
        if (words.length >= 2) {
            return {
                firstName: words[0],
                lastName: words.slice(1).join(' ')
            };
        } else if (words.length === 1) {
            return {
                firstName: words[0],
                lastName: ''
            };
        }
        
        return null;
    }
    
    handleConversationFlow(userInput) {
        const lowercaseInput = userInput.toLowerCase();
        console.log('Handling conversation flow, current step:', this.currentStep);
        
        switch (this.currentStep) {
            case 0: // Initial greeting and name
                if (this.getFieldValue('firstName')) {
                    this.askForAge();
                } else {
                    this.askForName();
                }
                break;
                
            case 1: // Personal information
                if (this.hasRequiredPersonalInfo()) {
                    this.moveToMedicalInfo();
                } else {
                    this.askForMissingPersonalInfo();
                }
                break;
                
            case 2: // Medical information
                this.handleMedicalInfo(userInput);
                break;
                
            case 3: // Emergency contact
                this.handleEmergencyContact(userInput);
                break;
                
            case 4: // Confirmation
                this.handleConfirmation(userInput);
                break;
        }
    }
    
    askForName() {
        const message = "I didn't catch your name clearly. Could you please tell me your first and last name?";
        this.addMessage('ai', message);
        this.speak(message, () => {
            setTimeout(() => this.startListening(), 1000);
        });
    }
    
    askForAge() {
        this.currentStep = 1;
        this.updateProgressStep(2);
        const message = `Thank you ${this.getFieldValue('firstName')}! How old are you?`;
        this.addMessage('ai', message);
        this.speak(message, () => {
            setTimeout(() => this.startListening(), 1000);
        });
    }
    
    hasRequiredPersonalInfo() {
        return this.getFieldValue('firstName') && 
               this.getFieldValue('age') && 
               this.getFieldValue('phone');
    }
    
    askForMissingPersonalInfo() {
        const firstName = this.getFieldValue('firstName');
        const age = this.getFieldValue('age');
        const phone = this.getFieldValue('phone');
        
        let message = '';
        
        if (!age) {
            message = "What's your age?";
        } else if (!phone) {
            message = "Great! Could you provide your phone number?";
        } else {
            this.moveToMedicalInfo();
            return;
        }
        
        this.addMessage('ai', message);
        this.speak(message, () => {
            setTimeout(() => this.startListening(), 1000);
        });
    }
    
    moveToMedicalInfo() {
        this.currentStep = 2;
        this.updateProgressStep(3);
        
        const message = "Perfect! Now let's discuss your medical information. What symptoms or health concerns brought you to the hospital today?";
        
        this.addMessage('ai', message);
        this.speak(message, () => {
            setTimeout(() => this.startListening(), 1000);
        });
    }
    
    handleMedicalInfo(userInput) {
        const symptoms = this.getFieldValue('symptoms');
        
        if (!symptoms && (userInput.toLowerCase().includes('no') || userInput.toLowerCase().includes('nothing'))) {
            this.fillField('symptoms', 'No specific symptoms reported');
        }
        
        if (this.getFieldValue('symptoms')) {
            this.moveToEmergencyContact();
        } else {
            const message = "Could you describe your symptoms or the reason for your visit?";
            this.addMessage('ai', message);
            this.speak(message, () => {
                setTimeout(() => this.startListening(), 1000);
            });
        }
    }
    
    moveToEmergencyContact() {
        this.currentStep = 3;
        this.updateProgressStep(4);
        
        const message = "Thank you for that information. Now I need emergency contact details. Who should we contact in case of emergency?";
        
        this.addMessage('ai', message);
        this.speak(message, () => {
            setTimeout(() => this.startListening(), 1000);
        });
    }
    
    handleEmergencyContact(userInput) {
        const nameMatch = this.extractName(userInput);
        if (nameMatch) {
            this.fillField('emergencyName', `${nameMatch.firstName} ${nameMatch.lastName}`.trim());
        }
        
        // Move to confirmation after getting emergency contact
        this.moveToConfirmation();
    }
    
    moveToConfirmation() {
        this.currentStep = 4;
        
        const message = "Excellent! I've filled out your registration form with the information you provided. Please review the form on the right side of the screen. If everything looks correct, you can submit your registration. Is all the information accurate?";
        
        this.addMessage('ai', message);
        this.speak(message, () => {
            document.getElementById('submitBtn').disabled = false;
            setTimeout(() => this.startListening(), 1000);
        });
    }
    
    handleConfirmation(userInput) {
        const lowercaseInput = userInput.toLowerCase();
        
        if (lowercaseInput.includes('yes') || lowercaseInput.includes('correct') || 
            lowercaseInput.includes('good') || lowercaseInput.includes('right')) {
            
            const message = "Perfect! Your registration is ready. You can now submit the form by clicking the green 'Complete Registration' button.";
            this.addMessage('ai', message);
            this.speak(message);
            
            // Highlight the submit button
            const submitBtn = document.getElementById('submitBtn');
            if (submitBtn) {
                submitBtn.classList.add('btn-pulse');
                submitBtn.focus();
            }
            
        } else if (lowercaseInput.includes('no') || lowercaseInput.includes('wrong') || 
                   lowercaseInput.includes('incorrect')) {
            
            const message = "No problem! What would you like to change? Please tell me the correct information.";
            this.addMessage('ai', message);
            this.speak(message, () => {
                setTimeout(() => this.startListening(), 1000);
            });
            this.currentStep = 1; // Go back to collect information
        } else {
            const message = "I didn't understand. Could you please say 'yes' if the information is correct, or 'no' if you need to make changes?";
            this.addMessage('ai', message);
            this.speak(message, () => {
                setTimeout(() => this.startListening(), 1000);
            });
        }
    }
    
    getFieldValue(fieldId) {
        const field = document.getElementById(fieldId);
        return field ? field.value.trim() : '';
    }
    
    fillField(fieldId, value) {
        const field = document.getElementById(fieldId);
        if (field && value) {
            field.value = value.trim();
            field.classList.add('form-field-filled');
            
            // Trigger validation
            field.removeAttribute('readonly');
            field.removeAttribute('disabled');
            field.dispatchEvent(new Event('input', { bubbles: true }));
            field.setAttribute('readonly', true);
            
            console.log(`Filled ${fieldId} with: ${value}`);
        }
    }
    
    addMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const icon = sender === 'ai' ? '<i class="fas fa-robot me-2"></i>' : '<i class="fas fa-user me-2"></i>';
        const senderName = sender === 'ai' ? 'AI Assistant' : 'You';
        
        messageDiv.innerHTML = `<strong>${icon}${senderName}:</strong><br>${message}`;
        
        if (this.chatContainer) {
            this.chatContainer.appendChild(messageDiv);
            this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        }
    }
    
    showListeningIndicator(text) {
        if (this.statusIndicator) {
            this.statusIndicator.style.display = 'block';
            const statusText = document.getElementById('statusText');
            if (statusText) {
                statusText.textContent = text;
            }
        }
    }
    
    hideListeningIndicator() {
        if (this.statusIndicator) {
            this.statusIndicator.style.display = 'none';
        }
    }
    
    animateAvatar(speaking) {
        if (this.aiAvatar) {
            if (speaking) {
                this.aiAvatar.classList.add('speaking');
            } else {
                this.aiAvatar.classList.remove('speaking');
            }
        }
    }
    
    updateProgressStep(step) {
        // Remove all active/completed classes
        document.querySelectorAll('.progress-step').forEach(s => {
            s.classList.remove('active', 'completed');
        });
        
        // Mark completed steps
        for (let i = 1; i < step; i++) {
            const stepElement = document.getElementById(`step${i}`);
            if (stepElement) {
                stepElement.classList.add('completed');
            }
        }
        
        // Mark current step as active
        if (step <= 4) {
            const currentStepElement = document.getElementById(`step${step}`);
            if (currentStepElement) {
                currentStepElement.classList.add('active');
            }
        }
    }
}

// Initialize the AI Assistant
let aiAssistant;

window.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing AI Assistant...');
    try {
        aiAssistant = new AIHospitalAssistant();
        console.log('AI Assistant initialized successfully');
    } catch (error) {
        console.error('Error initializing AI Assistant:', error);
    }
});

// Global functions for button clicks
function startAIAssistant() {
    console.log('Start button clicked');
    if (aiAssistant) {
        aiAssistant.start();
    } else {
        console.error('AI Assistant not initialized');
        alert('AI Assistant not ready. Please refresh the page.');
    }
}

function stopAIAssistant() {
    console.log('Stop button clicked');
    if (aiAssistant) {
        aiAssistant.stop();
    }
}

// Add CSS for visual effects
const style = document.createElement('style');
style.textContent = `
    .btn-pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7);
        }
        
        70% {
            transform: scale(1.05);
            box-shadow: 0 0 0 10px rgba(40, 167, 69, 0);
        }
        
        100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(40, 167, 69, 0);
        }
    }
    
    .form-field-filled {
        background-color: #e8f5e8 !important;
        border-color: #28a745 !important;
        animation: fieldFill 0.3s ease-in-out;
    }
    
    @keyframes fieldFill {
        0% {
            transform: scale(1);
            background-color: #fff;
        }
        50% {
            transform: scale(1.02);
            background-color: #d4edda;
        }
        100% {
            transform: scale(1);
            background-color: #e8f5e8;
        }
    }
`;
document.head.appendChild(style);
