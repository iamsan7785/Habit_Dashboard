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

import hashlib
import joblib
import logging
import numpy as np
import pandas as pd
import random
import warnings
from pathlib import Path

from backend.analytics import calculate_wellness_score

try:
    from backend.behavior_analysis import (
        generate_behavior_insights,
        generate_personalized_recommendations,
        generate_behavior_summary,
        detect_habits,
        calculate_risk_level,
        generate_ai_explanation,
    )
except ModuleNotFoundError:
    def _fallback_snapshot(inputs: dict) -> dict:
        def _num(*keys, default=0.0):
            for key in keys:
                if key in inputs and inputs.get(key) is not None:
                    try:
                        return float(inputs.get(key))
                    except (TypeError, ValueError):
                        continue
            return float(default)

        screen_raw = _num('screen_time_before_sleep', 'night_phone_usage', 'screen_time', default=0.0)
        screen_hours = screen_raw / 60.0 if screen_raw > 24 else screen_raw
        return {
            'screen_hours': max(0.0, screen_hours),
            'screen_time': max(0.0, _num('screen_time', default=0.0)),
            'social_usage': max(0.0, _num('social_usage', default=0.0)),
            'gaming_usage': max(0.0, _num('gaming_usage', default=0.0)),
            'productive_usage': max(0.0, _num('productive_usage', default=0.0)),
            'sleep_hours': max(0.0, _num('sleep_hours', default=7.0)),
            'steps_today': max(0.0, _num('steps_today', 'steps', default=5000.0)),
            'night_notifications': max(0.0, _num('night_notifications', 'notifications_night', 'notifications', default=0.0)),
            'heart_rate': max(0.0, _num('heart_rate', default=70.0)),
            'noise_level': max(0.0, _num('noise_level', default=30.0)),
            'sleep_interruptions': max(0.0, _num('sleep_interruptions', 'sleep_interruption', default=0.0)),
        }

    def _stable_choice(options: list[str], seed: str) -> str:
        """Return a consistent random choice based on a seed string."""
        if not options:
            return ''
        h = hashlib.sha256(seed.encode('utf-8')).hexdigest()
        rnd = random.Random(int(h[:8], 16))
        return rnd.choice(options)

    def generate_behavior_insights(inputs: dict) -> dict:
        # Normalize inputs to ensure stable behavior across similar values
        s = _fallback_snapshot(inputs)

        # Build a list of behavior points, each derived directly from inputs.
        points: list[str] = []

        # Screen time before sleep insights
        if s['screen_hours'] >= 3:
            templates = [
                "High screen exposure detected before sleep ({value:.1f}h). This level of digital stimulation may delay melatonin production and reduce sleep quality.",
                "Your evening screen exposure is elevated ({value:.1f}h). Extended device use at night can make it harder to fall asleep.",
                "Extended digital activity before bed ({value:.1f}h) can interfere with your body’s natural sleep cues.",
            ]
            points.append(_stable_choice(templates, f"screen_before_sleep:{s['screen_hours']:.2f}").format(value=s['screen_hours']))
        elif s['screen_hours'] >= 1.5:
            templates = [
                "Moderate screen usage before sleep ({value:.1f}h). Try minimizing bright screens as bedtime approaches.",
                "Screen time before bed is noticeable ({value:.1f}h). Reducing it may help your sleep cycle.",
            ]
            points.append(_stable_choice(templates, f"screen_before_sleep:{s['screen_hours']:.2f}").format(value=s['screen_hours']))
        else:
            templates = [
                "Screen exposure before bed is low ({value:.1f}h). This supports better sleep readiness.",
                "You keep evening screen time minimal ({value:.1f}h), which typically supports clearer sleep cues.",
            ]
            points.append(_stable_choice(templates, f"screen_before_sleep:{s['screen_hours']:.2f}").format(value=s['screen_hours']))

        # Physical activity insight
        if s['steps_today'] >= 6000:
            templates = [
                "Strong daily movement pattern detected ({value} steps). Physical activity at this level usually supports better sleep recovery.",
                "Good step count today ({value} steps). This level of activity often helps regulate sleep cycles.",
                "You logged {value} steps — that level of movement can help your body wind down more naturally.",
            ]
            points.append(_stable_choice(templates, f"steps_today:{int(s['steps_today'])}").format(value=int(s['steps_today'])))
        elif s['steps_today'] >= 3000:
            templates = [
                "Moderate activity today ({value} steps). A bit more movement could improve sleep depth.",
                "You walked {value} steps — adding a short walk could help strengthen sleep recovery.",
            ]
            points.append(_stable_choice(templates, f"steps_today:{int(s['steps_today'])}").format(value=int(s['steps_today'])))
        else:
            templates = [
                "Low daily movement detected ({value} steps). A short walk could improve mood and sleep regulation.",
                "With just {value} steps, consider light activity to support better sleep and stress management.",
            ]
            points.append(_stable_choice(templates, f"steps_today:{int(s['steps_today'])}").format(value=int(s['steps_today'])))

        # Sleep interruptions
        if s['sleep_interruptions'] > 2:
            templates = [
                "Frequent sleep interruptions detected ({value}). Interrupted sleep cycles can reduce deep sleep quality.",
                "You had {value} awakenings. This level of disruption makes it harder to get restorative sleep.",
            ]
            points.append(_stable_choice(templates, f"sleep_interruptions:{s['sleep_interruptions']:.1f}").format(value=s['sleep_interruptions']))
        else:
            templates = [
                "Sleep interruptions appear low ({value}), which supports more restorative sleep cycles.",
                "Fewer interruptions ({value}) suggest a calmer sleep environment.",
            ]
            points.append(_stable_choice(templates, f"sleep_interruptions:{s['sleep_interruptions']:.1f}").format(value=s['sleep_interruptions']))

        # Night notifications
        if s['night_notifications'] > 60:
            templates = [
                "Elevated nighttime notification activity ({value}). Frequent alerts may prevent the brain from reaching deep sleep stages.",
                "Your phone received {value} notifications at night. This level of disturbance can fragment sleep.",
            ]
            points.append(_stable_choice(templates, f"night_notifications:{int(s['night_notifications'])}").format(value=int(s['night_notifications'])))
        else:
            templates = [
                "Nighttime notifications are relatively low ({value}). This can help maintain deeper sleep stages.",
                "You received {value} notifications overnight — staying under 60 often supports better sleep continuity.",
            ]
            points.append(_stable_choice(templates, f"night_notifications:{int(s['night_notifications'])}").format(value=int(s['night_notifications'])))

        # Behavioral summary pattern
        if s['screen_hours'] >= 3 and s['sleep_interruptions'] > 2:
            pattern = "Possible lifestyle pattern: High evening screen use combined with interrupted sleep suggests your nighttime routine could be affecting rest quality."
        elif s['screen_hours'] >= 3:
            pattern = "Possible lifestyle pattern: Evening digital engagement is high; reducing it may improve sleep readiness."
        elif s['steps_today'] < 3000 and s['sleep_hours'] < 6:
            pattern = "Possible lifestyle pattern: Low daily activity and short sleep suggest the body may not be getting enough recovery time."
        else:
            pattern = "Possible lifestyle pattern: Your routine shows moderate digital engagement with some late-evening screen exposure."

        return {
            'digital_mind_mirror': {
                'title': 'Digital Mind Mirror',
                'reflection': 'Your recent behavior suggests:',
                'points': points,
                'possible_pattern': pattern,
            },
            'behavior_insights': points,
        }

    def generate_personalized_recommendations(inputs: dict) -> list:
        s = _fallback_snapshot(inputs)
        recs: list[str] = []

        if s['screen_hours'] > 3:
            templates = [
                "Reduce screen exposure at least 45 minutes before bedtime to help the brain transition into sleep mode.",
                "Try cutting off screen time 45 minutes before bed; this can ease the transition into sleep.",
            ]
            recs.append(_stable_choice(templates, f"rec_screen_before_sleep:{s['screen_hours']:.2f}"))

        if s['night_notifications'] > 50:
            templates = [
                "Enable 'Do Not Disturb' mode or silence non-essential notifications during sleep hours.",
                "Try muting notifications overnight to limit sleep disruption from frequent alerts.",
            ]
            recs.append(_stable_choice(templates, f"rec_night_notifications:{int(s['night_notifications'])}"))

        if s['steps_today'] < 3000:
            templates = [
                "Try adding a short walk or light activity during the day to improve sleep regulation.",
                "A brief mid-day walk could help boost daily activity and support better rest at night.",
            ]
            recs.append(_stable_choice(templates, f"rec_steps_today:{int(s['steps_today'])}"))

        if s['social_usage'] > s.get('productive_usage', 0) * 3:
            templates = [
                "Balancing social media usage with productive tasks may improve focus and daily efficiency.",
                "If social browsing feels excessive, try swapping one social session for a short productive habit.",
            ]
            recs.append(_stable_choice(templates, f"rec_social_vs_productive:{s['social_usage']:.2f}-{s.get('productive_usage', 0):.2f}"))

        if s['gaming_usage'] > 2:
            templates = [
                "Long gaming sessions close to bedtime may increase mental stimulation. Consider ending sessions earlier in the evening.",
                "If gaming extends late into the night, try shifting playtime earlier to help wind down.",
            ]
            recs.append(_stable_choice(templates, f"rec_gaming_usage:{s['gaming_usage']:.2f}"))

        if s['sleep_hours'] < 6:
            templates = [
                "Aim for at least 7–8 hours of sleep to support cognitive recovery and overall health.",
                "Increasing sleep duration to 7–8 hours can greatly improve mental clarity and resilience.",
            ]
            recs.append(_stable_choice(templates, f"rec_sleep_hours:{s['sleep_hours']:.2f}"))

        if not recs:
            recs.append("Keep tracking your habits—small adjustments over time can support better rest and focus.")

        return recs

    def generate_behavior_summary(inputs: dict) -> str:
        s = _fallback_snapshot(inputs)
        duration = "healthy duration" if s['sleep_hours'] >= 7 else "shorter duration"
        digital = "lower nighttime device interaction" if s['screen_hours'] < 2 else "increased nighttime device interaction"
        return f"Your sleep pattern today shows {duration} and {digital}."

    def detect_habits(inputs: dict) -> list:
        s = _fallback_snapshot(inputs)
        habits = []
        if s['screen_hours'] > 4:
            habits.append("Possible habit forming: extended device usage before bedtime.")
        if s['night_notifications'] > 80:
            habits.append("High nighttime notification activity may disrupt deep sleep cycles.")
        if s['steps_today'] < 1000:
            habits.append("Low daily movement detected which may reduce sleep recovery.")
        return habits or ["No high-risk habit signal detected; current pattern appears relatively stable."]

    def calculate_risk_level(inputs: dict) -> dict:
        s = _fallback_snapshot(inputs)
        score = (
            min(100.0, (s['screen_hours'] / 6.0) * 100.0) * 0.30
            + min(100.0, (s['sleep_interruptions'] / 6.0) * 100.0) * 0.25
            + min(100.0, (s['night_notifications'] / 120.0) * 100.0) * 0.20
            + min(100.0, s['noise_level']) * 0.10
            + min(100.0, max(0.0, (1 - s['steps_today'] / 8000.0) * 100.0)) * 0.15
        )
        level = "Low Risk" if score < 25 else "Moderate Risk" if score < 50 else "Elevated Risk" if score < 75 else "High Risk"
        return {'risk_score': round(score, 1), 'risk_level': level}

    def generate_ai_explanation(inputs: dict, prediction_score: float | None = None) -> str:
        s = _fallback_snapshot(inputs)
        base = (
            f"sleep duration ({s['sleep_hours']:.1f}h), heart rate ({s['heart_rate']:.0f} bpm), "
            f"and pre-sleep screen exposure ({s['screen_hours']:.1f}h)"
        )
        if prediction_score is None:
            return f"This prediction is influenced by {base}."
        return f"Your score is {prediction_score:.1f} because of {base}."

