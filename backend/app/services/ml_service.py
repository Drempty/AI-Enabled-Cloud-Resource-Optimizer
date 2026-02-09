"""
Machine Learning service for predictions and optimization
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import joblib
import os

# TensorFlow is optional - statistical methods work fine for most use cases
# Uncomment the following and install tensorflow if you want LSTM predictions
TENSORFLOW_AVAILABLE = False

# try:
#     from tensorflow import keras
#     from tensorflow.keras.models import Sequential, load_model
#     from tensorflow.keras.layers import LSTM, Dense, Dropout
#     from tensorflow.keras.optimizers import Adam
#     TENSORFLOW_AVAILABLE = True
# except ImportError:
#     TENSORFLOW_AVAILABLE = False

if not TENSORFLOW_AVAILABLE:
    print("ℹ️  Using statistical prediction methods (no TensorFlow). This is faster and works great!")

from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import IsolationForest


class MLService:
    """Machine Learning service for resource optimization"""
    
    def __init__(self):
        self.models_loaded = False
        self.cpu_model = None
        self.memory_model = None
        self.scaler_cpu = MinMaxScaler()
        self.scaler_memory = MinMaxScaler()
        self.anomaly_detector = None
        self.models_dir = "models"
        
        # Create models directory if it doesn't exist
        os.makedirs(self.models_dir, exist_ok=True)
    
    async def load_models(self):
        """Load pre-trained models or create new ones"""
        try:
            if TENSORFLOW_AVAILABLE:
                # Try to load existing models
                cpu_model_path = os.path.join(self.models_dir, "cpu_lstm_model.h5")
                memory_model_path = os.path.join(self.models_dir, "memory_lstm_model.h5")
                
                if os.path.exists(cpu_model_path):
                    self.cpu_model = load_model(cpu_model_path)
                else:
                    self.cpu_model = self._create_lstm_model()
                
                if os.path.exists(memory_model_path):
                    self.memory_model = load_model(memory_model_path)
                else:
                    self.memory_model = self._create_lstm_model()
            
            # Initialize anomaly detector
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            
            self.models_loaded = True
            print("✅ ML models loaded successfully")
        except Exception as e:
            print(f"⚠️  Error loading models: {e}")
            self.models_loaded = False
    
    def _create_lstm_model(self, sequence_length: int = 24, features: int = 1):
        """Create LSTM model for time series prediction"""
        if not TENSORFLOW_AVAILABLE:
            return None
            
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(sequence_length, features)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        return model
    
    async def predict_usage(
        self,
        historical_data: List[Dict],
        metric_type: str,
        prediction_hours: int = 168
    ) -> Tuple[List[float], float]:
        """
        Predict resource usage using LSTM or statistical methods
        
        Args:
            historical_data: List of historical metric dictionaries
            metric_type: Type of metric to predict ('cpu', 'memory', 'network')
            prediction_hours: Number of hours to predict
            
        Returns:
            Tuple of (predictions, confidence_score)
        """
        if not historical_data or len(historical_data) < 24:
            # Use simple statistical prediction if insufficient data
            return self._statistical_prediction(historical_data, metric_type, prediction_hours)
        
        # Extract metric values
        values = [d.get(f'{metric_type}_usage', 0) for d in historical_data]
        
        if TENSORFLOW_AVAILABLE and self.cpu_model is not None:
            return self._lstm_prediction(values, metric_type, prediction_hours)
        else:
            return self._statistical_prediction(historical_data, metric_type, prediction_hours)
    
    def _lstm_prediction(
        self,
        values: List[float],
        metric_type: str,
        prediction_hours: int
    ) -> Tuple[List[float], float]:
        """LSTM-based prediction"""
        try:
            # Prepare data
            values_array = np.array(values).reshape(-1, 1)
            
            # Select appropriate scaler and model
            if metric_type == 'cpu':
                scaler = self.scaler_cpu
                model = self.cpu_model
            else:
                scaler = self.scaler_memory
                model = self.memory_model
            
            # Scale data
            scaled_data = scaler.fit_transform(values_array)
            
            # Create sequences
            sequence_length = min(24, len(scaled_data) - 1)
            X = []
            for i in range(len(scaled_data) - sequence_length):
                X.append(scaled_data[i:i + sequence_length])
            
            if len(X) == 0:
                return self._statistical_prediction(
                    [{'cpu_usage': v} for v in values],
                    metric_type,
                    prediction_hours
                )
            
            X = np.array(X)
            
            # Make predictions
            predictions = []
            current_sequence = scaled_data[-sequence_length:].reshape(1, sequence_length, 1)
            
            for _ in range(prediction_hours):
                pred = model.predict(current_sequence, verbose=0)
                predictions.append(pred[0, 0])
                
                # Update sequence
                current_sequence = np.append(
                    current_sequence[:, 1:, :],
                    pred.reshape(1, 1, 1),
                    axis=1
                )
            
            # Inverse transform predictions
            predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
            predictions = predictions.flatten().tolist()
            
            # Ensure predictions are within valid range
            predictions = [max(0, min(100, p)) for p in predictions]
            
            # Calculate confidence based on variance
            confidence = self._calculate_confidence(values, predictions)
            
            return predictions, confidence
            
        except Exception as e:
            print(f"LSTM prediction error: {e}")
            return self._statistical_prediction(
                [{'cpu_usage': v} for v in values],
                metric_type,
                prediction_hours
            )
    
    def _statistical_prediction(
        self,
        historical_data: List[Dict],
        metric_type: str,
        prediction_hours: int
    ) -> Tuple[List[float], float]:
        """Statistical prediction using moving average and trend"""
        if not historical_data:
            # Return default predictions
            return [50.0] * prediction_hours, 0.5
        
        values = [d.get(f'{metric_type}_usage', 0) for d in historical_data]
        
        # Calculate statistics
        mean_value = np.mean(values)
        std_value = np.std(values)
        
        # Calculate trend
        if len(values) >= 2:
            x = np.arange(len(values))
            z = np.polyfit(x, values, 1)
            trend = z[0]
        else:
            trend = 0
        
        # Generate predictions with trend and seasonality
        predictions = []
        for i in range(prediction_hours):
            # Base prediction with trend
            base = mean_value + (trend * i)
            
            # Add hourly seasonality (simple sine wave)
            seasonality = std_value * 0.3 * np.sin(2 * np.pi * i / 24)
            
            # Add small random variation
            noise = np.random.normal(0, std_value * 0.1)
            
            prediction = base + seasonality + noise
            
            # Clamp to valid range
            prediction = max(0, min(100, prediction))
            predictions.append(prediction)
        
        # Calculate confidence
        confidence = max(0.5, 1.0 - (std_value / (mean_value + 1)))
        
        return predictions, confidence
    
    def _calculate_confidence(self, historical: List[float], predicted: List[float]) -> float:
        """Calculate prediction confidence score"""
        if not historical:
            return 0.5
        
        historical_std = np.std(historical)
        historical_mean = np.mean(historical)
        
        # Confidence based on stability of historical data
        stability_score = max(0, 1 - (historical_std / (historical_mean + 1)))
        
        # Confidence based on prediction variance
        if len(predicted) > 1:
            prediction_std = np.std(predicted[:min(24, len(predicted))])
            variance_score = max(0, 1 - (prediction_std / (np.mean(predicted) + 1)))
        else:
            variance_score = stability_score
        
        # Combined confidence
        confidence = (stability_score * 0.6 + variance_score * 0.4)
        
        return round(confidence, 2)
    
    async def detect_anomalies(self, metrics_data: List[Dict]) -> List[Dict]:
        """Detect anomalies in resource usage"""
        if not metrics_data or len(metrics_data) < 10:
            return []
        
        try:
            # Prepare features
            features = []
            for m in metrics_data:
                features.append([
                    m.get('cpu_usage', 0),
                    m.get('memory_usage', 0),
                    m.get('network_in_mb', 0) + m.get('network_out_mb', 0)
                ])
            
            X = np.array(features)
            
            # Fit and predict
            self.anomaly_detector.fit(X)
            predictions = self.anomaly_detector.predict(X)
            
            # Find anomalies
            anomalies = []
            for i, pred in enumerate(predictions):
                if pred == -1:  # -1 indicates anomaly
                    anomalies.append({
                        'timestamp': metrics_data[i].get('timestamp'),
                        'cpu_usage': metrics_data[i].get('cpu_usage'),
                        'memory_usage': metrics_data[i].get('memory_usage'),
                        'severity': self._calculate_anomaly_severity(metrics_data[i], metrics_data)
                    })
            
            return anomalies
        except Exception as e:
            print(f"Anomaly detection error: {e}")
            return []
    
    def _calculate_anomaly_severity(self, anomaly: Dict, all_data: List[Dict]) -> str:
        """Calculate anomaly severity"""
        cpu_values = [d.get('cpu_usage', 0) for d in all_data]
        mem_values = [d.get('memory_usage', 0) for d in all_data]
        
        cpu_mean = np.mean(cpu_values)
        mem_mean = np.mean(mem_values)
        
        cpu_deviation = abs(anomaly.get('cpu_usage', 0) - cpu_mean) / (cpu_mean + 1)
        mem_deviation = abs(anomaly.get('memory_usage', 0) - mem_mean) / (mem_mean + 1)
        
        max_deviation = max(cpu_deviation, mem_deviation)
        
        if max_deviation > 2:
            return 'high'
        elif max_deviation > 1:
            return 'medium'
        else:
            return 'low'
    
    async def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up ML service...")
        self.models_loaded = False
