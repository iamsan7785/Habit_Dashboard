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
import joblib
import os
import warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from typing import Dict

# Suppress warnings
warnings.filterwarnings('ignore')

# Import ML libraries
from sklearn.model_selection import train_test_split, cross_val_score, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error, classification_report, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_regression, f_classif
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import scipy.stats as stats

# XGBoost and LightGBM
try:
    from xgboost import XGBClassifier, XGBRegressor
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

try:
    from lightgbm import LGBMClassifier, LGBMRegressor
    LGBM_AVAILABLE = True
except ImportError:
    LGBM_AVAILABLE = False

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
# DATASET EXPANSION FUNCTIONS
# ============================================================================

def expand_sleep_dataset(df):
    """Add new sleep-related features with synthetic data."""
    np.random.seed(42)
    n = len(df)
    
    # Add new features with realistic synthetic data
    df = df.copy()
    df['deep_sleep_ratio'] = np.random.uniform(0.1, 0.4, n)  # Deep sleep as ratio of total sleep
    df['sleep_consistency'] = np.random.uniform(0.5, 1.0, n)  # Consistency score
    df['caffeine_intake'] = np.random.randint(0, 500, n)  # mg of caffeine
    df['exercise_before_bed'] = np.random.choice([0, 1], n, p=[0.7, 0.3])  # Binary
    df['bedtime_routine'] = np.random.choice([0, 1], n, p=[0.6, 0.4])  # Binary
    
    return df

def expand_study_dataset(df):
    """Add new study-related features with synthetic data."""
    np.random.seed(42)
    n = len(df)
    
    df = df.copy()
    df['study_session_count'] = np.random.randint(1, 8, n)
    df['break_frequency'] = np.random.randint(0, 10, n)
    df['productivity_app_usage'] = np.random.uniform(0, 5, n)  # hours
    df['focus_score'] = np.random.uniform(0, 100, n)
    df['distraction_events'] = np.random.randint(0, 20, n)
    df['learning_style'] = np.random.choice(['visual', 'auditory', 'kinesthetic'], n)
    df['study_environment'] = np.random.choice(['quiet', 'noisy', 'music'], n)
    
    return df

def expand_stress_dataset(df):
    """Add new stress-related features with synthetic data."""
    np.random.seed(42)
    n = len(df)
    
    df = df.copy()
    df['daily_workload'] = np.random.uniform(1, 10, n)
    df['deadline_pressure'] = np.random.uniform(1, 10, n)
    df['mental_fatigue_score'] = np.random.uniform(0, 100, n)
    df['social_interactions'] = np.random.randint(0, 50, n)
    df['relaxation_time'] = np.random.uniform(0, 4, n)  # hours
    df['mood_score'] = np.random.uniform(1, 10, n)
    df['stress_triggers'] = np.random.choice(['work', 'personal', 'health', 'none'], n)
    
    return df

def expand_health_dataset(df):
    """Add new health-related features with synthetic data."""
    np.random.seed(42)
    n = len(df)
    
    df = df.copy()
    df['water_intake'] = np.random.uniform(0.5, 4, n)  # liters
    df['exercise_minutes'] = np.random.randint(0, 120, n)
    df['calorie_intake'] = np.random.randint(1500, 3500, n)
    df['heart_rate_avg'] = np.random.uniform(60, 100, n)
    df['blood_pressure_systolic'] = np.random.randint(90, 140, n)
    df['blood_pressure_diastolic'] = np.random.randint(60, 90, n)
    df['stress_level_recent'] = np.random.uniform(1, 10, n)
    df['sleep_quality_recent'] = np.random.uniform(1, 10, n)
    
    return df

# ============================================================================
# FEATURE ENGINEERING FUNCTIONS
# ============================================================================

def create_derived_features_sleep(df):
    """Create derived features for sleep model."""
    df = df.copy()
    
    # Sleep Quality Metrics
    df['sleep_quality_score'] = (
        df['sleep_hours'] * df['deep_sleep_ratio'] * 100 - 
        df['sleep_interruption'] * 5 - 
        df['night_phone_usage'] * 0.5
    ).clip(0, 100)
    
    # Behavioral factors
    df['sleep_disruption_index'] = (
        df['notifications_night'] + 
        df['night_phone_usage'] / 10 + 
        df['sleep_interruption'] * 2
    )
    
    df['sleep_recovery_score'] = (
        df['deep_sleep_hours'] / df['sleep_hours'] * 100 + 
        (10 - df['heart_rate'] / 10) + 
        df['steps_today'] / 1000
    ).clip(0, 100)
    
    return df

