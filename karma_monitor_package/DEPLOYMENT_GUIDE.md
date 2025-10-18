# 🎯 Karma Monitor - Setup Guide

## 📦 **For Your Friend's PC (Deployment)**

### **Option 1: Python Installation (Recommended)**
1. **Download files needed**:
   ```
   tiktok_webhook_monitor.py
   requirements.txt
   start_monitor.bat
   updater.py
   version.json
   ```

2. **Your friend installs**:
   - Python 3.7+ from https://python.org
   - Open Command Prompt/PowerShell and run:
     ```
     pip install aiohttp requests
     ```

3. **Run the monitor**:
   - Double-click `start_monitor.bat`
   - Or run: `python tiktok_webhook_monitor.py`

### **Option 2: Standalone Executable (No Python needed)**
1. **You create the .exe**:
   ```bash
   # In your tikmon folder:
   python build_exe.py
   ```

2. **Send your friend**:
   - Just the `KarmaMonitor.exe` file from the `dist/` folder
   - They double-click to run - no installation needed!

---

## 🔄 **Auto-Update Setup**

### **GitHub Repository Setup**
1. **Create GitHub repo**:
   - Go to https://github.com/new
   - Name: `tikmon-releases` (or whatever you prefer)
   - Make it public (for easy auto-updates)

2. **Upload your code**:
   ```bash
   git init
   git add .
   git commit -m "Initial Karma Monitor release"
   git remote add origin https://github.com/YOUR_USERNAME/tikmon-releases.git
   git push -u origin main
   ```

3. **Create releases**:
   - Go to your repo → Releases → Create a new release
   - Tag: `v1.0.0` (increment for updates)
   - Upload your files or use the auto-generated source code

### **Enable Auto-Updates**
1. **Update the repo URL** in `updater.py`:
   - Change line: `GITHUB_REPO = "YOUR_USERNAME/tikmon-releases"`

2. **Auto-update methods**:
   
   **Manual check**:
   ```bash
   python updater.py
   ```
   
   **Silent auto-update**:
   ```bash
   python updater.py --silent
   ```

---

## 🚀 **Easy Deployment Script**

### **Send to Friend Package**
Create a deployment package with everything they need:

1. **Files to include**:
   - `tiktok_webhook_monitor.py` (main script)
   - `requirements.txt` (dependencies)
   - `start_monitor.bat` (launcher)
   - `updater.py` (auto-updater)
   - `version.json` (version tracking)
   - `setup_friend.bat` (auto-installer)

2. **Your friend runs**:
   - `setup_friend.bat` - installs everything automatically
   - `start_monitor.bat` - starts the monitor

---

## 🎮 **Usage for Your Friend**

### **First Time Setup**
1. Extract all files to a folder (like `C:\KarmaMonitor\`)
2. Run `setup_friend.bat` (installs Python dependencies)
3. Run `start_monitor.bat` (starts monitoring)

### **Daily Use**
- Just double-click `start_monitor.bat`
- See the clean Karma Monitor interface
- Get Discord notifications when streams start/end

### **Updates**
- Monitor automatically checks for updates
- Or manually run `updater.py` for latest version

---

## 🔧 **Advanced: Startup Integration**

To start automatically with Windows:

1. **Create shortcut** to `start_monitor.bat`
2. **Copy shortcut** to startup folder:
   - Press `Win+R`, type: `shell:startup`
   - Paste the shortcut there
3. **Monitor starts** with Windows boot

---

## 📞 **Support**

If your friend has issues:
1. Check `tiktok_monitor.log` for errors
2. Ensure Python 3.7+ is installed
3. Run `pip install -r requirements.txt` again
4. Restart the monitor

**That's it! Your friend will have a working Karma Monitor! 🎉**