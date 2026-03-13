"""
Complete ML Pipeline for Smartphone Health and Habit Tracking System
======================================================================

This module trains four separate machine learning models for:
1. Sleep Score Prediction (Time Series)
2. Study Score Prediction (Time Series)
3. Stress Level Classification (Random Forest)
4. Health Score Regression (Random Forest)

Models are saved for later use in prediction APIs.
"""

import pandas as pd
import numpy as np
import pickle
import os
import warnings
from datetime import datetime
from pathlib import Path

# Suppress warnings
warnings.filterwarnings('ignore')

# Import ML libraries
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error, classification_report
from sklearn.linear_model import LinearRegression

# For time series models
try:
    from statsmodels.tsa.arima.model import ARIMA
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False

try:
    from fbprophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    try:
        from prophet import Prophet
        PROPHET_AVAILABLE = True
    except ImportError:
        PROPHET_AVAILABLE = False

print("=" * 80)
print("SMARTPHONE HEALTH AND HABIT TRACKING - ML PIPELINE")
print("=" * 80)
print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# 1. SLEEP SCORE MODEL (Time Series)
# ============================================================================
def train_sleep_model():
    """
    Train Sleep Score prediction model using time series data.
    Uses regression with lag features to capture temporal patterns.
    """
    print("\n" + "=" * 80)
    print("1. TRAINING SLEEP SCORE MODEL")
    print("=" * 80)
    
    # Load dataset
    df_sleep = pd.read_csv('sleep_score_dataset.csv')
    df_sleep['timestamp'] = pd.to_datetime(df_sleep['timestamp'])
    df_sleep = df_sleep.sort_values('timestamp').reset_index(drop=True)
    
    print(f"✓ Loaded dataset with {len(df_sleep)} rows")
    print(f"  Features: {list(df_sleep.columns)}")
    print(f"  Date range: {df_sleep['timestamp'].min()} to {df_sleep['timestamp'].max()}")
    
    # Create lag features for time series (include new sleep behavior features)
    df_sleep_features = df_sleep.copy()
    for col in [
        'sleep_hours', 'screen_time_before_sleep', 'notifications_night', 'heart_rate', 'steps_today',
        'deep_sleep_hours', 'night_phone_usage', 'sleep_interruption', 'wake_time', 'noise_level', 'ambient_light_level'
    ]:
        for lag in [1, 2, 3]:
            df_sleep_features[f'{col}_lag_{lag}'] = df_sleep_features[col].shift(lag)
    
    # Remove rows with NaN values (created by lag features)
    df_sleep_features = df_sleep_features.dropna()
    
    # Prepare features and target
    feature_cols = [col for col in df_sleep_features.columns if col not in ['timestamp', 'sleep_score']]
    X = df_sleep_features[feature_cols]
    y = df_sleep_features['sleep_score']
    
    # Split data - use chronological split for time series
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train regression model
    sleep_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        random_state=42,
        n_jobs=-1,
        min_samples_split=5,
        min_samples_leaf=2
    )
    sleep_model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = sleep_model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = sleep_model.score(X_test_scaled, y_test)
    
    print(f"\n✓ Model trained successfully!")
    print(f"  RMSE: {rmse:.3f}")
    print(f"  MAE:  {mae:.3f}")
    print(f"  R² Score: {r2:.3f}")
    
    # Save model and scaler
    with open('sleep_model.pkl', 'wb') as f:
        pickle.dump({'model': sleep_model, 'scaler': scaler, 'feature_cols': feature_cols}, f)
    print(f"✓ Saved sleep_model.pkl")
    
    return sleep_model, scaler, feature_cols


# ============================================================================
# 2. STUDY SCORE MODEL (Time Series)
# ============================================================================
def train_study_model():
    """
    Train Study Score prediction model using time series data.
    Uses regression with lag features to capture productivity patterns.
    """
    print("\n" + "=" * 80)
    print("2. TRAINING STUDY SCORE MODEL")
    print("=" * 80)
    
    # Load dataset
    df_study = pd.read_csv('study_drift_dataset.csv')
    df_study['timestamp'] = pd.to_datetime(df_study['timestamp'])
    df_study = df_study.sort_values('timestamp').reset_index(drop=True)
    
    print(f"✓ Loaded dataset with {len(df_study)} rows")
    print(f"  Features: {list(df_study.columns)}")
    print(f"  Date range: {df_study['timestamp'].min()} to {df_study['timestamp'].max()}")
    
    # Create lag features for time series (include new study behavior features)
    df_study_features = df_study.copy()
    for col in [
        'screen_time', 'productive_usage', 'social_usage', 'gaming_usage', 'notifications', 'unlock_count',
        'study_hours', 'app_switching_frequency', 'notifications_during_study', 'break_frequency',
        'phone_usage_during_study', 'completed_tasks'
    ]:
        for lag in [1, 2, 3]:
            df_study_features[f'{col}_lag_{lag}'] = df_study_features[col].shift(lag)
    
    # Remove rows with NaN values
    df_study_features = df_study_features.dropna()
    
    # Prepare features and target
    feature_cols = [col for col in df_study_features.columns if col not in ['timestamp', 'study_score']]
    X = df_study_features[feature_cols]
    y = df_study_features['study_score']
    
    # Split data - chronological split for time series
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train regression model
    study_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        random_state=42,
        n_jobs=-1,
        min_samples_split=5,
        min_samples_leaf=2
    )
    study_model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = study_model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = study_model.score(X_test_scaled, y_test)
    
    print(f"\n✓ Model trained successfully!")
    print(f"  RMSE: {rmse:.3f}")
    print(f"  MAE:  {mae:.3f}")
    print(f"  R² Score: {r2:.3f}")
    
    # Save model and scaler
    with open('study_model.pkl', 'wb') as f:
        pickle.dump({'model': study_model, 'scaler': scaler, 'feature_cols': feature_cols}, f)
    print(f"✓ Saved study_model.pkl")
    
    return study_model, scaler, feature_cols


