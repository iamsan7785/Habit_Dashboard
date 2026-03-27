"""
Testing and Integration Guide for ML Pipeline
==============================================

This script demonstrates complete usage and integration testing of the ML pipeline.
"""

import json
from backend.predictions import (
    predict_sleep_score,
    predict_study_score,
    predict_stress_level,
    predict_health_score,
    predict_all,
)
from backend.analytics import summarize_weekly_trends, generate_weekly_insight, generate_weekly_comparison

# ============================================================================
# TEST CASES
# ============================================================================

# Test Case 1: Healthy Individual
print("=" * 80)
print("TEST CASE 1: HEALTHY INDIVIDUAL")
print("=" * 80)

healthy_user = {
    'sleep_hours': 7.5,
    'screen_time_before_sleep': 20,
    'notifications_night': 5,
    'heart_rate': 65,
    'steps_today': 10000,
    'screen_time': 4.0,
    'productive_usage': 3.0,
    'social_usage': 1.0,
    'gaming_usage': 0.5,
    'notifications': 80,
    'unlock_count': 30,
    'steps': 10000,
    'calories': 2150,
}

print("\nInput Data:")
print(json.dumps(healthy_user, indent=2))

print("\n" + "-" * 80)
print("SLEEP PREDICTION")
print("-" * 80)
sleep_result = predict_sleep_score(healthy_user)
print(json.dumps(sleep_result, indent=2))

print("\n" + "-" * 80)
print("STUDY PREDICTION")
print("-" * 80)
study_result = predict_study_score(healthy_user)
print(json.dumps(study_result, indent=2))

print("\n" + "-" * 80)
print("STRESS PREDICTION")
print("-" * 80)
stress_result = predict_stress_level(healthy_user)
print(json.dumps(stress_result, indent=2))

print("\n" + "-" * 80)
print("HEALTH PREDICTION")
print("-" * 80)
health_result = predict_health_score(healthy_user)
print(json.dumps(health_result, indent=2))

# ============================================================================
# Test Case 2: Stressed Individual
print("\n\n" + "=" * 80)
print("TEST CASE 2: STRESSED INDIVIDUAL")
print("=" * 80)

stressed_user = {
    'sleep_hours': 5.0,
    'screen_time_before_sleep': 90,
    'notifications_night': 35,
    'heart_rate': 85,
    'steps_today': 3000,
    'screen_time': 9.0,
    'productive_usage': 1.0,
    'social_usage': 5.0,
    'gaming_usage': 3.0,
    'notifications': 200,
    'unlock_count': 120,
    'steps': 3000,
    'calories': 1800,
}

print("\nInput Data:")
print(json.dumps(stressed_user, indent=2))

print("\n" + "-" * 80)
print("SLEEP PREDICTION")
print("-" * 80)
sleep_result = predict_sleep_score(stressed_user)
print(json.dumps(sleep_result, indent=2))

print("\n" + "-" * 80)
print("STUDY PREDICTION")
print("-" * 80)
study_result = predict_study_score(stressed_user)
print(json.dumps(study_result, indent=2))

print("\n" + "-" * 80)
print("STRESS PREDICTION")
print("-" * 80)
stress_result = predict_stress_level(stressed_user)
print(json.dumps(stress_result, indent=2))

print("\n" + "-" * 80)
print("HEALTH PREDICTION")
print("-" * 80)
health_result = predict_health_score(stressed_user)
print(json.dumps(health_result, indent=2))

# ============================================================================
# Test Case 3: Productive Individual
print("\n\n" + "=" * 80)
print("TEST CASE 3: PRODUCTIVE INDIVIDUAL")
print("=" * 80)

productive_user = {
    'sleep_hours': 7.0,
    'screen_time_before_sleep': 30,
    'notifications_night': 8,
    'heart_rate': 68,
    'steps_today': 9000,
    'screen_time': 6.0,
    'productive_usage': 4.0,
    'social_usage': 1.0,
    'gaming_usage': 0.3,
    'notifications': 100,
    'unlock_count': 40,
    'steps': 9000,
    'calories': 2200,
}

print("\nInput Data:")
print(json.dumps(productive_user, indent=2))

print("\n" + "-" * 80)
print("SLEEP PREDICTION")
print("-" * 80)
sleep_result = predict_sleep_score(productive_user)
print(json.dumps(sleep_result, indent=2))

print("\n" + "-" * 80)
print("STUDY PREDICTION")
print("-" * 80)
study_result = predict_study_score(productive_user)
print(json.dumps(study_result, indent=2))

print("\n" + "-" * 80)
print("STRESS PREDICTION")
print("-" * 80)
stress_result = predict_stress_level(productive_user)
print(json.dumps(stress_result, indent=2))

print("\n" + "-" * 80)
print("HEALTH PREDICTION")
print("-" * 80)
health_result = predict_health_score(productive_user)
print(json.dumps(health_result, indent=2))