warnings.filterwarnings('ignore')


# ---------------------------------------------------------------------------
# Helper analysis utilities
# ---------------------------------------------------------------------------

def _clip_value(val, min_val, max_val):
    """Clip a numeric value to a safe range."""
    try:
        v = float(val)
    except (TypeError, ValueError):
        return min_val
    return max(min_val, min(max_val, v))


def _sanitize_stress_inputs(data: dict) -> dict:
    """Validate and normalize incoming stress feature inputs.

    This ensures real-life inputs are clamped to the ranges used during
    model training and prevents unrealistic inputs from destabilizing
    predictions.
    """

    def _first_numeric(*keys, default=0.0):
        for key in keys:
            if key in data and data.get(key) is not None:
                try:
                    return float(data.get(key))
                except (TypeError, ValueError):
                    continue
        return float(default)

    return {
        # Core features expected by the stress model (in training order)
        'screen_time':   _clip_value(_first_numeric('screen_time', 'total_screen_time'), 0, 14),
        'notifications': _clip_value(_first_numeric('notifications', 'notification_count'), 0, 300),
        'unlock_count':  _clip_value(_first_numeric('unlock_count'), 0, 200),
        'steps':         _clip_value(_first_numeric('steps', 'steps_today'), 0, 30000),
        'social_usage':  _clip_value(_first_numeric('social_usage'), 0, 8),
        'gaming_usage':  _clip_value(_first_numeric('gaming_usage'), 0, 6),
        'sleep_hours':   _clip_value(_first_numeric('sleep_hours'), 3, 12),
        'heart_rate':    _clip_value(_first_numeric('heart_rate'), 45, 120),

        # Additional features used by the model (maintained for compatibility)
        'daily_workload':      _clip_value(_first_numeric('daily_workload'), 0, 10),
        'deadline_pressure':   _clip_value(_first_numeric('deadline_pressure'), 0, 10),
        'mental_fatigue_score': _clip_value(_first_numeric('mental_fatigue_score'), 0, 100),
        'social_interactions': _clip_value(_first_numeric('social_interactions'), 0, 50),
        'relaxation_time':     _clip_value(_first_numeric('relaxation_time'), 0, 10),
        'mood_score':          _clip_value(_first_numeric('mood_score'), 0, 10),
    }