# ============================================================================
# 3. STRESS LEVEL MODEL (Classification)
# ============================================================================
def train_stress_model():
    """
    Train Stress Level prediction model using Random Forest classification.
    Predicts stress level (Low, Medium, High) from behavioral features.
    """
    print("\n" + "=" * 80)
    print("3. TRAINING STRESS LEVEL CLASSIFIER")
    print("=" * 80)
    
    # Load dataset
    df_stress = pd.read_csv('stress_prediction_dataset.csv')
    
    print(f"✓ Loaded dataset with {len(df_stress)} rows")
    print(f"  Features: {list(df_stress.columns)}")
    print(f"  Class distribution:\n{df_stress['stress_level'].value_counts()}")
    
    # Encode stress levels
    label_encoder = LabelEncoder()
    df_stress['stress_level_encoded'] = label_encoder.fit_transform(df_stress['stress_level'])
    
    print(f"\n  Stress level classes: {dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))}")
    
    # Prepare features and target
    feature_cols = [col for col in df_stress.columns if col not in ['stress_level', 'stress_level_encoded']]
    X = df_stress[feature_cols]
    y = df_stress['stress_level_encoded']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train classifier
    stress_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        random_state=42,
        n_jobs=-1,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight='balanced'
    )
    stress_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = stress_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✓ Model trained successfully!")
    print(f"  Accuracy: {accuracy:.3f}")
    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    
    # Save model, scaler, and label encoder
    with open('stress_model.pkl', 'wb') as f:
        pickle.dump({
            'model': stress_model,
            'scaler': scaler,
            'label_encoder': label_encoder,
            'feature_cols': feature_cols
        }, f)
    print(f"✓ Saved stress_model.pkl")
    
    return stress_model, scaler, label_encoder, feature_cols


# ============================================================================
# 4. HEALTH SCORE MODEL (Regression)
# ============================================================================
def train_health_model():
    """
    Train Health Score prediction model using Random Forest regression.
    Predicts overall health score based on multiple health indicators.
    """
    print("\n" + "=" * 80)
    print("4. TRAINING HEALTH SCORE REGRESSOR")
    print("=" * 80)
    
    # Load dataset
    df_health = pd.read_csv('overall_health_score_dataset.csv')
    
    print(f"✓ Loaded dataset with {len(df_health)} rows")
    print(f"  Features: {list(df_health.columns)}")
    print(f"  Health Score Range: {df_health['health_score'].min():.1f} - {df_health['health_score'].max():.1f}")
    
    # Prepare features and target
    feature_cols = [col for col in df_health.columns if col != 'health_score']
    X = df_health[feature_cols]
    y = df_health['health_score']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    # Train regressor
    health_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        random_state=42,
        n_jobs=-1,
        min_samples_split=5,
        min_samples_leaf=2
    )
    health_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = health_model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = health_model.score(X_test, y_test)
    
    print(f"\n✓ Model trained successfully!")
    print(f"  RMSE: {rmse:.3f}")
    print(f"  MAE:  {mae:.3f}")
    print(f"  R² Score: {r2:.3f}")
    
    # Save model and scaler
    with open('health_model.pkl', 'wb') as f:
        pickle.dump({'model': health_model, 'scaler': scaler, 'feature_cols': feature_cols}, f)
    print(f"✓ Saved health_model.pkl")
    
    return health_model, scaler, feature_cols


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == '__main__':
    try:
        # Train all models
        sleep_model, sleep_scaler, sleep_features = train_sleep_model()
        study_model, study_scaler, study_features = train_study_model()
        stress_model, stress_scaler, stress_le, stress_features = train_stress_model()
        health_model, health_scaler, health_features = train_health_model()
        
        # Summary
        print("\n" + "=" * 80)
        print("TRAINING COMPLETE")
        print("=" * 80)
        print("\n✓ All models trained and saved successfully!")
        print("\nGenerated files:")
        print("  • sleep_model.pkl")
        print("  • study_model.pkl")
        print("  • stress_model.pkl")
        print("  • health_model.pkl")
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n✗ Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
