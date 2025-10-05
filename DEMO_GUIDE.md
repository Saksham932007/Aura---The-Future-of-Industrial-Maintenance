# Aura Demo Setup and Testing Guide

## Quick Start (Recommended)

1. **One-Command Demo Launch:**
   ```bash
   cd /home/sakshamkapoor/Projects/Aura
   python run_demo.py
   ```
   
   This will automatically:
   - Install required dependencies
   - Generate training data and train ML model
   - Start the backend API server
   - Begin real-time data simulation
   - Open the dashboard in your browser

## Manual Setup (Alternative)

If you prefer to run components separately:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train ML Model
```bash
cd ml_model
python train_model.py
```

### 3. Start Backend Server
```bash
cd backend
python app.py
```

### 4. Open Dashboard
Navigate to: http://localhost:5000

## Testing Checklist

### ✅ System Components
- [ ] Data simulation generates realistic sensor data
- [ ] ML model trains successfully and makes predictions
- [ ] Backend API responds to all endpoints
- [ ] Frontend dashboard loads and displays data
- [ ] Real-time updates work correctly

### ✅ Core Features
- [ ] Machine health scores update in real-time
- [ ] Color-coded health indicators work (green/yellow/orange/red)
- [ ] Alerts are generated for failing machines
- [ ] Machine cards show correct sensor readings
- [ ] System overview displays correct statistics

### ✅ Interactive Features
- [ ] Clicking machine cards opens detailed modal
- [ ] Modal shows real-time charts for temperature and vibration
- [ ] Maintenance scheduling form works
- [ ] Issue acknowledgment functionality works
- [ ] Maintenance history is displayed and updated

### ✅ UI/UX Polish
- [ ] Smooth animations and transitions
- [ ] Responsive design works on different screen sizes
- [ ] Loading states and error handling
- [ ] Professional color scheme and typography
- [ ] Icons and visual indicators are clear

### ✅ API Endpoints Testing

Test these URLs while the demo is running:

1. **Health Check:** http://localhost:5000/api/health
2. **System Status:** http://localhost:5000/api/status
3. **Alerts:** http://localhost:5000/api/alerts
4. **Machine Details:** http://localhost:5000/api/machine/Machine_001

### ✅ Demo Flow Validation

1. **Initial Load:**
   - Dashboard loads with 5 machines
   - All machines start with reasonable health scores
   - System health percentage is calculated correctly

2. **Real-time Updates:**
   - Health scores change over time
   - Machine states transition (healthy → warning → critical)
   - Alerts appear when machines degrade
   - Sensor readings update every few seconds

3. **Machine Interaction:**
   - Click any machine card to open detailed view
   - Charts display historical data
   - Maintenance actions can be scheduled
   - Modal closes properly

4. **Alert Generation:**
   - Watch for machines transitioning to warning/critical states
   - Alerts appear in the recent alerts panel
   - Alert badges show on machine cards

## Troubleshooting

### Common Issues:

1. **Port 5000 already in use:**
   ```bash
   # Kill any process using port 5000
   sudo lsof -ti:5000 | xargs kill -9
   ```

2. **Module import errors:**
   ```bash
   # Ensure you're in the project directory
   cd /home/sakshamkapoor/Projects/Aura
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Browser doesn't open automatically:**
   - Manually navigate to http://localhost:5000

4. **Data not updating:**
   - Check console output for errors
   - Verify backend server is running
   - Check browser developer tools for API errors

### Performance Notes:

- The demo simulates 5 machines with updates every 3 seconds
- Historical data covers 30-90 days for training
- Charts display last 24 hours of data
- ML model uses Random Forest for predictions

## Demo Presentation Tips

### Key Selling Points:
1. **Real-time Monitoring:** Show live health score changes
2. **Predictive Alerts:** Demonstrate early warning system
3. **Intuitive UI:** Highlight ease of use and visual clarity
4. **Actionable Insights:** Show maintenance recommendations
5. **Cost Savings:** Explain how preventing downtime saves money

### Demo Script:
1. Start with system overview - highlight overall health
2. Show healthy vs. degrading machines side by side
3. Click on a critical machine to show detailed analysis
4. Point out specific sensor readings and trends
5. Demonstrate maintenance scheduling workflow
6. Show how alerts help prioritize maintenance

### Technical Highlights:
- Machine learning powered predictions
- Real-time data processing
- Modern responsive web interface
- RESTful API architecture
- Scalable design for industrial environments

## Success Metrics

The demo is successful if:
- ✅ All 5 machines display and update correctly
- ✅ Health scores vary realistically (some healthy, some degrading)
- ✅ At least one alert is generated during the demo
- ✅ Machine detail modals work smoothly
- ✅ Maintenance scheduling completes successfully
- ✅ UI is responsive and professional-looking
- ✅ No console errors or broken functionality

## Next Steps for Production

1. **Database Integration:** Replace in-memory storage with proper database
2. **Authentication:** Add user login and role-based access
3. **Real Sensor Integration:** Connect to actual industrial sensors
4. **Advanced Analytics:** Add more sophisticated ML models
5. **Mobile App:** Create companion mobile application
6. **Reporting:** Add PDF/Excel report generation
7. **Notifications:** Implement email/SMS alert system