"""
Prediction Functions for Smartphone Health and Habit Tracking System
=====================================================================

This module loads trained models using joblib and provides prediction
functions that accept user input as dictionaries.

Models (located at project root):
- sleep_model.pkl
- study_model.pkl
- stress_model.pkl
- health_model.pkl
- stress_label_encoder.pkl (falls back to inline encoder in stress_model.pkl)

Functions:
- predict_sleep(data)
- predict_study(data)
- predict_stress(data)
- predict_health(data)
"""

import joblib
import numpy as np
import pandas as pd
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')


# ---------------------------------------------------------------------------
# Helper analysis utilities
# ---------------------------------------------------------------------------

def _compute_contributions(values_dict, keys):
    """Return percentage contribution of each key relative to the sum of absolute values."""
    total = sum(abs(values_dict.get(k, 0)) for k in keys)
    if total <= 0:
        return {k: 0.0 for k in keys}
    return {k: round(100.0 * abs(values_dict.get(k, 0)) / total, 1) for k in keys}


def _classify_score(score: float) -> str:
    """Map numeric score to a human-friendly category."""
    if score >= 85:
        return "Great"
    if score >= 70:
        return "Good"
    if score >= 50:
        return "Normal"
    if score >= 30:
        return "Moderate"
    return "Bad"


def _get_recommendations(category: str) -> list:
    """Return a list of recommendations for a given category or stress level."""
    recs = {
        "Great": [
            "Keep up the excellent habits!",
            "Continue maintaining your routine.",
        ],
        "Good": [
            "You're doing well – stay consistent.",
            "Small tweaks can push you to 'Great'.",
        ],
        "Normal": [
            "Consider making modest improvements.",
            "Track habits closely and set small goals.",
        ],
        "Moderate": [
            "Try adjusting your schedule or habits.",
            "Focus on one area at a time to improve.",
        ],
        "Bad": [
            "Major changes may be needed; start today.",
            "Seek support or professional advice if necessary.",
        ],
        # stress-specific
        "Low": [
            "You're in a good place; keep relaxing activities.",
        ],
        "Medium": [
            "Incorporate short breaks and mindfulness.",
            "Limit screen time and notifications.",
        ],
        "High": [
            "Practice meditation or deep‑breathing exercises.",
            "Consider talking to someone you trust.",
        ],
    }
    return recs.get(category, [])


def _create_explanation(contribs: dict) -> str:
    """Generate a brief explanation string from contribution percentages."""
    if not contribs:
        return ""
    sorted_feats = sorted(contribs.items(), key=lambda kv: kv[1], reverse=True)
    top = [k for k, _ in sorted_feats[:2]]
    if len(top) == 1:
        return f"Most of the score was influenced by {top[0]}."
    return f"Key factors were {top[0]} and {top[1]}."

# ============================================================================
# MODEL LOADING (using joblib)
# ============================================================================

# .pkl files live at project root (one level above backend/)
_BASE = Path(__file__).resolve().parent.parent


def _load(name):
    """Helper to load a .pkl file with joblib, falling back to pickle."""
    path = _BASE / name
    if not path.exists():
        raise FileNotFoundError(f"{name} not found. Please run ml_pipeline.py first.")
    try:
        return joblib.load(path)
    except Exception:
        import pickle
        with open(path, 'rb') as f:
            return pickle.load(f)


def load_sleep_model():
    data = _load('sleep_model.pkl')
    return data['model'], data['scaler'], data['feature_cols']


def load_study_model():
    data = _load('study_model.pkl')
    return data['model'], data['scaler'], data['feature_cols']


def load_stress_model():
    data = _load('stress_model.pkl')
    label_encoder = data.get('label_encoder', None)
    if label_encoder is None:
        label_encoder = _load('stress_label_encoder.pkl')
    return data['model'], data['scaler'], label_encoder, data['feature_cols']


def load_health_model():
    data = _load('health_model.pkl')
    return data['model'], data['scaler'], data['feature_cols']


# ============================================================================
# SLEEP SCORE PREDICTION
# ============================================================================

