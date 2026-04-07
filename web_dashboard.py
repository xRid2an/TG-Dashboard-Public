from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import threading

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'ganti_dengan_random_string_disini')

# Password dari environment variable
ADMIN_PASSWORD = os.getenv('DASHBOARD_PASSWORD', 'admin123')

# Path ke data bot
DATA_FILE = Path("data.json")
SERVICE_LIST_DIR = Path("service_list")

def load_bot_data():
    """Load data dari file bot"""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "muted": {}, "notifications": [], "service_enabled": True}

def get_total_numbers():
    """Hitung total nomor di semua service"""
    total = 0
    if SERVICE_LIST_DIR.exists():
        for folder in SERVICE_LIST_DIR.iterdir():
            if folder.is_dir():
                for file in folder.glob("*.txt"):
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        total += len([l for l in f.readlines() if l.strip()])
    return total

def get_service_stats():
    """Statistik per service"""
    stats = []
    if SERVICE_LIST_DIR.exists():
        for folder in SERVICE_LIST_DIR.iterdir():
            if folder.is_dir():
                total = 0
                for file in folder.glob("*.txt"):
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        total += len([l for l in f.readlines() if l.strip()])
                stats.append({
                    "name": folder.name,
                    "total": total,
                    "files": len(list(folder.glob("*.txt")))
                })
    return sorted(stats, key=lambda x: x['total'], reverse=True)

# HTML Template untuk dashboard
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TG Bot Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            color: #333;
            font-size: 24px;
        }
        .logout-btn {
            background: #e53e3e;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 8px;
            transition: 0.3s;
        }
        .logout-btn:hover {
            background: #c53030;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-card h3 {
            color: #667eea;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .stat-card .value {
            font-size: 36px;
            font-weight: bold;
            color: #333;
        }
        .stat-card .unit {
            font-size: 14px;
            color: #666;
            margin-left: 5px;
        }
        .section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th {
            background: #f7f7f7;
            color: #667eea;
            font-weight: 600;
        }
        tr:hover {
            background: #f9f9f9;
        }
        .service-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }
        .service-item {
            background: #f7f7f7;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .service-name {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .service-stats {
            color: #666;
            font-size: 14px;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            background: #5a67d8;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Telegram Bot Dashboard</h1>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Users</h3>
                <div class="value">{{ total_users }}</div>
            </div>
            <div class="stat-card">
                <h3>Total Numbers</h3>
                <div class="value">{{ total_numbers }}</div>
            </div>
            <div class="stat-card">
                <h3>Active Today</h3>
                <div class="value">{{ active_today }}</div>
            </div>
            <div class="stat-card">
                <h3>Muted Users</h3>
                <div class="value">{{ muted_users }}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Service Statistics</h2>
            <div class="service-list">
                {% for service in services %}
                <div class="service-item">
                    <div class="service-name">{{ service.name }}</div>
                    <div class="service-stats">
                        📁 {{ service.files }} files | 🔢 {{ service.total }} numbers
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="section">
            <h2>👥 Recent Users</h2>
            <table>
                <thead>
                    <tr><th>User ID</th><th>Name</th><th>Last Active</th><th>Total Seen</th></tr>
                </thead>
                <tbody>
                    {% for user in recent_users %}
                    <tr>
                        <td>{{ user.id }}</td>
                        <td>{{ user.name }}</td>
                        <td>{{ user.last_active }}</td>
                        <td>{{ user.total_seen }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>🔇 Muted Users</h2>
            <table>
                <thead>
                    <tr><th>User ID</th><th>Muted Since</th><th>Type</th></tr>
                </thead>
                <tbody>
                    {% for muted in muted_list %}
                    <tr>
                        <td>{{ muted.id }}</td>
                        <td>{{ muted.since }}</td>
                        <td>{{ muted.type }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        // Auto refresh every 30 seconds
        setInterval(() => {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return '''
        <form method="post" style="text-align:center; margin-top:100px;">
            <h2>Login Dashboard</h2>
            <input type="password" name="password" placeholder="Password" required style="padding:10px; margin:10px;">
            <button type="submit" style="padding:10px 20px;">Login</button>
        </form>
        ''', 401
    return '''
    <form method="post" style="text-align:center; margin-top:100px;">
        <h2>Login Dashboard</h2>
        <input type="password" name="password" placeholder="Password" required style="padding:10px; margin:10px;">
        <button type="submit" style="padding:10px 20px;">Login</button>
    </form>
    '''

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    data = load_bot_data()
    
    # Hitung statistik
    total_users = len(data.get('users', {}))
    muted_users = len(data.get('muted', {}))
    
    # Hitung active today (users yang aktif dalam 24 jam)
    today_cutoff = datetime.now() - timedelta(hours=24)
    active_today = 0
    recent_users_list = []
    
    for uid, user_data in data.get('users', {}).items():
        last_active = user_data.get('last_active', '')
        if last_active:
            try:
                last_active_dt = datetime.fromisoformat(last_active)
                if last_active_dt > today_cutoff:
                    active_today += 1
                # Ambil 20 user terbaru
                if len(recent_users_list) < 20:
                    recent_users_list.append({
                        'id': uid,
                        'name': user_data.get('full_name', 'Unknown')[:30],
                        'last_active': last_active_dt.strftime('%Y-%m-%d %H:%M'),
                        'total_seen': user_data.get('total_seen', 0)
                    })
            except:
                pass
    
    # Muted users list
    muted_list = []
    for uid, mute_data in data.get('muted', {}).items():
        muted_list.append({
            'id': uid,
            'since': datetime.fromisoformat(mute_data.get('at', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M'),
            'type': 'Permanent' if mute_data.get('permanent') else 'Temporary'
        })
    
    return render_template_string(
        HTML_TEMPLATE,
        total_users=total_users,
        total_numbers=get_total_numbers(),
        active_today=active_today,
        muted_users=muted_users,
        services=get_service_stats(),
        recent_users=recent_users_list,
        muted_list=muted_list
    )

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/ping')
def ping():
    """Endpoint untuk keep alive"""
    return "OK", 200

@app.route('/api/stats')
def api_stats():
    """API endpoint untuk monitoring"""
    data = load_bot_data()
    return jsonify({
        'status': 'active',
        'total_users': len(data.get('users', {})),
        'total_numbers': get_total_numbers(),
        'timestamp': datetime.now().isoformat()
    })

def run_dashboard():
    """Jalankan Flask server"""
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
