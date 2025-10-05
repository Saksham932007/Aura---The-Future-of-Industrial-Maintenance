from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import time
import sys
import os
from datetime import datetime, timedelta
import json

# Add paths for imports
sys.path.append('/home/sakshamkapoor/Projects/Aura/data')
sys.path.append('/home/sakshamkapoor/Projects/Aura/ml_model')

from simulate_data import DataSimulator
from train_model import AuraMachineHealthModel
from config import Config
from models import MachineData, Alert, MaintenanceLog

class AuraAPI:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config.from_object(Config)
        CORS(self.app, origins=Config.CORS_ORIGINS)
        
        # Initialize components
        self.data_simulator = DataSimulator()
        self.ml_model = AuraMachineHealthModel()
        
        # Data storage
        self.machines = {}
        self.alerts = []
        self.maintenance_logs = []
        self.historical_data = []
        
        # Initialize machines
        self._initialize_machines()
        
        # Load or train ML model
        self._initialize_ml_model()
        
        # Setup routes
        self._setup_routes()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_machines(self):
        """Initialize machine objects"""
        for machine_id, config in Config.MACHINES.items():
            machine = MachineData(
                machine_id=machine_id,
                name=config['name'],
                machine_type=config['type'],
                location=config['location']
            )
            # Set some initial maintenance dates
            machine.last_maintenance = datetime.now() - timedelta(days=30)
            machine.next_maintenance = datetime.now() + timedelta(days=60)
            self.machines[machine_id] = machine
        
        print(f"Initialized {len(self.machines)} machines")
    
    def _initialize_ml_model(self):
        """Initialize and load ML model"""
        try:
            self.ml_model.load_model()
            print("ML model loaded successfully")
        except Exception as e:
            print(f"Error loading ML model: {e}")
            print("Training new model...")
            self.ml_model.train_model()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/')
        def serve_dashboard():
            """Serve the main dashboard"""
            return send_from_directory('/home/sakshamkapoor/Projects/Aura/frontend', 'index.html')
        
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            """Serve static files"""
            return send_from_directory('/home/sakshamkapoor/Projects/Aura/frontend', filename)
        
        @self.app.route('/api/status')
        def get_status():
            """Get current status of all machines"""
            try:
                # Update all machine data
                self._update_machine_data()
                
                status_data = {
                    'timestamp': datetime.now().isoformat(),
                    'machines': {mid: machine.to_dict() for mid, machine in self.machines.items()},
                    'system_health': self._calculate_system_health(),
                    'active_alerts': len([a for a in self.alerts if not a.resolved]),
                    'total_machines': len(self.machines)
                }
                
                return jsonify(status_data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/machine/<machine_id>')
        def get_machine_details(machine_id):
            """Get detailed information for a specific machine"""
            try:
                if machine_id not in self.machines:
                    return jsonify({'error': 'Machine not found'}), 404
                
                machine = self.machines[machine_id]
                
                # Get recent alerts for this machine
                recent_alerts = [
                    alert.to_dict() for alert in self.alerts 
                    if alert.machine_id == machine_id and 
                    alert.timestamp > datetime.now() - timedelta(days=7)
                ]
                
                # Get maintenance history
                maintenance_history = [
                    log.to_dict() for log in self.maintenance_logs 
                    if log.machine_id == machine_id
                ]
                
                # Get historical sensor data (last 24 hours simulated)
                historical_readings = self._get_historical_readings(machine_id)
                
                return jsonify({
                    'machine': machine.to_dict(),
                    'recent_alerts': recent_alerts,
                    'maintenance_history': maintenance_history,
                    'historical_readings': historical_readings
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/predict', methods=['POST'])
        def predict_failure():
            """Predict failure for given sensor data"""
            try:
                data = request.get_json()
                
                if not data or 'sensor_data' not in data:
                    return jsonify({'error': 'Invalid request data'}), 400
                
                sensor_data = data['sensor_data']
                analysis = self.ml_model.analyze_machine_health(sensor_data)
                
                return jsonify({
                    'prediction': analysis,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/alerts')
        def get_alerts():
            """Get recent alerts"""
            try:
                limit = request.args.get('limit', 50, type=int)
                severity = request.args.get('severity', None)
                
                filtered_alerts = self.alerts
                if severity:
                    filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
                
                # Sort by timestamp (newest first) and limit
                filtered_alerts = sorted(filtered_alerts, key=lambda x: x.timestamp, reverse=True)[:limit]
                
                return jsonify({
                    'alerts': [alert.to_dict() for alert in filtered_alerts],
                    'total_count': len(filtered_alerts)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
        def acknowledge_alert(alert_id):
            """Acknowledge an alert"""
            try:
                alert = next((a for a in self.alerts if a.alert_id == alert_id), None)
                if not alert:
                    return jsonify({'error': 'Alert not found'}), 404
                
                alert.acknowledged = True
                return jsonify({'message': 'Alert acknowledged', 'alert': alert.to_dict()})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/maintenance', methods=['POST'])
        def log_maintenance():
            """Log a maintenance activity"""
            try:
                data = request.get_json()
                
                required_fields = ['machine_id', 'activity_type', 'description']
                if not all(field in data for field in required_fields):
                    return jsonify({'error': 'Missing required fields'}), 400
                
                # Create maintenance log
                log = MaintenanceLog(
                    machine_id=data['machine_id'],
                    activity_type=data['activity_type'],
                    description=data['description'],
                    technician=data.get('technician', 'System')
                )
                
                if 'duration' in data:
                    log.duration = data['duration']
                if 'parts_used' in data:
                    log.parts_used = data['parts_used']
                if 'cost' in data:
                    log.cost = data['cost']
                
                self.maintenance_logs.append(log)
                
                # Update machine maintenance dates
                if data['machine_id'] in self.machines:
                    machine = self.machines[data['machine_id']]
                    machine.last_maintenance = datetime.now()
                    
                    # Reset health score if major maintenance
                    if data['activity_type'] in ['repair', 'replacement']:
                        machine.health_score = min(100, machine.health_score + 20)
                
                return jsonify({
                    'message': 'Maintenance logged successfully',
                    'log': log.to_dict()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/health')
        def health_check():
            """API health check"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'components': {
                    'data_simulator': 'running',
                    'ml_model': 'loaded' if self.ml_model.model is not None else 'not_loaded',
                    'machines': len(self.machines),
                    'alerts': len(self.alerts)
                }
            })
    
    def _update_machine_data(self):
        """Update all machine data with current readings and predictions"""
        current_readings = self.data_simulator.get_all_current_readings()
        
        for machine_id, reading_data in current_readings.items():
            if machine_id in self.machines:
                machine = self.machines[machine_id]
                
                # Update sensor readings
                machine.current_readings = {
                    'temperature': round(reading_data['temperature'], 1),
                    'vibration': round(reading_data['vibration'], 2),
                    'rotation_speed': round(reading_data['rotation_speed'], 0),
                    'load': round(reading_data['load'], 1),
                    'timestamp': reading_data['timestamp'].isoformat()
                }
                
                # Get ML prediction
                analysis = self.ml_model.analyze_machine_health(reading_data)
                
                # Update machine health data
                machine.health_score = analysis['health_score']
                machine.failure_probability = analysis['failure_probability']
                machine.alert_level = analysis['alert_level']
                machine.potential_issues = analysis['potential_issues']
                machine.recommendation = analysis['recommendation']
                machine.last_updated = datetime.now()
                
                # Generate alerts if needed
                self._check_and_generate_alerts(machine_id, machine, analysis)
    
    def _check_and_generate_alerts(self, machine_id, machine, analysis):
        """Check if alerts should be generated and create them"""
        current_time = datetime.now()
        
        # Check if we need to generate an alert
        should_alert = False
        alert_message = ""
        alert_severity = "info"
        
        if analysis['alert_level'] == 'danger':
            should_alert = True
            alert_message = f"CRITICAL: {machine.name} requires immediate attention"
            alert_severity = "danger"
        elif analysis['alert_level'] == 'critical':
            should_alert = True
            alert_message = f"WARNING: {machine.name} showing signs of deterioration"
            alert_severity = "critical"
        elif analysis['alert_level'] == 'warning':
            # Only alert for warning level if health score dropped significantly
            if machine.health_score < 70:
                should_alert = True
                alert_message = f"NOTICE: {machine.name} health score declining"
                alert_severity = "warning"
        
        # Check for specific sensor alerts
        readings = machine.current_readings
        if readings.get('temperature', 0) > 95:
            should_alert = True
            alert_message = f"HIGH TEMPERATURE: {machine.name} - {readings['temperature']}°C"
            alert_severity = "critical"
        elif readings.get('vibration', 0) > 1.2:
            should_alert = True
            alert_message = f"EXCESSIVE VIBRATION: {machine.name} - {readings['vibration']}"
            alert_severity = "critical"
        
        # Create alert if needed and not recently alerted
        if should_alert:
            # Check for recent similar alerts (cooldown)
            recent_alerts = [
                a for a in self.alerts 
                if a.machine_id == machine_id and 
                a.timestamp > current_time - timedelta(seconds=Config.ALERT_COOLDOWN)
            ]
            
            if not recent_alerts:
                alert = Alert(
                    machine_id=machine_id,
                    alert_type='health_degradation',
                    severity=alert_severity,
                    message=alert_message,
                    details={
                        'health_score': machine.health_score,
                        'failure_probability': machine.failure_probability,
                        'sensor_readings': readings,
                        'potential_issues': analysis['potential_issues'],
                        'recommendation': analysis['recommendation']
                    }
                )
                
                self.alerts.append(alert)
                
                # Keep only recent alerts (memory management)
                if len(self.alerts) > Config.MAX_ALERTS:
                    self.alerts = self.alerts[-Config.MAX_ALERTS:]
                
                print(f"Generated alert: {alert_message}")
    
    def _calculate_system_health(self):
        """Calculate overall system health percentage"""
        if not self.machines:
            return 100
        
        total_health = sum(machine.health_score for machine in self.machines.values())
        average_health = total_health / len(self.machines)
        return round(average_health, 1)
    
    def _get_historical_readings(self, machine_id, hours=24):
        """Get simulated historical readings for a machine"""
        # Generate some historical data for demonstration
        historical = []
        now = datetime.now()
        
        for i in range(hours):
            timestamp = now - timedelta(hours=hours-i)
            
            # Get a reading (this would normally come from a database)
            reading = self.data_simulator.get_current_readings(machine_id)
            historical.append({
                'timestamp': timestamp.isoformat(),
                'temperature': reading['temperature'],
                'vibration': reading['vibration'],
                'rotation_speed': reading['rotation_speed'],
                'load': reading['load']
            })
        
        return historical
    
    def _start_background_tasks(self):
        """Start background data simulation and processing"""
        def background_worker():
            print("Starting background data simulation...")
            while True:
                try:
                    # Update machine data every few seconds
                    self._update_machine_data()
                    time.sleep(Config.SIMULATION_INTERVAL)
                except Exception as e:
                    print(f"Error in background worker: {e}")
                    time.sleep(5)
        
        # Start background thread
        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()
        print("Background simulation started")
    
    def run(self, host='0.0.0.0', port=5000, debug=True):
        """Run the Flask application"""
        print(f"\n🚀 Starting Aura API Server...")
        print(f"📊 Dashboard: http://localhost:{port}")
        print(f"🔧 API Health: http://localhost:{port}/api/health")
        print(f"📈 Machine Status: http://localhost:{port}/api/status")
        print("="*50)
        
        self.app.run(host=host, port=port, debug=debug, threaded=True)

def create_app():
    """Application factory"""
    return AuraAPI()

if __name__ == '__main__':
    # Create and run the application
    api = create_app()
    api.run()