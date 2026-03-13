"""Analytics helpers for HabitCheck AI dashboard.

This module provides non-ML heuristics used by the dashboard for
wellness scoring, insights generation, personality classification,
burnout risk estimation, and weekly trend summaries.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


def _parse_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _normalize_stress_level(stress: Any) -> float:
    """Normalize stress to a numeric scale (1-3) for calculations."""
    if stress is None:
        return 2.0
    if isinstance(stress, (int, float)):
        return float(stress)
    s = str(stress).strip().lower()
    if s in ("low", "l"):
        return 1.0
    if s in ("medium", "med", "m"):
        return 2.0
    if s in ("high", "h"):
        return 3.0
    # Try parse numeric string
    try:
        return float(s)
    except Exception:
        return 2.0


def calculate_wellness_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate a wellness score in the 0–100 range, plus status and breakdown."""
    steps = _parse_float(data.get("steps") or data.get("steps_today") or 0)
    screen_time = _parse_float(data.get("total_screen_time") or data.get("screen_time") or 0)
    sleep_hours = _parse_float(data.get("sleep_hours") or 0)
    stress_level = _normalize_stress_level(data.get("stress_level") or data.get("stress"))

    sleep_score = min((sleep_hours / 8.0) * 30.0, 30.0)
    step_score = min((steps / 8000.0) * 25.0, 25.0)
    screen_score = max(25.0 - (screen_time * 2.0), 0.0)
    stress_score = max(20.0 - (stress_level * 4.0), 0.0)

    total = round(sleep_score + step_score + screen_score + stress_score, 1)
    status = (
        "Healthy"
        if total >= 80
        else "Balanced"
        if total >= 60
        else "Moderate Risk"
        if total >= 40
        else "High Risk"
    )

    return {
        "score": total,
        "status": status,
        "breakdown": {
            "sleep_score": round(sleep_score, 1),
            "step_score": round(step_score, 1),
            "screen_score": round(screen_score, 1),
            "stress_score": round(stress_score, 1),
        },
    }


def generate_insights(data: Dict[str, Any]) -> List[str]:
    """Create a short list of AI-style insights based on the latest user data."""
    insights: List[str] = []
    screen_time = _parse_float(data.get("total_screen_time") or data.get("screen_time") or 0)
    sleep_hours = _parse_float(data.get("sleep_hours") or 0)
    steps = _parse_float(data.get("steps") or data.get("steps_today") or 0)
    notifications = _parse_float(data.get("notification_count") or data.get("notifications") or 0)
    unlock_count = _parse_float(data.get("unlock_count") or 0)
    stress_level = _normalize_stress_level(data.get("stress_level") or data.get("stress"))

    if screen_time > 7:
        insights.append("High screen time detected which may increase stress.")
    if sleep_hours < 6:
        insights.append("Low sleep detected. This may affect focus and productivity.")
    if steps > 6000:
        insights.append("Good physical activity detected which can reduce stress.")
    if notifications > 180:
        insights.append("Many notifications are creating digital noise. Consider muting non-critical alerts.")
    if unlock_count > 120:
        insights.append("Frequent phone unlocks may be a sign of distraction during the day.")
    if not insights:
        insights.append("Your recent habits look fairly balanced. Keep monitoring for changes.")

    return insights


def classify_personality(data: Dict[str, Any]) -> Dict[str, str]:
    """Classify a simple digital personality type based on usage patterns."""
    screen_time = _parse_float(data.get("total_screen_time") or data.get("screen_time") or 0)
    unlock_count = _parse_float(data.get("unlock_count") or 0)
    steps = _parse_float(data.get("steps") or data.get("steps_today") or 0)
    sleep_hours = _parse_float(data.get("sleep_hours") or 0)
    notifications = _parse_float(data.get("notification_count") or data.get("notifications") or 0)

    if screen_time > 8 and unlock_count > 120:
        return {
            "type": "Digital Overuser",
            "description": "Your device usage is very high and may lead to fatigue if sustained. Consider scheduled breaks and screen-free periods.",
        }
    if steps > 7000 and sleep_hours > 7:
        return {
            "type": "Balanced User",
            "description": "You have a strong balance between movement and rest — this is a great foundation for long-term wellbeing.",
        }
    if notifications > 150:
        return {
            "type": "Highly Distracted User",
            "description": "A high notification volume can fragment attention. Try batching notifications or using do-not-disturb windows.",
        }
    return {
        "type": "Normal User",
        "description": "Your patterns are within typical ranges. Small habit tweaks can help you feel even better.",
    }


