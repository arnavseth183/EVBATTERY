# 📱 EV Battery Passport - Mobile App Development Guide

## **🎯 Converting to Play Store App**

This guide explains how to convert the current Streamlit web application into a mobile app for Google Play Store deployment.

---

## **🏗️ Architecture Overview**

### **Current Architecture:**
```
Streamlit Web App → Python Backend → JSON Files → Smart Contracts
```

### **Target Mobile Architecture:**
```
Mobile App (React Native/Flutter) → REST API → Python Backend → JSON Files → Smart Contracts
```

---

## **📋 Development Roadmap**

### **Phase 1: Backend API Development (2-3 weeks)**
- [ ] Create REST API endpoints
- [ ] User authentication API
- [ ] Battery data management API
- [ ] QR code generation API
- [ ] Blockchain integration API

### **Phase 2: Mobile App Development (4-6 weeks)**
- [ ] Choose mobile framework
- [ ] Set up mobile project
- [ ] Design mobile UI
- [ ] Implement core features
- [ ] Add QR scanning
- [ ] Test on devices

### **Phase 3: Play Store Deployment (1-2 weeks)**
- [ ] Configure build settings
- [ ] Create app signing
- [ ] Prepare store listing
- [ ] Submit for review

---

## **🛠️ Technology Stack Options**

### **Option 1: React Native (Recommended)**
**Pros:**
- JavaScript/TypeScript (easier learning curve)
- Large community and libraries
- Cross-platform (iOS + Android)
- Hot reload for fast development
- Excellent QR scanning libraries

**Cons:**
- Performance slightly lower than native
- Some native features require bridges

**Libraries Needed:**
```json
{
  "dependencies": {
    "react-native": "^0.72.0",
    "react-navigation": "^6.0.0",
    "axios": "^1.4.0",
    "react-native-camera": "^4.2.0",
    "react-native-qrcode-scanner": "^1.5.5",
    "react-native-qrcode-generator": "^0.0.1",
    "@react-native-async-storage/async-storage": "^1.18.0",
    "react-native-chart-kit": "^6.12.0"
  }
}
```

### **Option 2: Flutter**
**Pros:**
- Excellent performance
- Beautiful UI out of the box
- Single codebase for iOS/Android
- Strong Google support

**Cons:**
- Dart language (less common)
- Smaller community than React Native
- Steeper learning curve

### **Option 3: Native Android (Kotlin)**
**Pros:**
- Best performance
- Full Android features
- Native UI components

**Cons:**
- Android only (no iOS)
- Longer development time
- More complex codebase

---

## **🔧 Phase 1: Backend API Development**

### **Create REST API Server**

