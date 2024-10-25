from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from functools import wraps
from datetime import datetime
import json
import requests

app = Flask(__name__)
app.secret_key = "a secret key"  # As per blueprint recommendation
socketio = SocketIO(app)

# Hardcoded password as specified
PASSWORD = "3987q89deb789dnq98a8dnal2neoiedn1209e"

# Time tracking data
TIME_DATA = [
    {"date": "10/17", "hours": 0.2, "day": "Thu", "formattedTime": "0:12", "hourlyPay": True},
    {"date": "10/18", "hours": 0.2, "day": "Fri", "formattedTime": "0:12", "hourlyPay": True},
    {"date": "10/19", "hours": 3.02, "day": "Sat", "formattedTime": "3:01", "hourlyPay": True},
    {"date": "10/20", "hours": 3, "day": "Sun", "formattedTime": "3:00", "hourlyPay": True},
    {"date": "10/21", "hours": 9.55, "day": "Mon", "formattedTime": "9:33", "hourlyPay": True},
    {"date": "10/22", "hours": 2.33, "day": "Tue", "formattedTime": "2:20", "hourlyPay": True},
    {"date": "10/23", "hours": 4.4, "day": "Wed", "formattedTime": "4:24", "hourlyPay": True},
    {"date": "10/24", "hours": 4.77, "day": "Thu", "formattedTime": "4:46", "hourlyPay": False},
    {"date": "10/25", "hours": 3.02, "day": "Fri", "formattedTime": "3:01", "hourlyPay": False}
]

# Word count data storage
WORD_COUNT_DATA = []
WORD_COUNT_LOGS = []

def get_location_from_ip(ip):
    try:
        if ip in ['127.0.0.1', 'localhost', '0.0.0.0']:
            return "Local Development"
            
        response = requests.get(f'https://ipapi.co/{ip}/json/')
        if response.status_code == 200:
            data = response.json()
            city = data.get('city', 'Unknown City')
            country = data.get('country_name', 'Unknown Country')
            return f"{city}, {country}"
    except:
        pass
    return "Unknown Location"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid password")
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', time_data=TIME_DATA, word_count_data=WORD_COUNT_DATA, word_count_logs=WORD_COUNT_LOGS)

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@socketio.on('word_count_entry')
def handle_word_count(data):
    # Create the entry with timestamp and location
    location = get_location_from_ip(request.remote_addr)
    entry = {
        'date': data['date'],
        'totalWords': data['totalWords'],
        'pricePerWord': data['pricePerWord'],
        'totalAmount': data['totalWords'] * data['pricePerWord'],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'location': location
    }
    
    # Update or add to word count data
    existing_entry = next((item for item in WORD_COUNT_DATA if item['date'] == entry['date']), None)
    if existing_entry:
        WORD_COUNT_DATA.remove(existing_entry)
    WORD_COUNT_DATA.append(entry)
    
    # Add to logs
    log_entry = {
        'timestamp': entry['timestamp'],
        'location': entry['location'],
        'date': entry['date'],
        'totalWords': entry['totalWords'],
        'totalAmount': entry['totalAmount']
    }
    WORD_COUNT_LOGS.append(log_entry)
    
    # Broadcast the updates to all clients
    emit('word_count_update', {
        'wordCountData': WORD_COUNT_DATA,
        'logs': WORD_COUNT_LOGS
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, use_reloader=True, log_output=True)
