# 🚀 Egyptian Voter Inquiry Bot - Render Deployment Guide

## Quick Setup

### 1. Environment Variables (Required)

Add these environment variables in your Render dashboard:

| Variable | Description | Example |
|----------|-------------|---------|
| `SPREADSHEET_ID` | Your Google Sheet ID | `1-rCGPx6vyE...` |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | Full JSON content of service account file | See below |
| `PYTHONUNBUFFERED` | Enable immediate log output | `1` |
| `PORT` | Port number (auto-set by Render) | `10000` |

### 2. GOOGLE_APPLICATION_CREDENTIALS_JSON Setup

**Important**: This is the most critical step!

1. Open your `credentials.json` or `service_account.json` file
2. Copy the **entire content** (from `{` to `}`)
3. Paste it as the value in Render's environment variables

Example content:
```json
{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "your-bot@your-project.iam.gserviceaccount.com",
  ...
}
```

### 3. Share Google Sheet

**Critical**: Share your Google Sheet with the service account email!

1. Find `client_email` in your JSON file
2. Open your Google Sheet
3. Click **Share**
4. Add the `client_email` address
5. Grant **Editor** permissions

---

## 🔄 Keep Alive (24/7 Uptime)

Free tier on Render sleeps after 15 minutes of inactivity.

**Solution**: Use [UptimeRobot](https://uptimerobot.com) (free):

1. Create account at uptimerobot.com
2. Add new monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://your-app.onrender.com/health`
   - **Interval**: Every 5 minutes

✅ Your app will stay alive 24/7!

---

## 📁 Files Updated

- `Dockerfile` - Fixed apt-key deprecation issue
- `main.py` - Added environment variable support for credentials
- `requirements.txt` - Cleaned up dependencies
- `dashboard.py` - Web dashboard for monitoring

---

## 🔧 Troubleshooting

### "Failed to connect to Google Sheets"

1. Verify `GOOGLE_APPLICATION_CREDENTIALS_JSON` is set correctly
2. Ensure JSON is valid (use [JSONLint](https://jsonlint.com))
3. Make sure Google Sheet is shared with `client_email`

### Build fails: "apt-key: not found"

✅ Fixed! Make sure you push the updated `Dockerfile` to GitHub.

---

## 📊 Available Endpoints

- `/` - Dashboard (main interface)
- `/health` - Health check for monitoring
- `/api/status` - Current progress (JSON)
- `/api/start` - Start bot (POST)
- `/api/stop` - Stop bot (POST)

---

## 🌐 Deployment Steps

1. Push code to GitHub
2. Connect GitHub repo to Render
3. Set environment variables (see above)
4. Deploy! (Render auto-detects Dockerfile)
5. Set up UptimeRobot for 24/7 uptime

---

**For detailed Arabic guides, see:**
- `دليل_النشر_السريع_Render.md` - Quick guide
- `دليل_النشر_على_Render.md` - Comprehensive guide
- `RENDER_SETUP_GUIDE.md` - Environment variables setup

---

**Last Updated**: Fixed Dockerfile & added environment variable support ✅
