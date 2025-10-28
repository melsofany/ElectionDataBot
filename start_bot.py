#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل بوت الاستعلام
"""

import sys
import traceback

if __name__ == "__main__":
    try:
        print("=" * 70)
        print("🗳️  بوت الاستعلام عن بيانات الناخبين من الهيئة العليا للانتخابات")
        print("=" * 70)
        print()
        
        # استيراد وتشغيل البوت
        from main import VoterInquiryBot
        
        bot = VoterInquiryBot()
        
        # الاتصال بـ Google Sheets
        bot.connect_to_sheets()
        
        # قراءة البيانات
        voters_data = bot.get_voters_data()
        
        if not voters_data:
            print("⚠️ لا توجد بيانات للمعالجة")
            sys.exit(0)
        
        print(f"\n📊 سيتم معالجة {len(voters_data)} صف")
        print()
        
        # إعداد Selenium
        bot.setup_selenium()
        
        # تحضير ورقة النتائج
        bot.prepare_results_sheet()
        
        # بدء المعالجة
        print("\n" + "=" * 70)
        print("🚀 بدء الاستعلام عن البيانات...")
        print("=" * 70)
        print()
        
        bot.process_voters(voters_data)
        
        # إغلاق المتصفح
        if bot.driver:
            bot.driver.quit()
        
        print("\n" + "=" * 70)
        print("✅ اكتملت المعالجة بنجاح!")
        print("=" * 70)
        print(f"\n📁 النتائج متوفرة في Google Sheet - ورقة: نتائج_الاستعلام")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⏸️  تم إيقاف البرنامج بواسطة المستخدم")
        print("💾 التقدم محفوظ - يمكنك تشغيل البرنامج مرة أخرى للمتابعة")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n\n❌ حدث خطأ: {str(e)}")
        print("\nتفاصيل الخطأ:")
        traceback.print_exc()
        sys.exit(1)
