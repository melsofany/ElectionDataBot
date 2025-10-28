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
        # محاولة قراءة ملف سجل البوت
        bot_log_file = "bot_output.log"
        
        if os.path.exists(bot_log_file):
            with open(bot_log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    # إرجاع آخر 100 سطر
                    return ''.join(lines[-100:])
        
        # إذا لم يوجد ملف السجل، التحقق من وجود progress
        if os.path.exists(PROGRESS_FILE):
            progress = get_progress()
            if progress.get('total_processed', 0) > 0:
                return f"✓ البوت يعمل...\n✓ تمت معالجة {progress['total_processed']} صف\n\nللمزيد من التفاصيل، شغّل البوت مرة أخرى..."
        
        return "📋 في انتظار بدء العملية...\n\nاضغط على زر 'بدء العملية' للبدء في معالجة الأرقام القومية"
        
    except Exception as e:
        return f"⏳ في انتظار بدء العملية...\n\n(للمطورين: {str(e)})"

def run_bot():
    """تشغيل البوت في thread منفصل"""
    global bot_process
    try:
        # فتح ملف لحفظ السجلات
        log_file_path = "bot_output.log"
        
        with open(log_file_path, 'w', encoding='utf-8') as log_file:
            bot_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1  # Line buffered
            )
            
            # قراءة وكتابة السجلات سطر بسطر
            for line in bot_process.stdout:
                log_file.write(line)
                log_file.flush()  # تأكد من الكتابة الفورية
                print(line, end='')  # طباعة في الكونسول أيضاً
                
    except Exception as e:
        error_msg = f"خطأ في تشغيل البوت: {str(e)}\n"
        print(error_msg)
        # كتابة الخطأ في ملف السجل
        with open("bot_output.log", 'a', encoding='utf-8') as f:
            f.write(error_msg)

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
