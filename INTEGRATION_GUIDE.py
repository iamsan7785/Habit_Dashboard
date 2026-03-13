"""
Flask App Integration Example
=============================

Example of how to integrate the ML pipeline into your existing Flask app (app.py).
"""

# ============================================================================
# INTEGRATION GUIDE FOR app.py
# ============================================================================

"""
Step 1: Add imports to your app.py
----------------------------------

from flask import Blueprint, request, jsonify
from ml_api import ml_bp
from predictions import predict_all, predict_sleep_score, predict_study_score, predict_stress_level, predict_health_score


Step 2: Register the Blueprint
------------------------------

app = Flask(__name__)
app.register_blueprint(ml_bp)


Step 3: Example routes to add to app.py
---------------------------------------
"""

# Example routes for integration:

def get_app_integration_code():
    """
    Get example integration code for app.py
    """
    return """
# In your main app.py

from flask import Flask, render_template, request, jsonify
from ml_api import ml_bp
from predictions import predict_all

app = Flask(__name__)

# Register ML API Blueprint
app.register_blueprint(ml_bp)


# Example: Dashboard route that loads predictions
@app.route('/dashboard')
def dashboard():
    '''Display dashboard with health metrics'''
    return render_template('dashboard.html')


# Example: Get current user predictions
@app.route('/api/current-health', methods=['GET'])
def current_health():
    '''Get current user health data from database and make predictions'''
    try:
        # Example: Get user's current data from database or request
        user_data = {
            'sleep_hours': 6.5,
            'screen_time_before_sleep': 45,
            'notifications_night': 12,
            'heart_rate': 72,
            'steps_today': 8500,
            'screen_time': 5.5,
            'productive_usage': 2.0,
            'social_usage': 2.5,
            'gaming_usage': 1.0,
            'notifications': 120,
            'unlock_count': 45,
            'steps': 8500,
            'calories': 2100,
        }
        
        # Get all predictions
        results = predict_all(user_data)
        
        return jsonify({
            'success': True,
            'data': results,
            'timestamp': results['timestamp']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Example: Update predictions based on form submission
@app.route('/api/update-metrics', methods=['POST'])
def update_metrics():
    '''Update user metrics and get new predictions'''
    try:
        data = request.get_json()
        
        # Store in database if needed
        # db.save_user_metrics(current_user.id, data)
        
        # Get predictions
        results = predict_all(data)
        
        return jsonify({
            'success': True,
            'predictions': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""


# ============================================================================
# JAVASCRIPT FRONTEND INTEGRATION
# ============================================================================

def get_frontend_integration_code():
    """
    Get example JavaScript code for frontend integration.
    """
    return """
<!-- In your template (e.g., templates/dashboard.html) -->

<script>
// Fetch predictions from API
async function loadPredictions() {
    try {
        const response = await fetch('/api/predict/all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sleep_hours: document.getElementById('sleep_hours').value || 7,
                screen_time_before_sleep: document.getElementById('screen_time_before_sleep').value || 120,
                notifications_night: document.getElementById('notifications_night').value || 10,
                heart_rate: document.getElementById('heart_rate').value || 70,
                steps_today: document.getElementById('steps_today').value || 8000,
                screen_time: document.getElementById('screen_time').value || 5,
                productive_usage: document.getElementById('productive_usage').value || 2,
                social_usage: document.getElementById('social_usage').value || 2,
                gaming_usage: document.getElementById('gaming_usage').value || 1,
                notifications: document.getElementById('notifications').value || 100,
                unlock_count: document.getElementById('unlock_count').value || 50,
                steps: document.getElementById('steps').value || 8000,
                calories: document.getElementById('calories').value || 2100
            })
        });
        
        const results = await response.json();
        
        // Update UI with predictions
        displaySleepScore(results.sleep);
        displayStudyScore(results.study);
        displayStressLevel(results.stress);
        displayHealthScore(results.health);
        
    } catch (error) {
        console.error('Error loading predictions:', error);
    }
}