def create_derived_features_study(df):
    """Create derived features for study model."""
    df = df.copy()
    
    # Productivity Metrics
    df['study_efficiency'] = (df['completed_tasks'] / (df['study_hours'] + 0.1)).clip(0, 10)
    df['focus_index'] = df['focus_score'] / (df['app_switching_frequency'] + 1)
    df['distraction_index'] = (
        df['phone_usage_during_study'] + 
        df['notifications_during_study'] + 
        df['app_switching_frequency']
    )
    
    # Study quality indicators
    df['study_intensity'] = df['study_hours'] / (df['study_session_count'] + 0.1)
    df['break_efficiency'] = df['completed_tasks'] / (df['break_frequency'] + 1)
    
    return df

def create_derived_features_stress(df):
    """Create derived features for stress model."""
    df = df.copy()
    
    # Stress Metrics
    df['stress_index'] = (
        df['daily_workload'] + 
        df['deadline_pressure'] + 
        df['mental_fatigue_score'] + 
        df['screen_time'] / 2
    ) / 4
    
    df['digital_overload'] = (
        df['screen_time'] + 
        df['social_usage'] + 
        df['gaming_usage'] + 
        df['notifications']
    )
    
    df['work_life_balance'] = df['sleep_hours'] / (df['screen_time'] / 24 + 0.1)
    
    return df

def create_derived_features_health(df):
    """Create derived features for health model."""
    df = df.copy()
    
    # Health Score
    df['health_index'] = (
        df['water_intake'] * 10 + 
        df['exercise_minutes'] / 10 + 
        df['steps'] / 1000
    ) / 3
    
    df['metabolic_score'] = (
        df['calorie_intake'] / 2000 + 
        df['exercise_minutes'] / 60 + 
        (100 - df['heart_rate_avg']) / 10
    )
    
    df['lifestyle_score'] = (
        df['sleep_hours'] / 8 * 25 + 
        df['steps'] / 10000 * 25 + 
        (10 - df['screen_time'] / 240) * 25 + 
        df['productive_usage'] / 4 * 25
    ).clip(0, 100)
    
    return df

def add_trend_features(df, target_col, window=3):
    """Add short-term trend features."""
    df = df.copy()
    
    # Rolling averages
    df[f'last_{window}_day_avg'] = df[target_col].rolling(window=window, min_periods=1).mean()
    
    # Trend (difference from previous)
    df[f'{target_col}_trend'] = df[target_col].diff().fillna(0)
    
    return df

# ============================================================================
# PREPROCESSING PIPELINE
# ============================================================================

def detect_overfitting_status(train_score: float, test_score: float, gap_threshold: float = 0.10) -> str:
    """Mark model as overfitting when the train-test gap is significant."""
    return "OVERFITTING" if (train_score - test_score) > gap_threshold else "OK"


def print_model_score_block(
    model_name: str,
    train_score: float,
    test_score: float,
    metric_label: str,
    metric_value: float,
    gap_threshold: float = 0.10
) -> Dict[str, float]:
    """Print standardized model score block for clean output."""
    status = detect_overfitting_status(train_score, test_score, gap_threshold=gap_threshold)
    print("\n" + "-" * 50)
    print(f"Model Name: {model_name}")
    print(f"Train Score: {train_score:.4f}")
    print(f"Test Score: {test_score:.4f}")
    print(f"{metric_label}: {metric_value:.4f}")
    print(f"Overfitting Status: {status}")
    if status == "OVERFITTING":
        print("Warning: Overfitting detected")
    print("-" * 50)
    return {
        'model_name': model_name,
        'train_score': train_score,
        'test_score': test_score,
        'status': status,
        'metric_label': metric_label,
        'metric_value': metric_value
    }


def validate_dataset(df: pd.DataFrame, dataset_name: str):
    """Print basic dataset quality checks."""
    missing_values = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    print(f"✓ {dataset_name} validation")
    print(f"  Missing values: {missing_values}")
    print(f"  Duplicate rows: {duplicate_rows}")


