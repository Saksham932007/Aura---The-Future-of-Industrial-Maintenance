# Aura - The Future of Industrial Maintenance

## Vision

Aura is an intelligent predictive maintenance platform that empowers industrial operators to anticipate machine failures before they happen, preventing costly downtime and improving operational efficiency.

## Elevator Pitch

Machines talk, but are you listening? Aura is a smart, user-friendly platform that uses machine learning to translate real-time sensor data from industrial equipment into clear, actionable predictions. It alerts you to potential failures, identifies root causes, and helps you schedule maintenance proactively.

## Project Structure

```
Aura/
├── README.md
├── requirements.txt
├── run_demo.py          # Single script to start the entire demo
├── backend/
│   ├── app.py           # Flask API server
│   ├── models.py        # Data models and ML model loading
│   └── config.py        # Configuration settings
├── frontend/
│   ├── index.html       # Main dashboard (single-page app)
│   ├── styles.css       # Custom styles
│   └── script.js        # Dashboard logic and API integration
├── data/
│   ├── sensor_data.csv  # Historical training data
│   └── simulate_data.py # Real-time data simulation
└── ml_model/
    ├── train_model.py   # Model training script
    ├── model.pkl        # Trained ML model
    └── scaler.pkl       # Data preprocessing scaler
```

## Features

- **Real-time Dashboard**: Visual machine health monitoring
- **Machine Health Score**: 0-100% dynamic health scoring
- **Predictive Alerts**: Early warning system for potential failures
- **Sensor Data Visualization**: Real-time and historical charts
- **Maintenance Log**: Track maintenance activities and alerts

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS, Chart.js
- **Backend**: Python, Flask
- **Machine Learning**: scikit-learn
- **Data**: CSV simulation with real-time updates

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Run the demo: `python run_demo.py`
3. Open browser to `http://localhost:5000`

## Demo Instructions

The demo will automatically:

1. Generate training data and train the ML model
2. Start the Flask backend API
3. Begin real-time data simulation
4. Serve the frontend dashboard

## 🤖 Machine Learning Engine - Random Forest classifier with 85%+ accuracy

Watch as machine health scores change in real-time and alerts are generated when failures are predicted!
