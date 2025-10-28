#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وحدة الاتصال بـ Google Sheets عبر Replit Connector
"""

import os
import requests
import gspread
from google.oauth2.credentials import Credentials

def get_access_token():
    """الحصول على access token من Replit Connector"""
    hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
    
    if not hostname:
        raise Exception('REPLIT_CONNECTORS_HOSTNAME غير موجود في المتغيرات البيئية')
    
    # الحصول على X_REPLIT_TOKEN
    repl_identity = os.environ.get('REPL_IDENTITY')
    web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')
    
    if repl_identity:
        x_replit_token = f'repl {repl_identity}'
    elif web_repl_renewal:
        x_replit_token = f'depl {web_repl_renewal}'
    else:
        raise Exception('لم يتم العثور على REPL_IDENTITY أو WEB_REPL_RENEWAL')
    
    # طلب الاتصال
    url = f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-sheet'
    headers = {
        'Accept': 'application/json',
        'X_REPLIT_TOKEN': x_replit_token
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f'فشل الحصول على الاتصال: {response.status_code} - {response.text}')
        
        data = response.json()
        items = data.get('items', [])
        
        if not items:
            raise Exception('لم يتم العثور على اتصال Google Sheets. تأكد من إعداد التكامل في Replit.')
        
        connection = items[0]
        settings = connection.get('settings', {})
        
        # محاولة الحصول على access token من مواقع مختلفة
        access_token = (
            settings.get('access_token') or
            settings.get('oauth', {}).get('credentials', {}).get('access_token')
        )
        
        if not access_token:
            raise Exception('لم يتم العثور على access token في الاتصال')
        
        return access_token
    except requests.exceptions.RequestException as e:
        raise Exception(f'خطأ في الاتصال بـ Replit Connectors: {str(e)}')

def get_google_sheets_client():
    """إنشاء client لـ Google Sheets باستخدام Replit Connector"""
    try:
        access_token = get_access_token()
        
        # إنشاء Credentials باستخدام access token
        credentials = Credentials(token=access_token)
        
        # إنشاء gspread client
        gc = gspread.authorize(credentials)
        
        return gc
        
    except Exception as e:
        raise Exception(f'فشل الاتصال بـ Google Sheets: {str(e)}')

def test_connection():
    """اختبار الاتصال بـ Google Sheets"""
    try:
        gc = get_google_sheets_client()
        print("✓ تم الاتصال بـ Google Sheets بنجاح!")
        return True
    except Exception as e:
        print(f"✗ خطأ في الاتصال: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