// Display sleep score
function displaySleepScore(data) {
    document.getElementById('sleep-score').textContent = data.sleep_score;
    document.getElementById('sleep-interpretation').textContent = data.interpretation;
    updateProgress('sleep-progress', data.sleep_score);
}

// Display study score
function displayStudyScore(data) {
    document.getElementById('study-score').textContent = data.study_score;
    document.getElementById('study-interpretation').textContent = data.interpretation;
    updateProgress('study-progress', data.study_score);
}

// Display stress level
function displayStressLevel(data) {
    const stressElement = document.getElementById('stress-level');
    stressElement.textContent = data.stress_level;
    stressElement.className = 'stress-' + data.stress_level.toLowerCase();
    
    const riskFactors = document.getElementById('risk-factors');
    riskFactors.innerHTML = data.risk_factors
        .map(factor => `<li>${factor}</li>`)
        .join('');
    
    const recommendations = document.getElementById('stress-recommendations');
    recommendations.innerHTML = data.recommendations
        .map(rec => `<li>${rec}</li>`)
        .join('');
}

// Display health score
function displayHealthScore(data) {
    document.getElementById('health-score').textContent = data.health_score;
    document.getElementById('health-status').textContent = data.health_status;
    updateProgress('health-progress', data.health_score);
    
    // Display component scores
    const components = data.component_scores;
    document.getElementById('sleep-component').textContent = components.sleep.toFixed(1);
    document.getElementById('activity-component').textContent = components.activity.toFixed(1);
    document.getElementById('nutrition-component').textContent = components.nutrition.toFixed(1);
    document.getElementById('hr-component').textContent = components.heart_rate.toFixed(1);
    document.getElementById('screen-component').textContent = components.screen_time.toFixed(1);
    document.getElementById('productivity-component').textContent = components.productivity.toFixed(1);
}

// Update progress bar
function updateProgress(elementId, value) {
    const element = document.getElementById(elementId);
    element.style.width = value + '%';
    element.textContent = value.toFixed(1);
}

// Load predictions on page load
document.addEventListener('DOMContentLoaded', function() {
    loadPredictions();
    
    // Reload predictions when user updates data
    document.getElementById('update-btn').addEventListener('click', loadPredictions);
    
    // Also reload every 5 minutes if auto-update is enabled
    if (document.getElementById('auto-update').checked) {
        setInterval(loadPredictions, 5 * 60 * 1000);
    }
});
</script>
"""


# ============================================================================
# HTML TEMPLATE EXAMPLE
# ============================================================================

def get_template_example():
    """
    Get example HTML template for dashboard.
    """
    return """
<!-- templates/dashboard.html -->

{% extends 'base.html' %}