def _adjust_stress_score(raw_score: float | None, features: dict) -> float | None:
    """Apply a small, interpretable behavioral adjustment to the model score.

    This helps ensure stability and sensibility when small, real-world changes
    occur in key features (sleep, screen time, activity).
    """
    if raw_score is None:
        return None

    score = float(raw_score)

    # Small adjustments to improve sensitivity without overriding model output.
    adj = 0.0

    # More screen time → slightly higher stress
    adj += (features.get('screen_time', 0) - 5) * 0.5

    # More sleep → slightly lower stress
    adj -= max(0.0, features.get('sleep_hours', 7) - 7) * 0.5

    # More steps → slightly lower stress
    adj -= max(0.0, features.get('steps', 8000) - 8000) / 2000.0 * 2.0

    # Keep adjustments bounded to avoid overly large changes
    adj = max(-10.0, min(10.0, adj))

    return max(0.0, min(100.0, score + adj))


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


# Domain-specific weights and normalisation maxes
# -----------------------------------------------
# Study: only the 12 form inputs; study_hours carries the highest weight.
_STUDY_WEIGHTS = {
    'study_hours':                35,
    'productive_usage':           20,
    'screen_time':                15,
    'notifications':              10,
    'phone_usage_during_study':   10,
    'completed_tasks':             5,
    'break_frequency':             5,
    'app_switching_frequency':     4,
    'notifications_during_study':  4,
    'social_usage':                3,
    'gaming_usage':                3,
    'unlock_count':                2,
}
# Expected realistic maxima used for normalisation (minutes-based dataset)
_STUDY_MAXES = {
    'study_hours':                12,
    'productive_usage':           300,
    'screen_time':                600,
    'notifications':              500,
    'phone_usage_during_study':   300,
    'completed_tasks':            20,
    'break_frequency':            20,
    'app_switching_frequency':    100,
    'notifications_during_study': 200,
    'social_usage':               480,
    'gaming_usage':               240,
    'unlock_count':               500,
}

