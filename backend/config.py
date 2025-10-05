import os
from datetime import datetime, timedelta

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'aura-industrial-maintenance-2024'
    DEBUG = True
    
    # Data simulation settings
    SIMULATION_INTERVAL = 3  # seconds between data updates
    
    # ML Model settings
    MODEL_UPDATE_INTERVAL = 60  # seconds between model predictions
    HEALTH_SCORE_THRESHOLD = {
        'healthy': 80,
        'warning': 60,
        'critical': 40
    }
    
    # Machine settings
    MACHINES = {
        'Machine_001': {
            'name': 'Conveyor Belt A',
            'type': 'Conveyor',
            'location': 'Production Line 1',
            'install_date': '2022-01-15'
        },
        'Machine_002': {
            'name': 'Hydraulic Press B',
            'type': 'Press',
            'location': 'Assembly Bay 2',
            'install_date': '2021-08-20'
        },
        'Machine_003': {
            'name': 'Motor Drive C',
            'type': 'Motor',
            'location': 'Power Station',
            'install_date': '2020-11-10'
        },
        'Machine_004': {
            'name': 'Compressor D',
            'type': 'Compressor',
            'location': 'Utility Room',
            'install_date': '2023-03-05'
        },
        'Machine_005': {
            'name': 'Pump System E',
            'type': 'Pump',
            'location': 'Cooling Circuit',
            'install_date': '2022-09-12'
        }
    }
    
    # Alert settings
    ALERT_COOLDOWN = 300  # 5 minutes between similar alerts
    MAX_ALERTS = 100  # Maximum stored alerts
    
    # API settings
    CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']