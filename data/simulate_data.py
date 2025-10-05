import pandas as pd
import numpy as np
import time
import json
from datetime import datetime, timedelta
import threading
import random

class DataSimulator:
    def __init__(self):
        self.machines = {
            'Machine_001': {'name': 'Conveyor Belt A', 'type': 'Conveyor'},
            'Machine_002': {'name': 'Hydraulic Press B', 'type': 'Press'},
            'Machine_003': {'name': 'Motor Drive C', 'type': 'Motor'},
            'Machine_004': {'name': 'Compressor D', 'type': 'Compressor'},
            'Machine_005': {'name': 'Pump System E', 'type': 'Pump'}
        }
        
        # Normal operating ranges for each sensor type
        self.normal_ranges = {
            'temperature': {'min': 65, 'max': 85, 'critical': 95},
            'vibration': {'min': 0.1, 'max': 0.8, 'critical': 1.2},
            'rotation_speed': {'min': 1450, 'max': 1550, 'critical': 1600},
            'load': {'min': 70, 'max': 90, 'critical': 95}
        }
        
        # Machine states: 0=healthy, 1=degrading, 2=critical
        self.machine_states = {machine_id: 0 for machine_id in self.machines.keys()}
        
        # Failure simulation probabilities
        self.failure_patterns = {
            'Machine_001': 'vibration_high',  # Conveyor belt issues
            'Machine_002': 'temperature_high',  # Hydraulic overheating
            'Machine_003': 'rotation_anomaly',  # Motor issues
            'Machine_004': 'load_high',  # Compressor overload
            'Machine_005': 'temperature_vibration'  # Multiple issues
        }
        
        # Current sensor readings
        self.current_readings = {}
        self.initialize_readings()
        
        # Data storage
        self.historical_data = []
        self.current_alerts = {}
        
    def initialize_readings(self):
        """Initialize all machines with normal readings"""
        for machine_id in self.machines.keys():
            self.current_readings[machine_id] = {
                'temperature': random.uniform(65, 85),
                'vibration': random.uniform(0.1, 0.8),
                'rotation_speed': random.uniform(1450, 1550),
                'load': random.uniform(70, 90),
                'timestamp': datetime.now()
            }
    
    def generate_historical_data(self, days=30, samples_per_day=24):
        """Generate historical training data"""
        print("Generating historical training data...")
        data = []
        start_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            for hour in range(samples_per_day):
                timestamp = start_date + timedelta(days=day, hours=hour)
                
                for machine_id in self.machines.keys():
                    # Simulate normal operation most of the time
                    failure_prob = 0.05 if day < days - 7 else 0.15  # Higher failure rate in recent days
                    
                    if random.random() < failure_prob:
                        # Generate failure scenario
                        readings = self._generate_failure_scenario(machine_id)
                        failure = 1
                    else:
                        # Generate normal readings
                        readings = self._generate_normal_readings()
                        failure = 0
                    
                    data.append({
                        'machine_id': machine_id,
                        'timestamp': timestamp,
                        'temperature': readings['temperature'],
                        'vibration': readings['vibration'],
                        'rotation_speed': readings['rotation_speed'],
                        'load': readings['load'],
                        'failure': failure
                    })
        
        df = pd.DataFrame(data)
        df.to_csv('/home/sakshamkapoor/Projects/Aura/data/sensor_data.csv', index=False)
        print(f"Generated {len(df)} historical data points and saved to sensor_data.csv")
        return df
    
    def _generate_normal_readings(self):
        """Generate normal sensor readings with slight variations"""
        return {
            'temperature': random.uniform(65, 85) + random.gauss(0, 2),
            'vibration': random.uniform(0.1, 0.8) + random.gauss(0, 0.05),
            'rotation_speed': random.uniform(1450, 1550) + random.gauss(0, 10),
            'load': random.uniform(70, 90) + random.gauss(0, 3)
        }
    
    def _generate_failure_scenario(self, machine_id):
        """Generate readings that indicate potential failure"""
        pattern = self.failure_patterns.get(machine_id, 'temperature_high')
        
        if pattern == 'vibration_high':
            return {
                'temperature': random.uniform(80, 95),
                'vibration': random.uniform(1.0, 1.5),
                'rotation_speed': random.uniform(1400, 1600),
                'load': random.uniform(85, 95)
            }
        elif pattern == 'temperature_high':
            return {
                'temperature': random.uniform(90, 105),
                'vibration': random.uniform(0.5, 1.0),
                'rotation_speed': random.uniform(1500, 1580),
                'load': random.uniform(80, 95)
            }
        elif pattern == 'rotation_anomaly':
            return {
                'temperature': random.uniform(75, 90),
                'vibration': random.uniform(0.6, 1.1),
                'rotation_speed': random.uniform(1300, 1400) if random.random() < 0.5 else random.uniform(1600, 1700),
                'load': random.uniform(75, 90)
            }
        elif pattern == 'load_high':
            return {
                'temperature': random.uniform(85, 100),
                'vibration': random.uniform(0.7, 1.2),
                'rotation_speed': random.uniform(1420, 1580),
                'load': random.uniform(92, 100)
            }
        else:  # temperature_vibration
            return {
                'temperature': random.uniform(88, 102),
                'vibration': random.uniform(0.9, 1.4),
                'rotation_speed': random.uniform(1460, 1590),
                'load': random.uniform(85, 98)
            }
    
    def simulate_real_time_degradation(self, machine_id):
        """Simulate gradual machine degradation"""
        current_state = self.machine_states[machine_id]
        
        # Random chance of state change
        if random.random() < 0.02:  # 2% chance per update
            if current_state == 0 and random.random() < 0.3:
                self.machine_states[machine_id] = 1  # Start degrading
                print(f"{machine_id} started degrading")
            elif current_state == 1 and random.random() < 0.1:
                self.machine_states[machine_id] = 2  # Become critical
                print(f"{machine_id} became critical")
            elif current_state == 2 and random.random() < 0.05:
                self.machine_states[machine_id] = 0  # Recover (maintenance)
                print(f"{machine_id} recovered to healthy state")
    
    def get_current_readings(self, machine_id):
        """Get current sensor readings for a machine"""
        self.simulate_real_time_degradation(machine_id)
        state = self.machine_states[machine_id]
        
        if state == 0:  # Healthy
            readings = self._generate_normal_readings()
        elif state == 1:  # Degrading
            # Mix normal and failure patterns
            if random.random() < 0.7:
                readings = self._generate_normal_readings()
                # Add slight degradation
                readings['temperature'] += random.uniform(0, 8)
                readings['vibration'] += random.uniform(0, 0.2)
            else:
                readings = self._generate_failure_scenario(machine_id)
        else:  # Critical
            readings = self._generate_failure_scenario(machine_id)
        
        # Ensure readings stay within realistic bounds
        readings['temperature'] = max(20, min(120, readings['temperature']))
        readings['vibration'] = max(0, min(2.0, readings['vibration']))
        readings['rotation_speed'] = max(0, min(2000, readings['rotation_speed']))
        readings['load'] = max(0, min(100, readings['load']))
        
        readings['timestamp'] = datetime.now()
        self.current_readings[machine_id] = readings
        
        return readings
    
    def get_all_current_readings(self):
        """Get current readings for all machines"""
        all_readings = {}
        for machine_id in self.machines.keys():
            all_readings[machine_id] = self.get_current_readings(machine_id)
            all_readings[machine_id]['machine_info'] = self.machines[machine_id]
            all_readings[machine_id]['state'] = self.machine_states[machine_id]
        
        return all_readings
    
    def start_real_time_simulation(self, update_interval=5):
        """Start continuous real-time data simulation"""
        def simulate():
            while True:
                self.get_all_current_readings()
                time.sleep(update_interval)
        
        thread = threading.Thread(target=simulate, daemon=True)
        thread.start()
        print(f"Started real-time simulation with {update_interval}s interval")
        return thread

if __name__ == "__main__":
    # Create simulator and generate data
    simulator = DataSimulator()
    
    # Generate historical data for training
    historical_df = simulator.generate_historical_data(days=60, samples_per_day=24)
    
    # Start real-time simulation
    simulator.start_real_time_simulation(update_interval=3)
    
    # Display some real-time data
    print("\nReal-time simulation started. Displaying sample data:")
    for i in range(10):
        time.sleep(3)
        readings = simulator.get_all_current_readings()
        print(f"\nTime: {datetime.now().strftime('%H:%M:%S')}")
        for machine_id, data in readings.items():
            state_text = ['Healthy', 'Degrading', 'Critical'][data['state']]
            print(f"{machine_id} ({state_text}): T={data['temperature']:.1f}°C, V={data['vibration']:.2f}, RPM={data['rotation_speed']:.0f}, Load={data['load']:.1f}%")