# ---------------------------------------------------------------------------
# Calibrated Study Score — signed weights + normalization maxes
# ---------------------------------------------------------------------------
# Normalization ceiling for each feature (matches the minutes-based dataset).
_STUDY_NORM_MAXES = {
    'study_hours':               10,
    'productive_usage':         300,
    'completed_tasks':           20,
    'screen_time':              600,
    'notifications':            200,
    'phone_usage_during_study': 120,
    'app_switching_frequency':   50,
    'break_frequency':           20,
    'social_usage':             300,
    'gaming_usage':             300,
    'notifications_during_study': 200,
    'unlock_count':             200,
}

# Positive weights increase the score; negative weights reduce it.
_STUDY_SCORE_WEIGHTS = {
    'study_hours':               0.30,
    'productive_usage':          0.20,
    'completed_tasks':           0.15,
    'screen_time':              -0.10,
    'notifications':            -0.10,
    'phone_usage_during_study': -0.05,
    'app_switching_frequency':  -0.05,
    'break_frequency':          -0.05,
}

# Pre-computed totals used to map the weighted sum to [0, 1].
_STUDY_SCORE_POS_SUM = sum(w for w in _STUDY_SCORE_WEIGHTS.values() if w > 0)   # 0.65
_STUDY_SCORE_NEG_SUM = sum(abs(w) for w in _STUDY_SCORE_WEIGHTS.values() if w < 0)  # 0.35


def _compute_study_score(features_dict: dict) -> float:
    """Return a calibrated 0–100 study score.

    Positive-weight features (study_hours, productive_usage, completed_tasks)
    push the score toward 100; negative-weight features (screen_time,
    notifications, …) drag it toward 0.

    The weighted sum is linearly remapped so that:
      • perfect session (all positives at max, all negatives at 0) → 100
      • worst session  (all positives at 0,   all negatives at max) →   0
    """
    weighted_sum = 0.0
    for feat, weight in _STUDY_SCORE_WEIGHTS.items():
        val = float(features_dict.get(feat, 0))
        max_val = _STUDY_NORM_MAXES.get(feat, 1) or 1
        normalised = min(1.0, max(0.0, val / max_val))
        weighted_sum += weight * normalised
    # Shift from [−neg_sum, +pos_sum] to [0, 1], then scale to 100.
    score = (weighted_sum + _STUDY_SCORE_NEG_SUM) / (_STUDY_SCORE_POS_SUM + _STUDY_SCORE_NEG_SUM)
    return round(max(0.0, min(100.0, score * 100)), 1)


def _compute_study_contributions(features_dict: dict) -> dict:
    """Pie-chart contributions aligned with the calibrated scoring weights.

    Each slice = abs(weight) × normalised_value, normalised to sum to 100 %.
    This means the chart directly reflects the same logic as the score.
    """
    raw: dict = {}
    for feat, weight in _STUDY_SCORE_WEIGHTS.items():
        val = float(features_dict.get(feat, 0))
        max_val = _STUDY_NORM_MAXES.get(feat, 1) or 1
        normalised = min(1.0, max(0.0, val / max_val))
        raw[feat] = abs(weight) * normalised
    total = sum(raw.values()) or 1
    return {k: round(100.0 * v / total, 1) for k, v in raw.items()}


