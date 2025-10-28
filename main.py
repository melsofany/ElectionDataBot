#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة استعلام بيانات الناخبين من الهيئة العليا للانتخابات
تقوم بقراءة الأرقام القومية من Google Sheets والاستعلام عنها تلقائياً
"""

import os
import json
import time
import gspread
from google.oauth2.service_account import Credentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# استيراد وحدة الاتصال بـ Google Sheets عبر Replit
try:
    from google_sheets_connector import get_google_sheets_client
    USE_REPLIT_CONNECTOR = True
except ImportError:
    USE_REPLIT_CONNECTOR = False

# إعدادات الملفات
PROGRESS_FILE = "progress.json"
SPREADSHEET_ID = "1-rCGPx6vyEMm3zmR7ks3xZh63XcJk4ks78e5e9jfuyo"
SOURCE_SHEET = "Voters"
RESULTS_SHEET = "نتائج_الاستعلام"
INQUIRY_URL = "https://www.elections.eg/inquiry"

# الحد الأقصى للصفوف
MAX_ROWS = 80000


class VoterInquiryBot:
    """بوت الاستعلام عن بيانات الناخبين"""
    
    def __init__(self):
        self.gc = None
        self.spreadsheet = None
        self.driver = None
        self.progress = self.load_progress()
        
    def load_progress(self):
        """تحميل التقدم السابق"""
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"last_row": 0, "total_processed": 0, "last_updated": None}
    
    def save_progress(self):
        """حفظ التقدم الحالي"""
        self.progress["last_updated"] = datetime.now().isoformat()
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def connect_to_sheets(self):
        """الاتصال بـ Google Sheets"""
        print("جاري الاتصال بـ Google Sheets...")
        
        # محاولة استخدام Replit Connector أولاً
        if USE_REPLIT_CONNECTOR:
            try:
                print("  استخدام Replit Google Sheets Connector...")
                self.gc = get_google_sheets_client()
                self.spreadsheet = self.gc.open_by_key(SPREADSHEET_ID)
                print("✓ تم الاتصال بنجاح عبر Replit Connector")
                return
            except Exception as e:
                print(f"  تحذير: فشل الاتصال عبر Replit Connector: {str(e)}")
                print("  محاولة استخدام ملف credentials.json...")
        
        # الطريقة التقليدية: البحث عن ملف credentials
        creds_paths = [
            "credentials.json",
            "service_account.json",
            os.path.expanduser("~/.config/gspread/service_account.json")
        ]
        
        creds_file = None
        for path in creds_paths:
            if os.path.exists(path):
                creds_file = path
                break
        
        if not creds_file:
            raise FileNotFoundError(
                "لم يتم العثور على طريقة للاتصال بـ Google Sheets\n"
                "الرجاء:\n"
                "1. إعداد Google Sheets integration في Replit (مفضل)\n"
                "   أو\n"
                "2. وضع ملف credentials.json من Google Cloud Console"
            )
        
        # تعريف الصلاحيات المطلوبة
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # المصادقة
        credentials = Credentials.from_service_account_file(creds_file, scopes=scope)
        self.gc = gspread.authorize(credentials)
        
        # فتح الملف
        self.spreadsheet = self.gc.open_by_key(SPREADSHEET_ID)
        print("✓ تم الاتصال بنجاح عبر credentials.json")
    
    def setup_selenium(self):
        """إعداد Selenium WebDriver"""
        print("جاري إعداد المتصفح...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--lang=ar')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # محاولة استخدام ChromeDriver المثبت من النظام
        import shutil
        chromedriver_path = shutil.which('chromedriver')
        chromium_path = shutil.which('chromium') or shutil.which('chromium-browser')
        
        if chromium_path:
            chrome_options.binary_location = chromium_path
            print(f"  استخدام Chromium من: {chromium_path}")
        
        if chromedriver_path:
            print(f"  استخدام ChromeDriver من: {chromedriver_path}")
            service = Service(executable_path=chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            print("  تحميل ChromeDriver تلقائياً...")
            self.driver = webdriver.Chrome(options=chrome_options)
        
        print("✓ تم إعداد المتصفح بنجاح")
    
    def get_voters_data(self):
        """قراءة البيانات من ورقة Voters"""
        print(f"جاري قراءة البيانات من ورقة {SOURCE_SHEET}...")
        
        try:
            worksheet = self.spreadsheet.worksheet(SOURCE_SHEET)
        except gspread.exceptions.WorksheetNotFound:
            raise Exception(f"لم يتم العثور على ورقة باسم '{SOURCE_SHEET}' في الملف")
        
        # قراءة جميع البيانات دفعة واحدة للحصول على العدد الفعلي للصفوف
        all_data = worksheet.get_all_values()
        
        if len(all_data) < 2:
            raise Exception("الورقة فارغة أو لا تحتوي على بيانات")
        
        # تنظيف البيانات وإنشاء القائمة
        data = []
        for row_idx in range(1, min(len(all_data), MAX_ROWS + 1)):  # نبدأ من الصف 2 (index 1)
            row = all_data[row_idx]
            
            # استخراج الرقم القومي من العمود B (index 1)
            nat_id = row[1] if len(row) > 1 else ""
            nat_id_str = str(nat_id).strip() if nat_id else ""
            
            # استخراج الاسم من العمود C (index 2) إذا كان موجوداً
            name = row[2] if len(row) > 2 else ""
            name_str = str(name).strip() if name else ""
            
            # إضافة الصف إذا كان الرقم القومي موجوداً
            if nat_id_str:
                data.append({
                    'row_number': row_idx + 1,  # +1 لأن Excel/Sheets يبدأ من 1
                    'national_id': nat_id_str,
                    'name': name_str
                })
        
        print(f"✓ تم العثور على {len(data)} رقم قومي من إجمالي {len(all_data) - 1} صف")
        return data
    
    def query_election_data(self, national_id):
        """الاستعلام عن بيانات الناخب من موقع الهيئة"""
        try:
            # الذهاب لصفحة الاستعلام
            self.driver.get(INQUIRY_URL)
            time.sleep(3)
            
            # الانتقال إلى iframe الذي يحتوي على نموذج الاستعلام
            wait = WebDriverWait(self.driver, 15)
            try:
                # البحث عن iframe
                iframe = wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "iframe"))
                )
                self.driver.switch_to.frame(iframe)
                time.sleep(2)
            except:
                # في حالة عدم وجود iframe، نستمر بدون تبديل
                pass
            
            # البحث عن حقل الرقم القومي بطرق متعددة
            input_field = None
            
            # محاولة العثور على حقل الإدخال بطرق مختلفة
            try:
                input_field = wait.until(
                    EC.presence_of_element_located((By.NAME, "nationalId"))
                )
            except:
                try:
                    input_field = wait.until(
                        EC.presence_of_element_located((By.ID, "nationalId"))
                    )
                except:
                    input_field = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
                    )
            
            input_field.clear()
            input_field.send_keys(national_id)
            
            # البحث عن زر الاستعلام
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            except:
                try:
                    submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'استعلام')]")
                except:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "button")
            
            submit_button.click()
            
            # انتظار النتائج
            time.sleep(4)
            
            # استخراج البيانات من الصفحة
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            page_text = soup.get_text()
            
            result = {
                'مركز_الانتخاب': '',
                'العنوان': '',
                'رقم_اللجنة_الفرعية': '',
                'الرقم_في_الكشوف': '',
                'status': 'unknown',
                'error_message': ''
            }
            
            # التحقق من وجود رسائل خطأ
            error_keywords = ['غير موجود', 'خطأ', 'غير صحيح', 'لا يوجد', 'invalid', 'error', 'not found']
            if any(keyword in page_text.lower() for keyword in error_keywords):
                result['status'] = 'error'
                result['error_message'] = 'الرقم القومي غير موجود أو غير صحيح'
                return result
            
            # التحقق من Captcha
            if 'captcha' in page_text.lower() or 'robot' in page_text.lower():
                result['status'] = 'error'
                result['error_message'] = 'تم اكتشاف Captcha - يرجى المحاولة لاحقاً'
                return result
            
            # محاولة استخراج البيانات باستخدام عدة طرق
            # الطريقة 1: البحث النصي
            for line in page_text.split('\n'):
                line = line.strip()
                if 'مركز' in line and 'انتخاب' in line:
                    result['مركز_الانتخاب'] = line.replace('مركزك الإنتخابي:', '').replace('مركز الانتخاب:', '').strip()
                elif 'عنوان' in line and result['العنوان'] == '':
                    result['العنوان'] = line.replace('العنوان:', '').strip()
                elif 'لجنة' in line and 'فرعية' in line:
                    result['رقم_اللجنة_الفرعية'] = line.replace('رقم اللجنة الفرعية:', '').strip()
                elif 'كشوف' in line or 'رقمك' in line:
                    result['الرقم_في_الكشوف'] = line.replace('رقمك في الكشوف الانتخابية:', '').replace('رقمك في الكشوف:', '').strip()
            
            # التحقق من وجود أي بيانات
            if any([result['مركز_الانتخاب'], result['العنوان'], 
                    result['رقم_اللجنة_الفرعية'], result['الرقم_في_الكشوف']]):
                result['status'] = 'success'
            else:
                result['status'] = 'no_data'
                result['error_message'] = 'لم يتم العثور على بيانات - قد يحتاج الكود للتحديث حسب هيكل الموقع'
            
            # العودة للصفحة الرئيسية (الخروج من iframe)
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            
            return result
            
        except Exception as e:
            # التأكد من العودة للصفحة الرئيسية في حالة الخطأ
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            
            return {
                'مركز_الانتخاب': '',
                'العنوان': '',
                'رقم_اللجنة_الفرعية': '',
                'الرقم_في_الكشوف': '',
                'status': 'error',
                'error_message': f'خطأ في الاتصال: {str(e)}'
            }
    
    def create_results_sheet(self):
        """إنشاء ورقة النتائج إذا لم تكن موجودة"""
        try:
            worksheet = self.spreadsheet.worksheet(RESULTS_SHEET)
            print(f"ورقة '{RESULTS_SHEET}' موجودة بالفعل")
        except gspread.exceptions.WorksheetNotFound:
            print(f"جاري إنشاء ورقة جديدة باسم '{RESULTS_SHEET}'...")
            worksheet = self.spreadsheet.add_worksheet(
                title=RESULTS_SHEET,
                rows=MAX_ROWS + 10,
                cols=8
            )
            
            # إضافة العناوين
            headers = [
                'الاسم',
                'الرقم القومي',
                'مركز الانتخاب',
                'العنوان',
                'رقم اللجنة الفرعية',
                'الرقم في الكشوف',
                'الحالة',
                'ملاحظات'
            ]
            worksheet.update(values=[headers], range_name='A1:H1')
            print("✓ تم إنشاء الورقة بنجاح")
        
        return worksheet
    
    def write_result(self, worksheet, row_number, name, national_id, result):
        """كتابة نتيجة واحدة في الشيت"""
        data = [
            name,
            national_id,
            result.get('مركز_الانتخاب', ''),
            result.get('العنوان', ''),
            result.get('رقم_اللجنة_الفرعية', ''),
            result.get('الرقم_في_الكشوف', ''),
            result.get('status', ''),
            result.get('error_message', '')
        ]
        
        # الكتابة في الصف المناسب (نضيف 1 للعناوين)
        cell_range = f'A{row_number}:H{row_number}'
        worksheet.update(values=[data], range_name=cell_range)
    
    def run(self):
        """تشغيل البوت الرئيسي"""
        print("\n" + "="*60)
        print("بوت الاستعلام عن بيانات الناخبين")
        print("="*60 + "\n")
        
        try:
            # الاتصال بـ Google Sheets
            self.connect_to_sheets()
            
            # قراءة البيانات
            voters_data = self.get_voters_data()
            
            # تصفية البيانات التي لم تتم معالجتها بعد
            start_row = self.progress['last_row']
            remaining_data = [v for v in voters_data if v['row_number'] > start_row]
            
            if not remaining_data:
                print("✓ تمت معالجة جميع البيانات بالفعل!")
                return
            
            print(f"\nسيتم معالجة {len(remaining_data)} صف")
            print(f"البدء من الصف رقم {remaining_data[0]['row_number']}\n")
            
            # إعداد المتصفح
            self.setup_selenium()
            
            # إنشاء/فتح ورقة النتائج
            results_sheet = self.create_results_sheet()
            
            # معالجة كل صف
            for idx, voter in enumerate(remaining_data, 1):
                print(f"\n[{idx}/{len(remaining_data)}] معالجة: {voter['name']} - {voter['national_id']}")
                
                # الاستعلام عن البيانات
                result = self.query_election_data(voter['national_id'])
                
                # كتابة النتيجة
                result_row = voter['row_number']
                self.write_result(
                    results_sheet,
                    result_row,
                    voter['name'],
                    voter['national_id'],
                    result
                )
                
                # تحديث التقدم
                self.progress['last_row'] = voter['row_number']
                self.progress['total_processed'] += 1
                self.save_progress()
                
                if result['status'] == 'success':
                    print(f"  ✓ تم بنجاح - المركز: {result.get('مركز_الانتخاب', 'غير متوفر')}")
                else:
                    print(f"  ✗ خطأ: {result.get('error_message', 'غير معروف')}")
                
                # انتظار قصير بين الطلبات
                time.sleep(2)
                
                # عرض التقدم كل 10 صفوف
                if idx % 10 == 0:
                    print(f"\n{'='*40}")
                    print(f"التقدم: {idx}/{len(remaining_data)} ({idx/len(remaining_data)*100:.1f}%)")
                    print(f"{'='*40}\n")
            
            print("\n" + "="*60)
            print("✓ اكتملت المعالجة بنجاح!")
            print(f"تم معالجة {self.progress['total_processed']} صف إجمالي")
            print("="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n⚠ تم إيقاف البرنامج من قبل المستخدم")
            print(f"تم حفظ التقدم: آخر صف معالج هو {self.progress['last_row']}")
            print("يمكنك تشغيل البرنامج مرة أخرى للمتابعة من حيث توقفت\n")
            
        except Exception as e:
            print(f"\n✗ خطأ: {str(e)}")
            print(f"تم حفظ التقدم: آخر صف معالج هو {self.progress['last_row']}")
            raise
            
        finally:
            # إغلاق المتصفح
            if self.driver:
                self.driver.quit()
                print("تم إغلاق المتصفح")


def main():
    """النقطة الرئيسية للتشغيل"""
    bot = VoterInquiryBot()
    bot.run()


if __name__ == "__main__":
    main()
