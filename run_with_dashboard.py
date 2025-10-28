#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل البوت مع لوحة التحكم في نفس الوقت
"""

import threading
import time
import subprocess
import sys

def run_bot():
    """تشغيل البوت في thread منفصل"""
    time.sleep(3)  # انتظار تشغيل الـ dashboard أولاً
    print("🤖 تشغيل البوت...")
    subprocess.run([sys.executable, "main.py"])

def run_dashboard():
    """تشغيل لوحة التحكم"""
    print("📊 تشغيل لوحة التحكم...")
    subprocess.run([sys.executable, "dashboard.py"])

if __name__ == "__main__":
    # تشغيل البوت في خلفية
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # تشغيل لوحة التحكم (في المقدمة)
    run_dashboard()