def _classify_study_score(score: float) -> str:
    """Map a study score to Bad / Moderate / Good."""
    if score >= 70:
        return 'Good'
    if score >= 40:
        return 'Moderate'
    return 'Bad'


# Sleep: only sleep-relevant form inputs; sleep_hours carries the highest weight.
_SLEEP_WEIGHTS = {
    'sleep_hours':              40,
    'deep_sleep_hours':         20,
    'sleep_interruption':       15,
    'notifications_night':      10,
    'night_phone_usage':         8,
    'screen_time_before_sleep':  5,
    'noise_level':               4,
    'ambient_light_level':       3,
    'wake_time':                 2,
}
_SLEEP_MAXES = {
    'sleep_hours':              12,
    'deep_sleep_hours':         12,
    'sleep_interruption':       20,
    'notifications_night':      200,
    'night_phone_usage':        300,
    'screen_time_before_sleep': 300,
    'noise_level':              100,
    'ambient_light_level':      100,
    'wake_time':                24,
}


def _compute_domain_contributions(
    values_dict: dict,
    feature_weights: dict,
    feature_maxes: dict,
) -> dict:
    """Compute contribution percentages using domain weights and normalised input values.

    This ensures:
    - Only the features listed in ``feature_weights`` appear in the chart.
    - High-weight features (e.g. study_hours) dominate the distribution.
    - Different input values produce visibly different distributions.
    """
    raw: dict = {}
    for key, weight in feature_weights.items():
        val = abs(float(values_dict.get(key, 0)))
        max_val = feature_maxes.get(key, 1) or 1
        normalised = min(1.0, val / max_val)
        raw[key] = weight * normalised
    total = sum(raw.values()) or 1
    return {k: round(100.0 * v / total, 1) for k, v in raw.items()}


