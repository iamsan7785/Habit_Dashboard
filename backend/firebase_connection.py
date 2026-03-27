"""
Firebase Realtime Database Connection
======================================

Initialises firebase_admin and provides helper functions to
fetch user health data from the Realtime Database.

Database structure:
    users/{user_id}/health_data/{date}/{fields}

Usage:
    from firebase_connection import get_latest_health_data, verify_user
"""

import os

import firebase_admin
from firebase_admin import credentials, db as firebase_db

# ---------------------------------------------------------------------------
# Initialise Firebase Admin SDK (runs once on import)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_KEY_PATH = os.path.join(_PROJECT_ROOT, 'firebase_key.json')

LOCAL_USER_DATA = {
    '6a804b1ecaa99679': {
        'sleep_hours': 6.5,
        'steps': 8500,
        'heart_rate': 72,
        'total_screen_time': 5.5,
        'notification_count': 120,
        'productive_usage': 2.0,
        'social_usage': 2.5,
        'gaming_usage': 1.0,
        'calories_burned': 2100,
        'date': 'Local demo data',
    },
}

_firebase_init_error = None
if not firebase_admin._apps:
    try:
        _cred = credentials.Certificate(_KEY_PATH)
        firebase_admin.initialize_app(_cred, {
            'databaseURL': 'https://habitcheckapp-2ee93-default-rtdb.firebaseio.com/'
        })
    except Exception as exc:
        _firebase_init_error = exc


class FirebaseConnectionError(RuntimeError):
    """Raised when the app cannot authenticate with Firebase."""


def _friendly_firebase_error(exc: Exception) -> FirebaseConnectionError:
    """Convert low-level Firebase/Google auth errors into a user-safe message."""
    message = str(exc)
    if 'invalid_grant' in message or 'Invalid JWT Signature' in message:
        return FirebaseConnectionError(
            'Firebase authentication failed. The service-account key in '
            'firebase_key.json is invalid, expired, or no longer matches the '
            'Firebase project. Download a fresh private key from the Firebase '
            'Console and replace firebase_key.json.'
        )
    return FirebaseConnectionError(
        'Unable to connect to Firebase. Check firebase_key.json, the database '
        'URL, and your network connection.'
    )


def _get_local_health_data(user_id: str) -> dict | None:
    """Return bundled demo data when Firebase is unavailable."""
    data = LOCAL_USER_DATA.get(user_id)
    if data is None:
        return None
    return dict(data)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def verify_user(user_id: str) -> bool:
    """Return True if the user_id exists under /users in Firebase.
    Uses shallow=True so only keys are downloaded (not the full data tree)."""
    if _firebase_init_error is not None:
        return _get_local_health_data(user_id) is not None

    try:
        ref = firebase_db.reference(f'users/{user_id}')
        result = ref.get(shallow=True)
        return result is not None
    except Exception as exc:
        local_data = _get_local_health_data(user_id)
        if local_data is not None:
            return True
        raise _friendly_firebase_error(exc) from exc


def get_latest_health_data(user_id: str) -> dict | None:
    """
    Fetch the latest date entry from:
        users/{user_id}/health_data/{date}

    Returns a flat dict with the health fields, or None when no data exists.
    """
    if _firebase_init_error is not None:
        return _get_local_health_data(user_id)

    try:
        ref = firebase_db.reference(f'users/{user_id}/health_data')

        # Fetch only the latest date entry instead of entire history
        snapshot = ref.order_by_key().limit_to_last(1).get()
        if not snapshot:
            return None

        latest_date = list(snapshot.keys())[0]
        entry = snapshot[latest_date]

        return {
            'sleep_hours':        entry.get('sleep_hours', 0),
            'steps':              entry.get('steps', 0),
            'heart_rate':         entry.get('heart_rate', 0),
            'total_screen_time':  entry.get('total_screen_time', 0),
            'notification_count': entry.get('notification_count', 0),
            'productive_usage':   entry.get('productive_usage', 0),
            'social_usage':       entry.get('social_usage', 0),
            'gaming_usage':       entry.get('gaming_usage', 0),
            'calories_burned':    entry.get('calories_burned', 0),
            'date':               latest_date,
        }
    except Exception as exc:
        local_data = _get_local_health_data(user_id)
        if local_data is not None:
            return local_data
        raise _friendly_firebase_error(exc) from exc


def get_recent_health_data(user_id: str, days: int = 7) -> list[dict]:
    """Fetch the most recent N days of health_data for a user.

    The returned list is sorted oldest first (ascending date) to make it
    easier to render trend charts.
    """
    if _firebase_init_error is not None:
        demo = _get_local_health_data(user_id)
        if not demo:
            return []
        # Repeat demo data for the requested number of days
        return [dict(demo, date=f"demo_day_{i+1}") for i in range(days)]

    try:
        ref = firebase_db.reference(f'users/{user_id}/health_data')
        snapshot = ref.order_by_key().limit_to_last(days).get()
        if not snapshot:
            return []

        entries = []
        for date_key in sorted(snapshot.keys()):
            entry = snapshot[date_key] or {}
            entry = dict(entry)
            entry['date'] = date_key
            entries.append(entry)
        return entries

    except Exception as exc:
        local_data = _get_local_health_data(user_id)
        if local_data is not None:
            return [dict(local_data, date=f"demo_day_{i+1}") for i in range(days)]
        raise _friendly_firebase_error(exc) from exc
