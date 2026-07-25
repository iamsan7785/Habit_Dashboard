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

import json
import logging
import os

import firebase_admin
from firebase_admin import credentials, db as firebase_db

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Initialise Firebase Admin SDK (runs once on import)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_KEY_PATH = os.path.join(_PROJECT_ROOT, 'firebase_key.json')
_DEFAULT_DATABASE_URL = 'https://habitcheckapp-2ee93-default-rtdb.firebaseio.com/'


def _normalize_user_id(user_id: str) -> str:
    """Normalize a Firebase user ID without changing its case."""
    return str(user_id).strip()


def _load_firebase_credentials() -> tuple[str, object]:
    """Load Firebase credentials from Render env vars or the bundled key file."""
    env_json = (
        os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
        or os.getenv('FIREBASE_CREDENTIALS_JSON')
        or os.getenv('FIREBASE_KEY_JSON')
    )
    if env_json:
        return 'environment JSON', json.loads(env_json)

    env_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if env_path:
        return 'GOOGLE_APPLICATION_CREDENTIALS', env_path

    if os.path.exists(_KEY_PATH):
        return 'bundled firebase_key.json', _KEY_PATH

    raise FileNotFoundError(
        'No Firebase credentials found. Set FIREBASE_SERVICE_ACCOUNT_JSON, '
        'FIREBASE_CREDENTIALS_JSON, FIREBASE_KEY_JSON, or '
        'GOOGLE_APPLICATION_CREDENTIALS.'
    )


def _resolve_database_url() -> str:
    return os.getenv('FIREBASE_DATABASE_URL', _DEFAULT_DATABASE_URL)

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
        _cred_source, _cred_value = _load_firebase_credentials()
        _database_url = _resolve_database_url()
        firebase_admin.initialize_app(credentials.Certificate(_cred_value), {
            'databaseURL': _database_url,
        })
        logger.info('Firebase Admin initialized from %s with databaseURL=%s', _cred_source, _database_url)
    except Exception as exc:
        _firebase_init_error = exc
        logger.exception('Firebase Admin initialization failed')


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
    data = LOCAL_USER_DATA.get(_normalize_user_id(user_id))
    if data is None:
        return None
    return dict(data)


def _allow_local_demo_fallback() -> bool:
    """Only use demo data locally; Render should hit the real Firebase project."""
    return not bool(os.getenv('RENDER'))


def _log_firebase_read(action: str, path: str, user_id: str, result: object) -> None:
    logger.info('Firebase %s read | path=%s | user_id=%s | result=%s', action, path, user_id, result)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def verify_user(user_id: str) -> bool:
    """Return True if the user_id exists under /users in Firebase.
    Uses shallow=True so only keys are downloaded (not the full data tree)."""
    user_id = _normalize_user_id(user_id)
    path = f'users/{user_id}'

    if _firebase_init_error is not None:
        if _allow_local_demo_fallback():
            data = _get_local_health_data(user_id)
            _log_firebase_read('verify_user demo', path, user_id, data)
            return data is not None
        raise _friendly_firebase_error(_firebase_init_error)

    try:
        ref = firebase_db.reference(path)
        result = ref.get(shallow=True)
        _log_firebase_read('verify_user', path, user_id, result)
        return result is not None
    except Exception as exc:
        logger.exception('Firebase verify_user failed | path=%s | user_id=%s', path, user_id)
        if _allow_local_demo_fallback():
            local_data = _get_local_health_data(user_id)
            _log_firebase_read('verify_user demo fallback', path, user_id, local_data)
            if local_data is not None:
                return True
        raise _friendly_firebase_error(exc) from exc


def get_latest_health_data(user_id: str) -> dict | None:
    """
    Fetch the latest date entry from:
        users/{user_id}/health_data/{date}

    Returns a flat dict with the health fields, or None when no data exists.
    """
    user_id = _normalize_user_id(user_id)
    path = f'users/{user_id}/health_data'

    if _firebase_init_error is not None:
        if _allow_local_demo_fallback():
            data = _get_local_health_data(user_id)
            _log_firebase_read('get_latest_health_data demo', path, user_id, data)
            return data
        raise _friendly_firebase_error(_firebase_init_error)

    try:
        ref = firebase_db.reference(path)

        # Fetch only the latest date entry instead of entire history
        snapshot = ref.order_by_key().limit_to_last(1).get()
        _log_firebase_read('get_latest_health_data', path, user_id, snapshot)
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
        logger.exception('Firebase get_latest_health_data failed | path=%s | user_id=%s', path, user_id)
        if _allow_local_demo_fallback():
            local_data = _get_local_health_data(user_id)
            _log_firebase_read('get_latest_health_data demo fallback', path, user_id, local_data)
            if local_data is not None:
                return local_data
        raise _friendly_firebase_error(exc) from exc


def get_recent_health_data(user_id: str, days: int = 7) -> list[dict]:
    """Fetch the most recent N days of health_data for a user.

    The returned list is sorted oldest first (ascending date) to make it
    easier to render trend charts.
    """
    user_id = _normalize_user_id(user_id)
    path = f'users/{user_id}/health_data'

    if _firebase_init_error is not None:
        if _allow_local_demo_fallback():
            demo = _get_local_health_data(user_id)
            _log_firebase_read('get_recent_health_data demo', path, user_id, demo)
            if not demo:
                return []
            # Repeat demo data for the requested number of days
            return [dict(demo, date=f"demo_day_{i+1}") for i in range(days)]
        raise _friendly_firebase_error(_firebase_init_error)

    try:
        ref = firebase_db.reference(path)
        snapshot = ref.order_by_key().limit_to_last(days).get()
        _log_firebase_read('get_recent_health_data', path, user_id, snapshot)
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
        logger.exception('Firebase get_recent_health_data failed | path=%s | user_id=%s', path, user_id)
        if _allow_local_demo_fallback():
            local_data = _get_local_health_data(user_id)
            _log_firebase_read('get_recent_health_data demo fallback', path, user_id, local_data)
            if local_data is not None:
                return [dict(local_data, date=f"demo_day_{i+1}") for i in range(days)]
        raise _friendly_firebase_error(exc) from exc