def ensure_no_leakage(feature_cols, target_col: str):
    """Fail fast if target appears in feature columns."""
    if target_col in feature_cols:
        raise ValueError(f"Feature leakage detected: target column '{target_col}' is present in feature set")


def save_regression_plots(y_true, y_pred, model_name: str, output_file: str):
    """Save Actual vs Predicted and Residual plots in one image file."""
    residuals = y_true - y_pred

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Actual vs Predicted
    axes[0].scatter(y_true, y_pred, alpha=0.7, edgecolors='k')
    min_val = min(np.min(y_true), np.min(y_pred))
    max_val = max(np.max(y_true), np.max(y_pred))
    axes[0].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2)
    axes[0].set_title(f'{model_name}: Actual vs Predicted')
    axes[0].set_xlabel('Actual')
    axes[0].set_ylabel('Predicted')

    # Residual plot
    axes[1].scatter(y_pred, residuals, alpha=0.7, edgecolors='k')
    axes[1].axhline(y=0, color='r', linestyle='--', linewidth=2)
    axes[1].set_title(f'{model_name}: Residuals vs Predicted')
    axes[1].set_xlabel('Predicted')
    axes[1].set_ylabel('Residuals (Actual - Predicted)')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"✓ Saved plot: {output_file}")


def print_residual_outliers(y_true: pd.Series, y_pred: np.ndarray, model_name: str):
    """Identify and print residual outliers without deleting any rows."""
    residuals = y_true - y_pred
    threshold = 2 * np.std(residuals)
    outlier_mask = np.abs(residuals) > threshold
    outlier_indices = y_true.index[outlier_mask].tolist()

    print(f"  Residual outlier threshold (2*std): {threshold:.4f}")
    print(f"  Outlier indices (marked only, not removed): {outlier_indices}")
    print(f"  Total marked outliers in {model_name}: {len(outlier_indices)}")


def create_preprocessing_pipeline():
    """Create a robust preprocessing pipeline."""
    steps = [
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ]
    return Pipeline(steps)

# ============================================================================
# MODEL TRAINING FUNCTIONS
# ============================================================================

def train_ensemble_models(X_train, y_train, is_classification=False, cv_folds=5):
    """Train multiple models and return the best one."""
    models = {}
    
    # Adjust cross-validation folds based on data size to avoid errors on small datasets
    cv_folds = max(2, min(cv_folds, len(X_train)))
    
    if is_classification:
        base_models = {
            'RandomForest': RandomForestClassifier(
                random_state=42,
                n_jobs=-1,
                max_depth=12,
                min_samples_split=8,
                min_samples_leaf=2
            ),
            'GradientBoosting': GradientBoostingClassifier(random_state=42),
        }
        if XGB_AVAILABLE:
            base_models['XGBoost'] = XGBClassifier(random_state=42, n_jobs=-1)
        if LGBM_AVAILABLE:
            base_models['LightGBM'] = LGBMClassifier(random_state=42, n_jobs=-1)
    else:
        base_models = {
            'RandomForest': RandomForestRegressor(
                random_state=42,
                n_jobs=-1,
                max_depth=12,
                min_samples_split=8,
                min_samples_leaf=2
            ),
            'GradientBoosting': GradientBoostingRegressor(random_state=42),
        }
        if XGB_AVAILABLE:
            base_models['XGBoost'] = XGBRegressor(random_state=42, n_jobs=-1)
        if LGBM_AVAILABLE:
            base_models['LightGBM'] = LGBMRegressor(random_state=42, n_jobs=-1)
    
    # Hyperparameter spaces
    param_spaces = {
        'RandomForest': {
            'n_estimators': [100, 200, 300],
            'max_depth': [6, 10, 14],
            'min_samples_split': [6, 10, 14],
            'min_samples_leaf': [2, 4, 6],
            'max_features': ['sqrt', 'log2']
        },
        'GradientBoosting': {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'subsample': [0.8, 0.9, 1.0]
        },
        'XGBoost': {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'min_child_weight': [1, 3, 5],
            'subsample': [0.8, 0.9, 1.0],
            'colsample_bytree': [0.8, 0.9, 1.0]
        },
        'LightGBM': {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'min_child_samples': [10, 20, 30],
            'subsample': [0.8, 0.9, 1.0],
            'colsample_bytree': [0.8, 0.9, 1.0]
        }
    }
    
    best_model = None
    best_score = -np.inf if is_classification else np.inf
    best_name = None
    
    for name, model in base_models.items():
        print(f"  Training {name}...")
        
        # Randomized search
        search = RandomizedSearchCV(
            model, 
            param_spaces[name], 
            n_iter=10, 
            cv=cv_folds, 
            scoring='accuracy' if is_classification else 'neg_mean_squared_error',
            random_state=42,
            n_jobs=-1
        )
        
        search.fit(X_train, y_train)
        
        # Evaluate
        cv_scores = cross_val_score(search.best_estimator_, X_train, y_train, cv=cv_folds, 
                                   scoring='accuracy' if is_classification else 'neg_mean_squared_error')
        mean_score = cv_scores.mean()
        
        print(f"    Best params: {search.best_params_}")
        print(f"    CV Score: {mean_score:.4f}")
        
        models[name] = search.best_estimator_
        
        # Select best model
        if is_classification:
            if mean_score > best_score:
                best_score = mean_score
                best_model = search.best_estimator_
                best_name = name
        else:
            if -mean_score < best_score:  # Since neg_mean_squared_error
                best_score = -mean_score
                best_model = search.best_estimator_
                best_name = name
    
    print(f"  Best model: {best_name} with score: {best_score:.4f}")
    return best_model, models

