"""
Flask API for HabitCheck AI — Health & Habit Monitoring
========================================================

Standalone Flask application that:
 1. Serves a public landing page at /
 2. Provides login via Firebase user_id
 3. Connects to Firebase Realtime Database via firebase_connection module
 4. Serves a dashboard with prediction options
 5. Serves prediction pages with inputs auto-filled from Firebase
 6. Exposes JSON prediction endpoints consumed by the frontend
 7. Supports cross-origin requests (CORS) for Lovable / React frontends

Run:
    cd backend
    pip install -r ../ml_requirements.txt
    python ml_api.py

Environment variables (see .env.example):
    FLASK_SECRET_KEY  — secret key for session signing
    CORS_ORIGINS      — comma-separated allowed origins (default: *)
    FLASK_ENV         — "development" | "production"

Flow:
    http://127.0.0.1:5000/           → Landing home page
    http://127.0.0.1:5000/login      → Login page
    http://127.0.0.1:5000/dashboard  → Prediction options (after login)
    http://127.0.0.1:5000/sleep      → Sleep prediction (auto-filled)
    http://127.0.0.1:5000/study      → Study prediction (auto-filled)
    http://127.0.0.1:5000/stress     → Stress prediction (auto-filled)
    http://127.0.0.1:5000/overall    → Health prediction (auto-filled)
"""

import os
import sys
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS

# Load .env before anything else so all os.environ reads see the values
load_dotenv()

# ---------------------------------------------------------------------------
# Path setup — templates & static live one level above backend/
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ensure the backend package is importable
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from backend.firebase_connection import (
    FirebaseConnectionError,
    get_latest_health_data,
    get_recent_health_data,
    verify_user,
)
from backend.predictions import (
    predict_sleep,
    predict_study,
    predict_stress,
    predict_health,
    load_stress_model,
)
from backend.analytics import (
    calculate_wellness_score,
    generate_insights,
    classify_personality,
    estimate_burnout_risk,
    detect_behavior_patterns,
    daily_summary,
    summarize_weekly_trends,
)

# ---------------------------------------------------------------------------
# Flask App
# ---------------------------------------------------------------------------
app = Flask(
    __name__,
    template_folder=os.path.join(_PROJECT_ROOT, 'templates'),
    static_folder=os.path.join(_PROJECT_ROOT, 'static'),
)
_secret_key = os.environ.get('FLASK_SECRET_KEY')
if not _secret_key:
    if os.environ.get('FLASK_ENV', 'development').lower() == 'production':
        raise RuntimeError(
            'FLASK_SECRET_KEY must be set in production. '
            'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
        )
    # Development fallback — insecure, only acceptable locally
    _secret_key = 'habit_dashboard_secret_key_2026'
app.secret_key = _secret_key

# ---------------------------------------------------------------------------
# CORS — allow requests from Lovable / React frontends
# Set CORS_ORIGINS in .env as a comma-separated list of allowed origins.
# Use * only for local development; always specify explicit origins in production.
# ---------------------------------------------------------------------------
_cors_origins_env = os.environ.get('CORS_ORIGINS', '').strip()
if _cors_origins_env == '*':
    _cors_origins: list | str = '*'
elif _cors_origins_env:
    _cors_origins = [o.strip() for o in _cors_origins_env.split(',') if o.strip()]
else:
    # No CORS_ORIGINS set — fail fast in production, open in development
    if os.environ.get('FLASK_ENV', 'development').lower() == 'production':
        raise RuntimeError(
            'CORS_ORIGINS must be set in production to restrict cross-origin access. '
            'Set it to a comma-separated list of allowed origins, e.g.: '
            'CORS_ORIGINS=https://your-app.lovable.app'
        )
    _cors_origins = '*'
CORS(app, origins=_cors_origins, supports_credentials=True)


# ============================================================================
# DECORATORS
# ============================================================================

