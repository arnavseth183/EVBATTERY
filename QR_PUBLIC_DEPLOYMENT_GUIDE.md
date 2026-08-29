# 🌐 Public QR Code Deployment Guide

## **How to Make QR Codes Accessible to Anyone**

Currently, QR codes use `http://localhost:8000` which only works locally. To make them accessible to anyone who scans them, you need to deploy the web server publicly.

---

## **🚀 Deployment Options**

### **Option 1: Ngrok (Easiest for Testing)**
**Free, quick, perfect for demonstration**

**Step 1: Install Ngrok**
```bash
# Download from https://ngrok.com/download
# Or use: choco install ngrok (Windows)
```

**Step 2: Start QR Web Server**
```bash
python qr_web_server.py
```

**Step 3: Start Ngrok**
```bash
ngrok http 8000
```

**Step 4: Update Configuration**
Ngrok will give you a URL like: `https://abc123.ngrok-free.app`

Update your `.env` file:
```env
QR_SERVER_URL=https://abc123.ngrok-free.app
```

**Step 5: Generate New QR Codes**
- Add a new battery in the app
- QR codes will now use the public ngrok URL
- Anyone can scan and view battery information

---

### **Option 2: Cloud Hosting (Production)**
**For permanent public access**

#### **A. Render (Free Tier Available)**

**Step 1: Create `requirements.txt`**
```txt
flask
qrcode[pil]
pillow
```

**Step 2: Create `Procfile`**
```
web: python qr_web_server.py
```

**Step 3: Deploy to Render**
1. Push code to GitHub
2. Go to render.com
3. Create new web service
4. Connect your GitHub repo
5. Render will give you a public URL

**Step 4: Update Configuration**
```env
QR_SERVER_URL=https://your-app-name.onrender.com
```

#### **B. PythonAnywhere (Free Tier Available)**

**Step 1: Create Account**
- Sign up at pythonanywhere.com

**Step 2: Upload Files**
- Upload `qr_web_server.py` to your account
- Upload your battery data files

**Step 3: Configure Web App**
- Create a new web app
- Set it to run `qr_web_server.py`
- PythonAnywhere will give you a public URL

**Step 4: Update Configuration**
```env
QR_SERVER_URL=https://yourusername.pythonanywhere.com
```

#### **C. Heroku (Free Tier Available)**

**Step 1: Create `requirements.txt`**
```txt
flask
qrcode[pil]
pillow
gunicorn
```

**Step 2: Create `Procfile`**
```
web: gunicorn qr_web_server:app
```

**Step 3: Deploy to Heroku**
```bash
heroku create your-app-name
git push heroku main
```

**Step 4: Update Configuration**
```env
QR_SERVER_URL=https://your-app-name.herokuapp.com
```

---

### **Option 3: VPS/Cloud Server (Full Control)**

#### **A. DigitalOcean, AWS, Azure, etc.**

**Step 1: Get a Server**
- Create a VPS (e.g., DigitalOcean Droplet)
- Choose Ubuntu 20.04+

**Step 2: Install Dependencies**
```bash
sudo apt update
sudo apt install python3 python3-pip nginx
pip3 install flask qrcode[pil] pillow
```

**Step 3: Upload Files**
- Upload `qr_web_server.py` to server
- Upload battery data files

**Step 4: Run with Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 qr_web_server:app
```

**Step 5: Configure Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

**Step 6: Update Configuration**
```env
QR_SERVER_URL=https://your-domain.com
```

---

## **🔧 Configuration Setup**

### **Update `.env` File**
```env
# QR Code Server Configuration
QR_SERVER_URL=https://your-public-url.com

# Example configurations:
# Ngrok: QR_SERVER_URL=https://abc123.ngrok-free.app
# Render: QR_SERVER_URL=https://ev-battery-passport.onrender.com
# PythonAnywhere: QR_SERVER_URL=https://yourusername.pythonanywhere.com
# Heroku: QR_SERVER_URL=https://your-app-name.herokuapp.com
# Custom: QR_SERVER_URL=https://battery-passport.yourdomain.com
```

### **Update `config.py` (if not using .env)**
```python
# QR Code Server Configuration
QR_SERVER_URL = os.getenv("QR_SERVER_URL", "https://your-public-url.com")
```

---

## **📱 Testing Public Access**

**Step 1: Start Web Server**
```bash
python qr_web_server.py
```

**Step 2: Test Public URL**
```bash
# Test in browser
https://your-public-url.com/battery/EV-BATT-20260711-12345

# Test with curl
curl https://your-public-url.com/api/battery/EV-BATT-20260711-12345
```

**Step 3: Generate New QR Code**
- Add a new battery in the Streamlit app
- QR code will contain the public URL
- Scan with your phone to test

---

## **🔒 Security Considerations**

### **For Public Deployment:**

1. **Add Authentication** (Optional)
```python
# Add to qr_web_server.py
@app.route('/battery/<passport_id>')
@auth_required  # Add authentication decorator
def display_battery(passport_id):
    # Your existing code
```

2. **Rate Limiting**
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)

@app.route('/battery/<passport_id>')
@limiter.limit("10 per minute")
def display_battery(passport_id):
    # Your existing code
```

3. **HTTPS Only**
- Use SSL certificates (Let's Encrypt free)
- Redirect HTTP to HTTPS

4. **Data Privacy**
- Consider if battery data should be public
- Add password protection if needed

---

## **🎯 Quick Start with Ngrok (Recommended for Testing)**

**One-minute setup:**

```bash
# Terminal 1: Start web server
python qr_web_server.py

# Terminal 2: Start ngrok
ngrok http 

# Copy the ngrok URL (e.g., https://abc123.ngrok-free.app)

# Update .env file
QR_SERVER_URL=https://abc123.ngrok-free.app

# Restart Streamlit app
streamlit run app.py

# Add a new battery - QR code will use public URL
```

**Anyone can now scan the QR code and see battery information!**

---

## **📊 Deployment Comparison**

| Option | Cost | Difficulty | Best For | URL Format |
|--------|------|------------|----------|------------|
| **Ngrok** | Free | Easy | Testing/Demo | `https://xxx.ngrok-free.app` |
| **Render** | Free/Monthly | Medium | Production | `https://xxx.onrender.com` |
| **PythonAnywhere** | Free/Monthly | Medium | Production | `https://xxx.pythonanywhere.com` |
| **Heroku** | Free/Monthly | Medium | Production | `https://xxx.herokuapp.com` |
| **VPS** | $5-10/month | Hard | Full Control | `https://yourdomain.com` |

---

## **✅ Verification Checklist**

Before going public:

- [ ] Web server runs without errors
- [ ] Public URL is accessible from browser
- [ ] Battery data loads correctly
- [ ] QR codes contain public URL
- [ ] Mobile scanning works
- [ ] SSL/HTTPS configured (production)
- [ ] Rate limiting configured (production)
- [ ] Backup strategy in place

---

## **🚨 Troubleshooting**

**QR code still shows localhost:**
- Restart Streamlit app after changing .env
- Generate new QR code after URL change
- Clear browser cache

**Public URL not accessible:**
- Check web server is running
- Verify firewall allows port 8000
- Check cloud provider status
- Verify DNS propagation

**Battery data not loading:**
- Ensure data files are uploaded to server
- Check file paths in qr_web_server.py
- Verify file permissions

---

**Recommended for your project:** Start with **Ngrok** for testing, then deploy to **Render** or **PythonAnywhere** for production.