def evaluate_model(model, X_test, y_test, is_classification=False, feature_names=None):
    """Evaluate model and print detailed metrics."""
    y_pred = model.predict(X_test)
    
    if is_classification:
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # ROC-AUC for binary or handle multi-class
        if len(np.unique(y_test)) == 2:
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            roc_auc = roc_auc_score(y_test, y_pred_proba)
        else:
            roc_auc = None
        
        conf_matrix = confusion_matrix(y_test, y_pred)
        class_report = classification_report(y_test, y_pred)
        
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1 Score: {f1:.4f}")
        if roc_auc:
            print(f"  ROC-AUC: {roc_auc:.4f}")
        print(f"  Confusion Matrix:\n{conf_matrix}")
        print(f"  Classification Report:\n{class_report}")
        
        # Feature importance
        if hasattr(model, 'feature_importances_') and feature_names:
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1]
            print("  Top 10 Feature Importances:")
            for i in range(min(10, len(feature_names))):
                print(f"    {feature_names[indices[i]]}: {importances[indices[i]]:.4f}")
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'y_pred': y_pred
        }
    
    else:
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = model.score(X_test, y_test)
        
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE: {mae:.4f}")
        print(f"  R² Score: {r2:.4f}")
        
        # Feature importance
        if hasattr(model, 'feature_importances_') and feature_names:
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1]
            print("  Top 10 Feature Importances:")
            for i in range(min(10, len(feature_names))):
                print(f"    {feature_names[indices[i]]}: {importances[indices[i]]:.4f}")
        
        return {
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'y_pred': y_pred
        }
