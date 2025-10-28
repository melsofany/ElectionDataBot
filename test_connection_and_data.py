#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار الاتصال بـ Google Sheets والتحقق من وجود البيانات
"""

import sys
from google_sheets_connector import get_google_sheets_client

SPREADSHEET_ID = "1-rCGPx6vyEMm3zmR7ks3xZh63XcJk4ks78e5e9jfuyo"
SOURCE_SHEET = "Voters"

def main():
    try:
        print("=" * 60)
        print("اختبار الاتصال بـ Google Sheets")
        print("=" * 60)
        
        # الاتصال بـ Google Sheets
        print("\n1️⃣ جاري الاتصال بـ Google Sheets...")
        gc = get_google_sheets_client()
        print("   ✓ تم الاتصال بنجاح!")
        
        # فتح الملف
        print(f"\n2️⃣ جاري فتح الملف (ID: {SPREADSHEET_ID})...")
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        print(f"   ✓ تم فتح الملف: {spreadsheet.title}")
        
        # التحقق من وجود ورقة Voters
        print(f"\n3️⃣ جاري البحث عن ورقة '{SOURCE_SHEET}'...")
        try:
            worksheet = spreadsheet.worksheet(SOURCE_SHEET)
            print(f"   ✓ تم العثور على الورقة!")
        except Exception as e:
            print(f"   ✗ لم يتم العثور على الورقة: {str(e)}")
            print("\n📋 الأوراق المتوفرة في الملف:")
            for idx, ws in enumerate(spreadsheet.worksheets(), 1):
                print(f"     {idx}. {ws.title}")
            sys.exit(1)
        
        # قراءة البيانات
        print(f"\n4️⃣ جاري قراءة البيانات...")
        all_data = worksheet.get_all_values()
        print(f"   ✓ عدد الصفوف: {len(all_data)}")
        
        if len(all_data) < 2:
            print("   ⚠️ الورقة فارغة أو تحتوي على صف واحد فقط (العناوين)")
            sys.exit(1)
        
        # عرض أول 5 صفوف كمثال
        print(f"\n5️⃣ عينة من البيانات (أول 5 صفوف):")
        for idx in range(min(5, len(all_data))):
            row = all_data[idx]
            col_b = row[1] if len(row) > 1 else ""
            col_c = row[2] if len(row) > 2 else ""
            print(f"     الصف {idx + 1}: العمود B = '{col_b}', العمود C = '{col_c}'")
        
        # إحصائيات
        print(f"\n6️⃣ إحصائيات البيانات:")
        rows_with_nat_id = 0
        for idx in range(1, len(all_data)):  # نبدأ من الصف 2 (تخطي العناوين)
            row = all_data[idx]
            nat_id = row[1] if len(row) > 1 else ""
            if nat_id and str(nat_id).strip():
                rows_with_nat_id += 1
        
        print(f"   - إجمالي الصفوف: {len(all_data) - 1}")
        print(f"   - صفوف تحتوي على أرقام قومية: {rows_with_nat_id}")
        print(f"   - صفوف فارغة: {len(all_data) - 1 - rows_with_nat_id}")
        
        print("\n" + "=" * 60)
        print("✅ الاختبار ناجح! البيانات جاهزة للمعالجة")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