{% block content %}
<div class="dashboard-container">
    
    <!-- Input Form -->
    <div class="form-section">
        <h2>Update Your Health Metrics</h2>
        <form id="metrics-form">
            
            <!-- Sleep Section -->
            <fieldset>
                <legend>Sleep Metrics</legend>
                <div class="form-group">
                    <label>Sleep Hours: 
                        <input type="number" id="sleep_hours" step="0.1" min="0" max="12" value="7">
                    </label>
                </div>
                <div class="form-group">
                    <label>Screen Time Before Sleep (minutes):
                        <input type="number" id="screen_time_before_sleep" min="0" max="300" value="120">
                    </label>
                </div>
                <div class="form-group">
                    <label>Night Notifications:
                        <input type="number" id="notifications_night" min="0" max="100" value="10">
                    </label>
                </div>
                <div class="form-group">
                    <label>Heart Rate:
                        <input type="number" id="heart_rate" min="40" max="120" value="70">
                    </label>
                </div>
                <div class="form-group">
                    <label>Steps Today:
                        <input type="number" id="steps_today" min="0" max="50000" value="8000">
                    </label>
                </div>
            </fieldset>
            
            <!-- Daily Usage Section -->
            <fieldset>
                <legend>Daily Usage</legend>
                <div class="form-group">
                    <label>Screen Time (hours):
                        <input type="number" id="screen_time" step="0.5" min="0" max="24" value="5">
                    </label>
                </div>
                <div class="form-group">
                    <label>Productive Usage (hours):
                        <input type="number" id="productive_usage" step="0.5" min="0" max="12" value="2">
                    </label>
                </div>
                <div class="form-group">
                    <label>Social Media Usage (hours):
                        <input type="number" id="social_usage" step="0.5" min="0" max="12" value="2">
                    </label>
                </div>
                <div class="form-group">
                    <label>Gaming Usage (hours):
                        <input type="number" id="gaming_usage" step="0.5" min="0" max="12" value="1">
                    </label>
                </div>
                <div class="form-group">
                    <label>Notifications:
                        <input type="number" id="notifications" min="0" max="500" value="100">
                    </label>
                </div>
                <div class="form-group">
                    <label>Phone Unlocks:
                        <input type="number" id="unlock_count" min="0" max="500" value="50">
                    </label>
                </div>
            </fieldset>
            
            <!-- Health Section -->
            <fieldset>
                <legend>Health Metrics</legend>
                <div class="form-group">
                    <label>Steps:
                        <input type="number" id="steps" min="0" max="50000" value="8000">
                    </label>
                </div>
                <div class="form-group">
                    <label>Calories:
                        <input type="number" id="calories" min="800" max="4000" value="2100">
                    </label>
                </div>
            </fieldset>
            
            <button type="button" id="update-btn" class="btn btn-primary">Update Predictions</button>
            <label>
                <input type="checkbox" id="auto-update"> Auto-update every 5 minutes
            </label>
        </form>
    </div>
    
    <!-- Predictions Display -->
    <div class="predictions-section">
        
        <!-- Sleep Score -->
        <div class="card sleep-card">
            <h3>Sleep Score</h3>
            <div class="score-display">
                <div class="score-value" id="sleep-score">--</div>
                <div class="score-max">/100</div>
            </div>
            <div class="score-bar">
                <div class="progress-fill" id="sleep-progress"></div>
            </div>
            <p id="sleep-interpretation" class="interpretation"></p>
        </div>
        
        <!-- Study Score -->
        <div class="card study-card">
            <h3>Study Score</h3>
            <div class="score-display">
                <div class="score-value" id="study-score">--</div>
                <div class="score-max">/100</div>
            </div>
            <div class="score-bar">
                <div class="progress-fill" id="study-progress"></div>
            </div>
            <p id="study-interpretation" class="interpretation"></p>
        </div>
        
        <!-- Stress Level -->
        <div class="card stress-card">
            <h3>Stress Level</h3>
            <div class="stress-display">
                <span id="stress-level" class="stress-badge">--</span>
            </div>
            <div>
                <h4>Risk Factors:</h4>
                <ul id="risk-factors"></ul>
            </div>
            <div>
                <h4>Recommendations:</h4>
                <ul id="stress-recommendations"></ul>
            </div>
        </div>
        
        <!-- Health Score -->
        <div class="card health-card">
            <h3>Overall Health Score</h3>
            <div class="score-display">
                <div class="score-value" id="health-score">--</div>
                <div class="score-max">/100</div>
            </div>
            <div class="score-bar">
                <div class="progress-fill" id="health-progress"></div>
            </div>
            <p><strong>Status:</strong> <span id="health-status">--</span></p>
            
            <div class="component-scores">
                <h4>Component Breakdown:</h4>
                <div class="component-item">
                    <span>Sleep Quality:</span>
                    <strong id="sleep-component">--</strong>
                </div>
                <div class="component-item">
                    <span>Activity Level:</span>
                    <strong id="activity-component">--</strong>
                </div>
                <div class="component-item">
                    <span>Nutrition:</span>
                    <strong id="nutrition-component">--</strong>
                </div>
                <div class="component-item">
                    <span>Heart Rate:</span>
                    <strong id="hr-component">--</strong>
                </div>
                <div class="component-item">
                    <span>Screen Time:</span>
                    <strong id="screen-component">--</strong>
                </div>
                <div class="component-item">
                    <span>Productivity:</span>
                    <strong id="productivity-component">--</strong>
                </div>
            </div>
        </div>
        
    </div>
    
