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
import subprocess
import sys

app = Flask(__name__)

PROGRESS_FILE = "progress.json"
bot_process = None
bot_thread = None

def get_progress():
    """قراءة ملف التقدم"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"last_row": 0, "total_processed": 0, "last_updated": None}

def get_logs():
    """قراءة آخر السجلات"""
    try:
        if not os.path.exists('/tmp/logs'):
            return "في انتظار بدء العملية..."
        
        log_files = [f for f in os.listdir('/tmp/logs') if 'Voter_Inquiry_Bot' in f]
        if not log_files:
            return "في انتظار بدء العملية..."
        
        latest_log = sorted(log_files)[-1]
        log_path = f'/tmp/logs/{latest_log}'
        
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return ''.join(lines[-50:])
    except Exception as e:
        return f"في انتظار بدء العملية...\n(Debug: {str(e)})"

def run_bot():
    """تشغيل البوت في thread منفصل"""
    global bot_process
    try:
        bot_process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        for line in bot_process.stdout:
            pass
    except Exception as e:
        print(f"خطأ في تشغيل البوت: {str(e)}")

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('dashboard.html')

@app.route('/api/status')
def status():
    """API لجلب الحالة الحالية"""
    progress = get_progress()
    logs = get_logs()
    
    global bot_process
    is_running = bot_process is not None and bot_process.poll() is None
    
    return jsonify({
        'progress': progress,
        'logs': logs,
        'timestamp': datetime.now().isoformat(),
        'bot_running': is_running
    })

@app.route('/api/start', methods=['POST'])
def start_bot():
    """بدء تشغيل البوت"""
    global bot_thread, bot_process
    
    if bot_process and bot_process.poll() is None:
        return jsonify({
            'success': False,
            'message': 'البوت يعمل بالفعل'
        })
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    return jsonify({
        'success': True,
        'message': 'تم بدء البوت بنجاح'
    })

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """إيقاف البوت"""
    global bot_process
    
    if bot_process and bot_process.poll() is None:
        bot_process.terminate()
        bot_process.wait(timeout=5)
        return jsonify({
            'success': True,
            'message': 'تم إيقاف البوت'
        })
    
    return jsonify({
        'success': False,
        'message': 'البوت غير مشغل'
    })

@app.route('/api/reset', methods=['POST'])
def reset_progress():
    """إعادة تعيين التقدم"""
    try:
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
        return jsonify({
            'success': True,
            'message': 'تم إعادة تعيين التقدم بنجاح. يمكنك الآن بدء العملية من جديد.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ في إعادة التعيين: {str(e)}'
        })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
