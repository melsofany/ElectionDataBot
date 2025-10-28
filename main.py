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
                # البحث عن iframe الاستعلام الصحيح (وليس iframe الإعلانات)
                # محاولة 1: البحث عن iframe يحتوي على 'Inquiry' أو 'inquiry' في src
                iframe_found = False
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                print(f"  وجدت {len(iframes)} إطار iframe")
                
                for idx, iframe in enumerate(iframes):
                    try:
                        src = iframe.get_attribute('src') or ''
                        print(f"  iframe {idx}: src={src[:100] if src else 'no src'}")
                        
                        # البحث عن iframe الاستعلام
                        if 'inquiry' in src.lower() or 'gadget' in src.lower():
                            print(f"  ✓ تم العثور على iframe الاستعلام: {src[:100]}")
                            self.driver.switch_to.frame(iframe)
                            iframe_found = True
                            time.sleep(2)
                            break
                    except:
                        continue
                
                # إذا لم نجد iframe بناءً على src، نحاول البحث عن iframe يحتوي على حقل الرقم القومي
                if not iframe_found and len(iframes) > 0:
                    print("  محاولة البحث عن iframe من خلال وجود حقل الرقم القومي...")
                    for idx, iframe in enumerate(iframes):
                        try:
                            self.driver.switch_to.default_content()
                            self.driver.switch_to.frame(iframe)
                            
                            # محاولة العثور على حقل الرقم القومي
                            try:
                                input_field = self.driver.find_element(By.NAME, "nationalId")
                                print(f"  ✓ وجدت حقل الرقم القومي في iframe {idx}")
                                iframe_found = True
                                time.sleep(2)
                                break
                            except:
                                try:
                                    input_field = self.driver.find_element(By.ID, "nationalId")
                                    print(f"  ✓ وجدت حقل الرقم القومي في iframe {idx}")
                                    iframe_found = True
                                    time.sleep(2)
                                    break
                                except:
                                    self.driver.switch_to.default_content()
                                    continue
                        except:
                            continue
                
                if not iframe_found:
                    print("  تحذير: لم يتم العثور على iframe مناسب، المتابعة بدون تبديل")
                    self.driver.switch_to.default_content()
                    
            except Exception as e:
                print(f"  تحذير: خطأ في البحث عن iframe: {str(e)}")
                self.driver.switch_to.default_content()
            
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
            
            # البحث عن زر الاستعلام بطرق متعددة
            submit_button = None
            button_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.XPATH, "//button[contains(text(), 'استعلام')]"),
                (By.XPATH, "//input[@value='استعلام']"),
                (By.XPATH, "//a[contains(text(), 'استعلام')]"),
                (By.CSS_SELECTOR, "button"),
                (By.CSS_SELECTOR, "input[type='button']"),
                (By.TAG_NAME, "button"),
            ]
            
            for selector_type, selector_value in button_selectors:
                try:
                    submit_button = self.driver.find_element(selector_type, selector_value)
                    if submit_button:
                        break
                except:
                    continue
            
            if submit_button:
                submit_button.click()
            else:
                # إذا لم نجد زر، نحاول إرسال النموذج مباشرة
                from selenium.webdriver.common.keys import Keys
                input_field.send_keys(Keys.RETURN)
            
            # انتظار النتائج - انتظار أطول للتأكد من تحميل البيانات
            time.sleep(5)
            
            result = {
                'مركز_الانتخاب': '',
                'العنوان': '',
                'رقم_اللجنة_الفرعية': '',
                'الرقم_في_الكشوف': '',
                'status': 'unknown',
                'error_message': ''
            }
            
            # استخراج البيانات من الصفحة باستخدام BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            page_text = soup.get_text()
            
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
            
            # الطريقة الجديدة: استخراج البيانات من العناصر المحددة بـ IDs
            print("  محاولة استخراج البيانات من العناصر المحددة...")
            try:
                # انتظار ظهور نتائج الاستعلام
                wait = WebDriverWait(self.driver, 10)
                
                # المحاولة 1: استخراج باستخدام IDs المحددة
                selectors_map = {
                    'مركز_الانتخاب': ['centerName', 'center-name', 'votingCenter', 'voting-center', 'المركز'],
                    'العنوان': ['address', 'centerAddress', 'center-address', 'العنوان'],
                    'رقم_اللجنة_الفرعية': ['committeeNumber', 'committee-number', 'subCommittee', 'اللجنة'],
                    'الرقم_في_الكشوف': ['orderNumber', 'order-number', 'listNumber', 'الرقم']
                }
                
                for field_name, possible_ids in selectors_map.items():
                    for selector_id in possible_ids:
                        try:
                            # محاولة بـ ID
                            element = self.driver.find_element(By.ID, selector_id)
                            value = element.text.strip()
                            if value and len(value) > 0:
                                result[field_name] = value
                                print(f"  ✓ وجدت {field_name} من ID '{selector_id}': {value}")
                                break
                        except:
                            try:
                                # محاولة بـ class name
                                element = self.driver.find_element(By.CLASS_NAME, selector_id)
                                value = element.text.strip()
                                if value and len(value) > 0:
                                    result[field_name] = value
                                    print(f"  ✓ وجدت {field_name} من CLASS '{selector_id}': {value}")
                                    break
                            except:
                                continue
                
                # إذا وجدنا أي بيانات، نعتبر الاستخراج ناجحاً
                if any([result['مركز_الانتخاب'], result['العنوان'], 
                       result['رقم_اللجنة_الفرعية'], result['الرقم_في_الكشوف']]):
                    print("  ✓ تم استخراج البيانات بنجاح من العناصر المحددة")
            except Exception as e:
                print(f"  تحذير: خطأ في الاستخراج من العناصر المحددة: {str(e)}")
            
            # الطريقة 1: استخراج البيانات من جدول HTML
            try:
                # انتظار ظهور الجدول مع النتائج
                wait = WebDriverWait(self.driver, 10)
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, "//table//td[contains(text(), 'مركز')]")))
                except:
                    pass  # في حالة عدم وجود النتائج
                
                # البحث عن جميع صفوف الجدول
                table_rows = self.driver.find_elements(By.TAG_NAME, "tr")
                
                for row in table_rows:
                    try:
                        # الحصول على جميع الخلايا في الصف (td و th)
                        cells = row.find_elements(By.CSS_SELECTOR, "th, td")
                        
                        if len(cells) >= 2:
                            # الخلية الأولى = التسمية، الخلية الأخيرة = القيمة
                            label_cell = cells[0].text.strip()
                            value_cell = cells[-1].text.strip()
                            
                            # استخراج المركز الانتخابي
                            if 'مركز' in label_cell and 'انتخاب' in label_cell:
                                if value_cell and len(value_cell) > 2:
                                    result['مركز_الانتخاب'] = value_cell
                                    print(f"  ✓ وجدت المركز الانتخابي: {value_cell}")
                            
                            # استخراج العنوان
                            elif 'عنوان' in label_cell:
                                if value_cell and len(value_cell) > 5:
                                    result['العنوان'] = value_cell
                                    print(f"  ✓ وجدت العنوان: {value_cell}")
                            
                            # استخراج رقم اللجنة الفرعية
                            elif 'لجنة' in label_cell and 'فرعية' in label_cell:
                                if value_cell:
                                    result['رقم_اللجنة_الفرعية'] = value_cell
                                    print(f"  ✓ وجدت رقم اللجنة: {value_cell}")
                            
                            # استخراج الرقم في الكشوف
                            elif 'رقمك' in label_cell or ('كشوف' in label_cell and 'انتخابية' in label_cell):
                                if value_cell:
                                    result['الرقم_في_الكشوف'] = value_cell
                                    print(f"  ✓ وجدت الرقم في الكشوف: {value_cell}")
                    except Exception as row_error:
                        continue
                
                # إذا لم نجد البيانات في الجدول، نبحث في العناصر بطريقة مختلفة
                if not result['مركز_الانتخاب']:
                    # استراتيجية جديدة: ابحث عن عنصر "العنوان" أولاً، ثم احصل على العنصر السابق له (المركز الانتخابي)
                    try:
                        address_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'عنوان') or contains(text(), 'العنوان')]")
                        
                        for addr_elem in address_elements:
                            addr_text = addr_elem.text.strip()
                            
                            # تأكد أن هذا هو عنصر التسمية وليس القيمة
                            if 'عنوان' in addr_text.lower() and len(addr_text) < 50:
                                try:
                                    # محاولة الحصول على العنصر السابق (المركز الانتخابي)
                                    prev_elem = addr_elem.find_element(By.XPATH, "preceding-sibling::*[1]")
                                    if prev_elem:
                                        prev_text = prev_elem.text.strip()
                                        if prev_text and len(prev_text) > 2 and not result['مركز_الانتخاب']:
                                            result['مركز_الانتخاب'] = prev_text
                                            print(f"  ✓ وجدت المركز الانتخابي من العنصر السابق للعنوان: {prev_text}")
                                    
                                    # الحصول على العنوان من العنصر التالي
                                    next_elem = addr_elem.find_element(By.XPATH, "following-sibling::*[1]")
                                    if next_elem and not result['العنوان']:
                                        addr_value = next_elem.text.strip()
                                        if addr_value and len(addr_value) > 5:
                                            result['العنوان'] = addr_value
                                            print(f"  ✓ وجدت العنوان: {addr_value}")
                                    
                                    # إذا وجدنا البيانات، نوقف البحث
                                    if result['مركز_الانتخاب'] and result['العنوان']:
                                        break
                                except Exception as sibling_error:
                                    continue
                    except Exception as addr_error:
                        print(f"  تحذير: خطأ في البحث عن العنوان: {str(addr_error)}")
                    
                    # الطريقة القديمة كاحتياطي
                    if not result['مركز_الانتخاب']:
                        elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'مركز') or contains(text(), 'المركز') or contains(text(), 'لجنة') or contains(text(), 'عنوان') or contains(text(), 'كشوف')]")
                        
                        for element in elements:
                            element_text = element.text.strip()
                            parent_text = element.find_element(By.XPATH, "..").text.strip() if element else ""
                            
                            # محاولة استخراج المركز الانتخابي
                            if ('مركز' in element_text.lower() and 'انتخاب' in element_text.lower()) or 'المركز' in element_text:
                                # محاولة الحصول على القيمة من النص الكامل
                                full_text = parent_text if parent_text else element_text
                                for label in ['مركزك الإنتخابي:', 'مركزك الانتخابي:', 'المركز الانتخابي:', 'مركز الانتخاب:']:
                                    if label in full_text:
                                        result['مركز_الانتخاب'] = full_text.replace(label, '').strip()
                                        break
                                
                                # إذا لم نجد القيمة، نحاول الحصول على العنصر التالي
                                if not result['مركز_الانتخاب']:
                                    try:
                                        next_elem = element.find_element(By.XPATH, "following-sibling::*[1]")
                                        if next_elem and next_elem.text.strip():
                                            result['مركز_الانتخاب'] = next_elem.text.strip()
                                    except:
                                        pass
                            
                            # استخراج العنوان
                            if 'عنوان' in element_text.lower() and not result['العنوان']:
                                full_text = parent_text if parent_text else element_text
                                for label in ['العنوان:', 'عنوان اللجنة:', 'عنوان المركز:']:
                                    if label in full_text:
                                        result['العنوان'] = full_text.replace(label, '').strip()
                                        break
                                
                                if not result['العنوان']:
                                    try:
                                        next_elem = element.find_element(By.XPATH, "following-sibling::*[1]")
                                        if next_elem and next_elem.text.strip():
                                            result['العنوان'] = next_elem.text.strip()
                                    except:
                                        pass
                        
                        # استخراج رقم اللجنة
                        if 'لجنة' in element_text.lower() and 'فرعية' in element_text.lower():
                            full_text = parent_text if parent_text else element_text
                            for label in ['رقم اللجنة الفرعية:', 'اللجنة الفرعية:', 'لجنة فرعية رقم:']:
                                if label in full_text:
                                    result['رقم_اللجنة_الفرعية'] = full_text.replace(label, '').strip()
                                    break
                            
                            if not result['رقم_اللجنة_الفرعية']:
                                try:
                                    next_elem = element.find_element(By.XPATH, "following-sibling::*[1]")
                                    if next_elem and next_elem.text.strip():
                                        result['رقم_اللجنة_الفرعية'] = next_elem.text.strip()
                                except:
                                    pass
                        
                        # استخراج الرقم في الكشوف
                        if 'كشوف' in element_text.lower() or ('رقمك' in element_text.lower() and 'كشوف' in parent_text.lower()):
                            full_text = parent_text if parent_text else element_text
                            for label in ['رقمك في الكشوف الانتخابية:', 'رقمك في الكشوف:', 'الرقم في الكشوف:']:
                                if label in full_text:
                                    result['الرقم_في_الكشوف'] = full_text.replace(label, '').strip()
                                    break
                            
                            if not result['الرقم_في_الكشوف']:
                                try:
                                    next_elem = element.find_element(By.XPATH, "following-sibling::*[1]")
                                    if next_elem and next_elem.text.strip():
                                        result['الرقم_في_الكشوف'] = next_elem.text.strip()
                                except:
                                    pass
            except Exception as e:
                print(f"  تحذير: خطأ في الاستخراج باستخدام Selenium: {str(e)}")
            
            # الطريقة 2: البحث في جدول HTML باستخدام BeautifulSoup (كنسخة احتياطية)
            if not any([result['مركز_الانتخاب'], result['العنوان'], result['رقم_اللجنة_الفرعية'], result['الرقم_في_الكشوف']]):
                # البحث عن جميع صفوف الجدول باستخدام BeautifulSoup
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    
                    for row in rows:
                        cells = row.find_all('td')
                        
                        if len(cells) >= 2:
                            # الخلية الأولى = التسمية، الخلية الأخيرة = القيمة
                            label_text = cells[0].get_text(strip=True)
                            value_text = cells[-1].get_text(strip=True)
                            
                            # استخراج المركز الانتخابي
                            if 'مركز' in label_text and ('انتخاب' in label_text or 'إنتخاب' in label_text):
                                if value_text and len(value_text) > 2:
                                    result['مركز_الانتخاب'] = value_text
                                    print(f"  ✓ استخراج المركز من BeautifulSoup: {value_text}")
                            
                            # استخراج العنوان
                            elif 'عنوان' in label_text:
                                if value_text and len(value_text) > 5:
                                    result['العنوان'] = value_text
                            
                            # استخراج رقم اللجنة الفرعية
                            elif 'لجنة' in label_text and 'فرعية' in label_text:
                                if value_text:
                                    result['رقم_اللجنة_الفرعية'] = value_text
                            
                            # استخراج الرقم في الكشوف
                            elif 'رقمك' in label_text or ('كشوف' in label_text and 'انتخابية' in label_text):
                                if value_text:
                                    result['الرقم_في_الكشوف'] = value_text
                
                # إذا لم نجد البيانات من الجدول، نبحث في جميع العناصر
                if not result['مركز_الانتخاب']:
                    all_elements = soup.find_all(['div', 'span', 'p', 'td', 'th', 'label'])
                    
                    for elem in all_elements:
                        text = elem.get_text(strip=True)
                        
                        if 'مركز' in text and ('انتخاب' in text or 'إنتخاب' in text):
                            cleaned = text
                            for label in ['مركزك الإنتخابي:', 'مركزك الانتخابي:', 'المركز الانتخابي:', 'مركز الانتخاب:']:
                                cleaned = cleaned.replace(label, '')
                            cleaned = cleaned.strip()
                            if cleaned and len(cleaned) > 2:
                                result['مركز_الانتخاب'] = cleaned
                        
                        elif 'عنوان' in text and not result['العنوان']:
                            cleaned = text.replace('العنوان:', '').replace('عنوان اللجنة:', '').strip()
                            if cleaned and len(cleaned) > 5:
                                result['العنوان'] = cleaned
                        
                        elif 'لجنة' in text and 'فرعية' in text:
                            cleaned = text.replace('رقم اللجنة الفرعية:', '').replace('اللجنة الفرعية:', '').strip()
                            if cleaned and len(cleaned) > 0:
                                result['رقم_اللجنة_الفرعية'] = cleaned
                        
                        elif 'كشوف' in text or 'رقمك' in text:
                            cleaned = text.replace('رقمك في الكشوف الانتخابية:', '').replace('رقمك في الكشوف:', '').replace('الرقم في الكشوف:', '').strip()
                            if cleaned and len(cleaned) > 0:
                                result['الرقم_في_الكشوف'] = cleaned
            
            # التحقق من وجود أي بيانات
            if any([result['مركز_الانتخاب'], result['العنوان'], 
                    result['رقم_اللجنة_الفرعية'], result['الرقم_في_الكشوف']]):
                result['status'] = 'success'
                print(f"  ✓ تم استخراج: المركز={result['مركز_الانتخاب'][:30] if result['مركز_الانتخاب'] else 'غير متوفر'}")
            else:
                result['status'] = 'no_data'
                result['error_message'] = 'لم يتم العثور على بيانات - قد يحتاج الكود للتحديث حسب هيكل الموقع'
                
                # حفظ screenshot للمساعدة في التصحيح
                try:
                    screenshot_path = f"debug_screenshot_{national_id}.png"
                    self.driver.save_screenshot(screenshot_path)
                    print(f"  تم حفظ screenshot في: {screenshot_path}")
                except Exception as ss_error:
                    print(f"  تحذير: فشل حفظ screenshot: {str(ss_error)}")
            
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