def _enrich_with_behavior_outputs(result: dict, inputs: dict, prediction_score: float | None = None) -> dict:
    """Attach dynamic behavioral analysis fields to a prediction result."""
    behavior = generate_behavior_insights(inputs)
    personalized_recs = generate_personalized_recommendations(inputs)
    risk = calculate_risk_level(inputs)
    habits = detect_habits(inputs)
    summary = generate_behavior_summary(inputs)
    ai_explanation = generate_ai_explanation(inputs, prediction_score=prediction_score)

    enriched = dict(result)
    enriched['digital_mind_mirror'] = behavior.get('digital_mind_mirror', {})
    # Provide a flat list version of the mirror insights for easier rendering.
    enriched['digital_mind_mirror_insights'] = (
        behavior.get('digital_mind_mirror', {}).get('points', [])
    )
    enriched['behavior_insights'] = behavior.get('behavior_insights', [])
    enriched['habit_detection'] = habits
    enriched['risk_indicator'] = risk
    enriched['ai_explanation'] = ai_explanation
    enriched['behavior_summary'] = summary
    # Keep existing recommendations behavior but make them dynamic/personalized.
    existing_recs = list(result.get('recommendations') or [])
    merged_recs = []
    for item in personalized_recs + existing_recs:
        if item not in merged_recs:
            merged_recs.append(item)
    enriched['recommendations'] = merged_recs
    return enriched

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

        logging.info(f"Sleep prediction inputs: {data}")

        features_dict = {
            'sleep_hours':       _clip_value(data.get('sleep_hours', 7), 0, 12),
            'screen_time_before_sleep': _clip_value(data.get('screen_time_before_sleep', 120), 0, 300),
            'notifications_night':      _clip_value(data.get('notifications_night', 10), 0, 200),
            'heart_rate':               _clip_value(data.get('heart_rate', 70), 30, 200),
            'steps_today':              _clip_value(data.get('steps_today', 8000), 0, 50000),
            'deep_sleep_hours':         _clip_value(data.get('deep_sleep_hours', 2.0), 0, 12),
            'night_phone_usage':        _clip_value(data.get('night_phone_usage', 20.0), 0, 300),
            'sleep_interruption':       _clip_value(data.get('sleep_interruption', 1), 0, 20),
            'wake_time':                _clip_value(data.get('wake_time', 6.8), 0, 24),
            'noise_level':              _clip_value(data.get('noise_level', 3), 0, 100),
            'ambient_light_level':      _clip_value(data.get('ambient_light_level', 2), 0, 100),
        }

        logging.info(f"Sleep features dict: {features_dict}")

        # Compute derived features
        deep_sleep_ratio = features_dict['deep_sleep_hours'] / features_dict['sleep_hours'] if features_dict['sleep_hours'] > 0 else 0
        features_dict['sleep_quality_score'] = (
            features_dict['sleep_hours'] * deep_sleep_ratio - 
            features_dict['sleep_interruption'] * 5 - 
            features_dict['night_phone_usage'] * 0.5
        )
        features_dict['sleep_disruption_index'] = (
            features_dict['notifications_night'] + 
            features_dict['night_phone_usage'] / 10 + 
            features_dict['sleep_interruption'] * 2
        )
        features_dict['sleep_recovery_score'] = (
            features_dict['deep_sleep_hours'] + 
            (10 - features_dict['heart_rate'] / 10) + 
            features_dict['steps_today'] / 1000
        )

        # Fill lag features expected by the model with current values
        for lag in [1, 2, 3]:
            for col in ['sleep_hours', 'screen_time_before_sleep',
                        'notifications_night', 'heart_rate', 'steps_today',
                        'deep_sleep_hours', 'night_phone_usage', 'sleep_interruption', 'wake_time', 'noise_level', 'ambient_light_level',
                        'sleep_quality_score', 'sleep_disruption_index', 'sleep_recovery_score']:
                features_dict[f'{col}_lag_{lag}'] = features_dict.get(col, 0)

        feature_array = np.array(
            [features_dict.get(col, 0) for col in feature_cols]
        ).reshape(1, -1)

        feature_scaled = scaler.transform(feature_array)
        try:
            prediction = model.predict(feature_scaled)[0]
            prediction_score = float(prediction)
            score = round(max(0, min(100, prediction_score)), 1)
        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}

        logging.info(f"Study raw prediction: {prediction_score}, score: {score}")

        print("Received Inputs:", features_dict)
        print("Scaled Features:", feature_scaled.tolist())
        print("Prediction Score:", prediction_score)

        # analysis / breakdown — sleep-specific features only
        contributions = _compute_domain_contributions(
            features_dict, _SLEEP_WEIGHTS, _SLEEP_MAXES
        )
        category = _classify_score(score)
        recommendations = _get_recommendations(category)
        explanation = _create_explanation(contributions)

        key_factors = sorted(contributions.items(), key=lambda kv: kv[1], reverse=True)[:2]
        key_factors = [k for k, _ in key_factors]

        base_result = {
            'prediction': score,
            'score': score,
            'category': category,
            'label': category,
            'key_factors': key_factors,
            'contributions': contributions,
            'recommendations': recommendations,
            'explanation': explanation,
        }
        return _enrich_with_behavior_outputs(base_result, features_dict, prediction_score=score)
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

        logging.info("Study prediction request data: %s", data)

        features_dict = {
            'screen_time':       _clip_value(data.get('screen_time', 180), 0, 600),
            'productive_usage':  _clip_value(data.get('productive_usage', 60), 0, 300),
            'social_usage':      _clip_value(data.get('social_usage', 60), 0, 480),
            'gaming_usage':      _clip_value(data.get('gaming_usage', 30), 0, 240),
            'notifications':     _clip_value(data.get('notifications', 100), 0, 500),
            'sleep_hours':       _clip_value(data.get('sleep_hours', 7), 0, 12),
            'steps':             _clip_value(data.get('steps', 8000), 0, 50000),
            'heart_rate':        _clip_value(data.get('heart_rate', 70), 30, 200),
            'unlock_count':      _clip_value(data.get('unlock_count', 50), 0, 500),
            'study_hours':       _clip_value(data.get('study_hours', 3.5), 0, 24),
            'app_switching_frequency': _clip_value(data.get('app_switching_frequency', 20), 0, 100),
            'notifications_during_study': _clip_value(data.get('notifications_during_study', 8), 0, 200),
            'break_frequency':       _clip_value(data.get('break_frequency', 3), 0, 20),
            'phone_usage_during_study': _clip_value(data.get('phone_usage_during_study', 35.0), 0, 300),
            'completed_tasks':       _clip_value(data.get('completed_tasks', 6), 0, 100),
            'focus_score':           _clip_value(data.get('focus_score', 50), 0, 100),
            'study_session_count':   _clip_value(data.get('study_session_count', 1), 1, 10),
        }

        logging.info("Study features dict: %s", features_dict)

        # Compute derived features
        features_dict['study_efficiency'] = features_dict['completed_tasks'] / (features_dict['study_hours'] + 0.1)
        features_dict['focus_index'] = features_dict['focus_score'] / (features_dict['app_switching_frequency'] + 1)
        features_dict['distraction_index'] = (
            features_dict['phone_usage_during_study'] + 
            features_dict['notifications_during_study'] + 
            features_dict['app_switching_frequency']
        )
        features_dict['study_intensity'] = features_dict['study_hours'] / (features_dict['study_session_count'] + 0.1)
        features_dict['break_efficiency'] = features_dict['completed_tasks'] / (features_dict['break_frequency'] + 1)

        # Fill lag features
        for lag in [1, 2, 3]:
            for col in ['screen_time', 'productive_usage', 'social_usage',
                        'gaming_usage', 'notifications', 'unlock_count',
                        'study_hours', 'app_switching_frequency', 'notifications_during_study', 'break_frequency',
                        'phone_usage_during_study', 'completed_tasks', 'study_efficiency', 'focus_index', 'distraction_index', 'sleep_hours', 'steps', 'heart_rate']:
                features_dict[f'{col}_lag_{lag}'] = features_dict.get(col, 0)

        feature_array = np.array(
            [features_dict.get(col, 0) for col in feature_cols]
        ).reshape(1, -1)

        logging.info("Study feature vector (ordered): %s", feature_array.tolist())

        feature_scaled = scaler.transform(feature_array)

        logging.info("Study scaled features (first row): %s", feature_scaled.tolist())

        # --- Calibrated weighted score (bypasses raw ML output) ---
        score = _compute_study_score(features_dict)
        logging.info("Study calibrated score: %s", score)

        # Pie-chart contributions — same normalization & weights as the score
        contributions = _compute_study_contributions(features_dict)
        category = _classify_study_score(score)
        recommendations = _get_recommendations(category)
        explanation = _create_explanation(contributions)

        key_factors = sorted(contributions.items(), key=lambda kv: kv[1], reverse=True)[:2]
        key_factors = [k for k, _ in key_factors]

        base_result = {
            'prediction': score,
            'score': score,
            'category': category,
            'label': category,
            'key_factors': key_factors,
            'contributions': contributions,
            'recommendations': recommendations,
            'explanation': explanation,
        }
        return _enrich_with_behavior_outputs(base_result, features_dict, prediction_score=score)
    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# STRESS LEVEL PREDICTION
