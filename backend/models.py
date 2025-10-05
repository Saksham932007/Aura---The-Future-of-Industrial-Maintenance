from datetime import datetime, timedelta
import json

class MachineData:
    def __init__(self, machine_id, name, machine_type, location):
        self.machine_id = machine_id
        self.name = name
        self.type = machine_type
        self.location = location
        self.current_readings = {}
        self.health_score = 100
        self.alert_level = "healthy"
        self.last_maintenance = None
        self.next_maintenance = None
        self.failure_probability = 0.0
        self.potential_issues = []
        self.recommendation = "Continue normal operation"
        self.last_updated = datetime.now()
    
    def to_dict(self):
        return {
            'machine_id': self.machine_id,
            'name': self.name,
            'type': self.type,
            'location': self.location,
            'current_readings': self.current_readings,
            'health_score': self.health_score,
            'alert_level': self.alert_level,
            'failure_probability': self.failure_probability,
            'potential_issues': self.potential_issues,
            'recommendation': self.recommendation,
            'last_updated': self.last_updated.isoformat(),
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'next_maintenance': self.next_maintenance.isoformat() if self.next_maintenance else None
        }

class Alert:
    def __init__(self, machine_id, alert_type, severity, message, details=None):
        self.alert_id = f"{machine_id}_{int(datetime.now().timestamp())}"
        self.machine_id = machine_id
        self.alert_type = alert_type
        self.severity = severity  # 'info', 'warning', 'critical', 'danger'
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
        self.acknowledged = False
        self.resolved = False
    
    def to_dict(self):
        return {
            'alert_id': self.alert_id,
            'machine_id': self.machine_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'acknowledged': self.acknowledged,
            'resolved': self.resolved
        }

class MaintenanceLog:
    def __init__(self, machine_id, activity_type, description, technician=None):
        self.log_id = f"{machine_id}_{int(datetime.now().timestamp())}"
        self.machine_id = machine_id
        self.activity_type = activity_type  # 'inspection', 'repair', 'replacement', 'calibration'
        self.description = description
        self.technician = technician or "System"
        self.timestamp = datetime.now()
        self.duration = None
        self.parts_used = []
        self.cost = 0.0
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'machine_id': self.machine_id,
            'activity_type': self.activity_type,
            'description': self.description,
            'technician': self.technician,
            'timestamp': self.timestamp.isoformat(),
            'duration': self.duration,
            'parts_used': self.parts_used,
            'cost': self.cost
        }