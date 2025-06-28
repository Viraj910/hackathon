// AI Hospital Assistant - Rule-Based Intelligent System (No External APIs)
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
        
        // AI Knowledge Base - Simulates intelligent responses
        this.aiKnowledge = {
            greetings: [
                "Hello! I'm your AI medical assistant. I'll help you register today.",
                "Welcome! I'm here to make your registration quick and easy.",
                "Hi there! I'm your intelligent assistant, ready to help with your registration."
            ],
            confirmations: [
                "Perfect! Got that information.",
                "Excellent, I've recorded that.",
                "Great! Moving on to the next question.",
                "Thank you, that's been saved."
            ],
            encouragements: [
                "You're doing great! Just a few more questions.",
                "Almost done! This information helps us serve you better.",
                "Thank you for your patience. We're making good progress."
            ],
            clarifications: [
                "I didn't quite catch that. Could you please repeat?",
                "Let me try that again. Could you speak a bit more clearly?",
                "I want to make sure I got that right. Could you say that once more?"
            ]
        };
        
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
        this.updateProgressStep(1);
        
        // Update UI
        document.getElementById('startAssistant').disabled = true;
        document.getElementById('stopAssistant').disabled = false;
        
        // Get hospital name for personalized greeting
        const hospitalElement = document.querySelector('[name="selected_hospital"]');
        const hospital = hospitalElement ? hospitalElement.value : 'the hospital';
        
        // Use AI-generated personalized greeting
        const welcomeMessage = this.generateAIResponse({}, {hospital: hospital}, 'greeting');
        
        this.addMessage('ai', welcomeMessage);
        this.speak(welcomeMessage, () => {
            // Follow up with name request
            setTimeout(() => {
                const nameRequest = this.generateAIResponse({}, {}, 'nameRequest');
                this.addMessage('ai', nameRequest);
                this.speak(nameRequest, () => {
                    setTimeout(() => {
                        this.startListening();
                    }, 1000);
                });
            }, 1500);
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
        
        // Use AI context analysis
        const currentField = this.conversationContext.lastQuestion || 'general';
        const analysis = this.analyzeUserContext(userInput, currentField);
        
        console.log('AI Analysis:', analysis);
        
        // Provide intelligent feedback based on analysis
        if (analysis.sentiment === 'urgent') {
            const urgentResponse = "I understand this is urgent. I'm processing your information quickly to get you the help you need.";
            this.addMessage('ai', urgentResponse);
            this.speak(urgentResponse);
        } else if (analysis.intent === 'need_help') {
            const helpResponse = "Of course! I'm here to help. Just speak naturally, and I'll guide you through each step. What would you like help with?";
            this.addMessage('ai', helpResponse);
            this.speak(helpResponse);
            return;
        }
        
        // Extract information from user input
        const beforeExtraction = {
            gender: this.getFieldValue('gender')
        };
        
        this.extractAndFillData(userInput);
        
        // Check if voice corrections were applied and provide feedback
        const afterExtraction = {
            gender: this.getFieldValue('gender')
        };
        
        this.provideCorrectionFeedback(userInput, beforeExtraction, afterExtraction);
        
        // Provide intelligent confirmation if data was extracted
        const userData = {
            name: this.getFieldValue('firstName'),
            age: this.getFieldValue('age'),
            phone: this.getFieldValue('phone')
        };
        
        // Use AI understanding responses
        if (analysis.confidence > 0.7) {
            const response = this.generateAIResponse({}, userData, 'understanding');
            this.addMessage('ai', response);
            this.speak(response);
        }
        
        // Determine next step based on current conversation state
        this.handleConversationFlow(userInput);
    }
      applyVoiceCorrections(input) {
        // Common voice recognition corrections for medical/form contexts
        const corrections = {
            // Gender corrections - COMPREHENSIVE handling for "male"
            'mail': 'male',           // "mail" -> "male"
            'Mail': 'male',           // "Mail" -> "male"
            'MAIL': 'male',           // "MAIL" -> "male"
            'maile': 'male',          // "maile" -> "male"
            'mael': 'male',           // "mael" -> "male"
            'maail': 'male',          // "maail" -> "male"
            'mal': 'male',            // "mal" -> "male"
            'mel': 'male',            // "mel" -> "male"
            'meil': 'male',           // "meil" -> "male"
            'mailе': 'male',          // "mailе" -> "male" (with Cyrillic 'е')
            'maol': 'male',           // "maol" -> "male"
            'meile': 'male',          // "meile" -> "male"
            'mayl': 'male',           // "mayl" -> "male"
            'mayel': 'male',          // "mayel" -> "male"
            'malle': 'male',          // "malle" -> "male"
            'malee': 'male',          // "malee" -> "male"
            'maylee': 'male',         // "maylee" -> "male"
            'mayle': 'male',          // "mayle" -> "male"
            'mael': 'male',           // "mael" -> "male"
            'maeal': 'male',          // "maeal" -> "male"
            'maaile': 'male',         // "maaile" -> "male"
            'maiil': 'male',          // "maiil" -> "male"
            'maill': 'male',          // "maill" -> "male"
            'maale': 'male',          // "maale" -> "male"
            'mahle': 'male',          // "mahle" -> "male"
            'maale': 'male',          // "maale" -> "male"
            'mael': 'male',           // "mael" -> "male"
            
            // More phonetic variations for male
            'maail': 'male',          // double 'a'
            'maaile': 'male',         // extended 'a'
            'maiil': 'male',          // double 'i'
            'maill': 'male',          // double 'l'
            'maale': 'male',          // 'aa' + 'le'
            'myle': 'male',           // 'my' + 'le'
            'maell': 'male',          // 'mae' + 'll'
            'maylle': 'male',         // 'may' + 'lle'
            
            // Female variations - Enhanced
            'femail': 'female',       // "femail" -> "female"
            'femaile': 'female',      // "femaile" -> "female"
            'fem ale': 'female',      // "fem ale" -> "female"
            'femal': 'female',        // "femal" -> "female"
            'femeil': 'female',       // "femeil" -> "female"
            'femalle': 'female',      // "femalle" -> "female"
            'fimale': 'female',       // "fimale" -> "female"
            'feemale': 'female',      // "feemale" -> "female"
            'fe male': 'female',      // "fe male" -> "female"
            'feemail': 'female',      // "feemail" -> "female"
            'femael': 'female',       // "femael" -> "female"
            'femeale': 'female',      // "femeale" -> "female"
            'femaeel': 'female',      // "femaeel" -> "female"
            'feemaile': 'female',     // "feemaile" -> "female"
            'femaail': 'female',      // "femaail" -> "female"
            'femayel': 'female',      // "femayel" -> "female"
            'femayle': 'female',      // "femayle" -> "female"
            'phemale': 'female',      // "phemale" -> "female"
            'phemail': 'female',      // "phemail" -> "female"
            
            // Common medical word corrections
            'alergies': 'allergies',
            'alergy': 'allergy',
            'medecine': 'medicine',
            'medecines': 'medicines',
            'medecations': 'medications',
            'symtoms': 'symptoms',
            'symtom': 'symptom',
            
            // Phone number corrections
            'phone number': 'phone number',
            'telephone': 'phone',
            'cell phone': 'phone',
            'mobile': 'phone'
        };

        let correctedInput = input;
        
        // Apply word-by-word corrections while preserving context
        for (const [wrong, correct] of Object.entries(corrections)) {
            // Use word boundary regex to avoid partial matches
            const regex = new RegExp(`\\b${wrong}\\b`, 'gi');
            correctedInput = correctedInput.replace(regex, correct);
        }

        // Log corrections for debugging
        if (correctedInput !== input) {
            console.log('Voice corrections applied:');
            console.log('  Original:', input);
            console.log('  Corrected:', correctedInput);
        }

        return correctedInput;
    }
    
    extractAndFillData(input) {
        // Apply voice recognition corrections
        const correctedInput = this.applyVoiceCorrections(input);
        const lowercaseInput = correctedInput.toLowerCase();
        console.log('Extracting data from:', input);
        if (correctedInput !== input) {
            console.log('Voice correction applied. Original:', input, 'Corrected:', correctedInput);
        }
        
        // Extract name information - Only when we're at step 0 (asking for name) or if name fields are empty
        // Also avoid extracting names when we're explicitly asking for other information
        const isAskingForName = this.currentStep === 0 || 
                               this.conversationContext.lastQuestion === 'name' ||
                               (!this.getFieldValue('firstName') && !this.getFieldValue('lastName'));
        const isAskingForOtherInfo = this.conversationContext.lastQuestion && 
                                   (this.conversationContext.lastQuestion.includes('age') || 
                                    this.conversationContext.lastQuestion.includes('phone') ||
                                    this.conversationContext.lastQuestion.includes('address') ||
                                    this.conversationContext.lastQuestion.includes('gender'));
        
        if (isAskingForName && !isAskingForOtherInfo) {
            const nameMatch = this.extractName(input);
            if (nameMatch) {
                console.log('Found name:', nameMatch);
                if (nameMatch.firstName) this.fillField('firstName', nameMatch.firstName);
                if (nameMatch.lastName) this.fillField('lastName', nameMatch.lastName);
            }
        }
        
        // Extract date of birth - Enhanced to handle various voice formats
        if (this.conversationContext.lastQuestion === 'dateOfBirth' || lowercaseInput.includes('birth') || lowercaseInput.includes('born')) {
            let dobStr = '';
            
            // Convert spoken numbers to digits first
            const processedInput = this.convertSpokenNumbersToDigits(input);
            console.log('Processing date input:', input, '->', processedInput);
            
            // Pattern 1: Numeric date formats - Assume DD-MM-YYYY format
            const numericDateMatch = processedInput.match(/(\d{1,2})[\s\-\/](\d{1,2})[\s\-\/](\d{2,4})/);
            if (numericDateMatch) {
                const day = numericDateMatch[1];
                const month = numericDateMatch[2];
                const year = numericDateMatch[3].length === 2 ? '20' + numericDateMatch[3] : numericDateMatch[3];
                // Convert DD-MM-YYYY to YYYY-MM-DD for HTML date input
                dobStr = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
                console.log(`Date converted from DD-MM-YYYY: ${processedInput} -> ${dobStr}`);
            }
            
            // Pattern 2: Month name formats (January 15, 1990 OR 15 January 1990)
            const monthNameMatch = input.match(/(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s*(\d{4})/i) ||
                                 input.match(/(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})/i);
            if (monthNameMatch && !dobStr) {
                const months = {
                    january: '01', february: '02', march: '03', april: '04', 
                    may: '05', june: '06', july: '07', august: '08', 
                    september: '09', october: '10', november: '11', december: '12'
                };
                
                if (monthNameMatch[1] && isNaN(monthNameMatch[1])) {
                    // Month name first: "January 15, 1990"
                    const month = months[monthNameMatch[1].toLowerCase()];
                    const day = monthNameMatch[2];
                    const year = monthNameMatch[3];
                    dobStr = `${year}-${month}-${day.padStart(2, '0')}`;
                } else {
                    // Day first: "15 January 1990"
                    const day = monthNameMatch[1];
                    const month = months[monthNameMatch[2].toLowerCase()];
                    const year = monthNameMatch[3];
                    dobStr = `${year}-${month}-${day.padStart(2, '0')}`;
                }
            }
            
            // Pattern 3: Voice-friendly formats like "twenty eighth june nineteen ninety"
            // This would require more complex parsing, but for now we'll handle common spoken formats
            
            // Pattern 4: Simple year extraction if user just says a year
            const yearOnlyMatch = input.match(/\b(19|20)\d{2}\b/);
            if (yearOnlyMatch && !dobStr && this.conversationContext.lastQuestion === 'dateOfBirth') {
                // If only year is given, ask for month and day
                const year = yearOnlyMatch[0];
                this.addMessage('ai', `I heard ${year}. Could you also tell me the month and day? For example, "June 28th"`);
                this.speak(`I heard ${year}. Could you also tell me the month and day? For example, "June 28th"`, () => {
                    setTimeout(() => this.startListening(), 1000);
                });
                return;
            }
            
            if (dobStr) {
                console.log('Extracted date of birth:', dobStr);
                this.fillField('dateOfBirth', dobStr);
                
                // Calculate and display age
                const dobDate = new Date(dobStr);
                const today = new Date();
                let age = today.getFullYear() - dobDate.getFullYear();
                const monthDiff = today.getMonth() - dobDate.getMonth();
                if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dobDate.getDate())) {
                    age--;
                }
                
                // Update the calculated age display
                const ageDisplay = document.getElementById('calculatedAge');
                if (ageDisplay) {
                    ageDisplay.textContent = age >= 0 ? age : '-';
                }
                
                // Provide confirmation
                const confirmation = `Great! I've recorded your date of birth as ${dobStr} and calculated your age as ${age} years.`;
                console.log(confirmation);
            }
        }
        // Extract country code - Enhanced patterns
        if (this.conversationContext.lastQuestion === 'countryCode' || lowercaseInput.includes('country code') || lowercaseInput.includes('plus')) {
            let countryCode = '';
            
            // Pattern 1: Direct plus format "plus 91", "+91"
            const plusMatch = input.match(/(?:plus\s*)?(\+?)(\d{1,3})/i);
            if (plusMatch) {
                countryCode = `+${plusMatch[2]}`;
                this.fillSelectField('countryCode', countryCode);
                console.log('Extracted country code:', countryCode);
                
                // Provide confirmation
                const codeNames = {
                    '+1': 'USA/Canada',
                    '+44': 'United Kingdom', 
                    '+91': 'India',
                    '+86': 'China',
                    '+81': 'Japan',
                    '+49': 'Germany',
                    '+33': 'France',
                    '+61': 'Australia',
                    '+55': 'Brazil',
                    '+7': 'Russia'
                };
                const countryName = codeNames[countryCode] || 'your country';
                this.addMessage('ai', `Great! I've set your country code to ${countryCode} for ${countryName}.`);
                return; // Exit early so we don't extract anything else
            }
            
            // Pattern 2: Country name to code mapping
            const countryNames = {
                'india': '+91', 'indian': '+91',
                'usa': '+1', 'america': '+1', 'united states': '+1',
                'uk': '+44', 'britain': '+44', 'england': '+44', 'united kingdom': '+44',
                'china': '+86', 'chinese': '+86',
                'japan': '+81', 'japanese': '+81',
                'germany': '+49', 'german': '+49',
                'france': '+33', 'french': '+33',
                'australia': '+61', 'australian': '+61',
                'brazil': '+55', 'brazilian': '+55',
                'russia': '+7', 'russian': '+7'
            };
            
            for (const [country, code] of Object.entries(countryNames)) {
                if (lowercaseInput.includes(country)) {
                    this.fillSelectField('countryCode', code);
                    console.log('Extracted country code from name:', code);
                    this.addMessage('ai', `Perfect! I've set your country code to ${code} for ${country}.`);
                    return;
                }
            }
        }
        
        // Extract gender - Enhanced recognition system
        if (this.conversationContext.lastQuestion === 'gender' || lowercaseInput.includes('gender')) {
            console.log('Processing gender input:', input);
            console.log('Lowercase input:', lowercaseInput);
            console.log('Voice corrections already applied to input');
            
            let genderDetected = false;
            let detectedGender = '';
            
            // Method 1: Direct pattern matching for gender (most reliable)
            if (lowercaseInput.includes('male') && !lowercaseInput.includes('female')) {
                detectedGender = 'male';
                genderDetected = true;
            } else if (lowercaseInput.includes('female')) {
                detectedGender = 'female';
                genderDetected = true;
            } else if (lowercaseInput.includes('other') || lowercaseInput.includes('non-binary') || 
                       lowercaseInput.includes('non binary') || lowercaseInput.includes('prefer not')) {
                detectedGender = 'other';
                genderDetected = true;
            }
            
            // Method 2: Handle simple single-letter or truncated responses
            if (!genderDetected && this.conversationContext.lastQuestion === 'gender') {
                const trimmedInput = lowercaseInput.trim();
                
                // Single letter responses
                if (trimmedInput === 'm' || trimmedInput === 'male' || trimmedInput.startsWith('m ')) {
                    detectedGender = 'male';
                    genderDetected = true;
                } else if (trimmedInput === 'f' || trimmedInput === 'female' || trimmedInput.startsWith('f ')) {
                    detectedGender = 'female';
                    genderDetected = true;
                } else if (trimmedInput === 'o' || trimmedInput === 'other' || trimmedInput.startsWith('o ')) {
                    detectedGender = 'other';
                    genderDetected = true;
                }
                
                // Sentence format responses
                if (!genderDetected) {
                    if (trimmedInput.includes('i am m') || trimmedInput.includes('my gender is m') ||
                        trimmedInput.includes('i\'m m') || trimmedInput.includes('am male')) {
                        detectedGender = 'male';
                        genderDetected = true;
                    } else if (trimmedInput.includes('i am f') || trimmedInput.includes('my gender is f') ||
                               trimmedInput.includes('i\'m f') || trimmedInput.includes('am female')) {
                        detectedGender = 'female';
                        genderDetected = true;
                    }
                }
            }
            
            // Method 3: Phonetic similarity matching (after voice corrections)
            if (!genderDetected && this.conversationContext.lastQuestion === 'gender') {
                const phoneticMalePatterns = [
                    'mail', 'maile', 'mael', 'mal', 'mel', 'meil', 'maaal', 'maaile',
                    'mayel', 'mayl', 'maylee', 'mayle', 'malle', 'malee'
                ];
                
                const phoneticFemalePatterns = [
                    'femail', 'femaile', 'femal', 'femeil', 'femalle', 'fimale',
                    'fem ale', 'fe male', 'feemale'
                ];
                
                // Check for male patterns
                for (const pattern of phoneticMalePatterns) {
                    if (lowercaseInput === pattern || 
                        lowercaseInput === `i am ${pattern}` || 
                        lowercaseInput === `my gender is ${pattern}` || 
                        lowercaseInput === `${pattern} please` ||
                        lowercaseInput.includes(` ${pattern} `) ||
                        lowercaseInput.endsWith(` ${pattern}`)) {
                        detectedGender = 'male';
                        genderDetected = true;
                        console.log(`Gender detected as male from phonetic pattern: ${pattern}`);
                        break;
                    }
                }
                
                // Check for female patterns
                if (!genderDetected) {
                    for (const pattern of phoneticFemalePatterns) {
                        if (lowercaseInput === pattern || 
                            lowercaseInput === `i am ${pattern}` || 
                            lowercaseInput === `my gender is ${pattern}` || 
                            lowercaseInput === `${pattern} please` ||
                            lowercaseInput.includes(` ${pattern} `) ||
                            lowercaseInput.endsWith(` ${pattern}`)) {
                            detectedGender = 'female';
                            genderDetected = true;
                            console.log(`Gender detected as female from phonetic pattern: ${pattern}`);
                            break;
                        }
                    }
                }
            }
            
            // Apply the detected gender if found
            if (genderDetected && detectedGender) {
                this.fillSelectField('gender', detectedGender);
                
                let confirmationMessage = '';
                if (detectedGender === 'male') {
                    confirmationMessage = "Perfect! I've recorded your gender as male.";
                } else if (detectedGender === 'female') {
                    confirmationMessage = "Perfect! I've recorded your gender as female.";
                } else {
                    confirmationMessage = "Perfect! I've recorded your gender selection.";
                }
                
                this.addMessage('ai', confirmationMessage);
                console.log(`Gender successfully detected and set: ${detectedGender}`);
                
                // Continue to next field after successful detection
                setTimeout(() => this.askForMissingPersonalInfo(), 1000);
                return;
            }
            
            // Handle cases where gender wasn't detected
            if (!genderDetected && this.conversationContext.lastQuestion === 'gender') {
                const askCount = this.conversationContext.askCount?.gender || 0;
                
                if (askCount >= 3) {
                    // After 3 attempts, offer manual selection or skip
                    this.addMessage('ai', "I'm having difficulty understanding your voice input for gender. You can either click on the gender dropdown in the form to select manually, or say 'skip gender' to continue.");
                    this.speak("I'm having difficulty understanding your voice input for gender. You can either click on the gender dropdown in the form to select manually, or say 'skip gender' to continue.", () => {
                        setTimeout(() => this.startListening(), 1000);
                    });
                    return;
                } else if (askCount >= 2) {
                    this.addMessage('ai', "Let me try once more. Please say clearly: just 'male', 'female', or 'other'. I'm listening carefully now.");
                    this.speak("Let me try once more. Please say clearly: just 'male', 'female', or 'other'. I'm listening carefully now.", () => {
                        setTimeout(() => this.startListening(), 1000);
                    });
                    return;
                } else {
                    this.addMessage('ai', "I didn't catch that clearly. Could you please say 'male', 'female', or 'other'?");
                    this.speak("I didn't catch that clearly. Could you please say 'male', 'female', or 'other'?", () => {
                        setTimeout(() => this.startListening(), 1000);
                    });
                    return;
                }
            }
        }
        
        // Extract phone number
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
        
        // Email extraction removed - email field is no longer required
        
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
        
        // Handle general "next field" skip command
        if (lowercaseInput.includes('next field') || lowercaseInput.includes('skip field') || 
            lowercaseInput.includes('skip this') || lowercaseInput.includes('move on')) {
            
            // Determine which field to skip based on current context
            if (this.conversationContext.lastQuestion === 'phone' || lowercaseInput.includes('phone')) {
                this.fillField('phone', 'Skipped by user');
                this.addMessage('ai', "No problem! Let's skip the phone number and continue.");
            } else if (this.conversationContext.lastQuestion === 'address' || lowercaseInput.includes('address')) {
                this.fillField('address', 'Skipped by user');
                this.addMessage('ai', "Okay! Let's skip the address and continue.");
            } else if (this.conversationContext.lastQuestion === 'dateOfBirth' || lowercaseInput.includes('date') || lowercaseInput.includes('birth')) {
                this.fillField('dateOfBirth', '1990-01-01'); // Default date
                const ageDisplay = document.getElementById('calculatedAge');
                if (ageDisplay) ageDisplay.textContent = '35'; // Default age
                this.addMessage('ai', "Alright! Let's skip the date of birth and continue.");
            } else if (this.conversationContext.lastQuestion === 'gender' || lowercaseInput.includes('gender')) {
                this.fillSelectField('gender', 'other');
                this.addMessage('ai', "No problem! Let's skip gender selection and continue.");
            } else {
                this.addMessage('ai', "Let's move on to the next field.");
            }
            
            // Continue to next field
            setTimeout(() => this.askForMissingPersonalInfo(), 1000);
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
        
        if (lowercaseInput.includes('skip address')) {
            this.fillField('address', 'Skipped by user');
            this.addMessage('ai', "Okay! Let's continue without the address.");
            setTimeout(() => this.askForMissingPersonalInfo(), 1000);
            return;
        }
        
        if (lowercaseInput.includes('skip gender')) {
            this.fillSelectField('gender', 'other');
            this.addMessage('ai', "No problem! I've set your gender as 'other' and we'll continue.");
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
                    this.askForDOB();
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
        this.conversationContext.lastQuestion = 'name';
        const message = "To personalize your experience, could you please tell me your full name?";
        this.addMessage('ai', message);
        this.speak(message, () => {
            setTimeout(() => this.startListening(), 1000);
        });
    }
    
    askForDOB() {
        this.currentStep = 1;
        this.updateProgressStep(2);
        this.conversationContext.lastQuestion = 'dateOfBirth';
        const firstName = this.getFieldValue('firstName');
        const message = `Great, ${firstName}! What is your date of birth? Please say it in the format day-month-year, for example, twenty one ten two thousand five for 21-10-2005.`;
        this.addMessage('ai', message);
        this.speak(message, () => {
            setTimeout(() => this.startListening(), 1000);
        });
    }

    hasRequiredPersonalInfo() {
        const firstName = this.getFieldValue('firstName');
        const dob = this.getFieldValue('dateOfBirth');
        const gender = this.getFieldValue('gender');
        const phone = this.getFieldValue('phone');
        const countryCode = this.getFieldValue('countryCode');
        const address = this.getFieldValue('address');
        // Phone and country code are both required
        return firstName && dob && gender && phone && countryCode && address;
    }
    
    askForMissingPersonalInfo() {
        const firstName = this.getFieldValue('firstName');
        const dob = this.getFieldValue('dateOfBirth');
        const gender = this.getFieldValue('gender');
        const phone = this.getFieldValue('phone');
        const countryCode = this.getFieldValue('countryCode');
        const address = this.getFieldValue('address');
        
        console.log('Current field values:', {firstName, dob, gender, phone, countryCode, address});
        
        // Track how many times we've asked for the same info
        if (!this.conversationContext.askCount) {
            this.conversationContext.askCount = {};
        }
        
        let message = '';
        let currentAsk = '';
        
        if (!dob) {
            this.conversationContext.lastQuestion = 'dateOfBirth';
            const message = `What is your date of birth? Please say it in the format day-month-year, for example, twenty one ten two thousand five for 21-10-2005.`;
            this.addMessage('ai', message);
            this.speak(message, () => {
                setTimeout(() => this.startListening(), 1000);
            });
            return;
        } else if (!gender) {
            currentAsk = 'gender';
            this.conversationContext.lastQuestion = 'gender';
            this.conversationContext.askCount.gender = (this.conversationContext.askCount.gender || 0) + 1;
            
            if (this.conversationContext.askCount.gender === 1) {
                message = "For medical records, could you tell me your gender? You can say male, female, or other.";
            } else if (this.conversationContext.askCount.gender === 2) {
                message = "I didn't catch that clearly. Please say just 'male', 'female', or 'other' for your gender.";
            } else {
                message = "Let me try once more. For gender, please say clearly: 'male', 'female', or 'other'. I'm listening carefully.";
            }
        } else if (!countryCode) {
            this.conversationContext.lastQuestion = 'countryCode';
            const message = `What is your country code? For example, say plus nine one for India, plus one for USA.`;
            this.addMessage('ai', message);
            this.speak(message, () => {
                setTimeout(() => this.startListening(), 1000);
            });
            return;
        } else if (!phone) {
            this.conversationContext.lastQuestion = 'phone';
            const message = `What is your phone number? Please say the digits clearly.`;
            this.addMessage('ai', message);
            this.speak(message, () => {
                setTimeout(() => this.startListening(), 1000);
            });
            return;
        } else if (!address) {
            currentAsk = 'address';
            this.conversationContext.lastQuestion = 'address';
            this.conversationContext.askCount.address = (this.conversationContext.askCount.address || 0) + 1;
            
            console.log('Asking for address, attempt:', this.conversationContext.askCount.address);
            
            if (this.conversationContext.askCount.address <= 2) {
                message = "Now I need your address for medical records. Please tell me your street address, city, and state.";
            } else {
                message = "The AI system is having difficulty with your address. Please speak slowly, or say 'skip address' to continue.";
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
                // Phone extraction is handled by extractEmergencyInfo
                if (this.getFieldValue('emergencyPhone')) {
                    this.conversationContext.emergencyStep = 2;
                    message = "Perfect! What's their relationship to you? For example, spouse, parent, sibling, friend?";
                } else {
                    message = "I didn't catch that phone number. Could you please repeat it? You can say it digit by digit or as a complete number.";
                }
                break;
                
            case 2: // Ask for relationship
                // Check current relationship value after extraction
                const currentRelation = this.getFieldValue('emergencyRelation');
                
                // If relationship wasn't extracted automatically, try to extract from raw input
                if (!currentRelation) {
                    const cleanInput = userInput.trim();
                    if (cleanInput.length > 0) {
                        this.fillField('emergencyRelation', cleanInput.charAt(0).toUpperCase() + cleanInput.slice(1).toLowerCase());
                    }
                }
                
                if (this.getFieldValue('emergencyRelation')) {
                    this.moveToConfirmation();
                    return;
                } else {
                    message = "What's their relationship to you? For example: mother, father, spouse, sibling, friend.";
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
        console.log(`Extracting emergency info from: "${input}", step: ${this.conversationContext.emergencyStep}`);
        
        // Extract phone number for emergency contact if we're in the right step
        if (this.conversationContext.emergencyStep === 1 && !this.getFieldValue('emergencyPhone')) {
            console.log('Attempting to extract emergency phone number...');
            
            // More comprehensive phone number patterns
            const phonePatterns = [
                /\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b/,  // 123-456-7890 or 123.456.7890 or 123 456 7890
                /\b\d{10}\b/,                          // 1234567890
                /\(\d{3}\)\s*\d{3}[-.\s]?\d{4}/,      // (123) 456-7890
                /\b(\d{3})[\s\-\.](\d{3})[\s\-\.](\d{4})\b/,  // Various separators
                /\b(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\s*(\d)\b/  // Digit by digit
            ];
            
            let phoneMatch = null;
            for (const pattern of phonePatterns) {
                phoneMatch = input.match(pattern);
                if (phoneMatch) {
                    console.log(`Phone pattern matched: ${pattern.source}`);
                    break;
                }
            }
            
            if (phoneMatch) {
                let cleanPhone = phoneMatch[0].replace(/\s+/g, '').replace(/[^\d]/g, '');
                console.log(`Raw phone extracted: "${phoneMatch[0]}", cleaned: "${cleanPhone}"`);
                
                if (cleanPhone.length === 10) {
                    cleanPhone = cleanPhone.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
                    console.log('Emergency phone extracted by extractEmergencyInfo:', cleanPhone);
                    this.fillField('emergencyPhone', cleanPhone);
                } else if (cleanPhone.length > 10) {
                    // Handle cases where country code might be included
                    const lastTenDigits = cleanPhone.slice(-10);
                    const formattedPhone = lastTenDigits.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
                    console.log('Emergency phone (last 10 digits) extracted:', formattedPhone);
                    this.fillField('emergencyPhone', formattedPhone);
                } else {
                    console.log(`Phone number too short: ${cleanPhone} (${cleanPhone.length} digits)`);
                }
            } else {
                console.log('No phone number pattern matched in input');
            }
        }
        
        // Extract relationship keywords
        const relationships = ['mother', 'father', 'parent', 'spouse', 'husband', 'wife', 'partner', 
                              'son', 'daughter', 'child', 'brother', 'sister', 'sibling', 
                              'friend', 'uncle', 'aunt', 'cousin', 'grandmother', 'grandfather', 
                              'grandma', 'grandpa', 'mom', 'dad', 'mama', 'papa'];
        
        if (this.conversationContext.emergencyStep === 2 && !this.getFieldValue('emergencyRelation')) {
            console.log('Attempting to extract relationship...');
            for (const relation of relationships) {
                if (lowercaseInput.includes(relation)) {
                    const capitalizedRelation = relation.charAt(0).toUpperCase() + relation.slice(1);
                    console.log(`Relationship extracted: ${capitalizedRelation}`);
                    this.fillField('emergencyRelation', capitalizedRelation);
                    break;
                }
            }
        }
        
        // Extract name for emergency contact if we're in the right step
        if (this.conversationContext.emergencyStep === 0 && !this.getFieldValue('emergencyName')) {
            console.log('Attempting to extract emergency contact name...');
            const nameMatch = this.extractName(input);
            if (nameMatch) {
                const fullName = `${nameMatch.firstName} ${nameMatch.lastName}`.trim();
                console.log('Emergency name extracted by extractEmergencyInfo:', fullName);
                this.fillField('emergencyName', fullName);
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
            
            // Use AI-generated completion message
            const completionMessage = this.generateAIResponse({}, {}, 'completion');
            this.addMessage('ai', completionMessage);
            this.speak(completionMessage);
            
            // Add technical AI touch
            setTimeout(() => {
                const techMessage = "The AI system has also assigned you a token number and appointment slot. You'll see all the details on the next page!";
                this.addMessage('ai', techMessage);
                this.speak(techMessage);
            }, 3000);
            
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
        const value = field ? field.value.trim() : '';
        console.log(`[getFieldValue] ${fieldId}: "${value}" (field exists: ${!!field})`);
        return value;
    }
    
    fillField(fieldId, value) {
        console.log(`[fillField] Attempting to fill field: ${fieldId} with value: "${value}"`);
        console.log(`[fillField] Context - lastQuestion: ${this.conversationContext.lastQuestion}, currentStep: ${this.currentStep}, emergencyStep: ${this.conversationContext.emergencyStep}`);
        
        const field = document.getElementById(fieldId);
        if (field && value) {
            const oldValue = field.value;
            field.value = value.trim();
            field.classList.add('form-field-filled');
            
            // Trigger validation
            field.removeAttribute('readonly');
            field.removeAttribute('disabled');
            field.dispatchEvent(new Event('input', { bubbles: true }));
            field.setAttribute('readonly', true);
            
            console.log(`[fillField] ✅ Successfully filled ${fieldId}: "${oldValue}" -> "${field.value}"`);
            
            // Special handling for emergency contact fields
            if (fieldId.startsWith('emergency')) {
                console.log(`[fillField] Emergency field updated: ${fieldId} = "${field.value}"`);
                // Trigger a visual update
                field.style.backgroundColor = '#e8f5e8';
                setTimeout(() => {
                    field.style.backgroundColor = '';
                }, 2000);
            }
        } else {
            console.log(`[fillField] ❌ Failed to fill field ${fieldId}: field exists=${!!field}, has value=${!!value}, value type=${typeof value}`);
            if (!field) {
                console.log(`[fillField] Field element with ID "${fieldId}" not found in DOM`);
            }
            if (!value) {
                console.log(`[fillField] Value is empty, null, or undefined: "${value}"`);
            }
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
    
    // Enhanced AI Response Generator - Simulates intelligent conversation
    generateAIResponse(context, userData, intent = 'general') {
        const responses = {
            greeting: [
                `Hello! I'm your AI medical assistant. I can see you're registering for ${userData.hospital || 'the hospital'}. Let's get started!`,
                `Welcome! I'm an intelligent assistant designed to help with medical registrations. Ready to begin?`,
                `Hi! I'm your smart registration assistant. I'll make this process quick and personalized for you.`
            ],
            nameRequest: [
                "To personalize your experience, could you please tell me your full name?",
                "Let's start with your name. What should I call you?",
                "I'd love to know your name so I can assist you better. What's your full name?"
            ],
            nameConfirm: (name) => [
                `Nice to meet you, ${name}! I've got your name recorded.`,
                `Perfect! Hello ${name}, great to have you here today.`,
                `Excellent! I've saved your name as ${name}. Let's continue.`
            ],
            dobRequest: [
                "Now I need your date of birth for medical records. Please say it in day-month-year format, like twenty one ten two thousand five for 21-10-2005.",
                "For proper medical care, could you tell me your date of birth? Say it as day-month-year, for example, fifteen twelve nineteen ninety for 15-12-1990.",
                "What's your date of birth? Please say it in day-month-year format, like seven eight two thousand for 7-8-2000."
            ],
            dobConfirm: (dob, age) => [
                `Got it! Date of birth ${dob}, which makes you ${age} years old. Your information is being processed intelligently.`,
                `Perfect! Born on ${dob}, age ${age}. The AI is updating your profile.`,
                `Thank you! Date of birth ${dob} - I've calculated your age as ${age} years and updated your medical profile.`
            ],
            phoneRequest: [
                "I'll need your phone number for appointment confirmations. What's your number?",
                "Could you provide your contact number? This helps us reach you if needed.",
                "What's the best phone number to reach you at?"
            ],
            medicalContext: [
                "Now let's discuss your medical needs. This helps me provide better assistance.",
                "I'm switching to medical mode. Tell me about your symptoms or concerns.",
                "Let's focus on your health. What brings you to the hospital today?"
            ],
            smartTransition: (fromField, toField) => {
                const transitions = {
                    'name-dob': "Great! Now that I know who you are, let's get your date of birth for medical records.",
                    'dob-phone': "Perfect! Now I need a way to contact you. What's your country code and phone number?", 
                    'phone-address': "Excellent! Could you share your address for our records?",
                    'address-symptoms': "Now let's discuss your medical needs. What symptoms brought you here today?",
                    'symptoms-allergies': "Important question: Do you have any known allergies I should note?",
                    'allergies-medications': "Are you currently taking any medications?",
                    'medications-history': "Finally, any previous medical history I should be aware of?"
                };
                return transitions[`${fromField}-${toField}`] || "Let's move to the next question.";
            },
            understanding: [
                "I understand. Let me process that information.",
                "I see. That's been noted in your profile.",
                "Understood. The AI system is learning about your needs.",
                "Got it! I'm building a comprehensive picture of your situation."
            ],
            completion: [
                "Excellent! I've gathered all the necessary information. Your AI-assisted registration is complete!",
                "Perfect! The intelligent system has processed all your data. You're all set!",
                "Wonderful! Your smart registration is finished. The AI has prepared everything for your visit."
            ]
        };
        
        // Select random response from appropriate category
        const getRandomResponse = (category) => {
            if (Array.isArray(category)) {
                return category[Math.floor(Math.random() * category.length)];
            }
            return category;
        };
        
        switch (intent) {
            case 'greeting':
                return getRandomResponse(responses.greeting);
            case 'nameRequest':
                return getRandomResponse(responses.nameRequest);
            case 'nameConfirm':
                return getRandomResponse(responses.nameConfirm(userData.name));
            case 'dobRequest':
                return getRandomResponse(responses.dobRequest);
            case 'dobConfirm':
                return getRandomResponse(responses.dobConfirm(userData.dob, userData.age));
            case 'phoneRequest':
                return getRandomResponse(responses.phoneRequest);
            case 'medicalContext':
                return getRandomResponse(responses.medicalContext);
            case 'understanding':
                return getRandomResponse(responses.understanding);
            case 'completion':
                return getRandomResponse(responses.completion);
            case 'transition':
                return responses.smartTransition(context.from, context.to);
            default:
                return getRandomResponse(this.aiKnowledge.confirmations);
        }
    }
    
    // Intelligent context analyzer - simulates AI understanding
    analyzeUserContext(input, currentField) {
        const analysis = {
            confidence: 0,
            intent: 'unknown',
            sentiment: 'neutral',
            entities: [],
            nextAction: 'continue'
        };
        
        const lowercaseInput = input.toLowerCase();
        
        // Analyze sentiment
        const positiveWords = ['good', 'fine', 'great', 'excellent', 'yes', 'okay', 'sure'];
        const negativeWords = ['bad', 'terrible', 'no', 'not', 'none', 'never'];
        const urgentWords = ['urgent', 'emergency', 'severe', 'intense', 'critical'];
        
        if (positiveWords.some(word => lowercaseInput.includes(word))) {
            analysis.sentiment = 'positive';
        } else if (negativeWords.some(word => lowercaseInput.includes(word))) {
            analysis.sentiment = 'negative';
        } else if (urgentWords.some(word => lowercaseInput.includes(word))) {
            analysis.sentiment = 'urgent';
        }
        
        // Detect intent based on context
        if (currentField === 'symptoms' && (lowercaseInput.includes('pain') || lowercaseInput.includes('hurt'))) {
            analysis.intent = 'pain_report';
            analysis.confidence = 0.9;
        } else if (lowercaseInput.includes('skip') || lowercaseInput.includes('next')) {
            analysis.intent = 'skip_field';
            analysis.confidence = 0.95;
        } else if (lowercaseInput.includes('help') || lowercaseInput.includes('confused')) {
            analysis.intent = 'need_help';
            analysis.confidence = 0.9;
        }
        
        return analysis;
    }

    provideCorrectionFeedback(originalInput, before, after) {
        // Provide user feedback when voice corrections are applied
        const correctedInput = this.applyVoiceCorrections(originalInput);
        const lowercaseOriginal = originalInput.toLowerCase();
        
        // Check if gender was corrected to male
        if (!before.gender && after.gender === 'male') {
            // Check for various "male" misrecognitions
            const maleVariants = ['mail', 'maile', 'mael', 'mal', 'mel', 'meil', 'maol', 'meile', 'mayl', 'mayel'];
            const foundVariant = maleVariants.find(variant => 
                lowercaseOriginal.includes(variant) && 
                !lowercaseOriginal.includes('email') && 
                !lowercaseOriginal.includes('@')
            );
            
            if (foundVariant) {
                const feedback = `Perfect! I understood you said 'male' - voice recognition sometimes picks up '${foundVariant}' but I corrected it automatically!`;
                this.addMessage('ai', feedback);
                console.log('Provided correction feedback for male variant:', foundVariant);
                return;
            }
        }
        
        // Check if gender was corrected to female
        if (!before.gender && after.gender === 'female') {
            const femaleVariants = ['femail', 'femaile', 'fem ale', 'femal', 'femeil'];
            const foundVariant = femaleVariants.find(variant => lowercaseOriginal.includes(variant));
            
            if (foundVariant) {
                const feedback = `Perfect! I understood you said 'female' and corrected the voice recognition automatically.`;
                this.addMessage('ai', feedback);
                console.log('Provided correction feedback for female variant:', foundVariant);
                return;
            }
        }
        
        // General positive feedback for successful gender detection
        if (!before.gender && after.gender && this.conversationContext.lastQuestion === 'gender') {
            console.log('Gender successfully detected and recorded');
        }
    }

    // Helper function to convert spoken numbers to digits
    convertSpokenNumbersToDigits(input) {
        const numberWords = {
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
            'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
            'eleven': '11', 'twelve': '12', 'thirteen': '13', 'fourteen': '14', 'fifteen': '15',
            'sixteen': '16', 'seventeen': '17', 'eighteen': '18', 'nineteen': '19', 'twenty': '20',
            'thirty': '30', 'forty': '40', 'fifty': '50', 'sixty': '60', 'seventy': '70',
            'eighty': '80', 'ninety': '90', 'hundred': '100', 'thousand': '1000',
            'twenty one': '21', 'twenty two': '22', 'twenty three': '23', 'twenty four': '24',
            'twenty five': '25', 'twenty six': '26', 'twenty seven': '27', 'twenty eight': '28',
            'twenty nine': '29', 'thirty one': '31', 'thirty two': '32'
        };
        
        // Handle year patterns like "two thousand five" -> "2005"
        let result = input.toLowerCase();
        
        // Convert "two thousand" patterns
        result = result.replace(/two thousand/g, '2000');
        result = result.replace(/nineteen (\w+)/g, (match, part) => {
            const yearPart = numberWords[part] || part;
            return '19' + yearPart.padStart(2, '0');
        });
        
        // Convert individual number words
        for (const [word, digit] of Object.entries(numberWords)) {
            const regex = new RegExp(`\\b${word}\\b`, 'g');
            result = result.replace(regex, digit);
        }
        
        return result;
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