def predict_sleep(data):
    """
    Predict sleep score from user input.

    Parameters
    ----------
    data : dict
        Keys: sleep_hours, screen_time_before_sleep, notifications_night,
              heart_rate, steps_today

    Returns
    -------
    dict  –  { "prediction": <float> }  or  { "error": "..." }
    """
    try:
        model, scaler, feature_cols = load_sleep_model()

        features_dict = {
            'sleep_hours':       float(data.get('sleep_hours', 7)),
            'screen_time_before_sleep': float(data.get('screen_time_before_sleep', 120)),
            'notifications_night':      float(data.get('notifications_night', 10)),
            'heart_rate':               float(data.get('heart_rate', 70)),
            'steps_today':              float(data.get('steps_today', 8000)),
            'deep_sleep_hours':         float(data.get('deep_sleep_hours', 2.0)),
            'night_phone_usage':        float(data.get('night_phone_usage', 20.0)),
            'sleep_interruption':       float(data.get('sleep_interruption', 1)),
            'wake_time':                float(data.get('wake_time', 6.8)),
            'noise_level':              float(data.get('noise_level', 3)),
            'ambient_light_level':      float(data.get('ambient_light_level', 2)),
        }

        # Fill lag features expected by the model with current values
        for lag in [1, 2, 3]:
            for col in ['sleep_hours', 'screen_time_before_sleep',
                        'notifications_night', 'heart_rate', 'steps_today']:
                features_dict[f'{col}_lag_{lag}'] = features_dict.get(col, 0)

        feature_array = np.array(
            [features_dict.get(col, 0) for col in feature_cols]
        ).reshape(1, -1)

        feature_scaled = scaler.transform(feature_array)
        prediction = model.predict(feature_scaled)[0]
        prediction = max(0, min(100, prediction))
        score = round(float(prediction), 1)

        # analysis / breakdown
        orig_keys = [
            'sleep_hours','screen_time_before_sleep','notifications_night','heart_rate','steps_today',
            'deep_sleep_hours','night_phone_usage','sleep_interruption','wake_time','noise_level','ambient_light_level'
        ]
        contributions = _compute_contributions(features_dict, orig_keys)
        category = _classify_score(score)
        recommendations = _get_recommendations(category)
        explanation = _create_explanation(contributions)

        return {
            'prediction': score,
            'category': category,
            'contributions': contributions,
            'recommendations': recommendations,
            'explanation': explanation,
        }
    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# STUDY SCORE PREDICTION
# ============================================================================

def predict_study(data):
    """
    Predict study score from user input.

    Parameters
    ----------
    data : dict
        Keys: screen_time, productive_usage, social_usage, gaming_usage,
              notifications, unlock_count

    Returns
    -------
    dict  –  { "prediction": <float> }  or  { "error": "..." }
    """
    try:
        model, scaler, feature_cols = load_study_model()

        features_dict = {
            'screen_time':       float(data.get('screen_time', 5)),
            'productive_usage':  float(data.get('productive_usage', 2)),
            'social_usage':      float(data.get('social_usage', 2)),
            'gaming_usage':      float(data.get('gaming_usage', 1)),
            'notifications':     float(data.get('notifications', 100)),
            'unlock_count':      float(data.get('unlock_count', 50)),
            'study_hours':           float(data.get('study_hours', 3.5)),
            'app_switching_frequency': float(data.get('app_switching_frequency', 20)),
            'notifications_during_study': float(data.get('notifications_during_study', 8)),
            'break_frequency':       float(data.get('break_frequency', 3)),
            'phone_usage_during_study': float(data.get('phone_usage_during_study', 35.0)),
            'completed_tasks':       float(data.get('completed_tasks', 6)),
        }

        # Fill lag features
        for lag in [1, 2, 3]:
            for col in ['screen_time', 'productive_usage', 'social_usage',
                        'gaming_usage', 'notifications', 'unlock_count']:
                features_dict[f'{col}_lag_{lag}'] = features_dict.get(col, 0)

        feature_array = np.array(
            [features_dict.get(col, 0) for col in feature_cols]
        ).reshape(1, -1)

        feature_scaled = scaler.transform(feature_array)
        prediction = model.predict(feature_scaled)[0]
        prediction = max(0, min(100, prediction))
        score = round(float(prediction), 1)

        orig_keys = [
            'screen_time','productive_usage','social_usage','gaming_usage','notifications','unlock_count',
            'study_hours','app_switching_frequency','notifications_during_study',
            'break_frequency','phone_usage_during_study','completed_tasks'
        ]
        contributions = _compute_contributions(features_dict, orig_keys)
        category = _classify_score(score)
        recommendations = _get_recommendations(category)
        explanation = _create_explanation(contributions)

        return {
            'prediction': score,
            'category': category,
            'contributions': contributions,
            'recommendations': recommendations,
            'explanation': explanation,
        }
    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# STRESS LEVEL PREDICTION
# ============================================================================