def estimate_burnout_risk(data: Dict[str, Any]) -> Dict[str, Any]:
    """Estimate burnout risk percentage based on key signals."""
    screen_time = _parse_float(data.get("total_screen_time") or data.get("screen_time") or 0)
    sleep_hours = _parse_float(data.get("sleep_hours") or 0)
    notifications = _parse_float(data.get("notification_count") or data.get("notifications") or 0)
    stress_level = _normalize_stress_level(data.get("stress_level") or data.get("stress"))

    risk = 0.0
    # Screen time contribution (up to 30% risk)
    risk += min(screen_time / 12.0, 1.0) * 30.0
    # Sleep deficit contribution (up to 30% risk)
    risk += min(max(0.0, 8.0 - sleep_hours) / 8.0, 1.0) * 30.0
    # Stress contribution (up to 25% risk)
    stress_norm = min(max((stress_level - 1.0) / 2.0, 0.0), 1.0)
    risk += stress_norm * 25.0
    # Notifications contribution (up to 15% risk)
    risk += min(notifications / 300.0, 1.0) * 15.0

    score = round(min(max(risk, 0.0), 100.0), 1)
    return {
        "risk_percentage": score,
        "summary": "This score combines screen time, sleep, stress, and notification load to highlight potential burnout risk.",
    }


def detect_behavior_patterns(data: Dict[str, Any]) -> List[str]:
    """Detect simple correlations between habits and wellbeing signals."""
    patterns: List[str] = []
    screen_time = _parse_float(data.get("total_screen_time") or data.get("screen_time") or 0)
    sleep_hours = _parse_float(data.get("sleep_hours") or 0)
    steps = _parse_float(data.get("steps") or data.get("steps_today") or 0)
    notifications = _parse_float(data.get("notification_count") or data.get("notifications") or 0)
    stress_level = _normalize_stress_level(data.get("stress_level") or data.get("stress"))

    if screen_time > 7 and stress_level >= 2:
        patterns.append("High screen time is currently associated with elevated stress levels in your data.")
    if steps > 6000 and stress_level <= 2:
        patterns.append("Higher activity here correlates with lower stress, which is a positive sign.")
    if sleep_hours < 6:
        patterns.append("Lower sleep is linked to reduced focus and energy in many cases.")
    if notifications > 180 and stress_level >= 2:
        patterns.append("A high notification volume may be contributing to stress spikes.")

    if not patterns:
        patterns.append("No strong behavioral correlations detected yet. Keep collecting data for better insights.")

    return patterns


def daily_summary(data: Dict[str, Any], predicted_stress: Optional[str] = None) -> str:
    """Generate a concise daily summary sentence."""
    screen_time = _parse_float(data.get("total_screen_time") or data.get("screen_time") or 0)
    sleep_hours = _parse_float(data.get("sleep_hours") or 0)
    steps = _parse_float(data.get("steps") or data.get("steps_today") or 0)

    screen_text = f"{screen_time:.1f} hrs" if screen_time else "an unknown amount of time"
    steps_text = f"{int(steps):,} steps" if steps else "an unknown step count"
    sleep_text = f"{sleep_hours:.1f} hrs" if sleep_hours else "an unknown amount of sleep"

    stress_text = f"{predicted_stress}" if predicted_stress else "unavailable"
    return (
        f"Today you used your phone for {screen_text}, walked {steps_text}, and slept {sleep_text}. "
        f"Your predicted stress level is {stress_text}."
    )