def login_required(f):
    """Redirect to login page if no session user_id."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated


# ============================================================================
# PUBLIC PAGES
# ============================================================================

@app.route('/')
def home_page():
    """Landing home page — visible to everyone."""
    return render_template('home.html')


@app.route('/login', methods=['GET'])
def login_page():
    """Show login form."""
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def do_login():
    """Process login: validate user_id via Firebase, store in session."""
    user_id = (
        request.form.get('user_id')
        or (request.get_json(silent=True) or {}).get('user_id')
    )
    if not user_id:
        return render_template('login.html', error='Please enter a User ID.')

    try:
        if not verify_user(user_id):
            return render_template('login.html', error=f'User "{user_id}" not found in database.')
    except FirebaseConnectionError as exc:
        return render_template('login.html', error=str(exc)), 503

    session['user_id'] = user_id
    return redirect(url_for('dashboard_page'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home_page'))


# ============================================================================
# CUSTOM DISPLAY NAMES
# ============================================================================

USER_DISPLAY = {
    '6a804b1ecaa99679': {
        'name': 'Santanu',
        'greeting': 'We are excited to have you back! Here are your latest insights:',
    },
}


# ============================================================================
# DASHBOARD (after login)
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard_page():
    uid = session['user_id']
    info = USER_DISPLAY.get(uid, {})
    return render_template(
        'dashboard.html',
        user_id=uid,
        display_name=info.get('name', uid),
        greeting=info.get('greeting', ''),
    )


# ============================================================================
# PREDICTION PAGES
# ============================================================================

@app.route('/sleep')
@login_required
def sleep_page():
    return render_template('sleep.html')


@app.route('/study')
@login_required
def study_page():
    return render_template('study.html')


@app.route('/stress')
@login_required
def stress_page():
    return render_template('stress.html')


@app.route('/overall')
@login_required
def overall_page():
    return render_template('overall.html')

@app.route('/help')
@login_required
def help_page():
    """Simple help page showing usage instructions."""
    return render_template('help.html')


@app.route('/results')
@login_required
def results_page():
    """Render the shared results page; data is populated client-side."""
    return render_template('results.html')


# ============================================================================
# API — Firebase user data
# ============================================================================

@app.route('/api/user_data')
@login_required
def api_user_data():
    """Return the latest health_data for the session user as JSON."""
    user_id = session['user_id']
    try:
        data = get_latest_health_data(user_id)
    except FirebaseConnectionError as exc:
        return jsonify({'error': str(exc)}), 503

    if data is None:
        return jsonify({'error': 'No health data found for this user.'}), 404
    return jsonify(data), 200


def _compute_stress_probability(user_data: dict) -> float | None:
    """Return stress prediction probability (0-100) if available."""
    try:
        model, scaler, label_encoder, feature_cols = load_stress_model()
        # Prepare features the same way predict_stress does
        features = {
            'screen_time':   float(user_data.get('total_screen_time') or user_data.get('screen_time') or 0),
            'notifications': float(user_data.get('notification_count') or user_data.get('notifications') or 0),
            'unlock_count':  float(user_data.get('unlock_count') or 0),
            'sleep_hours':   float(user_data.get('sleep_hours') or 0),
            'steps':         float(user_data.get('steps') or user_data.get('steps_today') or 0),
            'heart_rate':    float(user_data.get('heart_rate') or 0),
            'social_usage':  float(user_data.get('social_usage') or 0),
            'gaming_usage':  float(user_data.get('gaming_usage') or 0),
        }
        feature_array = [features.get(col, 0) for col in feature_cols]
        feature_scaled = scaler.transform([feature_array])

        if not hasattr(model, 'predict_proba'):
            return None

        probs = model.predict_proba(feature_scaled)[0]
        pred = model.predict(feature_scaled)[0]
        # Find index of predicted class
        if hasattr(model, 'classes_'):
            labels = list(model.classes_)
            if pred in labels:
                idx = labels.index(pred)
                return round(float(probs[idx]) * 100.0, 1)
        return None
    except Exception:
        return None


@app.route('/api/dashboard')
@login_required
def api_dashboard():
    """Return a set of analytics for the dashboard.

    This endpoint is designed to power the new dashboard widgets with
    wellness scoring, insights, predictions, weekly trends, and more.
    """
    user_id = session['user_id']
    try:
        latest = get_latest_health_data(user_id)
        weekly = get_recent_health_data(user_id, days=7)
    except FirebaseConnectionError as exc:
        return jsonify({'error': str(exc)}), 503

    if not latest:
        return jsonify({'error': 'No health data found for this user.'}), 404

    # Draft out future prediction items
    stress_pred = predict_stress(latest)
    focus_pred = predict_study(latest)
    sleep_pred = predict_sleep(latest)
    stress_prob = _compute_stress_probability(latest)

    wellness = calculate_wellness_score({**latest, 'stress_level': stress_pred.get('stress_level')})
    insights = generate_insights(latest)
    personality = classify_personality(latest)
    burnout = estimate_burnout_risk({**latest, 'stress_level': stress_pred.get('stress_level')})
    patterns = detect_behavior_patterns({**latest, 'stress_level': stress_pred.get('stress_level')})
    summary_text = daily_summary(latest, predicted_stress=stress_pred.get('stress_level'))

    weekly_with_stress = []
    for entry in weekly:
        pred = predict_stress(entry)
        entry_copy = dict(entry)
        if 'stress_level' in pred:
            entry_copy['stress_level'] = pred['stress_level']
        weekly_with_stress.append(entry_copy)

    weekly_trends = summarize_weekly_trends(weekly_with_stress)
    # add simple AI-style insight for weekly habits
    from backend.analytics import generate_weekly_insight, generate_weekly_comparison
    weekly_insight = generate_weekly_insight(weekly_trends)
    weekly_comparison = generate_weekly_comparison(weekly_trends)

    sleep_risk = None
    try:
        if isinstance(sleep_pred, dict) and 'prediction' in sleep_pred:
            sleep_risk = round(max(0.0, min(100.0, 100.0 - float(sleep_pred['prediction']))), 1)
    except Exception:
        sleep_risk = None

    return jsonify({
        'wellness': wellness,
        'insights': insights,
        'future_prediction': {
            'stress': {
                'level': stress_pred.get('stress_level'),
                'probability': stress_prob,
            },
            'focus': {
                'score': focus_pred.get('prediction'),
            },
            'sleep_quality_risk': sleep_risk,
        },
        'weekly': weekly_trends,
        'weekly_insight': weekly_insight,
        'weekly_comparison': weekly_comparison,
        'personality': personality,
        'burnout': burnout,
        'patterns': patterns,
        'daily_summary': summary_text,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
    }), 200


# ============================================================================
# PREDICTION API ENDPOINTS (POST, JSON)
# ============================================================================

@app.route('/predict_sleep', methods=['POST'])
def api_predict_sleep():
    try:
        data = request.get_json(force=True)
        result = predict_sleep(data)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict_study', methods=['POST'])
def api_predict_study():
    try:
        data = request.get_json(force=True)
        result = predict_study(data)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict_stress', methods=['POST'])
def api_predict_stress():
    try:
        data = request.get_json(force=True)
        result = predict_stress(data)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict_health', methods=['POST'])
def api_predict_health():
    try:
        data = request.get_json(force=True)
        result = predict_health(data)
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    print("\n  HabitCheck AI — Health & Habit Dashboard")
    print("  =========================================")
    print("  http://127.0.0.1:5000/           → Home (landing)")
    print("  http://127.0.0.1:5000/login      → Login")
    print("  http://127.0.0.1:5000/dashboard  → Dashboard")
    print("  http://127.0.0.1:5000/sleep      → Sleep prediction")
    print("  http://127.0.0.1:5000/study      → Study prediction")
    print("  http://127.0.0.1:5000/stress     → Stress prediction")
    print("  http://127.0.0.1:5000/overall    → Health prediction\n")
    app.run(debug=True)