**File: `mobile_api_server.py`**
```python
"""
REST API for EV Battery Passport Mobile App
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import json
from pathlib import Path
from datetime import datetime
import hashlib

app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
jwt = JWTManager(app)

# Data directories
DATA_DIR = Path("data/processed")

# --------------------------------------------------
# AUTHENTICATION ENDPOINTS
# --------------------------------------------------

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Store user (simplified - use database in production)
    users_file = DATA_DIR / "mobile_users.json"
    users = {}
    
    if users_file.exists():
        with open(users_file, 'r') as f:
            users = json.load(f)
    
    if username in users:
        return jsonify({"status": "error", "message": "User already exists"}), 400
    
    users[username] = {
        "password_hash": password_hash,
        "wallet_address": f"0x{hashlib.sha256(username.encode()).hexdigest()[:40]}",
        "created_at": datetime.now().isoformat()
    }
    
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)
    
    return jsonify({
        "status": "success",
        "message": "User registered successfully",
        "wallet_address": users[username]["wallet_address"]
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Load users
    users_file = DATA_DIR / "mobile_users.json"
    if not users_file.exists():
        return jsonify({"status": "error", "message": "User not found"}), 401
    
    with open(users_file, 'r') as f:
        users = json.load(f)
    
    if username not in users:
        return jsonify({"status": "error", "message": "User not found"}), 401
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if users[username]["password_hash"] != password_hash:
        return jsonify({"status": "error", "message": "Invalid password"}), 401
    
    # Create JWT token
    access_token = create_access_token(identity=username)
    
    return jsonify({
        "status": "success",
        "access_token": access_token,
        "wallet_address": users[username]["wallet_address"]
    })

# --------------------------------------------------
# BATTERY DATA ENDPOINTS
# --------------------------------------------------

@app.route('/api/batteries', methods=['GET'])
@jwt_required()
def get_batteries():
    """Get all batteries for current user"""
    # Load batteries from JSON files
    all_batteries = []
    
    user_battery_file = DATA_DIR / "user_entered_batteries.json"
    if user_battery_file.exists():
        with open(user_battery_file, 'r') as f:
            all_batteries.extend(json.load(f))
    
    auto_battery_file = DATA_DIR / "auto_generated_batteries.json"
    if auto_battery_file.exists():
        with open(auto_battery_file, 'r') as f:
            all_batteries.extend(json.load(f))
    
    return jsonify({
        "status": "success",
        "data": all_batteries,
        "count": len(all_batteries)
    })

@app.route('/api/batteries', methods=['POST'])
@jwt_required()
def create_battery():
    """Create new battery record"""
    data = request.json
    
    # Generate passport ID
    timestamp = datetime.now().strftime('%Y%m%d')
    passport_id = f"EV-BATT-{timestamp}-{len(data.get('batteries', [])) + 1:05d}"
    
    # Add passport ID
    data['passport_id'] = passport_id
    data['timestamp'] = datetime.now().isoformat()
    
    # Save to file
    user_battery_file = DATA_DIR / "user_entered_batteries.json"
    batteries = []
    
    if user_battery_file.exists():
        with open(user_battery_file, 'r') as f:
            batteries = json.load(f)
    
    batteries.append(data)
    
    with open(user_battery_file, 'w') as f:
        json.dump(batteries, f, indent=2)
    
    # Generate QR code
    from utils.qr_generator import QRCodeGenerator
    qr_generator = QRCodeGenerator()
    qr_metadata = qr_generator.generate_battery_qr(data)
    
    return jsonify({
        "status": "success",
        "message": "Battery created successfully",
        "data": data,
        "qr_code_url": qr_metadata.get('qr_url')
    })

@app.route('/api/batteries/<passport_id>', methods=['GET'])
def get_battery(passport_id):
    """Get specific battery by passport ID"""
    # Search in all battery files
    for file_name in ["user_entered_batteries.json", "auto_generated_batteries.json"]:
        file_path = DATA_DIR / file_name
        if file_path.exists():
            with open(file_path, 'r') as f:
                batteries = json.load(f)
                for battery in batteries:
                    if battery.get('passport_id') == passport_id:
                        return jsonify({"status": "success", "data": battery})
    
    return jsonify({"status": "error", "message": "Battery not found"}), 404

# --------------------------------------------------
# AI PREDICTION ENDPOINTS
# --------------------------------------------------

@app.route('/api/predict/<passport_id>', methods=['POST'])
@jwt_required()
def predict_battery_health(passport_id):
    """Get AI prediction for battery"""
    # Load battery data
    battery = None
    for file_name in ["user_entered_batteries.json", "auto_generated_batteries.json"]:
        file_path = DATA_DIR / file_name
        if file_path.exists():
            with open(file_path, 'r') as f:
                batteries = json.load(f)
                for b in batteries:
                    if b.get('passport_id') == passport_id:
                        battery = b
                        break
        if battery:
            break
    
    if not battery:
        return jsonify({"status": "error", "message": "Battery not found"}), 404
    
    # Get prediction
    from ai_oracle.prediction.predictor import BatteryHealthPredictor
    from config import AppConfig
    
    config = AppConfig()
    predictor = BatteryHealthPredictor(config)
    
    prediction = predictor.predict_battery_health(battery)
    anomaly = predictor.predict_anomaly(battery)
    
    return jsonify({
        "status": "success",
        "health_prediction": prediction,
        "anomaly_detection": anomaly
    })

# --------------------------------------------------
# BLOCKCHAIN ENDPOINTS
# --------------------------------------------------

@app.route('/api/blockchain/register/<passport_id>', methods=['POST'])
@jwt_required()
def register_on_blockchain(passport_id):
    """Register battery on blockchain"""
    from blockchain_protocol.execution_engine.battery_passport_controller import BatteryPassportController
    from config import AppConfig
    
    config = AppConfig()
    protocol = BatteryPassportController(config)
    
    result = protocol.register_on_blockchain(passport_id)
    
    return jsonify(result)

if __name__ == '__main__':
    print("🚀 Mobile API Server starting...")
    print("📱 API available at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Install Dependencies:**
```bash
pip install flask flask-cors flask-jwt-extended
```

**Start API Server:**
```bash
python mobile_api_server.py
```

---

## **📱 Phase 2: React Native Mobile App Development**

### **Step 1: Initialize React Native Project**
```bash
npx react-native init EVBatteryPassport
cd EVBatteryPassport
```

### **Step 2: Install Dependencies**
```bash
npm install @react-navigation/native @react-navigation/stack
npm install axios react-native-camera react-native-qrcode-scanner
npm install @react-native-async-storage/async-storage
npm install react-native-chart-kit react-native-svg
npm install react-native-safe-area-context react-native-screens
```

### **Step 3: Project Structure**
```
EVBatteryPassport/
├── src/
│   ├── screens/
│   │   ├── LoginScreen.js
│   │   ├── DashboardScreen.js
│   │   ├── AddBatteryScreen.js
│   │   ├── BatteryRecordsScreen.js
│   │   ├── QRScannerScreen.js
│   │   └── BlockchainExplorerScreen.js
│   ├── components/
│   │   ├── BatteryCard.js
│   │   ├── HealthGauge.js
│   │   └── QRCodeDisplay.js
│   ├── services/
│   │   ├── api.js
│   │   ├── auth.js
│   │   └── storage.js
│   └── navigation/
│       └── AppNavigator.js
├── android/
├── ios/
└── package.json
```

### **Step 4: Key Screen Examples**

**Login Screen (`src/screens/LoginScreen.js`):**
```javascript
import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import { login } from '../services/auth';

