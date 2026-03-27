"""Train models for Habit & Health Prediction System.

This script orchestrates dataset loading, feature engineering, preprocessing,
model training, hyperparameter tuning, evaluation, and model export.

Run:
    python train_model.py
"""

from ml_pipeline import (
    train_sleep_model,
    train_study_model,
    train_stress_model,
    train_health_model,
)

if __name__ == '__main__':
    print("Starting training run...\n")

    sleep_model, sleep_preprocessor, sleep_features = train_sleep_model()
    study_model, study_preprocessor, study_features = train_study_model()
    stress_model, stress_preprocessor, stress_le, stress_features = train_stress_model()
    health_model, health_preprocessor, health_features = train_health_model()

    print("\nAll models trained and saved.")

    # Export combined artifacts for easy reuse / analysis
    import joblib

    joblib.dump({
        'sleep': sleep_model,
        'study': study_model,
        'stress': stress_model,
        'health': health_model,
    }, 'habit_health_model.pkl')

    joblib.dump({
        'sleep': sleep_preprocessor,
        'study': study_preprocessor,
        'stress': stress_preprocessor,
        'health': health_preprocessor,
    }, 'scaler.pkl')

    joblib.dump({
        'sleep': sleep_features,
        'study': study_features,
        'stress': stress_features,
        'health': health_features,
    }, 'feature_columns.pkl')

    print('Saved artifact files: habit_health_model.pkl, scaler.pkl, feature_columns.pkl')
