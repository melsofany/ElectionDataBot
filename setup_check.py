#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت للتحقق من جاهزية البيئة قبل تشغيل البوت
"""

import os
import sys

def check_credentials():
    """التحقق من وجود ملف credentials.json"""
    creds_paths = [
        "credentials.json",
        "service_account.json",
        os.path.expanduser("~/.config/gspread/service_account.json")
    ]
    
    for path in creds_paths:
        if os.path.exists(path):
            print(f"✓ تم العثور على ملف credentials في: {path}")
            return True
    
    return False

def main():
    print("\n" + "="*70)
    print("التحقق من جاهزية بيئة التشغيل")
    print("="*70 + "\n")
    
    all_checks_passed = True
    
    # التحقق من ملف credentials
    print("1. التحقق من ملف Google Credentials...")
    if check_credentials():
        print("   ✓ جاهز للاستخدام\n")
    else:
        print("   ✗ لم يتم العثور على credentials.json")
        print("\n   📋 الخطوات المطلوبة:")
        print("   1. اذهب إلى Google Cloud Console: https://console.cloud.google.com/")
        print("   2. أنشئ Service Account وفعّل Google Sheets API و Google Drive API")
        print("   3. حمّل ملف JSON credentials")
        print("   4. قم بتحميل الملف إلى هذا المشروع باسم 'credentials.json'")
        print("   5. شارك Google Sheet مع البريد الإلكتروني للـ Service Account\n")
        print("   📖 راجع ملف README.md للتعليمات التفصيلية\n")
        all_checks_passed = False
    
    # التحقق من المكتبات
    print("2. التحقق من المكتبات المطلوبة...")
    try:
        import gspread
        import selenium
        import bs4
        import pandas
        from google.oauth2.service_account import Credentials
        print("   ✓ جميع المكتبات مثبتة\n")
    except ImportError as e:
        print(f"   ✗ مكتبة مفقودة: {e}")
        print("   قم بتثبيت المكتبات باستخدام: uv add <package-name>\n")
        all_checks_passed = False
    
    # التحقق من ChromeDriver
    print("3. التحقق من ChromeDriver...")
    try:
        import shutil
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        chromedriver_path = shutil.which('chromedriver')
        chromium_path = shutil.which('chromium') or shutil.which('chromium-browser')
        
        if chromium_path:
            chrome_options.binary_location = chromium_path
        
        if chromedriver_path:
            service = Service(executable_path=chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        driver.quit()
        print("   ✓ ChromeDriver و Chromium جاهزان للاستخدام\n")
    except Exception as e:
        print(f"   ⚠ تحذير: {str(e)}")
        print("   قد يكون هناك مشكلة في إعداد المتصفح\n")
    
    print("="*70)
    if all_checks_passed:
        print("✅ البيئة جاهزة للتشغيل!")
        print("\nلتشغيل البوت، استخدم:")
        print("   python main.py")
    else:
        print("⚠️  يرجى إكمال الخطوات المطلوبة أعلاه")
        print("\nبعد إضافة credentials.json، يمكنك تشغيل:")
        print("   python main.py")
    print("="*70 + "\n")
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
