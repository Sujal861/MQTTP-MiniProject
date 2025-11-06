# 🪟 Windows Setup Guide - MQTT Security Project

**Complete Installation and Running Instructions for Windows 10/11**

---

## 📋 Table of Contents

1. [Prerequisites Installation](#prerequisites-installation)
2. [Certificate Generation](#certificate-generation)
3. [Running the System](#running-the-system)
4. [Testing](#testing)
5. [Troubleshooting](#troubleshooting)
6. [What We Accomplished](#what-we-accomplished)

---

## 🔧 Prerequisites Installation

### 1. Install Python 3.6+

**Download and Install:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python 3.11 or later (recommended)
3. Run the installer
4. ✅ **IMPORTANT:** Check "Add Python to PATH" during installation
5. Click "Install Now"

**Verify Installation:**
```powershell
python --version
```
Expected output: `Python 3.x.x`

---

### 2. Install OpenSSL

**Download and Install:**
1. Go to [slproweb.com/products/Win32OpenSSL.html](https://slproweb.com/products/Win32OpenSSL.html)
2. Download "Win64 OpenSSL v3.x.x" (full version, not Light)
3. Run the installer
4. Install to default location: `C:\Program Files\OpenSSL-Win64`
5. When asked, select "The OpenSSL binaries (/bin) directory"

**Add to PATH:**
1. Press `Win + X` → Select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "System variables", find "Path" → Click "Edit"
5. Click "New" → Add: `C:\Program Files\OpenSSL-Win64\bin`
6. Click "OK" on all windows
7. **Restart PowerShell**

**Verify Installation:**
```powershell
openssl version
```
Expected output: `OpenSSL 3.x.x`

---

### 3. Install Eclipse Mosquitto

**Download and Install:**
1. Go to [mosquitto.org/download](https://mosquitto.org/download/)
2. Download "mosquitto-x.x.x-install-windows-x64.exe"
3. Run the installer
4. Install to default location: `C:\Program Files\mosquitto`
5. Complete the installation

**Verify Installation:**
```powershell
& "C:\Program Files\mosquitto\mosquitto.exe" -h
```
Expected output: Mosquitto help text

---

### 4. Install Python Packages

**Open PowerShell and run:**
```powershell
pip install paho-mqtt matplotlib
```

**Verify Installation:**
```powershell
pip list | findstr "paho-mqtt"
pip list | findstr "matplotlib"
```

---

## 🔐 Certificate Generation

### Complete Certificate Setup Script

**Copy and paste this entire script into PowerShell:**

```powershell
# Navigate to project directory
cd C:\Users\YOUR_USERNAME\Desktop\MQTTP\AUTHENTICATION-AND-INTEGRITY-FOR-MQTT-PROTOCOL

# Create directories
Write-Host "Creating directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "certs" -Force | Out-Null
New-Item -ItemType Directory -Path "broker_config" -Force | Out-Null

# ============================================
# Generate CA (Certificate Authority)
# ============================================
Write-Host "\nGenerating Certificate Authority..." -ForegroundColor Cyan

openssl genrsa -out broker_config\ca.key 2048

openssl req -new -x509 -days 3650 `
    -key broker_config\ca.key `
    -out broker_config\ca.crt `
    -subj "/C=DE/ST=Bavaria/L=Deggendorf/O=DIT/OU=EmbeddedSecurity/CN=MQTT-CA"

Write-Host "✅ CA Certificate created" -ForegroundColor Green

# ============================================
# Generate Server Certificate
# ============================================
Write-Host "\nGenerating Server Certificate..." -ForegroundColor Cyan

openssl genrsa -out broker_config\server.key 2048

openssl req -new `
    -key broker_config\server.key `
    -out broker_config\server.csr `
    -subj "/C=DE/ST=Bavaria/L=Deggendorf/O=DIT/OU=EmbeddedSecurity/CN=localhost"

openssl x509 -req `
    -in broker_config\server.csr `
    -CA broker_config\ca.crt `
    -CAkey broker_config\ca.key `
    -CAcreateserial `
    -out broker_config\server.crt `
    -days 3650

Write-Host "✅ Server Certificate created" -ForegroundColor Green

# ============================================
# Generate Client Certificate
# ============================================
Write-Host "\nGenerating Client Certificate..." -ForegroundColor Cyan

openssl genrsa -out certs\client.key 2048

openssl req -new `
    -key certs\client.key `
    -out certs\client.csr `
    -subj "/C=DE/ST=Bavaria/L=Deggendorf/O=DIT/OU=EmbeddedSecurity/CN=mqtt-client"

openssl x509 -req `
    -in certs\client.csr `
    -CA broker_config\ca.crt `
    -CAkey broker_config\ca.key `
    -CAcreateserial `
    -out certs\client.crt `
    -days 3650

Write-Host "✅ Client Certificate created" -ForegroundColor Green

# ============================================
# Generate Shared HMAC Key
# ============================================
Write-Host "\nGenerating HMAC Shared Key..." -ForegroundColor Cyan

openssl rand -hex 32 | Out-File -FilePath "shared_key.txt" -Encoding ASCII -NoNewline

Write-Host "✅ Shared key created" -ForegroundColor Green

# ============================================
# Create Password File
# ============================================
Write-Host "\nCreating password file..." -ForegroundColor Cyan

"subin:subin123" | Out-File -FilePath "broker_config\passwd_file.txt" -Encoding ASCII

Write-Host "✅ Password file created" -ForegroundColor Green

# ============================================
# Create ACL File
# ============================================
Write-Host "\nCreating ACL file..." -ForegroundColor Cyan

@"
# ACL File for MQTT Broker
user subin
topic readwrite #
"@ | Out-File -FilePath "broker_config\acl_file.txt" -Encoding ASCII

Write-Host "✅ ACL file created" -ForegroundColor Green

# ============================================
# Hash Password File
# ============================================
Write-Host "\nHashing password file..." -ForegroundColor Cyan

& "C:\Program Files\mosquitto\mosquitto_passwd.exe" -U broker_config\passwd_file.txt

Write-Host "✅ Password file hashed" -ForegroundColor Green

# ============================================
# Summary
# ============================================
Write-Host "\n========================================" -ForegroundColor Yellow
Write-Host "   Certificate Generation Complete!" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

Write-Host "\nGenerated files:" -ForegroundColor White
Write-Host "  ✅ broker_config\ca.crt" -ForegroundColor Green
Write-Host "  ✅ broker_config\ca.key" -ForegroundColor Green
Write-Host "  ✅ broker_config\server.crt" -ForegroundColor Green
Write-Host "  ✅ broker_config\server.key" -ForegroundColor Green
Write-Host "  ✅ certs\client.crt" -ForegroundColor Green
Write-Host "  ✅ certs\client.key" -ForegroundColor Green
Write-Host "  ✅ shared_key.txt" -ForegroundColor Green
Write-Host "  ✅ broker_config\passwd_file.txt" -ForegroundColor Green
Write-Host "  ✅ broker_config\acl_file.txt" -ForegroundColor Green

Write-Host "\n🎉 Setup complete! You can now run the system." -ForegroundColor Green
```

**Expected Output:**
```
Creating directories...
Generating Certificate Authority...
✅ CA Certificate created
Generating Server Certificate...
✅ Server Certificate created
Generating Client Certificate...
✅ Client Certificate created
✅ Shared key created
✅ Password file created
✅ ACL file created
✅ Password file hashed
========================================
   Certificate Generation Complete!
========================================
```

---

## 🚀 Running the System

### **You Need 4 Terminal Windows**

#### **Terminal 1: Start Mosquitto Broker**

```powershell
cd C:\Users\YOUR_USERNAME\Desktop\MQTTP\AUTHENTICATION-AND-INTEGRITY-FOR-MQTT-PROTOCOL
& "C:\Program Files\mosquitto\mosquitto.exe" -c broker_config\mosquitto.conf -v
```

**✅ Expected Output:**
```
1730... : mosquitto version 2.0.18 starting
1730... : Config loaded from broker_config\mosquitto.conf.
1730... : Opening ipv4 listen socket on port 1884.
1730... : Opening ipv4 listen socket on port 8883.
1730... : mosquitto version 2.0.18 running
```

**⚠️ Keep this terminal running!**

---

#### **Terminal 2: Run Subscriber**

```powershell
cd C:\Users\YOUR_USERNAME\Desktop\MQTTP\AUTHENTICATION-AND-INTEGRITY-FOR-MQTT-PROTOCOL
python client\secure_subscriber.py
```

**✅ Expected Output:**
```
📡 Waiting for messages...
📶 Connected to broker securely!
✅ Subscribed to topic: secure/topic
```

**⚠️ Keep this terminal running!**

---

#### **Terminal 3: Run Publisher**

```powershell
cd C:\Users\YOUR_USERNAME\Desktop\MQTTP\AUTHENTICATION-AND-INTEGRITY-FOR-MQTT-PROTOCOL
python client\secure_publisher.py
```

**✅ Expected Output:**
```
📶 Publisher connected to broker securely.
✅ Published message with HMAC: Temperature is 23°C||d03c0358617447c7...
```

**In Terminal 2 (Subscriber), you should see:**
```
============================================================
🕒 Time: 2025-11-06 12:24:45
📨 Raw message received: Temperature is 23°C||d03c0358617447c7...
🧾 Parsed message: Temperature is 23°C
🔐 HMAC from message: d03c0358617447c7...
✅ Message is authentic!
============================================================
```

---

#### **Terminal 4: Run Dashboard (Optional)**

```powershell
cd C:\Users\YOUR_USERNAME\Desktop\MQTTP\AUTHENTICATION-AND-INTEGRITY-FOR-MQTT-PROTOCOL
python temperature_dashboard.py
```

**✅ Expected Result:**
- A window opens with a real-time temperature graph
- Console shows connection status and message logs

---

## 🧪 Testing

### Test 1: Normal Message Flow

1. Start Broker (Terminal 1)
2. Start Subscriber (Terminal 2)
3. Start Publisher (Terminal 3)
4. Verify subscriber shows "✅ Message is authentic!"

---

### Test 2: Tamper Detection

**In a new terminal:**
```powershell
cd C:\Users\YOUR_USERNAME\Desktop\MQTTP\AUTHENTICATION-AND-INTEGRITY-FOR-MQTT-PROTOCOL
python client\tamper_simulation.py
```

**✅ Expected Output in Publisher Terminal:**
```
📶 Connected to broker securely.
❌ Tampered message sent: Temperature is 100°C||WRONGHASH123
```

**✅ Expected Output in Subscriber Terminal:**
```
============================================================
🕒 Time: 2025-11-06 12:25:12
📨 Raw message received: Temperature is 100°C||WRONGHASH123
🧾 Parsed message: Temperature is 100°C
🔐 HMAC from message: WRONGHASH123
❌ HMAC verification failed!
🧮 Expected HMAC: a1b2c3d4e5f6789...
============================================================
```

**✅ This proves the integrity check is working!**

---

### Test 3: TLS Encryption

**Verify port is listening:**
```powershell
netstat -ano | findstr 8883
```

**Expected Output:**
```
TCP    0.0.0.0:8883           0.0.0.0:0              LISTENING       12345
```

---

## 🛠️ Troubleshooting

### Problem 1: "mosquitto: command not found"

**Solution:**
```powershell
& "C:\Program Files\mosquitto\mosquitto.exe" -c broker_config\mosquitto.conf -v
```
Use the full path with `&` operator.

---

### Problem 2: "ConnectionRefusedError [WinError 10061]"

**Cause:** Broker is not running.

**Solution:**
1. Start the broker first (Terminal 1)
2. Wait for "mosquitto version X.X.X running"
3. Then start clients

---

### Problem 3: "ModuleNotFoundError: No module named 'paho'"

**Solution:**
```powershell
pip install paho-mqtt
```

---

### Problem 4: "ModuleNotFoundError: No module named 'matplotlib'"

**Solution:**
```powershell
pip install matplotlib
```

---

### Problem 5: "openssl: command not found"

**Solution:**
1. Verify OpenSSL is installed: `C:\Program Files\OpenSSL-Win64`
2. Add to PATH (see Prerequisites section)
3. Restart PowerShell
4. Test: `openssl version`

---

### Problem 6: Broker starts but clients can't connect

**Check certificate paths in mosquitto.conf:**
```powershell
Get-Content broker_config\mosquitto.conf | Select-String "cafile|certfile|keyfile"
```

**Verify files exist:**
```powershell
Test-Path broker_config\ca.crt
Test-Path broker_config\server.crt
Test-Path broker_config\server.key
```

All should return `True`.

---

### Problem 7: Windows Firewall Blocking Port 8883

**Solution:**
```powershell
netsh advfirewall firewall add rule name="Mosquitto TLS 8883" dir=in action=allow protocol=TCP localport=8883
```

---

### Problem 8: Dashboard window not opening

**Check Tkinter installation:**
```powershell
python -m tkinter
```

If error, reinstall Python with Tkinter support.

---

## 📊 System Architecture

```
┌─────────────┐         TLS 8883 + HMAC        ┌─────────────┐
│  Publisher  │ ────────────────────────────────> │   Mosquitto │
│   (Client)  │                                 │    Broker   │
└─────────────┘                                 └─────────────┘
                                                       │
                                                       │ TLS 8883
                                                       │
                                    ┌──────────────────┴──────────────────┐
                                    │                                     │
                                    ▼                                     ▼
                            ┌─────────────┐                      ┌─────────────┐
                            │ Subscriber  │                      │  Dashboard  │
                            │   (Client)  │                      │   (Client)  │
                            └─────────────┘                      └─────────────┘
                                    │                                     │
                                    │                                     │
                                    └──────────> HMAC Verify <───────────┘
```

---

## 🔐 Security Features

### 1. TLS Encryption
- **Protocol:** TLS 1.2/1.3
- **Port:** 8883
- **Key Size:** 2048-bit RSA
- **Protection:** Eavesdropping, Man-in-the-middle attacks

### 2. Certificate Authentication
- **CA Certificate:** Self-signed root CA
- **Server Certificate:** Signed by CA
- **Client Certificate:** Signed by CA
- **Protection:** Unauthorized access, Impersonation

### 3. HMAC Integrity
- **Algorithm:** HMAC-SHA256
- **Key:** 32-byte shared secret
- **Protection:** Message tampering, Data modification

### 4. Access Control
- **Username/Password:** bcrypt hashed
- **ACL:** Topic-based permissions
- **Protection:** Unauthorized publishing/subscribing

---

## 📝 Quick Reference Commands

### Start Everything
```powershell
# Terminal 1 - Broker
& "C:\Program Files\mosquitto\mosquitto.exe" -c broker_config\mosquitto.conf -v

# Terminal 2 - Subscriber
python client\secure_subscriber.py

# Terminal 3 - Publisher
python client\secure_publisher.py

# Terminal 4 - Dashboard
python temperature_dashboard.py
```

### Stop Everything
- Press `Ctrl + C` in each terminal window

### Check Broker Status
```powershell
netstat -ano | findstr 8883
```

---

## 📁 Project Structure

```
AUTHENTICATION-AND-INTEGRITY-FOR-MQTT-PROTOCOL/
├── broker_config/
│   ├── ca.crt              # CA Certificate
│   ├── ca.key              # CA Private Key
│   ├── server.crt          # Server Certificate
│   ├── server.key          # Server Private Key
│   ├── passwd_file.txt     # Hashed passwords
│   ├── acl_file.txt        # Access Control List
│   └── mosquitto.conf      # Broker configuration
├── certs/
│   ├── client.crt          # Client Certificate
│   └── client.key          # Client Private Key
├── client/
│   ├── secure_publisher.py     # MQTT Publisher
│   ├── secure_subscriber.py    # MQTT Subscriber
│   └── tamper_simulation.py    # Tamper test
├── shared_key.txt              # HMAC Shared Key
├── temperature_dashboard.py    # Real-time dashboard
└── README.md                   # Project overview
```

---

## ✅ Setup Checklist

- [ ] Python 3.6+ installed
- [ ] OpenSSL installed and in PATH
- [ ] Mosquitto installed
- [ ] Python packages installed (`paho-mqtt`, `matplotlib`)
- [ ] Certificates generated (9 files)
- [ ] File paths updated in all scripts
- [ ] Broker starts successfully
- [ ] Subscriber connects and receives messages
- [ ] Publisher sends messages with HMAC
- [ ] Tamper detection works
- [ ] Dashboard displays real-time data

---

## 🎓 What We Accomplished

### Issues Resolved

1. **Missing Directory Structure**
   - Created `certs/` and `broker_config/` directories
   - Generated all required certificates and keys

2. **Bash Script Compatibility**
   - Original `.sh` scripts don't work on Windows PowerShell
   - Converted to native PowerShell/OpenSSL commands
   - All certificate generation now works on Windows

3. **Path Configuration**
   - Updated hardcoded Linux/Mac paths to Windows format
   - Fixed paths in all Python scripts and configuration files
   - Changed from: `C:/Users/subin/OneDrive/Desktop(1)/...`
   - Changed to: `C:/Users/sujal/Desktop/MQTTP/AUTHENTICATION-AND-INTEGRITY-FOR-MQTT-PROTOCOL/...`

4. **Mosquitto Integration**
   - Configured to use full path: `C:\Program Files\mosquitto\mosquitto.exe`
   - Password file hashing with `mosquitto_passwd` utility
   - ACL file created for access control

### Files Generated

```
✅ broker_config/ca.crt              (CA Certificate)
✅ broker_config/ca.key              (CA Private Key)
✅ broker_config/server.crt          (Server Certificate)
✅ broker_config/server.key          (Server Private Key)
✅ broker_config/passwd_file.txt     (Hashed passwords)
✅ broker_config/acl_file.txt        (Access Control List)
✅ certs/client.crt                  (Client Certificate)
✅ certs/client.key                  (Client Private Key)
✅ shared_key.txt                    (HMAC Shared Key - 32 bytes hex)
```

### Verified Functionality

✅ **TLS Encryption** - Port 8883 secure communication  
✅ **Publisher** - Successfully connects and sends messages  
✅ **Subscriber** - Receives and verifies HMAC integrity  
✅ **Tamper Detection** - Rejects messages with invalid HMAC  
✅ **Dashboard** - Real-time visualization with tkinter/matplotlib  

### Security Features Active

- **Encryption:** TLS 1.2/1.3 on port 8883
- **Authentication:** Username/password (bcrypt hashed)
- **Integrity:** HMAC-SHA256 message verification
- **Access Control:** ACL-based topic permissions

---

## 🎓 Academic Context

**Course:** Embedded Security  
**Program:** M.Sc. Applied Computer Science  
**University:** Deggendorf Institute of Technology, Germany  
**Year:** 2025

---

## 🎉 Success!

If you see:
- ✅ Broker running on port 8883
- ✅ Subscriber receiving messages
- ✅ Publisher sending HMAC-signed messages
- ✅ Tamper detection rejecting invalid messages
- ✅ Dashboard showing real-time data

**Congratulations! Your secure MQTT system is fully operational!** 🔐🚀

---

*Setup completed: November 6, 2025*  

*Last Updated: November 6, 2025*
