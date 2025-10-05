import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
import sys
sys.path.append('/home/sakshamkapoor/Projects/Aura/data')
from simulate_data import DataSimulator

class AuraMachineHealthModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = ['temperature', 'vibration', 'rotation_speed', 'load']
        self.model_path = '/home/sakshamkapoor/Projects/Aura/ml_model/model.pkl'
        self.scaler_path = '/home/sakshamkapoor/Projects/Aura/ml_model/scaler.pkl'
        
    def prepare_features(self, df):
        """Prepare features for training or prediction"""
        # Create additional features
        df = df.copy()
        
        # Temperature deviation from normal
        df['temp_deviation'] = abs(df['temperature'] - 75)  # 75°C as normal center
        
        # Vibration intensity categories
        df['vibration_high'] = (df['vibration'] > 0.8).astype(int)
        
        # Speed anomaly (too high or too low)
        df['speed_anomaly'] = ((df['rotation_speed'] < 1400) | (df['rotation_speed'] > 1600)).astype(int)
        
        # Load stress indicator
        df['load_stress'] = (df['load'] > 90).astype(int)
        
        # Combined risk factors
        df['risk_score'] = (
            (df['temperature'] > 85).astype(int) * 2 +
            (df['vibration'] > 0.8).astype(int) * 2 +
            (df['rotation_speed'] > 1600).astype(int) * 1 +
            (df['load'] > 90).astype(int) * 1
        )
        
        # Feature columns for model
        feature_cols = self.feature_columns + [
            'temp_deviation', 'vibration_high', 'speed_anomaly', 
            'load_stress', 'risk_score'
        ]
        
        return df[feature_cols]
    
    def train_model(self, data_path=None):
        """Train the machine learning model"""
        print("Training Aura ML Model...")
        
        # Generate data if not provided
        if data_path is None or not os.path.exists('/home/sakshamkapoor/Projects/Aura/data/sensor_data.csv'):
            print("Generating training data...")
            simulator = DataSimulator()
            df = simulator.generate_historical_data(days=90, samples_per_day=24)
        else:
            df = pd.read_csv(data_path)
        
        print(f"Training data shape: {df.shape}")
        print(f"Failure rate: {df['failure'].mean():.2%}")
        
        # Prepare features
        X = self.prepare_features(df)
        y = df['failure']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'  # Handle imbalanced data
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        print("\nModel Performance:")
        print(classification_report(y_test, y_pred))
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 5 Most Important Features:")
        print(feature_importance.head())
        
        # Save model and scaler
        self.save_model()
        
        return self.model
    
    def predict_failure_probability(self, sensor_data):
        """Predict failure probability for given sensor data"""
        if self.model is None:
            self.load_model()
        
        # Convert to DataFrame if it's a dict
        if isinstance(sensor_data, dict):
            sensor_data = pd.DataFrame([sensor_data])
        
        # Prepare features
        X = self.prepare_features(sensor_data)
        X_scaled = self.scaler.transform(X)
        
        # Get failure probabilities
        failure_probs = self.model.predict_proba(X_scaled)[:, 1]  # Probability of failure
        
        return failure_probs
    
    def calculate_health_score(self, sensor_data):
        """Calculate health score (0-100%) based on failure probability"""
        failure_prob = self.predict_failure_probability(sensor_data)[0]
        
        # Convert failure probability to health score
        # Lower failure probability = higher health score
        health_score = max(0, min(100, (1 - failure_prob) * 100))
        
        # Add some additional logic based on sensor readings
        if isinstance(sensor_data, dict):
            temp = sensor_data.get('temperature', 75)
            vibration = sensor_data.get('vibration', 0.4)
            load = sensor_data.get('load', 80)
            
            # Apply penalties for extreme values
            if temp > 95:
                health_score *= 0.8
            elif temp > 90:
                health_score *= 0.9
                
            if vibration > 1.2:
                health_score *= 0.7
            elif vibration > 1.0:
                health_score *= 0.85
                
            if load > 95:
                health_score *= 0.8
        
        return round(health_score, 1)
    
    def get_alert_level(self, health_score):
        """Determine alert level based on health score"""
        if health_score >= 80:
            return "healthy"
        elif health_score >= 60:
            return "warning"
        elif health_score >= 40:
            return "critical"
        else:
            return "danger"
    
    def analyze_machine_health(self, sensor_data):
        """Complete machine health analysis"""
        failure_prob = self.predict_failure_probability(sensor_data)[0]
        health_score = self.calculate_health_score(sensor_data)
        alert_level = self.get_alert_level(health_score)
        
        # Identify potential issues
        issues = []
        if isinstance(sensor_data, dict):
            if sensor_data.get('temperature', 0) > 90:
                issues.append("High temperature detected")
            if sensor_data.get('vibration', 0) > 1.0:
                issues.append("Excessive vibration")
            if sensor_data.get('rotation_speed', 1500) > 1600:
                issues.append("High rotation speed")
            elif sensor_data.get('rotation_speed', 1500) < 1400:
                issues.append("Low rotation speed")
            if sensor_data.get('load', 0) > 90:
                issues.append("High load stress")
        
        return {
            'health_score': health_score,
            'failure_probability': round(failure_prob * 100, 1),
            'alert_level': alert_level,
            'potential_issues': issues,
            'recommendation': self._get_recommendation(alert_level, issues)
        }
    
    def _get_recommendation(self, alert_level, issues):
        """Get maintenance recommendation based on analysis"""
        if alert_level == "healthy":
            return "Continue normal operation"
        elif alert_level == "warning":
            return "Schedule preventive maintenance within 1 week"
        elif alert_level == "critical":
            return "Schedule maintenance within 24 hours"
        else:
            return "URGENT: Stop operation and inspect immediately"
    
    def save_model(self):
        """Save trained model and scaler"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        print(f"Model saved to {self.model_path}")
        print(f"Scaler saved to {self.scaler_path}")
    
    def load_model(self):
        """Load trained model and scaler"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            print("Model and scaler loaded successfully")
        else:
            print("Model files not found. Training new model...")
            self.train_model()

if __name__ == "__main__":
    # Create and train model
    ml_model = AuraMachineHealthModel()
    ml_model.train_model()
    
    # Test predictions with sample data
    print("\n" + "="*50)
    print("TESTING MODEL PREDICTIONS")
    print("="*50)
    
    # Test cases
    test_cases = [
        {
            'name': 'Healthy Machine',
            'data': {'temperature': 75, 'vibration': 0.3, 'rotation_speed': 1500, 'load': 80}
        },
        {
            'name': 'Overheating Machine',
            'data': {'temperature': 95, 'vibration': 0.6, 'rotation_speed': 1520, 'load': 85}
        },
        {
            'name': 'High Vibration',
            'data': {'temperature': 80, 'vibration': 1.2, 'rotation_speed': 1480, 'load': 88}
        },
        {
            'name': 'Critical State',
            'data': {'temperature': 98, 'vibration': 1.4, 'rotation_speed': 1650, 'load': 95}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"Sensor data: {test_case['data']}")
        
        analysis = ml_model.analyze_machine_health(test_case['data'])
        print(f"Health Score: {analysis['health_score']}%")
        print(f"Failure Probability: {analysis['failure_probability']}%")
        print(f"Alert Level: {analysis['alert_level'].upper()}")
        print(f"Issues: {', '.join(analysis['potential_issues']) if analysis['potential_issues'] else 'None'}")
        print(f"Recommendation: {analysis['recommendation']}")
        print("-" * 40)