# ============================================================================

def predict_stress(data):
    """Predict stress level from user input.

    Parameters
    ----------
    data : dict
        Keys: screen_time, notifications, unlock_count, sleep_hours,
              steps, heart_rate, social_usage, gaming_usage

    Returns
    -------
    dict  –  { "stress_level": "Medium", "stress_score": <0-100>, ... } or { "error": "..." }
    """
    try:
        model, scaler, label_encoder, feature_cols = load_stress_model()

        # Normalize and validate user-provided inputs (realistic ranges)
        features_dict = _sanitize_stress_inputs(data)

        # Derived features to match training
        features_dict['stress_index'] = (
            features_dict['daily_workload'] +
            features_dict['deadline_pressure'] +
            features_dict['mental_fatigue_score'] +
            features_dict['screen_time'] / 2
        ) / 4
        features_dict['digital_overload'] = (
            features_dict['screen_time'] +
            features_dict['social_usage'] +
            features_dict['gaming_usage'] +
            features_dict['notifications']
        )
        features_dict['work_life_balance'] = features_dict['sleep_hours'] / (features_dict['screen_time'] / 24 + 0.1)

        # Trend / stability features (assume steady state for single input)
        features_dict['last_3_day_avg'] = features_dict['daily_workload']
        features_dict['daily_workload_trend'] = 0.0
        features_dict['mental_fatigue_score_trend'] = 0.0

        # Ensure feature order exactly matches training
        feature_array = np.array(
            [features_dict.get(col, 0) for col in feature_cols]
        ).reshape(1, -1)

        feature_scaled = scaler.transform(feature_array)

        # Get predicted class and probability if available
        prediction_encoded = model.predict(feature_scaled)[0]
        stress_level = label_encoder.inverse_transform([prediction_encoded])[0]

        stress_score_raw = None
        if hasattr(model, 'predict_proba'):
            try:
                probs = model.predict_proba(feature_scaled)[0]
                if hasattr(model, 'classes_'):
                    labels = list(model.classes_)
                    if prediction_encoded in labels:
                        idx = labels.index(prediction_encoded)
                        stress_score_raw = round(float(probs[idx]) * 100.0, 1)
            except Exception:
                stress_score_raw = None

        # Ensure the returned score reflects small behavioral changes while
        # preserving the core model prediction.
        stress_score = _adjust_stress_score(stress_score_raw, features_dict)

        # Behavioral reason detection (rule-based)
        detected_factors = []
        if features_dict['screen_time'] > 7:
            detected_factors.append('Excessive screen exposure may increase cognitive fatigue.')
        if features_dict['notifications'] > 120:
            detected_factors.append('Too many notifications can disrupt concentration.')
        if features_dict['unlock_count'] > 120:
            detected_factors.append('Frequent phone checking may indicate digital dependency.')
        if features_dict['social_usage'] > 3:
            detected_factors.append('High social media usage may increase comparison stress.')
        if features_dict['gaming_usage'] > 3:
            detected_factors.append('Excessive gaming can reduce productivity and increase stress.')
        if features_dict['sleep_hours'] < 6:
            detected_factors.append('Lack of sleep significantly increases stress levels.')
        if features_dict['sleep_hours'] > 9:
            detected_factors.append('Oversleeping may indicate irregular sleep patterns.')
        if features_dict['steps'] < 3000:
            detected_factors.append('Low physical activity can negatively affect mood and stress levels.')
        if features_dict['heart_rate'] > 95:
            detected_factors.append('Elevated resting heart rate may indicate physical or mental stress.')

        # Core suggestions (always present, but can be extended based on detected factors)
        suggestions = [
            'Reduce screen exposure (especially in the evening).',
            'Improve sleep duration and consistency.',
            'Reduce notification interruptions (use Do Not Disturb).',
            'Increase daily physical activity (steps).',
        ]

        # compute contributions on the inputs used
        orig_keys = ['screen_time', 'notifications', 'unlock_count',
                     'sleep_hours', 'steps', 'heart_rate',
                     'social_usage', 'gaming_usage']
        contributions = _compute_contributions(features_dict, orig_keys)
        recommendations = _get_recommendations(stress_level)
        explanation = _create_explanation(contributions)

        base_result = {
            'stress_level': str(stress_level),
            'stress_score': stress_score,
            'stress_score_raw': stress_score_raw,
            'detected_factors': detected_factors,
            'suggestions': suggestions,
            'contributions': contributions,
            'recommendations': recommendations,
            'explanation': explanation,
        }
        return _enrich_with_behavior_outputs(base_result, features_dict)
    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# HEALTH SCORE PREDICTION