def predict_stress(data):
    """
    Predict stress level from user input.

    Parameters
    ----------
    data : dict
        Keys: screen_time, notifications, unlock_count, sleep_hours,
              steps, heart_rate, social_usage, gaming_usage

    Returns
    -------
    dict  –  { "stress_level": "Medium" }  or  { "error": "..." }
    """
    try:
        model, scaler, label_encoder, feature_cols = load_stress_model()

        features_dict = {
            'screen_time':   float(data.get('screen_time', 6)),
            'notifications': float(data.get('notifications', 200)),
            'unlock_count':  float(data.get('unlock_count', 60)),
            'sleep_hours':   float(data.get('sleep_hours', 6)),
            'steps':         float(data.get('steps', 5000)),
            'heart_rate':    float(data.get('heart_rate', 75)),
            'social_usage':  float(data.get('social_usage', 3)),
            'gaming_usage':  float(data.get('gaming_usage', 1)),
        }

        feature_array = np.array(
            [features_dict.get(col, 0) for col in feature_cols]
        ).reshape(1, -1)

        feature_scaled = scaler.transform(feature_array)

        prediction_encoded = model.predict(feature_scaled)[0]
        stress_level = label_encoder.inverse_transform([prediction_encoded])[0]
        # compute contributions on the inputs used
        orig_keys = ['screen_time','notifications','unlock_count',
                     'sleep_hours','steps','heart_rate',
                     'social_usage','gaming_usage']
        contributions = _compute_contributions(features_dict, orig_keys)
        recommendations = _get_recommendations(stress_level)
        explanation = _create_explanation(contributions)
        return {
            'stress_level': str(stress_level),
            'contributions': contributions,
            'recommendations': recommendations,
            'explanation': explanation,
        }
    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# HEALTH SCORE PREDICTION
# ============================================================================

def predict_health(data):
    """
    Predict overall health score from user input.

    Parameters
    ----------
    data : dict
        Keys: sleep_hours, steps, calories, heart_rate, screen_time,
              social_usage, gaming_usage, productive_usage,
              notifications, unlock_count

    Returns
    -------
    dict  –  { "prediction": <float> }  or  { "error": "..." }
    """
    try:
        model, scaler, feature_cols = load_health_model()

        features_dict = {
            'sleep_hours':       float(data.get('sleep_hours', 7)),
            'steps':             float(data.get('steps', 8000)),
            'calories':          float(data.get('calories', 2100)),
            'heart_rate':        float(data.get('heart_rate', 70)),
            'screen_time':       float(data.get('screen_time', 5)),
            'social_usage':      float(data.get('social_usage', 2)),
            'gaming_usage':      float(data.get('gaming_usage', 1)),
            'productive_usage':  float(data.get('productive_usage', 2)),
            'notifications':     float(data.get('notifications', 120)),
            'unlock_count':      float(data.get('unlock_count', 40)),
        }

        feature_array = np.array(
            [features_dict.get(col, 0) for col in feature_cols]
        ).reshape(1, -1)

        feature_scaled = scaler.transform(feature_array)
        prediction = model.predict(feature_scaled)[0]
        prediction = max(0, min(100, prediction))
        score = round(float(prediction), 1)

        orig_keys = ['sleep_hours','steps','calories','heart_rate','screen_time',
                     'social_usage','gaming_usage','productive_usage',
                     'notifications','unlock_count']
        contributions = _compute_contributions(features_dict, orig_keys)
        category = _classify_score(score)
        recommendations = _get_recommendations(category)
        explanation = _create_explanation(contributions)

        return {
            'prediction': score,
            'category': category,
            'contributions': contributions,
            'recommendations': recommendations,
            'explanation': explanation,
        }
    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# BACKWARD-COMPATIBLE ALIASES
# ============================================================================
predict_sleep_score  = predict_sleep
predict_study_score  = predict_study
predict_stress_level = predict_stress
predict_health_score = predict_health


def predict_all(user_data):
    """Make all predictions for a user (convenience wrapper)."""
    return {
        'sleep':  predict_sleep(user_data),
        'study':  predict_study(user_data),
        'stress': predict_stress(user_data),
        'health': predict_health(user_data),
        'timestamp': pd.Timestamp.now().isoformat(),
    }


# ============================================================================
# QUICK SELF-TEST
# ============================================================================

if __name__ == '__main__':
    test_data = {
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

    print("Sleep :", predict_sleep(test_data))
    print("Study :", predict_study(test_data))
    print("Stress:", predict_stress(test_data))
    print("Health:", predict_health(test_data))
