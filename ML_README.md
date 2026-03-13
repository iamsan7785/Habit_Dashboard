# Smartphone Health and Habit Tracking - ML Pipeline

Complete machine learning pipeline for predicting health metrics and behavioral patterns from smartphone usage data.

## 📊 Overview

This system trains and deploys four separate machine learning models:

1. **Sleep Score Model** - Time series regression predicting sleep quality
2. **Study Score Model** - Time series regression predicting productivity
3. **Stress Level Model** - Classification predicting stress (Low/Medium/High)
4. **Health Score Model** - Regression predicting overall health (0-100)

## 📁 Files

### Core Pipeline
- `ml_pipeline.py` - Main training pipeline for all four models
- `predictions.py` - Prediction functions for user input
- `ml_api.py` - Flask API blueprint for web integration
- `generate_datasets.py` - Generate synthetic training data

### Generated Models (after training)
- `sleep_model.pkl` - Trained sleep score model
- `study_model.pkl` - Trained study score model
- `stress_model.pkl` - Trained stress level classifier
- `health_model.pkl` - Trained health score regressor

### Datasets (after generation)
- `sleep_score_dataset.csv` - Sleep data (2000 rows)
- `study_drift_dataset.csv` - Study data (2000 rows)
- `stress_prediction_dataset.csv` - Stress data (2000 rows)
- `overall_health_score_dataset.csv` - Health data (2000 rows)

## 🚀 Quick Start

### 1. Generate Datasets

```bash
python generate_datasets.py
```

Creates four CSV datasets with realistic smartphone and health data:
- 2000 rows per dataset
- Real-world feature correlations
- Multiple prediction targets (sleep_score, study_score, stress_level, health_score)

### 2. Train Models

```bash
python ml_pipeline.py
```

Trains all four models and saves them as pickle files:
- Sleep Score: RMSE ~1.5, R² ~0.93
- Study Score: RMSE ~3.3, R² ~0.85
- Stress Level: Accuracy ~89%
- Health Score: RMSE ~2.4, R² ~0.91

### 3. Make Predictions

```python
from predictions import predict_sleep_score, predict_study_score, predict_stress_level, predict_health_score

# Sleep prediction
sleep_result = predict_sleep_score({
    'sleep_hours': 6.5,
    'screen_time_before_sleep': 45,
    'notifications_night': 12,
    'heart_rate': 72,
    'steps_today': 8500
})
print(sleep_result)

# Study prediction
study_result = predict_study_score({
    'screen_time': 5.5,
    'productive_usage': 2.0,
    'social_usage': 2.5,
    'gaming_usage': 1.0,
    'notifications': 120,
    'unlock_count': 45
})
print(study_result)

# Stress prediction
stress_result = predict_stress_level({
    'screen_time': 6.5,
    'notifications': 200,
    'unlock_count': 60,
    'sleep_hours': 5.8,
    'steps': 4000,
    'heart_rate': 80,
    'social_usage': 3.5,
    'gaming_usage': 1.5
})
print(stress_result)

# Health prediction
health_result = predict_health_score({
    'sleep_hours': 7,
    'steps': 6000,
    'calories': 2100,
    'heart_rate': 72,
    'screen_time': 5,
    'social_usage': 2,
    'gaming_usage': 1,
    'productive_usage': 2.5,
    'notifications': 120,
    'unlock_count': 40
})
print(health_result)

# All predictions at once
from predictions import predict_all
all_results = predict_all({...all user data...})
```

## 🌐 Flask Integration

Integrate the ML models into your Flask app:

```python
from flask import Flask
from ml_api import ml_bp

app = Flask(__name__)
app.register_blueprint(ml_bp)

if __name__ == '__main__':
    app.run(debug=True)
```

### API Endpoints

#### `POST /api/predict/sleep`
Predict sleep score

**Request:**
```json
{
    "sleep_hours": 6.5,
    "screen_time_before_sleep": 45,
    "notifications_night": 12,
    "heart_rate": 72,
    "steps_today": 8500
}
```

**Response:**
```json
{
    "sleep_score": 67.9,
    "confidence": "High",
    "factors": ["sleep_hours", "notifications_night", "heart_rate"],
    "interpretation": "Fair sleep quality - consider reducing screen time before bed"
}
```

#### `POST /api/predict/study`
Predict study score