# ============================================================================

def predict_health(data):
    """Predict overall health score from user input.

    This implementation is intentionally deterministic and based on a weighted
    scoring system. Small changes in input values will result in small changes
    to the output score.

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

        # Collect inputs (default values used to keep behavior stable).
        features_dict = {
            'sleep_hours':       _clip_value(data.get('sleep_hours', 7), 0, 12),
            'steps':             _clip_value(data.get('steps', 8000), 0, 50000),
            'calories':          _clip_value(data.get('calories', 2100), 0, 5000),
            'heart_rate':        _clip_value(data.get('heart_rate', 70), 30, 200),
            'screen_time':       _clip_value(data.get('screen_time', 5), 0, 24),
            'social_usage':      _clip_value(data.get('social_usage', 2), 0, 24),
            'gaming_usage':      _clip_value(data.get('gaming_usage', 1), 0, 24),
            'productive_usage':  _clip_value(data.get('productive_usage', 2), 0, 24),
            'notifications':     _clip_value(data.get('notifications', 120), 0, 500),
            'unlock_count':      _clip_value(data.get('unlock_count', 40), 0, 500),
            # expanded health features
            'water_intake':      _clip_value(data.get('water_intake', 2.0), 0, 5),
            'exercise_minutes':  _clip_value(data.get('exercise_minutes', 30), 0, 240),
            'calorie_intake':    _clip_value(data.get('calorie_intake', 2200), 0, 5000),
            'heart_rate_avg':    _clip_value(data.get('heart_rate_avg', 70), 30, 220),
            'blood_pressure_systolic': _clip_value(data.get('blood_pressure_systolic', 120), 80, 200),
            'blood_pressure_diastolic': _clip_value(data.get('blood_pressure_diastolic', 80), 50, 140),
            'stress_level_recent': _clip_value(data.get('stress_level_recent', 5), 0, 10),
            'sleep_quality_recent': _clip_value(data.get('sleep_quality_recent', 6), 0, 10),
        }

        # Derived features
        features_dict['health_index'] = (
            features_dict['water_intake'] * 10 +
            features_dict['exercise_minutes'] / 10 +
            features_dict['steps'] / 1000
        ) / 3
        features_dict['metabolic_score'] = (
            features_dict['calorie_intake'] / 2000 +
            features_dict['exercise_minutes'] / 60 +
            (100 - features_dict['heart_rate_avg']) / 10
        )
        features_dict['lifestyle_score'] = (
            features_dict['sleep_hours'] / 8 * 25 +
            features_dict['steps'] / 10000 * 25 +
            (10 - features_dict['screen_time'] / 240) * 25 +
            features_dict['productive_usage'] / 4 * 25
        )

        # Trend/stability features
        features_dict['last_3_day_avg'] = features_dict['steps']
        features_dict['health_score_trend'] = 0.0

        feature_array = np.array(
            [features_dict.get(col, 0) for col in feature_cols]
        ).reshape(1, -1)

        feature_scaled = scaler.transform(feature_array)
        prediction = model.predict(feature_scaled)[0]
        score = max(0, min(100, float(prediction)))

        # Build output like the existing deterministic version
        contributions = _compute_contributions(features_dict, [k for k in feature_cols if k in features_dict])
        category = _classify_score(score)
        recommendations = _get_recommendations(category)
        explanation = _create_explanation(contributions)

        base_result = {
            'prediction': round(score, 1),
            'category': category,
            'contributions': contributions,
            'recommendations': recommendations,
            'explanation': explanation,
        }
        return _enrich_with_behavior_outputs(base_result, features_dict, prediction_score=score)
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
