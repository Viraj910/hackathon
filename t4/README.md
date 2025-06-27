# Hospital Form-Filling Website with Voice Input

A professional hospital patient admission form built with Flask, featuring voice input capabilities for easy form filling.

## 🌟 Features

- **Professional UI**: Clean, modern design with Bootstrap 5
- **Voice Input**: Click microphone buttons to speak and auto-fill form fields
- **Smart Voice Recognition**: Automatically detects and formats:
  - Age (converts word numbers to digits)
  - Gender (recognizes "male", "female", "other")
  - Blood groups (recognizes spoken blood types)
- **Form Validation**: Real-time validation with visual feedback
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Data Storage**: Saves form submissions to JSON file
- **Admin Dashboard**: View all submitted forms at `/view_submissions`
- **Accessibility**: Keyboard navigation and screen reader support

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Modern web browser (Chrome, Edge, Firefox, Safari)
- Microphone access for voice input

### Installation

1. **Clone or download this project**
   ```bash
   cd hospital-form-app
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to: http://localhost:5000

## 📱 How to Use

### Form Filling
1. Fill out the patient admission form
2. Use voice input by clicking the 🎤 microphone button next to any field
3. Speak clearly when prompted
4. Required fields are marked with *
5. Submit the form when complete

### Voice Input Tips
- **Age**: Say "twenty five" or "25"
- **Gender**: Say "male", "female", or "other"
- **Blood Group**: Say "A positive", "B negative", "O positive", etc.
- **Names/Addresses**: Speak clearly and naturally
- **Phone Numbers**: Say digits clearly with pauses

### Keyboard Shortcuts
- **Alt + V**: Start voice input for focused field
- **Escape**: Stop voice recognition
- **Tab**: Navigate between fields

## 🏥 Form Sections

### Personal Information
- Full Name
- Age
- Gender
- Phone Number
- Email Address
- Address

### Medical Information
- Blood Group
- Emergency Contact
- Known Allergies
- Medical History
- Reason for Visit

### Insurance Information
- Insurance Provider
- Insurance ID

## 🔧 Technical Details

### Project Structure
```
hospital-form-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── form_data.json        # Stored form submissions (auto-created)
├── static/
│   ├── css/
│   │   └── styles.css    # Custom CSS styles
│   └── js/
│       └── voice.js      # Voice recognition JavaScript
└── templates/
    ├── form.html         # Main form template
    ├── success.html      # Success page template
    └── admin.html        # Admin dashboard template
```

### Browser Compatibility
- **Chrome**: Full support (recommended)
- **Edge**: Full support
- **Firefox**: Limited voice support
- **Safari**: Limited voice support

### Voice Recognition
- Uses Web Speech API (webkitSpeechRecognition)
- Supports English (US) by default
- Can be configured for other languages in `voice.js`
- Fallback gracefully when voice not supported

## 🚀 Advanced Usage

### Admin Dashboard
Visit http://localhost:5000/view_submissions to see all form submissions.

### Customization
- **Colors/Styling**: Edit `static/css/styles.css`
- **Form Fields**: Modify `templates/form.html`
- **Voice Recognition**: Configure `static/js/voice.js`
- **Server Settings**: Adjust `app.py`

### Language Support
To change voice recognition language, edit line in `voice.js`:
```javascript
recognition.lang = 'en-IN'; // For Indian English
recognition.lang = 'es-ES'; // For Spanish
```

## 🔒 Security & Privacy

- Form data is stored locally in `form_data.json`
- No data is sent to external servers
- Voice processing happens in the browser
- HTTPS recommended for production deployment

## 🐛 Troubleshooting

### Voice Input Not Working
1. **Check browser compatibility** (use Chrome or Edge)
2. **Allow microphone access** when prompted
3. **Check microphone connection** in system settings
4. **Ensure HTTPS** for production sites (required by some browsers)

### Form Validation Errors
- Check that all required fields (*) are filled
- Verify phone numbers and email formats
- Ensure age is between 1-120

### Server Issues
- Check Python version (3.7+)
- Verify Flask installation: `pip show flask`
- Check port 5000 availability
- Look for error messages in terminal

## 📧 Support

For issues or questions:
1. Check browser console for JavaScript errors
2. Verify all files are in correct locations
3. Check Python/Flask installation
4. Review error messages in terminal

## 🎯 Future Enhancements

- Database integration (SQLite/PostgreSQL)
- User authentication and roles
- Email notifications
- PDF generation for forms
- Multi-language support
- Advanced voice commands
- Integration with hospital management systems

## 📄 License

This project is open source and available under the MIT License.

---

**Made with ❤️ for better healthcare accessibility**
