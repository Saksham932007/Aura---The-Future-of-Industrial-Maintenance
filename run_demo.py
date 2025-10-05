#!/usr/bin/env python3
"""
Aura - Industrial Maintenance Dashboard Demo Runner

This script sets up and runs the complete Aura demonstration including:
1. Data generation and ML model training
2. Backend API server startup
3. Real-time data simulation
4. Frontend dashboard serving

Usage: python run_demo.py
Then open: http://localhost:5000
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.append(str(project_root / 'data'))
sys.path.append(str(project_root / 'ml_model'))
sys.path.append(str(project_root / 'backend'))

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'flask', 'flask_cors', 'pandas', 'numpy', 
        'scikit-learn', 'joblib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                'flask==2.3.2', 'flask-cors==4.0.0', 'pandas==2.0.3', 
                'numpy==1.24.3', 'scikit-learn==1.3.0', 'joblib==1.3.1'
            ])
            print("✅ Packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please run:")
            print("   pip install -r requirements.txt")
            return False
    
    return True

def setup_ml_model():
    """Generate training data and train the ML model"""
    print("\n🤖 Setting up Machine Learning Model...")
    
    try:
        from train_model import AuraMachineHealthModel
        
        # Check if model already exists
        model_path = project_root / 'ml_model' / 'model.pkl'
        
        if model_path.exists():
            print("✅ ML model already exists, loading...")
            ml_model = AuraMachineHealthModel()
            ml_model.load_model()
        else:
            print("🔄 Training new ML model...")
            ml_model = AuraMachineHealthModel()
            ml_model.train_model()
        
        print("✅ ML model ready!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up ML model: {e}")
        return False

def start_data_simulation():
    """Start background data simulation"""
    print("\n📊 Starting data simulation...")
    
    try:
        from simulate_data import DataSimulator
        
        simulator = DataSimulator()
        
        # Generate initial historical data if needed
        data_file = project_root / 'data' / 'sensor_data.csv'
        if not data_file.exists():
            print("🔄 Generating historical training data...")
            simulator.generate_historical_data(days=30, samples_per_day=24)
        
        # Start real-time simulation
        simulator.start_real_time_simulation(update_interval=3)
        
        print("✅ Data simulation started!")
        return simulator
        
    except Exception as e:
        print(f"❌ Error starting data simulation: {e}")
        return None

def start_backend_server():
    """Start the Flask backend server"""
    print("\n🌐 Starting Backend API Server...")
    
    try:
        from app import AuraAPI
        
        # Create API instance
        api = AuraAPI()
        
        # Start server in a separate thread
        def run_server():
            api.run(host='0.0.0.0', port=5000, debug=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(3)
        
        print("✅ Backend server started on http://localhost:5000!")
        return True
        
    except Exception as e:
        print(f"❌ Error starting backend server: {e}")
        return False

def open_dashboard():
    """Open the dashboard in the default web browser"""
    dashboard_url = "http://localhost:5000"
    
    print(f"\n🚀 Opening Aura Dashboard...")
    print(f"📱 URL: {dashboard_url}")
    
    try:
        # Wait a moment for everything to be ready
        time.sleep(2)
        webbrowser.open(dashboard_url)
        print("✅ Dashboard opened in browser!")
    except Exception as e:
        print(f"❌ Could not open browser automatically: {e}")
        print(f"📝 Please manually open: {dashboard_url}")

def display_demo_info():
    """Display information about the demo"""
    print("\n" + "="*60)
    print("🎯 AURA DEMO IS NOW RUNNING!")
    print("="*60)
    print("\n📊 What you'll see in the dashboard:")
    print("   • Real-time machine health monitoring")
    print("   • Dynamic health scores (0-100%)")
    print("   • Predictive failure alerts")
    print("   • Interactive sensor data visualization")
    print("   • Machine-specific detailed views")
    print("   • Maintenance recommendations")
    
    print("\n🔧 Demo Features:")
    print("   • 5 simulated industrial machines")
    print("   • Real-time sensor data (temperature, vibration, RPM, load)")
    print("   • ML-powered predictive maintenance")
    print("   • Responsive modern UI with animations")
    print("   • Color-coded health status indicators")
    
    print("\n💡 Try These Actions:")
    print("   • Click on any machine card for detailed view")
    print("   • Watch health scores change in real-time")
    print("   • Observe alerts being generated for degrading machines")
    print("   • Check the recent alerts panel")
    
    print("\n🌐 URLs:")
    print("   • Dashboard: http://localhost:5000")
    print("   • API Health: http://localhost:5000/api/health")
    print("   • Machine Status: http://localhost:5000/api/status")
    
    print("\n⏹️  To stop the demo: Press Ctrl+C")
    print("="*60)

def main():
    """Main demo runner function"""
    print("🚀 Welcome to Aura - Industrial Maintenance Demo!")
    print("="*50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Setup ML model
    if not setup_ml_model():
        return
    
    # Start data simulation
    simulator = start_data_simulation()
    if not simulator:
        return
    
    # Start backend server
    if not start_backend_server():
        return
    
    # Open dashboard
    open_dashboard()
    
    # Display demo information
    display_demo_info()
    
    try:
        # Keep the demo running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping Aura Demo...")
        print("Thank you for trying Aura!")
        print("="*50)

if __name__ == "__main__":
    main()