def generate_weekly_insight(trends: Dict[str, Any]) -> str:
    """Create a simple natural-language summary of weekly habit trends."""
    dates = trends.get("dates") or []
    if not dates:
        return "No weekly data available yet."

    steps = trends.get("steps", [])
    screen = trends.get("screen_time", [])
    sleep = trends.get("sleep_hours", [])
    stress = trends.get("stress", [])

    # compute first vs last percent changes
    def pct_change(arr):
        if len(arr) < 2:
            return 0.0
        try:
            return round(((arr[-1] - arr[0]) / (arr[0] or 1)) * 100.0, 1)
        except Exception:
            return 0.0

    screen_pct = pct_change(screen)
    sleep_pct = pct_change(sleep)

    # highest steps day and lowest stress day
    high_steps_idx = steps.index(max(steps)) if steps else None
    low_stress_idx = stress.index(min(stress)) if stress else None

    def weekday_name(idx):
        try:
            return datetime.strptime(dates[idx], "%Y-%m-%d").strftime("%A")
        except Exception:
            return dates[idx]

    parts: List[str] = []
    if abs(screen_pct - sleep_pct) >= 1:
        direction = "increased" if screen_pct > sleep_pct else "decreased"
        diff = abs(screen_pct - sleep_pct)
        parts.append(
            f"This week your screen time {direction} by {diff}% compared to your sleep hours."
        )
    if high_steps_idx is not None:
        parts.append(
            f"Your step count was highest on {weekday_name(high_steps_idx)}."
        )
    if low_stress_idx is not None:
        parts.append(
            f"Stress levels were lowest on {weekday_name(low_stress_idx)}."
        )
    if not parts:
        parts.append("Your habits remained fairly steady this week.")

    return " ".join(parts)


def generate_weekly_comparison(trends: Dict[str, Any]) -> Dict[str, str]:
    """Return a breakdown of highest/lowest/most-active days plus stress trend."""
    dates = trends.get("dates") or []
    if not dates:
        return {}

    def weekday_name(idx):
        try:
            return datetime.strptime(dates[idx], "%Y-%m-%d").strftime("%A")
        except Exception:
            return dates[idx]

    result: Dict[str, str] = {}
    screen = trends.get("screen_time", [])
    if screen:
        idx = screen.index(max(screen))
        result["highest_screen_day"] = weekday_name(idx)
    sleep = trends.get("sleep_hours", [])
    if sleep:
        idx = sleep.index(min(sleep))
        result["lowest_sleep_day"] = weekday_name(idx)
    steps = trends.get("steps", [])
    if steps:
        idx = steps.index(max(steps))
        result["most_active_day"] = weekday_name(idx)
    stress = trends.get("stress", [])
    if len(stress) >= 2:
        first = stress[0]
        last = stress[-1]
        if last > first:
            trend = "increasing"
        elif last < first:
            trend = "decreasing"
        else:
            trend = "steady"
        result["stress_trend"] = trend
    return result



def summarize_weekly_trends(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return weekly averages and trend series from a list of daily entries."""
    if not entries:
        return {
            "dates": [],
            "steps": [],
            "screen_time": [],
            "sleep_hours": [],
            "stress": [],
            "averages": {
                "steps": 0,
                "screen_time": 0,
                "sleep_hours": 0,
                "stress": 0,
            },
        }

    dates = []
    steps = []
    screen_time = []
    sleep_hours = []
    stress = []

    for entry in entries:
        dates.append(entry.get("date", ""))
        steps.append(_parse_float(entry.get("steps") or entry.get("steps_today") or 0))
        screen_time.append(_parse_float(entry.get("total_screen_time") or entry.get("screen_time") or 0))
        sleep_hours.append(_parse_float(entry.get("sleep_hours") or 0))
        stress_val = entry.get("stress_level") or entry.get("stress")
        if stress_val is None:
            stress.append(0)
        else:
            if isinstance(stress_val, (int, float)):
                stress.append(_parse_float(stress_val))
            else:
                # Map textual stress to numeric for charting
                val = _normalize_stress_level(stress_val)
                stress.append(val * 10)  # scale to 0-30 for chart visibility

    def avg(arr: List[float]) -> float:
        if not arr:
            return 0.0
        return round(sum(arr) / len(arr), 1)

    totals = {
        "steps": round(sum(steps), 1),
        "screen_time": round(sum(screen_time), 1),
        "sleep_hours": round(sum(sleep_hours), 1),
        "stress": round(sum(stress), 1),
    }

    return {
        "dates": dates,
        "steps": steps,
        "screen_time": screen_time,
        "sleep_hours": sleep_hours,
        "stress": stress,
        "averages": {
            "steps": avg(steps),
            "screen_time": avg(screen_time),
            "sleep_hours": avg(sleep_hours),
            "stress": avg(stress),
        },
        "totals": totals,
    }
