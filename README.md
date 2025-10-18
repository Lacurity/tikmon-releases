# Lacs TikTok Monitor

![GitHub release](https://img.shields.io/github/v/release/Lacurity/tikmon)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A standalone Python script that monitors TikTok user **@0xlac** for:
- ✅ Live stream starts/ends
- ✅ New video uploads  
- ✅ Webhook notifications (Discord, Slack, etc.)
- ✅ Real-time status dashboard
- ✅ Auto-updates from GitHub

## 🎯 Features

```
╦  ╔═╗╔═╗╔═╗  ╔╦╗╔═╗╔╗╔╦╔╦╗╔═╗╦═╗
║  ╠═╣║  ╚═╗  ║║║║ ║║║║║ ║ ║ ║╠╦╝
╩═╝╩ ╩╚═╝╚═╝  ╩ ╩╚═╝╝╚╝╩ ╩ ╚═╝╩╚═
```

- **Real-time monitoring** - 30 second intervals
- **Live status dashboard** - `Checks: 21 | Failed: 0 | Live: 1 | Uploads: 0 | Webhooks: 5 | Uptime: 2h15m`
- **Multiple detection methods** - Web scraping + mobile endpoints
- **Auto-updates** - Stay current with latest features
- **Comprehensive logging** - All activity logged
- **Cross-platform** - Windows, Linux, macOS

## Setup Instructions

### 1. Install Python
Make sure you have Python 3.7+ installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Webhook URL
Edit `config.json` and replace `YOUR_WEBHOOK_URL_HERE` with your actual webhook URL:

#### For Discord:
1. Go to your Discord server settings
2. Navigate to Integrations → Webhooks
3. Create a new webhook or use existing one
4. Copy the webhook URL

#### For Slack:
1. Go to your Slack app settings
2. Create an incoming webhook
3. Copy the webhook URL

### 4. Run the Monitor
```bash
python tiktok_webhook_monitor.py
```

## Configuration Options

Edit `config.json` to customize the monitor:

```json
{
  "username": "0xlac",                    // TikTok username to monitor
  "webhook_url": "YOUR_WEBHOOK_URL_HERE", // Your webhook URL
  "check_interval": 30,                   // Seconds between live checks
  "monitor_uploads": true,                // Enable upload monitoring
  "upload_check_interval": 300,           // Seconds between upload checks
  "enable_logging": true,                 // Enable logging to file
  "webhook_settings": {
    "username": "TikTok Monitor",         // Webhook bot name
    "avatar_url": "https://..."           // Webhook bot avatar
  }
}
```

## Webhook Messages

The monitor sends different types of webhook messages:

### 🔴 Live Stream Started
- Notification when @0xlac goes live
- Includes viewer count and direct link
- Red color embed

### 📱 Live Stream Ended  
- Notification when stream ends
- Blue color embed

### 📹 New Upload
- Notification for new video uploads
- Includes video description and link
- Light blue color embed

## Running as a Service

### Windows (using Task Scheduler):
1. Open Task Scheduler
2. Create Basic Task
3. Set to run `python C:\path\to\tikmon\tiktok_webhook_monitor.py`
4. Set to run at startup and repeat every 1 minute

### Linux (using systemd):
Create `/etc/systemd/system/tiktok-monitor.service`:
```ini
[Unit]
Description=TikTok Monitor
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/tikmon
ExecStart=/usr/bin/python3 tiktok_webhook_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then run:
```bash
sudo systemctl enable tiktok-monitor.service
sudo systemctl start tiktok-monitor.service
```

## Troubleshooting

### "Configuration error: webhook_url is required"
- Make sure you've edited `config.json` with your actual webhook URL

### "All TikTok check methods failed"
- This is normal occasionally due to TikTok's anti-bot measures
- The script will keep retrying automatically

### Webhook not receiving messages
- Verify your webhook URL is correct
- Check the webhook service (Discord/Slack) is online
- Check the log file `tiktok_monitor.log` for error details

### Unicode encoding errors on Windows
- Fixed in latest version with UTF-8 encoding
- If issues persist, run in PowerShell with `chcp 65001` first

## Logs

The monitor creates a log file `tiktok_monitor.log` with detailed information:
- Live status checks
- Webhook sending status
- Errors and debugging info
- Timestamps for all activities

## Example Output

```
2025-10-16 21:12:39,602 - INFO - Starting TikTok monitor for @0xlac
2025-10-16 21:12:39,603 - INFO - Checking every 30 seconds
2025-10-16 21:13:12,727 - INFO - @0xlac just went LIVE!
2025-10-16 21:13:13,290 - INFO - Sent live notification for @0xlac
```

## What's Different from Discord Bot

This standalone version:
- ✅ No Discord bot required
- ✅ Works with any webhook service
- ✅ Lighter weight and faster
- ✅ Can run on any server/computer
- ✅ Multiple notification targets possible
- ✅ Independent of Discord server status

## Support

If you encounter issues:
1. Check the log file `tiktok_monitor.log`
2. Verify your webhook URL is working
3. Make sure Python dependencies are installed
4. Check that your internet connection is stable

## License

This project is for educational and personal use only. Please respect TikTok's terms of service.