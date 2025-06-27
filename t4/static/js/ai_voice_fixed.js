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
            const errorMsg = 'Sorry, your browser doesn\'t support voice recognition. Please use Chrome, Edge, or Safari for the best experience.';
            this.addMessage('ai', errorMsg);
            alert(errorMsg);
            return;
        }
        
        try {
            // Use the available recognition API
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            // Configure recognition settings
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            this.recognition.maxAlternatives = 1;
            
            // Set up event handlers
            this.setupRecognitionEventHandlers();
            
            console.log('Speech recognition initialized successfully');
        } catch (error) {
            console.error('Error initializing speech recognition:', error);
            const errorMsg = 'Error setting up voice recognition. Please refresh the page and try again.';
            this.addMessage('ai', errorMsg);
            alert(errorMsg);
        }
    }
    
    setupRecognitionEventHandlers() {
        if (!this.recognition) return;
        
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
        this.conversationContext = {}; // Reset conversation context
        this.updateProgressStep(1);
        
        // Update UI
        document.getElementById('startAssistant').disabled = true;
        document.getElementById('stopAssistant').disabled = false;
        
        const welcomeMessage = "Hi! I'm your AI Assistant. I'll help you with your registration today. Let's start with your full name.";
        
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
        
        // Add natural pauses and breathing sounds to text
        const naturalText = this.addNaturalSpeechPatterns(text);
        
        const utterance = new SpeechSynthesisUtterance(naturalText);
        
        // More human-like speech settings - optimized for natural conversation
        utterance.rate = 0.9;    // Natural conversational pace
        utterance.pitch = 0.95;  // Lower, more natural pitch
        utterance.volume = 1.0;  // Full volume for clarity
        
        // Advanced voice selection for maximum human-like quality
        const voices = this.synthesis.getVoices();
        if (voices.length > 0) {
            const bestVoice = this.selectBestVoice(voices);
            if (bestVoice) {
                utterance.voice = bestVoice;
                console.log('Selected voice:', bestVoice.name);
            }
        }
        
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
    
    selectBestVoice(voices) {
        // Priority 1: Most natural human voices
        const humanVoices = voices.filter(voice => 
            voice.name.toLowerCase().includes('zira') ||
            voice.name.toLowerCase().includes('david') ||
            voice.name.toLowerCase().includes('mark') ||
            voice.name.toLowerCase().includes('hazel') ||
            voice.name.toLowerCase().includes('aria') ||
            voice.name.toLowerCase().includes('jenny') ||
            voice.name.toLowerCase().includes('guy') ||
            voice.name.toLowerCase().includes('nova') ||
            voice.name.toLowerCase().includes('neural') ||
            voice.name.toLowerCase().includes('enhanced')
        );
        
        // Priority 2: High-quality premium voices
        const premiumVoices = voices.filter(voice => 
            voice.name.toLowerCase().includes('premium') ||
            voice.name.toLowerCase().includes('natural') ||
            voice.name.toLowerCase().includes('microsoft') ||
            voice.name.toLowerCase().includes('wavenet') ||
            voice.name.toLowerCase().includes('standard')
        );
        
        // Priority 3: Well-known quality voices
        const qualityVoices = voices.filter(voice => 
            voice.name.toLowerCase().includes('samantha') ||
            voice.name.toLowerCase().includes('alex') ||
            voice.name.toLowerCase().includes('karen') ||
            voice.name.toLowerCase().includes('daniel') ||
            voice.name.toLowerCase().includes('fiona') ||
            voice.name.toLowerCase().includes('tessa') ||
            voice.name.toLowerCase().includes('serena') ||
            voice.name.toLowerCase().includes('amelie')
        );
        
        // Priority 4: Female voices (often sound warmer in medical settings)
        const femaleVoices = voices.filter(voice => 
            voice.lang.startsWith('en') &&
            (voice.name.toLowerCase().includes('female') ||
             voice.name.toLowerCase().includes('woman'))
        );
        
        // Priority 5: Any good English voice
        const englishVoices = voices.filter(voice => 
            voice.lang.startsWith('en') && 
            !voice.name.toLowerCase().includes('robot') &&
            !voice.name.toLowerCase().includes('synthetic') &&
            !voice.name.toLowerCase().includes('compact') &&
            !voice.name.toLowerCase().includes('basic')
        );
        
        // Return the best available voice
        if (humanVoices.length > 0) return humanVoices[0];
        if (premiumVoices.length > 0) return premiumVoices[0];
        if (qualityVoices.length > 0) return qualityVoices[0];
        if (femaleVoices.length > 0) return femaleVoices[0];
        if (englishVoices.length > 0) return englishVoices[0];
        return voices[0]; // Fallback to first available voice
    }
    
    addNaturalSpeechPatterns(text) {
        // Add natural pauses and speech patterns
        let naturalText = text;
        
        // Add natural breathing pauses and fillers for more human-like speech
        naturalText = naturalText.replace(/\. /g, '... ');
        naturalText = naturalText.replace(/, /g, ', ');
        
        // Add natural hesitations and conversational markers
        naturalText = naturalText.replace(/(\w+)(\s+)(and|but|so|however|also|now|well|okay|let's)(\s+)/gi, '$1$2... $3$4');
        
        // Make questions sound more natural with slight pauses
        naturalText = naturalText.replace(/\?/g, '?');
        
        // Add natural emphasis patterns
        naturalText = naturalText.replace(/\b(please|thank you|sorry|great|perfect|wonderful)\b/gi, (match) => {
            return match; // Keep natural emphasis
        });
        
        // Add conversational breathing spaces
        if (naturalText.length > 50) {
            naturalText = naturalText.replace(/(\w+\s+\w+\s+\w+)\s+(and|or|but|so)\s+/gi, '$1, $2 ');
        }
        
        return naturalText;
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
        
        // Only extract name if we don't have both first and last name yet
        const currentFirstName = this.getFieldValue('firstName');
        const currentLastName = this.getFieldValue('lastName');
        
        if (!currentFirstName || !currentLastName) {
            // Extract name information only if we're missing name data
            const nameMatch = this.extractName(input);
            if (nameMatch) {
                console.log('Found name:', nameMatch);
                if (nameMatch.firstName && !currentFirstName) this.fillField('firstName', nameMatch.firstName);
                if (nameMatch.lastName && !currentLastName) this.fillField('lastName', nameMatch.lastName);
            }
        }
        
        // Extract age only if we don't have it yet or if we're specifically asking for age
        const currentAge = this.getFieldValue('age');
        if (!currentAge || this.conversationContext.lastQuestion === 'age') {
            const ageMatch = input.match(/\b(\d{1,3})\s*(?:years?\s*old|age)\b/i) || 
                            input.match(/\bage\s*(?:is\s*)?(\d{1,3})\b/i) ||
                            input.match(/\bi\s*am\s*(\d{1,3})\b/i) ||
                            input.match(/(\d{1,3})\s*years?\s*old/i);
            if (ageMatch) {
                console.log('Found age:', ageMatch[1]);
                this.fillField('age', ageMatch[1]);
            }
        }
        
        // Extract gender only if we don't have it yet or if we're specifically asking for gender
        const currentGender = this.getFieldValue('gender');
        if (!currentGender || this.conversationContext.lastQuestion === 'gender') {
            if (lowercaseInput.includes('male') && !lowercaseInput.includes('female')) {
                this.fillSelectField('gender', 'male');
            } else if (lowercaseInput.includes('female')) {
                this.fillSelectField('gender', 'female');
            } else if (lowercaseInput.includes('other') || lowercaseInput.includes('non-binary') || 
                       lowercaseInput.includes('non binary') || lowercaseInput.includes('prefer not')) {
                this.fillSelectField('gender', 'other');
            }
        }
        
        // Extract phone number only if we don't have it yet or if we're specifically asking for phone
        const currentPhone = this.getFieldValue('phone');
        if (!currentPhone || this.conversationContext.lastQuestion === 'phone') {
            const phoneMatch = input.match(/\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b/) ||
                              input.match(/\b\d{10}\b/) ||
                              input.match(/\(\d{3}\)\s*\d{3}[-.\s]?\d{4}/) ||
                              input.match(/\b(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\b/) ||
                              input.match(/\b(\d{3})\s+(\d{3})\s+(\d{4})\b/);
            if (phoneMatch) {
                console.log('Found phone:', phoneMatch[0]);
                let cleanPhone = phoneMatch[0].replace(/\s+/g, '').replace(/[^\d]/g, '');
                if (cleanPhone.length === 10) {
                    // Format as XXX-XXX-XXXX
                    cleanPhone = cleanPhone.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
                }
                this.fillField('phone', cleanPhone);
            }
        }
        
        // Extract email - improved patterns for voice input
        const emailMatch = input.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/) ||
                          this.extractEmailFromVoice(input);
        if (emailMatch) {
            const email = typeof emailMatch === 'string' ? emailMatch : emailMatch[0];
            console.log('Found email:', email);
            this.fillField('email', email);
        }
        
        // Extract address - improved detection for any step
        if (this.currentStep <= 1 && !this.getFieldValue('address')) {
            // More flexible address detection
            if (lowercaseInput.includes('street') || lowercaseInput.includes('avenue') || 
                lowercaseInput.includes('road') || lowercaseInput.includes('drive') ||
                lowercaseInput.includes('boulevard') || lowercaseInput.includes('lane') ||
                lowercaseInput.includes('address') || lowercaseInput.includes('live at') ||
                lowercaseInput.includes('my address is') || lowercaseInput.includes('i live at') ||
                lowercaseInput.includes('place') || lowercaseInput.includes('court') ||
                lowercaseInput.includes('way') || lowercaseInput.includes('circle') ||
                // Also detect if input has numbers (likely street address)
                /\d+.*(?:street|avenue|road|drive|boulevard|lane|place|court|way|circle)/i.test(input) ||
                // Or if it's a response to "what's your address"
                (this.conversationContext.lastQuestion && this.conversationContext.lastQuestion.includes('address'))) {
                
                // Clean up common voice-to-text issues
                let cleanAddress = input.replace(/(?:my\s+address\s+is\s+|i\s+live\s+at\s+|address\s+is\s+|my\s+home\s+address\s+is\s+)/gi, '').trim();
                
                // If the response doesn't seem like a real address, try to extract it differently
                if (cleanAddress.length > 5) { // Must be at least a few characters
                    this.fillField('address', cleanAddress);
                    console.log('Found address:', cleanAddress);
                }
            }
        }
        
        // Extract symptoms, allergies, medications (handled in medical step now)
        if (this.currentStep >= 2) {
            this.extractMedicalInfo(input);
        }
    }
    
    extractEmailFromVoice(input) {
        const lowercaseInput = input.toLowerCase();
        
        // Pattern 1: Standard "name dot name at domain dot com" format
        const voicePattern1 = /([a-zA-Z0-9]+)(?:\s+dot\s+([a-zA-Z0-9]+))?\s+at\s+([a-zA-Z0-9]+)(?:\s+dot\s+([a-zA-Z0-9]+))+/i;
        const match1 = lowercaseInput.match(voicePattern1);
        
        if (match1) {
            let email = match1[1]; // first part
            if (match1[2]) email += '.' + match1[2]; // second part if exists
            email += '@' + match1[3]; // domain part
            if (match1[4]) email += '.' + match1[4]; // extension
            
            // Handle additional dots
            const remainingInput = lowercaseInput.substring(match1.index + match1[0].length);
            const additionalDots = remainingInput.match(/\s+dot\s+([a-zA-Z0-9]+)/gi);
            if (additionalDots) {
                additionalDots.forEach(dot => {
                    const part = dot.replace(/\s+dot\s+/gi, '');
                    email += '.' + part;
                });
            }
            
            return email;
        }
        
        // Pattern 2: Letter-by-letter spelling like "j o h n at g m a i l dot c o m"
        const letterPattern = /([a-z](?:\s+[a-z])*)\s+at\s+([a-z](?:\s+[a-z])*)\s+dot\s+([a-z](?:\s+[a-z])*)/i;
        const match2 = lowercaseInput.match(letterPattern);
        
        if (match2) {
            const username = match2[1].replace(/\s+/g, '');
            const domain = match2[2].replace(/\s+/g, '');
            const extension = match2[3].replace(/\s+/g, '');
            return `${username}@${domain}.${extension}`;
        }
        
        // Pattern 3: Mixed format like "john smith at g m a i l dot com"
        const mixedPattern = /([a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+)*)\s+at\s+([a-z](?:\s+[a-z])*)\s+dot\s+([a-z](?:\s+[a-z])*)/i;
        const match3 = lowercaseInput.match(mixedPattern);
        
        if (match3) {
            const username = match3[1].replace(/\s+/g, '').toLowerCase();
            const domain = match3[2].replace(/\s+/g, '');
            const extension = match3[3].replace(/\s+/g, '');
            return `${username}@${domain}.${extension}`;
        }
        
        // Pattern 4: Handle underscore as "underscore"
        const underscorePattern = /([a-zA-Z0-9]+)\s+underscore\s+([a-zA-Z0-9]+)\s+at\s+([a-zA-Z0-9]+)\s+dot\s+([a-zA-Z0-9]+)/i;
        const match4 = lowercaseInput.match(underscorePattern);
        
        if (match4) {
            return `${match4[1]}_${match4[2]}@${match4[3]}.${match4[4]}`;
        }
        
        return null;
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
        
        // Handle "next field" command - universal skip to next field
        if (lowercaseInput.includes('next field') || lowercaseInput.includes('skip field') || 
            lowercaseInput.includes('next question') || lowercaseInput.includes('skip question')) {
            this.handleNextFieldCommand();
            return;
        }
        
        // Handle skip commands
        if (lowercaseInput.includes('skip phone') || lowercaseInput.includes('skip number')) {
            this.fillField('phone', 'Skipped by user');
            this.addMessage('ai', "No problem! Let's continue without the phone number.");
            // Continue to next field
            setTimeout(() => this.askForMissingPersonalInfo(), 1000);
            return;
        }
        
        if (lowercaseInput.includes('skip email')) {
            this.fillField('email', 'Skipped by user');
            this.addMessage('ai', "Alright! Let's continue without the email address.");
            setTimeout(() => this.askForMissingPersonalInfo(), 1000);
            return;
        }
        
        if (lowercaseInput.includes('skip address')) {
            this.fillField('address', 'Skipped by user');
            this.addMessage('ai', "Okay! Let's continue without the address.");
            setTimeout(() => this.askForMissingPersonalInfo(), 1000);
            return;
        }
        
        // Special handling for address collection - if we're asking for address and user gives any reasonable response
        if (this.conversationContext.lastQuestion === 'address' && !this.getFieldValue('address')) {
            const addressAttempts = this.conversationContext.askCount?.address || 0;
            
            // If we've asked for address multiple times, accept any non-empty response
            if (addressAttempts >= 2 && userInput.trim().length > 3) {
                this.fillField('address', userInput.trim());
                this.addMessage('ai', "Perfect! I've got your address noted down.");
                setTimeout(() => this.askForMissingPersonalInfo(), 1000);
                return;
            }
        }
        
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
        this.conversationContext.lastQuestion = 'age';
        const firstName = this.getFieldValue('firstName');
        const message = `Perfect, ${firstName}! How old are you?`;
        this.addMessage('ai', message);
        this.speak(message, () => {
            setTimeout(() => this.startListening(), 1000);
        });
    }
    
    hasRequiredPersonalInfo() {
        const firstName = this.getFieldValue('firstName');
        const age = this.getFieldValue('age');
        const gender = this.getFieldValue('gender');
        const phone = this.getFieldValue('phone');
        const email = this.getFieldValue('email');
        const address = this.getFieldValue('address');
        
        // Phone is optional if user has tried multiple times or skipped
        const phoneCount = this.conversationContext.askCount?.phone || 0;
        const hasRequiredPhone = phone || phoneCount >= 3;
        
        // Address is optional if user has tried multiple times or skipped
        const addressCount = this.conversationContext.askCount?.address || 0;
        const hasRequiredAddress = address || addressCount >= 3;
        
        return firstName && age && gender && hasRequiredPhone && email && hasRequiredAddress;
    }
    
    askForMissingPersonalInfo() {
        const firstName = this.getFieldValue('firstName');
        const age = this.getFieldValue('age');
        const gender = this.getFieldValue('gender');
        const phone = this.getFieldValue('phone');
        const email = this.getFieldValue('email');
        const address = this.getFieldValue('address');
        
        console.log('Current field values:', {firstName, age, gender, phone, email, address});
        
        // Track how many times we've asked for the same info
        if (!this.conversationContext.askCount) {
            this.conversationContext.askCount = {};
        }
        
        let message = '';
        let currentAsk = '';
        
        if (!age) {
            currentAsk = 'age';
            this.conversationContext.lastQuestion = 'age';
            message = "What's your age?";
        } else if (!gender) {
            currentAsk = 'gender';
            this.conversationContext.lastQuestion = 'gender';
            message = "What's your gender? Male, female, or other?";
        } else if (!phone) {
            currentAsk = 'phone';
            this.conversationContext.lastQuestion = 'phone';
            this.conversationContext.askCount.phone = (this.conversationContext.askCount.phone || 0) + 1;
            
            if (this.conversationContext.askCount.phone <= 2) {
                message = "What's your phone number?";
            } else {
                // After 2 attempts, offer to skip or ask differently
                message = "I'm having trouble understanding your phone number. You can say 'skip phone' to continue without it, or try saying the numbers more slowly.";
            }
        } else if (!email) {
            currentAsk = 'email';
            this.conversationContext.lastQuestion = 'email';
            this.conversationContext.askCount.email = (this.conversationContext.askCount.email || 0) + 1;
            
            if (this.conversationContext.askCount.email <= 2) {
                message = "What's your email?";
            } else {
                message = "I'm having trouble with your email. Please say it very slowly, like 'j-o-h-n dot s-m-i-t-h at g-m-a-i-l dot c-o-m', or say 'skip email'.";
            }
        } else if (!address) {
            currentAsk = 'address';
            this.conversationContext.lastQuestion = 'address';
            this.conversationContext.askCount.address = (this.conversationContext.askCount.address || 0) + 1;
            
            console.log('Asking for address, attempt:', this.conversationContext.askCount.address);
            
            if (this.conversationContext.askCount.address <= 2) {
                message = "Great! What's your home address? Please include the street number, street name, city, and state. For example, '123 Main Street, New York, New York'.";
            } else {
                message = "I'm having trouble understanding your address. Please speak slowly and clearly, or say 'skip address' to continue without it.";
            }
        } else {
            console.log('All personal info collected, moving to medical info');
            this.moveToMedicalInfo();
            return;
        }
        
        console.log('Asking for:', currentAsk, 'Message:', message);
        this.addMessage('ai', message);
        this.speak(message, () => {
            setTimeout(() => this.startListening(), 1000);
        });
    }
    
    moveToMedicalInfo() {
        this.currentStep = 2;
        this.updateProgressStep(3);
        this.conversationContext.lastQuestion = null; // Clear context when moving to new section
        
        const message = "Perfect! Now let's discuss your medical information. What symptoms or health concerns brought you to the hospital today?";
        
        this.addMessage('ai', message);
        this.speak(message, () => {
            setTimeout(() => this.startListening(), 1000);
        });
    }
    
    handleMedicalInfo(userInput) {
        const symptoms = this.getFieldValue('symptoms');
        const allergies = this.getFieldValue('allergies');
        const medications = this.getFieldValue('medications');
        const medicalHistory = this.getFieldValue('medicalHistory');
        
        // Initialize medical step tracking
        if (!this.conversationContext.medicalStep) {
            this.conversationContext.medicalStep = 0;
        }
        
        // Process current input for medical info
        this.extractMedicalInfo(userInput);
        
        let message = '';
        
        switch (this.conversationContext.medicalStep) {
            case 0: // Ask for symptoms
                if (!symptoms && (userInput.toLowerCase().includes('no') || userInput.toLowerCase().includes('nothing'))) {
                    this.fillField('symptoms', 'No specific symptoms reported');
                }
                
                if (this.getFieldValue('symptoms')) {
                    this.conversationContext.medicalStep = 1;
                    message = "Thanks for letting me know. Now, do you have any allergies I should be aware of? This could be allergies to medications, foods, or anything else.";
                } else {
                    message = "So, what brings you in today? Could you tell me about your symptoms or the main reason for your visit?";
                }
                break;
                
            case 1: // Ask for allergies
                if (!allergies && (userInput.toLowerCase().includes('no') || userInput.toLowerCase().includes('none'))) {
                    this.fillField('allergies', 'No known allergies');
                }
                
                if (this.getFieldValue('allergies')) {
                    this.conversationContext.medicalStep = 2;
                    message = "Perfect, I've got that noted. Are you currently taking any medications or supplements?";
                } else {
                    message = "Please tell me about any allergies you have, or say 'no allergies' if you don't have any.";
                }
                break;
                
            case 2: // Ask for medications
                if (!medications && (userInput.toLowerCase().includes('no') || userInput.toLowerCase().includes('none'))) {
                    this.fillField('medications', 'No current medications');
                }
                
                if (this.getFieldValue('medications')) {
                    this.conversationContext.medicalStep = 3;
                    message = "Thanks for that information. Now, do you have any significant medical history or previous surgeries I should know about?";
                } else {
                    message = "Could you tell me about any medications or supplements you're currently taking? If you're not taking any, just say 'no medications'.";
                }
                break;
                
            case 3: // Ask for medical history
                if (!medicalHistory && (userInput.toLowerCase().includes('no') || userInput.toLowerCase().includes('none'))) {
                    this.fillField('medicalHistory', 'No significant medical history');
                }
                
                if (this.getFieldValue('medicalHistory')) {
                    this.moveToEmergencyContact();
                    return;
                } else {
                    message = "Please tell me about any previous medical conditions, surgeries, or hospitalizations, or say 'no history' if none.";
                }
                break;
        }
        
        this.addMessage('ai', message);
        this.speak(message, () => {
            setTimeout(() => this.startListening(), 1000);
        });
    }
    
    extractMedicalInfo(input) {
        const lowercaseInput = input.toLowerCase();
        
        // Extract symptoms
        if (this.conversationContext.medicalStep === 0 || 
            lowercaseInput.includes('pain') || lowercaseInput.includes('hurt') || 
            lowercaseInput.includes('ache') || lowercaseInput.includes('sick') ||
            lowercaseInput.includes('symptom') || lowercaseInput.includes('feel')) {
            if (!this.getFieldValue('symptoms')) {
                this.fillField('symptoms', input);
            }
        }
        
        // Extract allergies
        if (this.conversationContext.medicalStep === 1 ||
            lowercaseInput.includes('allergic') || lowercaseInput.includes('allergy') ||
            lowercaseInput.includes('reaction')) {
            if (!this.getFieldValue('allergies')) {
                this.fillField('allergies', input);
            }
        }
        
        // Extract medications
        if (this.conversationContext.medicalStep === 2 ||
            lowercaseInput.includes('medication') || lowercaseInput.includes('medicine') ||
            lowercaseInput.includes('pill') || lowercaseInput.includes('drug') ||
            lowercaseInput.includes('taking')) {
            if (!this.getFieldValue('medications')) {
                this.fillField('medications', input);
            }
        }
        
        // Extract medical history
        if (this.conversationContext.medicalStep === 3 ||
            lowercaseInput.includes('surgery') || lowercaseInput.includes('operation') ||
            lowercaseInput.includes('hospital') || lowercaseInput.includes('condition') ||
            lowercaseInput.includes('medical history')) {
            if (!this.getFieldValue('medicalHistory')) {
                this.fillField('medicalHistory', input);
            }
        }
    }
    
    moveToEmergencyContact() {
        this.currentStep = 3;
        this.updateProgressStep(4);
        
        const message = "We're almost done! Now I just need to get emergency contact information. Who should we contact in case of an emergency?";
        
        this.addMessage('ai', message);
        this.speak(message, () => {
            setTimeout(() => this.startListening(), 1000);
        });
    }
    
    handleEmergencyContact(userInput) {
        const emergencyName = this.getFieldValue('emergencyName');
        const emergencyPhone = this.getFieldValue('emergencyPhone');
        const emergencyRelation = this.getFieldValue('emergencyRelation');
        
        // Initialize emergency step tracking
        if (!this.conversationContext.emergencyStep) {
            this.conversationContext.emergencyStep = 0;
        }
        
        // Extract emergency contact information
        this.extractEmergencyInfo(userInput);
        
        let message = '';
        
        switch (this.conversationContext.emergencyStep) {
            case 0: // Ask for emergency contact name
                const nameMatch = this.extractName(userInput);
                if (nameMatch) {
                    this.fillField('emergencyName', `${nameMatch.firstName} ${nameMatch.lastName}`.trim());
                }
                
                if (this.getFieldValue('emergencyName')) {
                    this.conversationContext.emergencyStep = 1;
                    message = `Great! And what's ${this.getFieldValue('emergencyName')}'s phone number?`;
                } else {
                    message = "Could you give me the full name of your emergency contact?";
                }
                break;
                
            case 1: // Ask for emergency contact phone
                // Extract phone number for emergency contact
                const phoneMatch = userInput.match(/\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b/) ||
                                  userInput.match(/\b\d{10}\b/) ||
                                  userInput.match(/\(\d{3}\)\s*\d{3}[-.\s]?\d{4}/) ||
                                  userInput.match(/\b(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\b/);
                if (phoneMatch) {
                    let cleanPhone = phoneMatch[0].replace(/\s+/g, '').replace(/[^\d]/g, '');
                    if (cleanPhone.length === 10) {
                        cleanPhone = cleanPhone.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
                    }
                    this.fillField('emergencyPhone', cleanPhone);
                }
                
                if (this.getFieldValue('emergencyPhone')) {
                    this.conversationContext.emergencyStep = 2;
                    message = "Perfect! What's their relationship to you? For example, spouse, parent, sibling, friend?";
                } else {
                    message = "Please provide their phone number.";
                }
                break;
                
            case 2: // Ask for relationship
                if (!emergencyRelation) {
                    this.fillField('emergencyRelation', userInput);
                }
                
                if (this.getFieldValue('emergencyRelation')) {
                    this.moveToConfirmation();
                    return;
                } else {
                    message = "What's their relationship to you?";
                }
                break;
        }
        
        this.addMessage('ai', message);
        this.speak(message, () => {
            setTimeout(() => this.startListening(), 1000);
        });
    }
    
    extractEmergencyInfo(input) {
        const lowercaseInput = input.toLowerCase();
        
        // Extract relationship keywords
        const relationships = ['mother', 'father', 'parent', 'spouse', 'husband', 'wife', 'partner', 
                              'son', 'daughter', 'child', 'brother', 'sister', 'sibling', 
                              'friend', 'uncle', 'aunt', 'cousin', 'grandmother', 'grandfather'];
        
        for (const relation of relationships) {
            if (lowercaseInput.includes(relation)) {
                if (!this.getFieldValue('emergencyRelation')) {
                    this.fillField('emergencyRelation', relation.charAt(0).toUpperCase() + relation.slice(1));
                    break;
                }
            }
        }
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
            
            const message = "Wonderful! We're all set. I've filled out your entire registration form, and everything looks great. You can now complete your registration by clicking the green 'Complete Registration' button below. Thank you for choosing our hospital - we'll take excellent care of you!";
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
    
    fillSelectField(fieldId, value) {
        const field = document.getElementById(fieldId);
        if (field && value) {
            field.value = value.trim();
            field.classList.add('form-field-filled');
            
            // For select elements, we need to enable them temporarily
            field.removeAttribute('disabled');
            field.dispatchEvent(new Event('change', { bubbles: true }));
            field.setAttribute('disabled', true);
            
            console.log(`Selected ${fieldId} with: ${value}`);
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
        } else {
            console.error('Chat container not found, but message would be:', message);
            // Try to find the container again
            this.chatContainer = document.getElementById('chatContainer');
            if (this.chatContainer) {
                this.chatContainer.appendChild(messageDiv);
                this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
            }
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
    
    getRandomAcknowledgment() {
        const acknowledgments = [
            "Perfect!",
            "Great!",
            "Wonderful!",
            "Excellent!",
            "That's helpful!",
            "Thank you!",
            "Got it!",
            "Noted!",
            "I've got that down."
        ];
        return acknowledgments[Math.floor(Math.random() * acknowledgments.length)];
    }
    
    getRandomTransition() {
        const transitions = [
            "Now,",
            "Next,",
            "Alright,",
            "Okay,",
            "Great! So,",
            "Perfect! Now,",
            "Let's move on.",
            "Moving along,",
            "And now"
        ];
        return transitions[Math.floor(Math.random() * transitions.length)];
    }
    
    addConversationalVariation(baseMessage) {
        // Add some variety to make responses feel more human
        if (Math.random() > 0.7) {
            const acknowledgment = this.getRandomAcknowledgment();
            return `${acknowledgment} ${baseMessage}`;
        }
        return baseMessage;
    }
    
    handleNextFieldCommand() {
        console.log('Next field command received, current step:', this.currentStep);
        
        // Determine current field being asked and skip it appropriately
        switch (this.currentStep) {
            case 0: // Initial greeting and name
                if (!this.getFieldValue('firstName')) {
                    this.fillField('firstName', 'Skipped by user');
                    this.fillField('lastName', 'Skipped by user');
                    this.addMessage('ai', "I'll skip the name for now. Let's move on to your age.");
                    setTimeout(() => this.askForAge(), 1000);
                } else {
                    this.addMessage('ai', "We've already got your name. Let me continue with the next question.");
                    setTimeout(() => this.askForAge(), 1000);
                }
                break;
                
            case 1: // Personal information
                const currentField = this.getCurrentPersonalField();
                if (currentField) {
                    this.skipCurrentPersonalField(currentField);
                } else {
                    this.addMessage('ai', "Let's move on to the medical information section.");
                    setTimeout(() => this.moveToMedicalInfo(), 1000);
                }
                break;
                
            case 2: // Medical information
                this.skipCurrentMedicalField();
                break;
                
            case 3: // Emergency contact
                this.skipCurrentEmergencyField();
                break;
                
            case 4: // Confirmation
                this.addMessage('ai', "I'll proceed with the form submission. Please review the information and click the submit button when ready.");
                break;
                
            default:
                this.addMessage('ai', "I'll skip to the next section.");
                break;
        }
    }
    
    getCurrentPersonalField() {
        // Return the current field being asked for in personal info step
        if (!this.getFieldValue('age')) return 'age';
        if (!this.getFieldValue('gender')) return 'gender';
        if (!this.getFieldValue('phone')) return 'phone';
        if (!this.getFieldValue('email')) return 'email';
        if (!this.getFieldValue('address')) return 'address';
        return null;
    }
    
    skipCurrentPersonalField(fieldName) {
        const fieldMessages = {
            'age': "I'll skip the age for now.",
            'gender': "I'll skip the gender information.",
            'phone': "No problem, I'll skip the phone number.",
            'email': "I'll skip the email for now.",
            'address': "I'll skip the address information."
        };
        
        this.fillField(fieldName, 'Skipped by user');
        const message = fieldMessages[fieldName] || "I'll skip this field.";
        this.addMessage('ai', message + " Let's continue.");
        
        setTimeout(() => this.askForMissingPersonalInfo(), 1000);
    }
    
    skipCurrentMedicalField() {
        const medicalStep = this.conversationContext.medicalStep || 0;
        const fieldMessages = [
            { field: 'symptoms', message: "I'll skip the symptoms for now." },
            { field: 'allergies', message: "I'll skip the allergy information." },
            { field: 'medications', message: "I'll skip the medication information." },
            { field: 'medicalHistory', message: "I'll skip the medical history." }
        ];
        
        if (medicalStep < fieldMessages.length) {
            const currentField = fieldMessages[medicalStep];
            this.fillField(currentField.field, 'Skipped by user');
            this.addMessage('ai', currentField.message + " Let's continue.");
            
            this.conversationContext.medicalStep = medicalStep + 1;
            
            // Continue with next medical field or move to emergency contact
            if (this.conversationContext.medicalStep >= fieldMessages.length) {
                setTimeout(() => this.moveToEmergencyContact(), 1000);
            } else {
                setTimeout(() => this.handleMedicalInfo(''), 1000);
            }
        } else {
            this.addMessage('ai', "Let's move on to emergency contact information.");
            setTimeout(() => this.moveToEmergencyContact(), 1000);
        }
    }
    
    skipCurrentEmergencyField() {
        const emergencyStep = this.conversationContext.emergencyStep || 0;
        
        switch (emergencyStep) {
            case 0: // Skip emergency name
                this.fillField('emergencyName', 'Skipped by user');
                this.addMessage('ai', "I'll skip the emergency contact name.");
                this.conversationContext.emergencyStep = 1;
                setTimeout(() => this.handleEmergencyContact(''), 1000);
                break;
                
            case 1: // Skip emergency phone
                this.fillField('emergencyPhone', 'Skipped by user');
                this.addMessage('ai', "I'll skip the emergency contact phone number.");
                this.conversationContext.emergencyStep = 2;
                setTimeout(() => this.handleEmergencyContact(''), 1000);
                break;
                
            case 2: // Skip emergency relationship
                this.fillField('emergencyRelation', 'Skipped by user');
                this.addMessage('ai', "I'll skip the relationship information and move to confirmation.");
                setTimeout(() => this.moveToConfirmation(), 1000);
                break;
                
            default:
                this.addMessage('ai', "Let's move on to the final confirmation.");
                setTimeout(() => this.moveToConfirmation(), 1000);
                break;
        }
    }
}

// Initialize the AI Assistant
let aiAssistant;

window.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing AI Assistant...');
    
    // Check if required elements exist
    const requiredElements = ['chatContainer', 'aiAvatar', 'listeningStatus', 'startAssistant', 'stopAssistant'];
    const missingElements = [];
    
    requiredElements.forEach(id => {
        if (!document.getElementById(id)) {
            missingElements.push(id);
        }
    });
    
    if (missingElements.length > 0) {
        console.error('Missing required elements:', missingElements);
        return;
    }
    
    try {
        aiAssistant = new AIHospitalAssistant();
        console.log('AI Assistant initialized successfully');
        
        // Add event listeners to buttons
        const startButton = document.getElementById('startAssistant');
        const stopButton = document.getElementById('stopAssistant');
        
        if (startButton) {
            startButton.addEventListener('click', startAIAssistant);
        }
        
        if (stopButton) {
            stopButton.addEventListener('click', stopAIAssistant);
        }
        
        console.log('Button event listeners added');
        
    } catch (error) {
        console.error('Error initializing AI Assistant:', error);
    }
});

// Global functions for button clicks
function startAIAssistant() {
    console.log('Start button clicked');
    
    // Check for microphone permissions
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(function(stream) {
                // Stop the stream immediately, we just needed to check permissions
                stream.getTracks().forEach(track => track.stop());
                
                if (aiAssistant) {
                    aiAssistant.start();
                } else {
                    console.error('AI Assistant not initialized');
                    alert('AI Assistant not ready. Please refresh the page.');
                }
            })
            .catch(function(error) {
                console.error('Microphone access denied:', error);
                alert('Microphone access is required for voice registration. Please allow microphone access and try again.');
            });
    } else {
        // Fallback for older browsers
        if (aiAssistant) {
            aiAssistant.start();
        } else {
            console.error('AI Assistant not initialized');
            alert('AI Assistant not ready. Please refresh the page.');
        }
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