export default function LoginScreen({ navigation }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    try {
      const response = await login(username, password);
      if (response.status === 'success') {
        navigation.navigate('Dashboard');
      }
    } catch (error) {
      alert('Login failed');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>EV Battery Passport</Text>
      <TextInput
        style={styles.input}
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />
      <Button title="Login" onPress={handleLogin} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20 },
  title: { fontSize: 24, fontWeight: 'bold', textAlign: 'center', marginBottom: 20 },
  input: { borderWidth: 1, padding: 10, marginBottom: 10, borderRadius: 5 }
});
```

**Dashboard Screen (`src/screens/DashboardScreen.js`):**
```javascript
import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { getBatteries } from '../services/api';
import BatteryCard from '../components/BatteryCard';

export default function DashboardScreen() {
  const [batteries, setBatteries] = useState([]);

  useEffect(() => {
    loadBatteries();
  }, []);

  const loadBatteries = async () => {
    try {
      const response = await getBatteries();
      setBatteries(response.data);
    } catch (error) {
      console.error('Error loading batteries:', error);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>My Batteries</Text>
      <FlatList
        data={batteries}
        keyExtractor={(item) => item.passport_id}
        renderItem={({ item }) => <BatteryCard battery={item} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 20 }
});
```

**API Service (`src/services/api.js`):**
```javascript
import axios from 'axios';

const API_BASE_URL = 'http://your-api-server.com/api';

export const getBatteries = async () => {
  const token = await AsyncStorage.getItem('access_token');
  const response = await axios.get(`${API_BASE_URL}/batteries`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};

export const createBattery = async (batteryData) => {
  const token = await AsyncStorage.getItem('access_token');
  const response = await axios.post(`${API_BASE_URL}/batteries`, batteryData, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};

export const getBatteryPrediction = async (passportId) => {
  const token = await AsyncStorage.getItem('access_token');
  const response = await axios.post(`${API_BASE_URL}/predict/${passportId}`, {}, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};
```

---

## **🚀 Phase 3: Play Store Deployment**

### **Step 1: Configure Android Build**

**Update `android/app/build.gradle`:**
```gradle
android {
    compileSdkVersion 33
    defaultConfig {
        applicationId "com.evbattery.passport"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "1.0.0"
    }
    signingConfigs {
        release {
            storeFile file('your-keystore.jks')
            storePassword 'your-store-password'
            keyAliasyour-key-alias
            keyPassword 'your-key-password'
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

### **Step 2: Generate Signing Key**
```bash
keytool -genkey -v -keystore your-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias your-key-alias
```

### **Step 3: Build Release APK**
```bash
cd android
./gradlew assembleRelease
```

### **Step 4: Create Google Play Console Account**
1. Go to [Google Play Console](https://play.google.com/console)
2. Pay $25 one-time registration fee
3. Create new application
4. Fill in app details:
   - App name: "EV Battery Passport"
   - Description: "Track and manage your EV battery health with blockchain-powered digital passports"
   - Screenshots (required)
   - Icon (512x512)
   - Feature graphic (1024x500)

### **Step 5: Upload APK**
1. Go to "Release Management" → "App Releases"
2. Create new release
3. Upload APK from `android/app/build/outputs/apk/release/`
4. Add release notes
5. Submit for review

### **Step 6: Store Listing Requirements**

**App Description:**
```
EV Battery Passport - Track Your Battery Health

Monitor your electric vehicle battery health with our comprehensive tracking system. 
Features:
• Real-time health monitoring (SoH, SoC, temperature)
• AI-powered health predictions
• Blockchain-secured battery records
• QR code scanning for instant access
• Degradation tracking and alerts
• Performance analytics

Perfect for EV owners, fleet managers, and battery manufacturers.
```

**Privacy Policy URL:** Required - create a simple privacy policy page

**Screenshots Required:**
- Phone screenshots (at least 2)
- Tablet screenshots (optional)

---

## **💰 Cost Breakdown**

### **Development Costs:**
- **Backend API Development:** $0 (using existing Python)
- **React Native Development:** $0 (open source)
- **Testing Devices:** $200-500 (or use emulators)

### **Deployment Costs:**
- **Google Play Registration:** $25 (one-time)
- **Server Hosting:** $5-20/month (Render/PythonAnywhere/DigitalOcean)
- **Domain Name:** $10-15/year (optional)

### **Total Estimated Cost:** $40-540 (one-time) + $5-20/month

---

## **⏱️ Timeline Estimate**

- **Week 1-2:** Backend API development
- **Week 3-6:** React Native app development
- **Week 7:** Testing and bug fixes
- **Week 8:** Play Store submission and review

**Total: 8 weeks for production-ready app**

---

## **🎯 Quick Start Checklist**

### **Immediate Actions:**
1. [ ] Choose mobile framework (React Native recommended)
2. [ ] Set up development environment
3. [ ] Create mobile API server
4. [ ] Initialize React Native project
5. [ ] Design mobile UI mockups

### **Development Phase:**
1. [ ] Implement authentication screens
2. [ ] Create battery management screens
3. [ ] Add QR scanning functionality
4. [ ] Integrate AI prediction API
5. [ ] Add blockchain registration
6. [ ] Test on real devices

### **Deployment Phase:**
1. [ ] Generate signing key
2. [ ] Build release APK
3. [ ] Create Play Console account
4. [ ] Prepare store listing
5. [ ] Submit for review

---

## **📚 Additional Resources**

- [React Native Documentation](https://reactnative.dev/)
- [Google Play Console Guide](https://support.google.com/googleplay/android-developer)
- [React Navigation](https://reactnavigation.org/)
- [Axios Documentation](https://axios-http.com/)

---

## **🚨 Important Notes**

1. **Backend Required:** Mobile app needs the Python API server running
2. **Internet Connection:** App requires internet for API calls
3. **Security:** Implement proper authentication and encryption
4. **Testing:** Test on multiple Android devices
5. **Updates:** Plan for regular app updates and maintenance

---

**Recommended Approach:** Start with React Native for fastest development, use existing Python backend, deploy to Render or similar hosting, then submit to Play Store after thorough testing.
