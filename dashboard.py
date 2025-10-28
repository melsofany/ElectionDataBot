#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
لوحة تحكم لعرض التقدم والنتائج في الوقت الفعلي
"""

import os
import json
import time
from flask import Flask, render_template, jsonify
from datetime import datetime
import threading

app = Flask(__name__)

PROGRESS_FILE = "progress.json"

def get_progress():
    """قراءة ملف التقدم"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"last_row": 0, "total_processed": 0, "last_updated": None}

def get_logs():
    """قراءة آخر السجلات"""
    log_files = [f for f in os.listdir('/tmp/logs') if 'Voter_Inquiry_Bot' in f]
    if not log_files:
        return "لا توجد سجلات بعد..."
    
    latest_log = sorted(log_files)[-1]
    log_path = f'/tmp/logs/{latest_log}'
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return ''.join(lines[-50:])  # آخر 50 سطر
    except:
        return "خطأ في قراءة السجلات"

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('dashboard.html')

@app.route('/api/status')
def status():
    """API لجلب الحالة الحالية"""
    progress = get_progress()
    logs = get_logs()
    
    return jsonify({
        'progress': progress,
        'logs': logs,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