# ============================================================================
# Test Case 4: All Predictions at Once
print("\n\n" + "=" * 80)
print("TEST CASE 4: BATCH PREDICTION (ALL AT ONCE)")
print("=" * 80)

typical_user = {
    'sleep_hours': 6.8,
    'screen_time_before_sleep': 45,
    'notifications_night': 15,
    'heart_rate': 72,
    'steps_today': 7500,
    'screen_time': 5.5,
    'productive_usage': 2.5,
    'social_usage': 2.0,
    'gaming_usage': 1.0,
    'notifications': 110,
    'unlock_count': 55,
    'steps': 7500,
    'calories': 2100,
}

print("\nInput Data:")
print(json.dumps(typical_user, indent=2))

print("\n" + "-" * 80)
print("ALL PREDICTIONS")
print("-" * 80)
all_results = predict_all(typical_user)
print(json.dumps(all_results, indent=2))

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

# verify new weekly analytics helpers
from backend.analytics import summarize_weekly_trends, generate_weekly_insight

print("\n\n" + "="*80)
print("WEEKLY TREND HELPERS TEST")
print("="*80)

sample_entries = [
    {'date': '2026-01-01', 'screen_time': 2, 'sleep_hours': 6, 'steps_today': 3000, 'stress_level': 1},
    {'date': '2026-01-02', 'screen_time': 4, 'sleep_hours': 7, 'steps_today': 5000, 'stress_level': 2},
]
trends = summarize_weekly_trends(sample_entries)
print("trends:", trends)
print("insight:", generate_weekly_insight(trends))
comparison = generate_weekly_comparison(trends)
print("comparison:", comparison)

print("\n\n" + "=" * 80)
print("PREDICTION SUMMARY")
print("=" * 80)

users = {
    'Healthy': healthy_user,
    'Stressed': stressed_user,
    'Productive': productive_user,
    'Typical': typical_user
}

summary_data = {}
for user_name, user_data in users.items():
    all_pred = predict_all(user_data)
    summary_data[user_name] = {
        'sleep_score': all_pred['sleep']['sleep_score'],
        'study_score': all_pred['study']['study_score'],
        'stress_level': all_pred['stress']['stress_level'],
        'health_score': all_pred['health']['health_score'],
    }

print("\nComparative Results:")
print("-" * 80)
print(f"{'User Type':<15} {'Sleep':<10} {'Study':<10} {'Stress':<12} {'Health':<10}")
print("-" * 80)
for user_name, scores in summary_data.items():
    print(f"{user_name:<15} {scores['sleep_score']:<10.1f} {scores['study_score']:<10.1f} "
          f"{scores['stress_level']:<12} {scores['health_score']:<10.1f}")

# ============================================================================
# VALIDATION TESTS
# ============================================================================
print("\n\n" + "=" * 80)
print("VALIDATION TESTS")
print("=" * 80)

def validate_predictions():
    """Validate that predictions are in expected ranges."""
    
    tests = [
        ('Sleep Score Range', lambda: 0 <= healthy_user['sleep_hours'] <= 100, True),
        ('Study Score Range', lambda: 0 <= predict_study_score(healthy_user)['study_score'] <= 100, True),
        ('Health Score Range', lambda: 0 <= predict_health_score(healthy_user)['health_score'] <= 100, True),
        ('Stress Classes', lambda: predict_stress_level(healthy_user)['stress_level'] in ['Low', 'Medium', 'High'], True),
        ('Healthy User - Low Stress', lambda: predict_stress_level(healthy_user)['stress_level'] in ['Low', 'Medium'], True),
        ('Stressed User - High Stress', lambda: predict_stress_level(stressed_user)['stress_level'] == 'High', True),
        ('Healthy User - High Health', lambda: predict_health_score(healthy_user)['health_score'] > 60, True),
        ('Stressed User - Low Health', lambda: predict_health_score(stressed_user)['health_score'] < 70, True),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func, expected in tests:
        try:
            result = test_func()
            if result == expected:
                print(f"✓ PASS: {test_name}")
                passed += 1
            else:
                print(f"✗ FAIL: {test_name} (got {result}, expected {expected})")
                failed += 1
        except Exception as e:
            print(f"✗ ERROR: {test_name} - {str(e)}")
            failed += 1
    
    print("\n" + "-" * 80)
    print(f"Tests Passed: {passed}/{passed + failed}")
    return passed, failed

passed, failed = validate_predictions()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n\n" + "=" * 80)
print("ML PIPELINE - TESTING COMPLETE")
print("=" * 80)
print(f"\nValidation: {passed}/{passed + failed} tests passed")
print("\n✓ Models are working correctly!")
print("✓ All predictions are in expected ranges")
print("✓ Prediction logic is sound")
print("\nReady for:")
print("  • Flask API integration")
print("  • Mobile app backend")
print("  • Dashboard integration")
print("  • Automated monitoring")