**Request:**
```json
{
    "screen_time": 5.5,
    "productive_usage": 2.0,
    "social_usage": 2.5,
    "gaming_usage": 1.0,
    "notifications": 120,
    "unlock_count": 45
}
```

**Response:**
```json
{
    "study_score": 17.7,
    "productivity_ratio": 36.4,
    "screen_time_hours": 5.5,
    "distractions": 3.5,
    "interpretation": "Poor productivity - significant restructuring needed"
}
```

#### `POST /api/predict/stress`
Predict stress level

**Request:**
```json
{
    "screen_time": 6.5,
    "notifications": 200,
    "unlock_count": 60,
    "sleep_hours": 5.8,
    "steps": 4000,
    "heart_rate": 80,
    "social_usage": 3.5,
    "gaming_usage": 1.5
}
```

**Response:**
```json
{
    "stress_level": "Low",
    "confidence": 53.7,
    "probability_distribution": {
        "High": 3.6,
        "Low": 53.7,
        "Medium": 42.7
    },
    "risk_factors": ["No major risk factors detected"],
    "recommendations": [
        "Maintain current healthy habits",
        "Continue regular exercise and sleep schedule",
        "Monitor stress levels weekly"
    ]
}
```

#### `POST /api/predict/health`
Predict overall health score

**Request:**
```json
{
    "sleep_hours": 7,
    "steps": 6000,
    "calories": 2100,
    "heart_rate": 72,
    "screen_time": 5,
    "social_usage": 2,
    "gaming_usage": 1,
    "productive_usage": 2.5,
    "notifications": 120,
    "unlock_count": 40
}
```

**Response:**
```json
{
    "health_score": 58.4,
    "health_status": "Fair",
    "component_scores": {
        "sleep": 65.0,
        "activity": 70.8,
        "nutrition": 84.0,
        "heart_rate": 86.0,
        "screen_time": 98.2,
        "productivity": 50.0
    },
    "recommendations": [
        "Improve sleep: Aim for 7-8 hours per night",
        "Increase productive app usage and minimize distractions"
    ]
}
```

#### `POST /api/predict/all`
Get all predictions in one request

**Request:** Union of all above fields

**Response:** Combined predictions for all models

#### `GET /api/predict/health`
Health check (verify all models are loaded)

**Response:**
```json
{
    "status": "healthy",
    "models": {
        "sleep_model": "loaded",
        "study_model": "loaded",
        "stress_model": "loaded",
        "health_model": "loaded"
    }
}
```

## 📈 Model Details

### 1. Sleep Score Model
- **Type:** Random Forest Regression with lag features
- **Features:** 20 (including 3-day lag features)
- **Target:** Sleep score (0-100)
- **Performance:** R² = 0.933, MAE = 1.089
- **Use:** Detect sleep quality degradation and predict future sleep scores

### 2. Study Score Model
- **Type:** Random Forest Regression with lag features
- **Features:** 18 (including 3-day lag features)
- **Target:** Study score (0-100)
- **Performance:** R² = 0.854, MAE = 2.524
- **Use:** Identify productivity drift and predict study effectiveness

### 3. Stress Level Model
- **Type:** Random Forest Classification (3 classes)
- **Features:** 8 (scaled)
- **Target:** Stress level (Low, Medium, High)
- **Performance:** Accuracy = 0.892
- **Class distribution:** High (67%), Medium (21%), Low (12%)
- **Use:** Real-time stress prediction with risk factors

### 4. Health Score Model
- **Type:** Random Forest Regression
- **Features:** 10 (scaled)
- **Target:** Health score (0-100)
- **Performance:** R² = 0.913, MAE = 1.806
- **Use:** Comprehensive health assessment from multiple indicators

## 🔧 Feature Engineering

### Time Series Features (Sleep & Study)
- **Lag features:** 1-day, 2-day, 3-day lags for temporal patterns
- **Temporal split:** 80% train, 20% test (chronological)
- **Normalization:** StandardScaler on all features

### Classification Features (Stress)
- **Scaling:** StandardScaler
- **Class balancing:** Balanced class weights
- **Train-test split:** 80-20 with stratification

### Regression Features (Health)
- **Scaling:** StandardScaler
- **Multiple domains:** Sleep, activity, nutrition, physiology, technology use
- **Train-test split:** 80-20 random split

