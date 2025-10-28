#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت اختبار لفحص هيكل موقع الانتخابات ومعرفة العناصر الموجودة
"""

import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# رقم قومي اختباري (يمكن تغييره)
TEST_NATIONAL_ID = "29012011234567"  # رقم اختباري - غيره لرقم حقيقي للاختبار

def test_website():
    print("=" * 60)
    print("فحص هيكل موقع الانتخابات")
    print("=" * 60)
    
    # إعداد Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--lang=ar')
    
    chromedriver_path = shutil.which('chromedriver')
    chromium_path = shutil.which('chromium') or shutil.which('chromium-browser')
    
    if chromium_path:
        chrome_options.binary_location = chromium_path
    
    if chromedriver_path:
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # الذهاب للصفحة
        print(f"\n1. فتح الصفحة: https://www.elections.eg/inquiry")
        driver.get("https://www.elections.eg/inquiry")
        time.sleep(3)
        
        # فحص iframes
        print("\n2. فحص iframes...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"   وجدت {len(iframes)} iframe")
        
        for idx, iframe in enumerate(iframes):
            src = iframe.get_attribute('src') or 'no src'
            id_attr = iframe.get_attribute('id') or 'no id'
            name_attr = iframe.get_attribute('name') or 'no name'
            print(f"   iframe {idx}: src={src[:80]}, id={id_attr}, name={name_attr}")
        
        # محاولة الدخول لكل iframe
        iframe_found = False
        for idx, iframe in enumerate(iframes):
            try:
                src = iframe.get_attribute('src') or ''
                if 'gadget' in src.lower() or 'inquiry' in src.lower():
                    print(f"\n3. الدخول إلى iframe {idx} ({src[:80]})")
                    driver.switch_to.frame(iframe)
                    iframe_found = True
                    time.sleep(2)
                    break
            except:
                continue
        
        if not iframe_found and len(iframes) > 0:
            print(f"\n3. محاولة الدخول إلى iframe 0")
            driver.switch_to.frame(iframes[0])
            time.sleep(2)
        
        # البحث عن حقل الرقم القومي
        print("\n4. البحث عن حقل الرقم القومي...")
        input_selectors = [
            ('name', 'nationalId'),
            ('id', 'nationalId'),
            ('id', 'national-id'),
            ('id', 'txtNationalId'),
            ('name', 'national_id'),
            ('css', 'input[type="text"]'),
            ('css', 'input[placeholder*="قومي"]'),
            ('css', 'input[placeholder*="رقم"]'),
        ]
        
        input_field = None
        for selector_type, selector_value in input_selectors:
            try:
                if selector_type == 'name':
                    input_field = driver.find_element(By.NAME, selector_value)
                elif selector_type == 'id':
                    input_field = driver.find_element(By.ID, selector_value)
                elif selector_type == 'css':
                    input_field = driver.find_element(By.CSS_SELECTOR, selector_value)
                
                if input_field:
                    print(f"   ✓ وجدت حقل الإدخال: {selector_type}={selector_value}")
                    break
            except:
                continue
        
        if not input_field:
            print("   ✗ لم أجد حقل الرقم القومي!")
            print("\n   جميع عناصر input في الصفحة:")
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                inp_type = inp.get_attribute('type') or 'no type'
                inp_id = inp.get_attribute('id') or 'no id'
                inp_name = inp.get_attribute('name') or 'no name'
                inp_placeholder = inp.get_attribute('placeholder') or 'no placeholder'
                print(f"      - type={inp_type}, id={inp_id}, name={inp_name}, placeholder={inp_placeholder}")
            driver.quit()
            return
        
        # إدخال الرقم القومي
        print(f"\n5. إدخال الرقم القومي: {TEST_NATIONAL_ID}")
        input_field.clear()
        input_field.send_keys(TEST_NATIONAL_ID)
        
        # البحث عن زر الاستعلام
        print("\n6. البحث عن زر الاستعلام...")
        button_selectors = [
            ('css', 'button[type="submit"]'),
            ('css', 'input[type="submit"]'),
            ('xpath', '//button[contains(text(), "استعلام")]'),
            ('xpath', '//input[@value="استعلام"]'),
            ('css', 'button'),
        ]
        
        submit_button = None
        for selector_type, selector_value in button_selectors:
            try:
                if selector_type == 'css':
                    submit_button = driver.find_element(By.CSS_SELECTOR, selector_value)
                elif selector_type == 'xpath':
                    submit_button = driver.find_element(By.XPATH, selector_value)
                
                if submit_button:
                    print(f"   ✓ وجدت زر الإرسال: {selector_type}={selector_value}")
                    break
            except:
                continue
        
        if submit_button:
            submit_button.click()
            print("   ✓ تم الضغط على زر الاستعلام")
        else:
            print("   محاولة إرسال النموذج بـ Enter")
            from selenium.webdriver.common.keys import Keys
            input_field.send_keys(Keys.RETURN)
        
        # الانتظار للنتائج
        print("\n7. انتظار النتائج (10 ثواني)...")
        time.sleep(10)
        
        # حفظ screenshot
        screenshot_path = "test_result_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"   ✓ تم حفظ screenshot: {screenshot_path}")
        
        # فحص HTML بعد النتائج
        print("\n8. فحص HTML للنتائج...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # البحث عن جداول
        tables = soup.find_all('table')
        print(f"   وجدت {len(tables)} جدول")
        
        if tables:
            for idx, table in enumerate(tables[:3]):  # أول 3 جداول فقط
                print(f"\n   جدول {idx}:")
                rows = table.find_all('tr')
                for row_idx, row in enumerate(rows[:10]):  # أول 10 صفوف
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        print(f"      صف {row_idx}: {' | '.join(cell_texts)}")
        
        # البحث عن divs بمعرفات محددة
        print("\n9. البحث عن divs/spans بمعرفات محددة...")
        possible_ids = [
            'centerName', 'center-name', 'votingCenter', 'voting-center',
            'address', 'centerAddress', 'center-address',
            'committeeNumber', 'committee-number', 'subCommittee',
            'orderNumber', 'order-number', 'listNumber'
        ]
        
        for element_id in possible_ids:
            try:
                element = driver.find_element(By.ID, element_id)
                print(f"   ✓ وجدت عنصر بـ ID={element_id}: {element.text[:50]}")
            except:
                pass
        
        # البحث عن نصوص عربية مميزة
        print("\n10. البحث عن نصوص عربية في الصفحة...")
        keywords = ['مركز', 'انتخاب', 'عنوان', 'لجنة', 'فرعية', 'كشوف']
        for keyword in keywords:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
            if elements:
                print(f"   وجدت {len(elements)} عنصر يحتوي على '{keyword}'")
                for elem in elements[:3]:  # أول 3 عناصر
                    tag = elem.tag_name
                    text = elem.text[:100]
                    print(f"      - <{tag}>: {text}")
        
        # طباعة جزء من HTML
        print("\n11. عينة من HTML بعد الإرسال:")
        print("=" * 60)
        body_text = soup.get_text()
        print(body_text[:2000])  # أول 2000 حرف
        print("=" * 60)
        
        # حفظ HTML كامل للفحص
        with open("test_result.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("\n✓ تم حفظ HTML الكامل في: test_result.html")
        
    except Exception as e:
        print(f"\n✗ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
        print("\n" + "=" * 60)
        print("انتهى الفحص")
        print("=" * 60)

if __name__ == "__main__":
    test_website()