def train_sleep_model():
    """
    Train Sleep Score prediction model with leakage-safe evaluation.
    """
    print("\n" + "=" * 80)
    print("1. TRAINING SLEEP SCORE MODEL")
    print("=" * 80)
    
    # Load dataset and validate quality
    df_sleep = pd.read_csv('sleep_score_dataset.csv')
    validate_dataset(df_sleep, 'Sleep dataset')

    print(f"✓ Loaded dataset with {len(df_sleep)} rows")
    print(f"  Features: {list(df_sleep.columns)}")

    # Strict feature list requested
    feature_cols = [
        'sleep_hours',
        'screen_time_before_sleep',
        'notifications_night',
        'heart_rate',
        'steps_today'
    ]
    ensure_no_leakage(feature_cols, 'sleep_score')
    X = df_sleep[feature_cols].copy()
    y = df_sleep['sleep_score'].copy()

    # Keep only numeric features to keep preprocessing stable
    X = X.select_dtypes(include=[np.number])
    feature_cols = X.columns.tolist()

    # Use shuffled split to avoid ordering bias
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=True
    )

    # Preprocessing pipeline (fit on training set only)
    preprocessor = create_preprocessing_pipeline()
    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.transform(X_test)

    # Train only requested model
    sleep_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=5,
        min_samples_split=8,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    )
    sleep_model.fit(X_train, y_train)

    # Evaluate with held-out test predictions only
    y_test_pred = sleep_model.predict(X_test)
    train_score = sleep_model.score(X_train, y_train)
    test_score = sleep_model.score(X_test, y_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    mae = mean_absolute_error(y_test, y_test_pred)

    print("\n✓ Sleep model evaluation (test set only for predictions)")
    print(f"  RMSE (test): {rmse:.4f}")
    print(f"  MAE (test): {mae:.4f}")
    score_summary = print_model_score_block('Sleep Model', train_score, test_score, 'RMSE', rmse)

    save_regression_plots(y_test, y_test_pred, 'Sleep Model', 'sleep_plot.png')
    print_residual_outliers(y_test, y_test_pred, 'Sleep Model')
    
    # Save model and preprocessor
    joblib.dump({
        'model': sleep_model,
        'scaler': preprocessor,
        'feature_cols': feature_cols
    }, 'sleep_model.pkl')
    print(f"✓ Saved sleep_model.pkl")
    
    return sleep_model, preprocessor, feature_cols, score_summary


# ============================================================================
# 2. STUDY SCORE MODEL (Time Series)
# ============================================================================
def train_study_model():
    """
    Train Study Score prediction model with leakage-safe split and evaluation.
    """
    print("\n" + "=" * 80)
    print("2. TRAINING STUDY SCORE MODEL")
    print("=" * 80)
    
    # Load and expand dataset
    df_study = pd.read_csv('study_drift_dataset.csv')
    df_study['timestamp'] = pd.to_datetime(df_study['timestamp'])
    df_study = df_study.sort_values('timestamp').reset_index(drop=True)
    
    # Expand with new features
    df_study = expand_study_dataset(df_study)
    
    # Create derived features
    df_study = create_derived_features_study(df_study)
    
    # Requested feature engineering for bias reduction and interpretability
    df_study['distraction_score'] = df_study['social_usage'] + df_study['gaming_usage']
    df_study['focus_ratio'] = df_study['productive_usage'] / (df_study['screen_time'] + 1)

    # Clip target into realistic range
    df_study['study_score'] = df_study['study_score'].clip(0, 100)
    
    print(f"✓ Loaded and enhanced dataset with {len(df_study)} rows")
    print(f"  Features: {list(df_study.columns)}")
    print(f"  Date range: {df_study['timestamp'].min()} to {df_study['timestamp'].max()}")
    
    # Create lag features for behavioral predictors only (no target leakage)
    df_study_features = df_study.copy()
    lag_cols = [
        'screen_time', 'productive_usage', 'social_usage', 'gaming_usage', 'notifications', 'unlock_count',
        'study_hours', 'app_switching_frequency', 'notifications_during_study', 'break_frequency',
        'phone_usage_during_study', 'completed_tasks', 'study_efficiency', 'focus_index', 'distraction_index'
    ]
    for col in lag_cols:
        for lag in [1, 2, 3]:
            df_study_features[f'{col}_lag_{lag}'] = df_study_features[col].shift(lag)
    
    # Remove rows with NaN values
    df_study_features = df_study_features.dropna()
    
    # Prepare features and target
    # Guard against leakage by removing any target-like columns.
    leakage_prone_cols = [
        col for col in df_study_features.columns
        if 'study_score' in col and col != 'study_score'
    ]
    feature_cols = [
        col for col in df_study_features.columns
        if col not in ['timestamp', 'study_score'] + leakage_prone_cols
    ]
    ensure_no_leakage(feature_cols, 'study_score')
    X = df_study_features[feature_cols]
    y = df_study_features['study_score']

    # Keep only numeric features
    X = X.select_dtypes(include=[np.number])
    feature_cols = X.columns.tolist()

    # Split data with shuffle to avoid temporal ordering bias in evaluation.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=True
    )

    # Preprocessing pipeline (fit on training set only)
    preprocessor = create_preprocessing_pipeline()
    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.transform(X_test)

    # Train only on training data.
    study_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=4,
        min_samples_split=8,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    )
    study_model.fit(X_train, y_train)

    # Evaluate only on the held-out test set.
    y_test_pred = study_model.predict(X_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    train_score = study_model.score(X_train, y_train)
    test_score = study_model.score(X_test, y_test)

    print("\n✓ Study model evaluation (test set only for predictions)")
    print(f"  RMSE (test): {test_rmse:.4f}")
    print(f"  Train Score (R2): {train_score:.4f}")
    print(f"  Test Score (R2): {test_score:.4f}")

    score_summary = print_model_score_block('Study Model', train_score, test_score)

    save_regression_plots(y_test, y_test_pred, 'Study Model', 'study_plot.png')
    print_residual_outliers(y_test, y_test_pred, 'Study Model')

    residuals = y_test - y_test_pred
    print(f"  Residual mean (target near 0): {np.mean(residuals):.4f}")
    print(f"  Residual std: {np.std(residuals):.4f}")
    
    # Save model and preprocessor
    joblib.dump({
        'model': study_model,
        'model_name': 'RandomForestRegressor(max_depth=4)',
        'scaler': preprocessor,
        'feature_cols': feature_cols
    }, 'study_model.pkl')
    print(f"✓ Saved study_model.pkl")
    
    return study_model, preprocessor, feature_cols, score_summary


# ============================================================================
# 3. STRESS LEVEL MODEL (Classification)
# ============================================================================
def train_stress_model():
    """
    Train Stress Level classifier with leakage-safe evaluation.
    """
    print("\n" + "=" * 80)
    print("3. TRAINING STRESS LEVEL CLASSIFIER")
    print("=" * 80)
    
    # Load dataset and validate quality
    df_stress = pd.read_csv('stress_prediction_dataset.csv')
    validate_dataset(df_stress, 'Stress dataset')

    print(f"✓ Loaded dataset with {len(df_stress)} rows")
    print(f"  Features: {list(df_stress.columns)}")
    print(f"  Class distribution:\n{df_stress['stress_level'].value_counts()}")
    
    # Encode stress levels
    label_encoder = LabelEncoder()
    df_stress['stress_level_encoded'] = label_encoder.fit_transform(df_stress['stress_level'])
    
    print(f"\n  Stress level classes: {dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))}")
    
    # Strict feature list requested
    feature_cols = [
        'screen_time',
        'notifications',
        'unlock_count',
        'sleep_hours',
        'steps',
        'heart_rate',
        'social_usage',
        'gaming_usage'
    ]
    ensure_no_leakage(feature_cols, 'stress_level')
    X = df_stress[feature_cols]
    y = df_stress['stress_level_encoded']

    # Keep only numeric features
    X = X.select_dtypes(include=[np.number])
    feature_cols = X.columns.tolist()

    # Split data with shuffle enabled
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y, shuffle=True
    )

    # Preprocessing pipeline (fit on training set only)
    preprocessor = create_preprocessing_pipeline()
    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.transform(X_test)

    # Train requested classifier only
    stress_model = RandomForestClassifier(
        n_estimators=300,
        max_depth=5,
        min_samples_split=8,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    )
    stress_model.fit(X_train, y_train)

    # Evaluate with held-out test predictions only
    y_test_pred = stress_model.predict(X_test)
    train_score = stress_model.score(X_train, y_train)
    test_score = stress_model.score(X_test, y_test)
    accuracy = accuracy_score(y_test, y_test_pred)
    conf_matrix = confusion_matrix(y_test, y_test_pred)
    class_report = classification_report(y_test, y_test_pred, target_names=label_encoder.classes_)

    print("\n✓ Stress model evaluation (test set only for predictions)")
    print(f"  Accuracy (test): {accuracy:.4f}")
    print(f"  Confusion Matrix:\n{conf_matrix}")
    print(f"  Classification Report:\n{class_report}")

    score_summary = print_model_score_block('Stress Model', train_score, test_score, 'Accuracy', accuracy)

    # Save confusion matrix visualization
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(conf_matrix, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(
        xticks=np.arange(conf_matrix.shape[1]),
        yticks=np.arange(conf_matrix.shape[0]),
        xticklabels=label_encoder.classes_,
        yticklabels=label_encoder.classes_,
        title='Stress Model Confusion Matrix',
        ylabel='True label',
        xlabel='Predicted label'
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
    thresh = conf_matrix.max() / 2.0
    for i in range(conf_matrix.shape[0]):
        for j in range(conf_matrix.shape[1]):
            ax.text(j, i, format(conf_matrix[i, j], 'd'), ha='center', va='center', color='white' if conf_matrix[i, j] > thresh else 'black')
    fig.tight_layout()
    plt.savefig('stress_confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("✓ Saved plot: stress_confusion_matrix.png")

    # Save model and encoders
    joblib.dump({
        'model': stress_model,
        'scaler': preprocessor,
        'label_encoder': label_encoder,
        'feature_cols': feature_cols
    }, 'stress_model.pkl')
    joblib.dump(label_encoder, 'stress_label_encoder.pkl')
    print(f"✓ Saved stress_model.pkl")
    print(f"✓ Saved stress_label_encoder.pkl")
    
    return stress_model, preprocessor, label_encoder, feature_cols, score_summary


# ============================================================================
# 4. HEALTH SCORE MODEL (Regression)
# ============================================================================
def train_health_model():
    """
    Train Health Score prediction model with leakage-safe evaluation.
    """
    print("\n" + "=" * 80)
    print("4. TRAINING HEALTH SCORE REGRESSOR")
    print("=" * 80)
    
    # Load dataset and validate quality
    df_health = pd.read_csv('overall_health_score_dataset.csv')
    validate_dataset(df_health, 'Health dataset')

    # Requested feature engineering
    df_health['engagement'] = df_health['productive_usage'] - (df_health['social_usage'] + df_health['gaming_usage'])

    print(f"✓ Loaded dataset with {len(df_health)} rows")
    print(f"  Features: {list(df_health.columns)}")
    print(f"  Health Score Range: {df_health['health_score'].min():.1f} - {df_health['health_score'].max():.1f}")
    
    # Strict feature list requested
    feature_cols = [
        'sleep_hours',
        'steps',
        'calories',
        'heart_rate',
        'screen_time',
        'social_usage',
        'gaming_usage',
        'productive_usage',
        'notifications',
        'unlock_count',
        'engagement'
    ]
    ensure_no_leakage(feature_cols, 'health_score')
    X = df_health[feature_cols]
    y = df_health['health_score']

    # Keep only numeric features
    X = X.select_dtypes(include=[np.number])
    feature_cols = X.columns.tolist()

    # Split data with shuffle enabled
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=True
    )

    # Preprocessing pipeline (fit on training set only)
    preprocessor = create_preprocessing_pipeline()
    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.transform(X_test)

    # Train requested model only
    health_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=5,
        min_samples_split=8,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    )
    health_model.fit(X_train, y_train)

    # Evaluate with held-out test predictions only
    y_test_pred = health_model.predict(X_test)
    train_score = health_model.score(X_train, y_train)
    test_score = health_model.score(X_test, y_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    mae = mean_absolute_error(y_test, y_test_pred)

    print("\n✓ Health model evaluation (test set only for predictions)")
    print(f"  RMSE (test): {rmse:.4f}")
    print(f"  MAE (test): {mae:.4f}")
    score_summary = print_model_score_block('Health Model', train_score, test_score, 'RMSE', rmse)

    save_regression_plots(y_test, y_test_pred, 'Health Model', 'health_plot.png')
    print_residual_outliers(y_test, y_test_pred, 'Health Model')
    
    # Save model and preprocessor
    joblib.dump({
        'model': health_model,
        'scaler': preprocessor,
        'feature_cols': feature_cols
    }, 'health_model.pkl')
    print(f"✓ Saved health_model.pkl")
    
    return health_model, preprocessor, feature_cols, score_summary


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == '__main__':
    try:
        # Train all models
        sleep_model, sleep_scaler, sleep_features, sleep_summary = train_sleep_model()
        study_model, study_scaler, study_features, study_summary = train_study_model()
        stress_model, stress_scaler, stress_le, stress_features, stress_summary = train_stress_model()
        health_model, health_scaler, health_features, health_summary = train_health_model()
        
        # Summary
        print("\n" + "=" * 80)
        print("TRAINING COMPLETE")
        print("=" * 80)
        print("\n✓ All models trained and saved successfully!")
        print("\nModel Generalization Summary:")
        for summary in [sleep_summary, study_summary, stress_summary, health_summary]:
            print(
                f"  {summary['model_name']}: "
                f"Train={summary['train_score']:.4f}, "
                f"Test={summary['test_score']:.4f}, "
                f"Status={summary['status']}"
            )
        print("\nGenerated files:")
        print("  • sleep_model.pkl")
        print("  • study_model.pkl")
        print("  • stress_model.pkl")
        print("  • stress_label_encoder.pkl")
        print("  • health_model.pkl")
        print("  • sleep_plot.png")
        print("  • study_plot.png")
        print("  • stress_confusion_matrix.png")
        print("  • health_plot.png")
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n✗ Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