## 📊 Data Characteristics

### User Demographics
- Age range: 18-30 years
- Target: Smartphone users with health tracking capability
- Data collection: Automated from smartphone sensors and apps

### Features (Realistic Ranges)
- **Screen time:** 0.5-10 hours/day
- **Sleep hours:** 3-10 hours
- **Steps:** 500-25,000 per day
- **Heart rate:** 50-120 bpm
- **Notifications:** 0-120 per day
- **Phone unlocks:** 10-300 per day

### Scores (0-100 Scale)
- **Sleep score:** 44-98 (real distribution)
- **Study score:** 0-75 (highly variable)
- **Health score:** 24-79 (realistic health variation)

## 🤖 Model Training Details

### Data Preprocessing
1. Load CSV data
2. Type conversion (timestamp → datetime)
3. Sort by timestamp (time series only)
4. Create lag features (time series models)
5. Remove NaN values
6. Feature scaling (StandardScaler)
7. Train-test split

### Training Parameters
```python
RandomForestRegressor(
    n_estimators=100,
    max_depth=20,
    random_state=42,
    n_jobs=-1,
    min_samples_split=5,
    min_samples_leaf=2
)

RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    random_state=42,
    n_jobs=-1,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight='balanced'  # For imbalanced classes
)
```

### Model Persistence
- Models saved as pickle files (.pkl)
- Includes model object, scaler, and feature info
- Loaded on-demand in prediction functions
- ~100 KB total for all models

## 📝 Example Usage

### Standalone Predictions
```python
from predictions import predict_all

user_data = {
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

results = predict_all(user_data)
print(f"Sleep: {results['sleep']['sleep_score']}")
print(f"Study: {results['study']['study_score']}")
print(f"Stress: {results['stress']['stress_level']}")
print(f"Health: {results['health']['health_score']}")
```

### Flask Web Integration
```python
from flask import Flask, render_template
from ml_api import ml_bp

app = Flask(__name__)
app.register_blueprint(ml_bp)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Frontend Integration (JavaScript)
```javascript
async function getPredictions(userData) {
    const response = await fetch('/api/predict/all', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(userData)
    });
    return await response.json();
}

// Usage
const results = await getPredictions({
    sleep_hours: 6.5,
    screen_time_before_sleep: 45,
    notifications_night: 12,
    // ... other fields
});

console.log(`Health Score: ${results.health.health_score}`);
console.log(`Stress Level: ${results.stress.stress_level}`);
```

## 🔍 Interpretation Guide

### Sleep Score (0-100)
- **85+:** Excellent - Maintain current habits
- **70-84:** Good - Minor improvements recommended
- **50-69:** Fair - Consider reducing screen time before bed
- **<50:** Poor - Urgent intervention needed

### Study Score (0-100)
- **70+:** Excellent productivity
- **50-69:** Good with minor distractions
- **30-49:** Below average
- **<30:** Poor productivity

### Stress Level
- **Low:** Healthy stress levels, maintain habits
- **Medium:** Reduce notifications and social media
- **High:** Urgent intervention (increase sleep, activity, reduce screen)

### Health Score (0-100)
- **80+:** Excellent health status
- **60-79:** Good overall health
- **40-59:** Fair - Multiple improvements needed
- **<40:** Poor - Significant lifestyle changes required

## 🛠️ Dependencies

```
pandas>=1.3.0
numpy>=1.21.0
scikit-learn>=1.0.0
flask>=2.0.0
(Optional) statsmodels>=0.13.0  # For ARIMA
(Optional) prophet>=1.1.0  # For Prophet forecasting
```

## 📚 References

- Model types: Random Forest, Classification, Regression
- Time series: Lag features for temporal patterns
- Evaluation: RMSE, MAE, R² score, Accuracy, Classification report
- Deployment: Flask blueprint for easy integration

## 🔐 Security Notes

- Models contain no sensitive user data
- Predictions are stateless (no data storage)
- Scale data consistently (use saved scalers)
- Validate input ranges in production

## 🚀 Future Enhancements

- Real-time predictions with streaming data
- LSTM models for deeper temporal patterns
- Anomaly detection for unusual patterns
- Custom user profiles and trend analysis
- Mobile app backend integration
- Database logging of predictions
- Model retraining pipeline
- A/B testing new model versions
