from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Get form data
        data = request.form.to_dict()
        
        # Add timestamp
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to JSON file (optional)
        save_form_data(data)
        
        return render_template('ai_success.html', data=data)
    
    return render_template('ai_form.html')

@app.route('/legacy', methods=['GET', 'POST'])
def legacy_form():
    """Legacy form for comparison"""
    if request.method == 'POST':
        # Get form data
        data = request.form.to_dict()
        
        # Add timestamp
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to JSON file (optional)
        save_form_data(data)
        
        return render_template('success.html', data=data)
    
    return render_template('form.html')

def save_form_data(data):
    """Save form data to JSON file"""
    file_path = 'form_data.json'
    
    # Load existing data if file exists
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []
    
    # Add new entry
    existing_data.append(data)
    
    # Save back to file
    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=2)

@app.route('/view_submissions')
def view_submissions():
    """View all form submissions (admin view)"""
    file_path = 'form_data.json'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    
    return render_template('admin.html', submissions=data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)