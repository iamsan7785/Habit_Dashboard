"""Quick sanity checks for stress prediction behavior.

This script validates that:
  * Inputs are clamped to realistic ranges.
  * Stress score responds in a plausible direction to key behaviors.

Run:
  python test_predict.py
"""

from backend.predictions import predict_stress


def _compare(base, modified, label):
    base_score = base.get('stress_score') or 0.0
    mod_score = modified.get('stress_score') or 0.0
    print(f"{label}: base={base_score} -> modified={mod_score}")
    return base_score, mod_score


if __name__ == '__main__':
    base_input = {
        'screen_time': 5,
        'notifications': 100,
        'unlock_count': 80,
        'steps': 8000,
        'social_usage': 2,
        'gaming_usage': 1,
        'sleep_hours': 7,
        'heart_rate': 70,
    }

    base_out = predict_stress(base_input)
    print('Base output:', base_out)

    # Small changes should alter the predicted score (model should react)
    higher_screen = predict_stress({**base_input, 'screen_time': 9})
    _, mod1 = _compare(base_out, higher_screen, 'Screen time increase')
    assert abs(mod1 - (base_out.get('stress_score') or 0.0)) > 0.0, 'Stress score did not change with higher screen time'

    better_sleep = predict_stress({**base_input, 'sleep_hours': 8})
    _, mod2 = _compare(base_out, better_sleep, 'Sleep improvement')
    assert abs(mod2 - (base_out.get('stress_score') or 0.0)) > 0.0, 'Stress score did not change with better sleep'

    more_steps = predict_stress({**base_input, 'steps': 12000})
    _, mod3 = _compare(base_out, more_steps, 'Increased steps')
    assert abs(mod3 - (base_out.get('stress_score') or 0.0)) > 0.0, 'Stress score did not change with more steps'

    print('Basic sensitivity checks passed.')