</div>

<!-- Load the JavaScript -->
<script src="{{ url_for('static', filename='predictions.js') }}"></script>

{% endblock %}
"""


# ============================================================================
# DATABASE EXAMPLE
# ============================================================================

def get_database_integration():
    """
    Get example of how to integrate with database.
    """
    return """
# In a models.py or db.py file

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserMetrics(db.Model):
    '''Store user health metrics for tracking'''
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Sleep metrics
    sleep_hours = db.Column(db.Float)
    screen_time_before_sleep = db.Column(db.Float)
    notifications_night = db.Column(db.Integer)
    
    # Daily usage
    screen_time = db.Column(db.Float)
    productive_usage = db.Column(db.Float)
    social_usage = db.Column(db.Float)
    gaming_usage = db.Column(db.Float)
    notifications = db.Column(db.Integer)
    unlock_count = db.Column(db.Integer)
    
    # Health metrics
    heart_rate = db.Column(db.Float)
    steps = db.Column(db.Integer)
    calories = db.Column(db.Integer)
    
    def to_dict(self):
        '''Convert to dictionary for predictions'''
        return {
            'sleep_hours': self.sleep_hours,
            'screen_time_before_sleep': self.screen_time_before_sleep,
            'notifications_night': self.notifications_night,
            'screen_time': self.screen_time,
            'productive_usage': self.productive_usage,
            'social_usage': self.social_usage,
            'gaming_usage': self.gaming_usage,
            'notifications': self.notifications,
            'unlock_count': self.unlock_count,
            'heart_rate': self.heart_rate,
            'steps': self.steps,
            'calories': self.calories,
        }


class PredictionResult(db.Model):
    '''Store prediction results for history/analytics'''
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Predictions
    sleep_score = db.Column(db.Float)
    study_score = db.Column(db.Float)
    stress_level = db.Column(db.String(20))
    health_score = db.Column(db.Float)
    
    # Full prediction data (JSON)
    prediction_data = db.Column(db.JSON)


# Usage in app.py
@app.route('/api/metrics', methods=['POST'])
def save_metrics():
    from predictions import predict_all
    
    data = request.get_json()
    
    # Save metrics to database
    metrics = UserMetrics(
        user_id=current_user.id,
        sleep_hours=data.get('sleep_hours'),
        screen_time_before_sleep=data.get('screen_time_before_sleep'),
        # ... other fields
    )
    db.session.add(metrics)
    
    # Get predictions
    predictions = predict_all(data)
    
    # Save prediction results
    result = PredictionResult(
        user_id=current_user.id,
        sleep_score=predictions['sleep']['sleep_score'],
        study_score=predictions['study']['study_score'],
        stress_level=predictions['stress']['stress_level'],
        health_score=predictions['health']['health_score'],
        prediction_data=predictions
    )
    db.session.add(result)
    db.session.commit()
    
    return jsonify({'success': True, 'predictions': predictions})
"""


if __name__ == '__main__':
    print("=" * 80)
    print("FLASK APPLICATION INTEGRATION GUIDE")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print("1. MAIN APP INTEGRATION CODE")
    print("=" * 80)
    print(get_app_integration_code())
    
    print("\n" + "=" * 80)
    print("2. JAVASCRIPT FRONTEND CODE")
    print("=" * 80)
    print(get_frontend_integration_code())
    
    print("\n" + "=" * 80)
    print("3. HTML TEMPLATE EXAMPLE")
    print("=" * 80)
    print(get_template_example())
    
    print("\n" + "=" * 80)
    print("4. DATABASE INTEGRATION")
    print("=" * 80)
    print(get_database_integration())
    
    print("\n" + "=" * 80)
    print("INTEGRATION GUIDE COMPLETE")
    print("=" * 80)
