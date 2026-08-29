"""
Simple Web Server for QR Code Battery Information Display
Serves battery information pages when QR codes are scanned
"""

from flask import Flask, render_template_string, jsonify
import json
from pathlib import Path

app = Flask(__name__)

# HTML template for battery information display
BATTERY_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EV Battery Passport - {{ battery.passport_id }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .section {
            margin-bottom: 25px;
        }
        
        .section h2 {
            color: #1E3A8A;
            font-size: 1.5em;
            margin-bottom: 15px;
            border-bottom: 3px solid #3B82F6;
            padding-bottom: 10px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .info-item {
            background: #F0F9FF;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #3B82F6;
        }
        
        .info-item label {
            display: block;
            color: #1E3A8A;
            font-weight: bold;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .info-item span {
            color: #000;
            font-size: 1.1em;
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .status-good {
            background: #10B981;
            color: white;
        }
        
        .status-warning {
            background: #F59E0B;
            color: white;
        }
        
        .status-danger {
            background: #EF4444;
            color: white;
        }
        
        .footer {
            background: #1E3A8A;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }
        
        .error {
            background: #FEF2F2;
            border: 2px solid #EF4444;
            color: #DC2626;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔋 EV Battery Passport</h1>
            <p>Secure Battery Identification System</p>
        </div>
        
        <div class="content">
            {% if battery %}
            <div class="section">
                <h2>📋 Battery Information</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <label>Passport ID</label>
                        <span>{{ battery.passport_id }}</span>
                    </div>
                    <div class="info-item">
                        <label>Manufacturer</label>
                        <span>{{ battery.manufacturer }}</span>
                    </div>
                    <div class="info-item">
                        <label>Battery Type</label>
                        <span>{{ battery.battery_type }}</span>
                    </div>
                    <div class="info-item">
                        <label>Capacity</label>
                        <span>{{ battery.capacity_kwh }} kWh</span>
                    </div>
                    <div class="info-item">
                        <label>Production Date</label>
                        <span>{{ battery.production_date }}</span>
                    </div>
                    <div class="info-item">
                        <label>Data Source</label>
                        <span>{{ battery.data_source }}</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🏥 Health Status</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <label>Health Status</label>
                        <span class="status-badge status-{{ 'good' if battery.health_status in ['EXCELLENT', 'GOOD'] else 'warning' if battery.health_status in ['FAIR', 'DEGRADED'] else 'danger' }}">
                            {{ battery.health_status }}
                        </span>
                    </div>
                    <div class="info-item">
                        <label>State of Health (SoH)</label>
                        <span>{{ battery.soh }}%</span>
                    </div>
                    <div class="info-item">
                        <label>State of Charge (SoC)</label>
                        <span>{{ battery.soc }}%</span>
                    </div>
                    <div class="info-item">
                        <label>Total Cycles</label>
                        <span>{{ battery.total_cycles }}</span>
                    </div>
                    <div class="info-item">
                        <label>Temperature</label>
                        <span>{{ battery.temperature_celsius }}°C</span>
                    </div>
                    <div class="info-item">
                        <label>Temperature Status</label>
                        <span>{{ battery.temperature_status }}</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Performance Metrics</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <label>Degradation Rate</label>
                        <span>{{ "%.4f"|format(battery.degradation_per_cycle|float) }}% per cycle</span>
                    </div>
                    <div class="info-item">
                        <label>User Wallet</label>
                        <span style="font-size: 0.9em;">{{ battery.user_wallet[:10] }}...{{ battery.user_wallet[-8:] }}</span>
                    </div>
                    {% if battery.registered_at %}
                    <div class="info-item">
                        <label>Registered At</label>
                        <span>{{ battery.registered_at }}</span>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% else %}
            <div class="error">
                <h2>❌ Battery Not Found</h2>
                <p>The requested battery passport could not be found in the system.</p>
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>EV Battery Passport System | Scan QR codes to view battery information</p>
        </div>
    </div>
</body>
</html>
"""


def load_battery_data(passport_id):
    """Load battery data from JSON files"""
    # Search in user entered batteries
    user_battery_file = Path("data/processed/user_entered_batteries.json")
    if user_battery_file.exists():
        try:
            with open(user_battery_file, 'r') as f:
                user_batteries = json.load(f)
                for battery in user_batteries:
                    if battery.get('passport_id') == passport_id:
                        return battery
        except Exception as e:
            print(f"Error loading user batteries: {e}")
    
    # Search in auto generated batteries
    auto_battery_file = Path("data/processed/auto_generated_batteries.json")
    if auto_battery_file.exists():
        try:
            with open(auto_battery_file, 'r') as f:
                auto_batteries = json.load(f)
                for battery in auto_batteries:
                    if battery.get('passport_id') == passport_id:
                        return battery
        except Exception as e:
            print(f"Error loading auto batteries: {e}")
    
    # Search in battery passports
    battery_passport_file = Path("data/processed/battery_passports.json")
    if battery_passport_file.exists():
        try:
            with open(battery_passport_file, 'r') as f:
                content = f.read().strip()
                if content:
                    battery_passports = json.loads(content)
                    if passport_id in battery_passports:
                        return battery_passports[passport_id]
        except Exception as e:
            print(f"Error loading battery passports: {e}")
    
    return None


def load_user_history(user_wallet):
    """Load all battery data for a specific user wallet"""
    all_batteries = []
    
    # Load from user entered batteries
    user_battery_file = Path("data/processed/user_entered_batteries.json")
    if user_battery_file.exists():
        try:
            with open(user_battery_file, 'r') as f:
                user_batteries = json.load(f)
                user_batteries = [b for b in user_batteries if b.get('user_wallet') == user_wallet]
                all_batteries.extend(user_batteries)
        except Exception as e:
            print(f"Error loading user batteries: {e}")
    
    # Load from auto generated batteries
    auto_battery_file = Path("data/processed/auto_generated_batteries.json")
    if auto_battery_file.exists():
        try:
            with open(auto_battery_file, 'r') as f:
                auto_batteries = json.load(f)
                auto_batteries = [b for b in auto_batteries if b.get('user_wallet') == user_wallet]
                all_batteries.extend(auto_batteries)
        except Exception as e:
            print(f"Error loading auto batteries: {e}")
    
    # Sort by timestamp
    all_batteries.sort(key=lambda x: x.get('timestamp', ''))
    
    return all_batteries


@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EV Battery Passport QR Server</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            h1 { color: #1E3A8A; }
            .info { background: #F0F9FF; padding: 20px; border-radius: 10px; margin: 20px; }
        </style>
    </head>
    <body>
        <h1>🔋 EV Battery Passport QR Server</h1>
        <div class="info">
            <p>This server displays battery information when QR codes are scanned.</p>
            <p>Access battery information at: <code>/battery/&lt;passport_id&gt;</code></p>
            <p>Example: <code>/battery/EV-BATT-20260711-12345</code></p>
        </div>
    </body>
    </html>
    """)


@app.route('/battery/<passport_id>')
def display_battery(passport_id):
    """Display battery information page"""
    try:
        battery = load_battery_data(passport_id)
        return render_template_string(BATTERY_TEMPLATE, battery=battery)
    except Exception as e:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { background: #FEF2F2; border: 2px solid #EF4444; color: #DC2626; padding: 20px; border-radius: 10px; }
            </style>
        </head>
        <body>
            <div class="error">
                <h2>Error Loading Battery Information</h2>
                <p>{{ error }}</p>
                <p>Passport ID: {{ passport_id }}</p>
            </div>
        </body>
        </html>
        """, error=str(e), passport_id=passport_id)


@app.route('/api/battery/<passport_id>')
def api_battery(passport_id):
    """API endpoint for battery data"""
    battery = load_battery_data(passport_id)
    if battery:
        return jsonify({"status": "success", "data": battery})
    else:
        return jsonify({"status": "error", "message": "Battery not found"}), 404


# HTML template for user history display
USER_HISTORY_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Account History - {{ user_wallet[:12] }}...</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .content {
            padding: 30px;
        }
        
        .user-info {
            background: #F0F9FF;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 25px;
            border-left: 4px solid #3B82F6;
        }
        
        .timeline {
            margin-top: 25px;
        }
        
        .timeline-item {
            background: white;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            position: relative;
        }
        
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -15px;
            top: 20px;
            width: 12px;
            height: 12px;
            background: #3B82F6;
            border-radius: 50%;
        }
        
        .timeline-item h3 {
            color: #1E3A8A;
            margin-bottom: 10px;
        }
        
        .timeline-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .info-label {
            color: #6B7280;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .info-value {
            color: #1F2937;
            font-weight: 500;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .status-good {
            background: #10B981;
            color: white;
        }
        
        .status-warning {
            background: #F59E0B;
            color: white;
        }
        
        .status-danger {
            background: #EF4444;
            color: white;
        }
        
        .summary {
            background: #F0F9FF;
            padding: 20px;
            border-radius: 10px;
            margin-top: 25px;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .summary-item {
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 8px;
        }
        
        .summary-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #1E3A8A;
        }
        
        .summary-label {
            color: #6B7280;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .footer {
            background: #1E3A8A;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }
        
        .no-data {
            text-align: center;
            padding: 40px;
            color: #6B7280;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👤 User Account History</h1>
            <p>Complete Battery Entry Timeline</p>
        </div>
        
        <div class="content">
            <div class="user-info">
                <h2>Account Information</h2>
                <p><strong>Wallet:</strong> {{ user_wallet[:10] }}...{{ user_wallet[-8:] }}</p>
                <p><strong>Total Batteries:</strong> {{ batteries|length }}</p>
            </div>
            
            {% if batteries %}
            <div class="timeline">
                <h2 style="color: #1E3A8A; margin-bottom: 20px;">📅 Entry Timeline</h2>
                
                {% for battery in batteries %}
                <div class="timeline-item">
                    <h3>🔋 {{ battery.passport_id }}</h3>
                    <p style="color: #6B7280; font-size: 0.9em;">{{ battery.timestamp }}</p>
                    
                    <div class="timeline-info">
                        <div>
                            <div class="info-label">Manufacturer</div>
                            <div class="info-value">{{ battery.manufacturer }}</div>
                        </div>
                        <div>
                            <div class="info-label">Battery Type</div>
                            <div class="info-value">{{ battery.battery_type }}</div>
                        </div>
                        <div>
                            <div class="info-label">Capacity</div>
                            <div class="info-value">{{ battery.capacity_kwh }} kWh</div>
                        </div>
                        <div>
                            <div class="info-label">SoH</div>
                            <div class="info-value">{{ battery.soh }}%</div>
                        </div>
                        <div>
                            <div class="info-label">Cycles</div>
                            <div class="info-value">{{ battery.total_cycles }}</div>
                        </div>
                        <div>
                            <div class="info-label">Status</div>
                            <div class="info-value">
                                <span class="status-badge status-{{ 'good' if battery.health_status in ['EXCELLENT', 'GOOD'] else 'warning' if battery.health_status in ['FAIR', 'DEGRADED'] else 'danger' }}">
                                    {{ battery.health_status }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div class="summary">
                <h2 style="color: #1E3A8A; margin-bottom: 15px;">📊 Account Summary</h2>
                <div class="summary-grid">
                    <div class="summary-item">
                        <div class="summary-value">{{ batteries|length }}</div>
                        <div class="summary-label">Total Batteries</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value">{{ "%.1f"|format(batteries|map(attribute='soh')|sum / batteries|length) }}%</div>
                        <div class="summary-label">Avg SoH</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value">{{ "%.1f"|format(batteries|map(attribute='capacity_kwh')|sum) }} kWh</div>
                        <div class="summary-label">Total Capacity</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-value">{{ "%.0f"|format(batteries|map(attribute='total_cycles')|sum / batteries|length) }}</div>
                        <div class="summary-label">Avg Cycles</div>
                    </div>
                </div>
            </div>
            {% else %}
            <div class="no-data">
                <h2>📭 No Battery Records Found</h2>
                <p>This account has no battery entries yet.</p>
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>EV Battery Passport System | User Account History</p>
        </div>
    </div>
</body>
</html>
"""


@app.route('/user/<user_wallet>')
def display_user_history(user_wallet):
    """Display user account history page"""
    try:
        batteries = load_user_history(user_wallet)
        return render_template_string(USER_HISTORY_TEMPLATE, user_wallet=user_wallet, batteries=batteries)
    except Exception as e:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { background: #FEF2F2; border: 2px solid #EF4444; color: #DC2626; padding: 20px; border-radius: 10px; }
            </style>
        </head>
        <body>
            <div class="error">
                <h2>Error Loading User History</h2>
                <p>{{ error }}</p>
            </div>
        </body>
        </html>
        """, error=str(e))


@app.route('/api/user/<user_wallet>')
def api_user_history(user_wallet):
    """API endpoint for user history data"""
    batteries = load_user_history(user_wallet)
    if batteries:
        return jsonify({"status": "success", "data": batteries, "count": len(batteries)})
    else:
        return jsonify({"status": "error", "message": "No batteries found for this user"}), 404


if __name__ == '__main__':
    print("🚀 Starting EV Battery Passport QR Server...")
    print("📱 Access battery pages at: http://localhost:8000/battery/<passport_id>")
    app.run(host='0.0.0.0', port=8000, debug=True)
