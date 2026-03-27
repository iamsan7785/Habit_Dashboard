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

Run:
    cd backend
    pip install -r ../ml_requirements.txt
    python ml_api.py

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
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, make_response, send_from_directory

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
logging.basicConfig(level=logging.INFO)
app.secret_key = 'habit_dashboard_secret_key_2026'


def _disable_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


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


@app.route('/download-apk')
def download_apk():
    """Force-download the Android APK from static/app."""
    return send_from_directory(
        directory=os.path.join(app.static_folder, 'app'),
        path='HabitCheck.apk',
        as_attachment=True,
        download_name='HabitCheck.apk',
    )


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
    '6a804b1ecaa99679':{
        'name': 'Santanu',
        'greeting': 'We are excited to have you back! Here are your latest insights:',
    },
    '5963bd75800cd9c3':{
        'name':'Barsha',
        'greeting':'We are excited to have you back! Here are your lastest insights:',
    },
    '52348a32095f973e':{
        'name':'Shruti',
        'greeting':'We are excited to have you back! Here are your lastest insights:',
    },
    'aeafcd077dfda43a':{
        'name':'Deep',
        'greeting':'We are excited to have you back! Here are your lastest insights:',
    }
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
    return _disable_cache(make_response(render_template('results.html')))


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
        from backend.predictions import predict_stress
        result = predict_stress(user_data)
        if isinstance(result, dict) and 'stress_score' in result and result['stress_score'] is not None:
            return float(result['stress_score'])
    except Exception:
        pass
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
        logging.info('Received sleep prediction input: %s', data)
        result = predict_sleep(data)
        if 'error' in result:
            return _disable_cache(jsonify(result)), 400
        return _disable_cache(jsonify(result)), 200
    except Exception as e:
        logging.error('Sleep prediction failed', exc_info=True)
        return _disable_cache(jsonify({'error': str(e)})), 500


@app.route('/predict_study', methods=['POST'])
def api_predict_study():
    try:
        data = request.get_json(force=True)
        logging.info('Received study prediction input: %s', data)
        result = predict_study(data)
        if 'error' in result:
            return _disable_cache(jsonify(result)), 400
        return _disable_cache(jsonify(result)), 200
    except Exception as e:
        logging.error('Study prediction failed', exc_info=True)
        return _disable_cache(jsonify({'error': str(e)})), 500


@app.route('/predict_stress', methods=['POST'])
def api_predict_stress():
    try:
        data = request.get_json(force=True)
        logging.info('Received stress prediction input: %s', data)
        result = predict_stress(data)
        if 'error' in result:
            return _disable_cache(jsonify(result)), 400
        return _disable_cache(jsonify(result)), 200
    except Exception as e:
        logging.error('Stress prediction failed', exc_info=True)
        return _disable_cache(jsonify({'error': str(e)})), 500


@app.route('/predict_health', methods=['POST'])
def api_predict_health():
    try:
        data = request.get_json(force=True)
        logging.info('Received health prediction input: %s', data)
        result = predict_health(data)
        if 'error' in result:
            return _disable_cache(jsonify(result)), 400
        return _disable_cache(jsonify(result)), 200
    except Exception as e:
        logging.error('Health prediction failed', exc_info=True)
        return _disable_cache(jsonify({'error': str(e)})), 500


# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    print("\n  HabitCheck AI — Health & Habit Dashboard")
    print("  =========================================")
    print(f"  http://127.0.0.1:{port}/           → Home (landing)")
    print(f"  http://127.0.0.1:{port}/login      → Login")
    print(f"  http://127.0.0.1:{port}/dashboard  → Dashboard")
    print(f"  http://127.0.0.1:{port}/sleep      → Sleep prediction")
    print(f"  http://127.0.0.1:{port}/study      → Study prediction")
    print(f"  http://127.0.0.1:{port}/stress     → Stress prediction")
    print(f"  http://127.0.0.1:{port}/overall    → Health prediction\n")
    app.run(debug=True, port=port)
