# 📘 دليل نشر بوت الاستعلام عن بيانات الناخبين على Render

## 🎯 نظرة عامة

هذا الدليل يشرح كيفية نشر بوت الاستعلام عن بيانات الناخبين على منصة **Render** مع ضمان عمله بشكل مستمر **24/7** دون توقف.

---

## ✅ المتطلبات الأساسية

1. **حساب على GitHub** - لرفع الكود
2. **حساب على Render.com** (مجاني) - [التسجيل هنا](https://render.com)
3. **Google Sheets** معد بالبيانات (ورقة "Voters" بالأرقام القومية)
4. **Google Service Account** لربط البوت بـ Google Sheets

---

## 📦 الخطوة 1: رفع المشروع على GitHub

### 1.1 إنشاء مستودع جديد على GitHub

1. افتح [GitHub](https://github.com) وسجل الدخول
2. اضغط على زر **"New Repository"** (مستودع جديد)
3. أدخل اسم المستودع مثل: `egyptian-voter-inquiry-bot`
4. اختر **Public** أو **Private**
5. اضغط **"Create repository"**

### 1.2 رفع الكود من Replit إلى GitHub

افتح **Shell** في Replit وقم بتنفيذ الأوامر التالية:

```bash
# إعداد Git إذا لم يكن معداً
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"

# إضافة GitHub كـ remote
git remote add github https://github.com/YOUR_USERNAME/egyptian-voter-inquiry-bot.git

# رفع الكود
git push github main
```

**ملاحظة**: إذا طلب منك كلمة المرور، استخدم **Personal Access Token** من [GitHub Settings](https://github.com/settings/tokens).

---

## 🚀 الخطوة 2: النشر على Render

### 2.1 إنشاء Web Service جديد

1. سجل الدخول إلى [Render Dashboard](https://dashboard.render.com)
2. اضغط على **"New +"** ← **"Web Service"**
3. اختر **"Build and deploy from a Git repository"**
4. اضغط **"Connect GitHub"** وامنح Render الصلاحيات
5. اختر مستودعك: `egyptian-voter-inquiry-bot`

### 2.2 ضبط الإعدادات

في صفحة إعداد الـ Web Service:

| الإعداد | القيمة |
|--------|--------|
| **Name** | `egyptian-voter-inquiry-bot` |
| **Region** | `Frankfurt` (أو أقرب منطقة لك) |
| **Branch** | `main` |
| **Runtime** | `Docker` |
| **Plan** | `Free` |

**ملاحظة**: Render سيكتشف تلقائياً ملف `Dockerfile` ويستخدمه للبناء.

### 2.3 إعداد متغيرات البيئة (Environment Variables)

اضغط على **"Environment"** ← **"Add Environment Variable"** وأضف المتغيرات التالية:

| المفتاح (Key) | القيمة (Value) | الوصف |
|--------------|---------------|-------|
| `SPREADSHEET_ID` | `1-rCGPx6vyE...` | معرّف Google Sheet الخاص بك |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | `{محتوى ملف JSON}` | **مهم!** محتوى ملف Service Account كامل |
| `PYTHONUNBUFFERED` | `1` | لعرض السجلات مباشرة |
| `PORT` | `10000` | المنفذ الذي يستخدمه Render |

**📌 الحصول على SPREADSHEET_ID**:
- افتح Google Sheet الخاص بك
- انسخ الرابط: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
- الـ `SPREADSHEET_ID` هو الجزء بين `/d/` و `/edit`

**📌 الحصول على GOOGLE_APPLICATION_CREDENTIALS_JSON**:
1. افتح ملف `credentials.json` أو `service_account.json` بمحرر نصوص
2. انسخ **المحتوى الكامل** للملف (من `{` إلى `}`)
3. الصق المحتوى في قيمة المتغير في Render

**مثال على المحتوى**:
```json
{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "your-bot@your-project.iam.gserviceaccount.com",
  ...
}
```

### 2.4 إعداد Google Service Account

**⚠️ خطوة مهمة جداً**: يجب مشاركة Google Sheet مع Service Account!

1. افتح ملف `credentials.json` (الذي وضعت محتواه في `GOOGLE_APPLICATION_CREDENTIALS_JSON`)
2. ابحث عن قيمة `"client_email"` في الملف
   - مثال: `"your-bot@your-project.iam.gserviceaccount.com"`
3. افتح Google Sheet الخاص بك
4. اضغط على زر **"Share"** (مشاركة) في الأعلى
5. أضف البريد الإلكتروني `client_email`
6. امنحه صلاحية **"Editor"** (محرر)
7. اضغط **"Send"** أو **"Done"**

✅ **الكود جاهز ولا يحتاج تعديل!** البرنامج يقرأ من المتغير البيئي تلقائياً

---

## 🎉 الخطوة 3: بدء النشر

1. اضغط على **"Create Web Service"**
2. Render سيبدأ في:
   - تحميل الكود من GitHub
   - بناء Docker Image (تثبيت Chrome + ChromeDriver)
   - تشغيل التطبيق

**⏱ التقدم المتوقع**:
- البناء: 5-10 دقائق (المرة الأولى)
- التشغيل: 1-2 دقيقة

3. بعد اكتمال النشر، ستحصل على رابط مثل:
   ```
   https://egyptian-voter-inquiry-bot.onrender.com
   ```

---

## 🔄 الخطوة 4: منع النوم بعد 15 دقيقة

### المشكلة
الخطة المجانية في Render تُنام التطبيق بعد **15 دقيقة** من عدم النشاط.

### ✅ الحل: استخدام UptimeRobot (مجاني)

**UptimeRobot** سيرسل طلب HTTP كل 5 دقائق لإبقاء التطبيق نشطاً.

#### 4.1 التسجيل في UptimeRobot

1. افتح [uptimerobot.com](https://uptimerobot.com)
2. سجل حساب مجاني
3. اضغط **"+ Add New Monitor"**

#### 4.2 إعداد المراقب (Monitor)

| الإعداد | القيمة |
|--------|--------|
| **Monitor Type** | HTTP(s) |
| **Friendly Name** | `Egyptian Voter Bot Keep-Alive` |
| **URL** | `https://your-app.onrender.com/health` |
| **Monitoring Interval** | `5 minutes` |

5. اضغط **"Create Monitor"**

**✅ الآن التطبيق سيظل نشطاً 24/7!**

---

## 📊 الخطوة 5: التحقق من عمل التطبيق

### 5.1 افتح لوحة التحكم

افتح الرابط: `https://your-app.onrender.com`

يجب أن ترى:
- ✅ لوحة تحكم البوت باللغة العربية
- ✅ أزرار: "بدء العملية"، "إيقاف"، "إعادة تعيين التقدم"
- ✅ إحصائيات: آخر صف معالج، إجمالي المعالج

### 5.2 اختبار البوت

1. اضغط على زر **"▶️ بدء العملية"**
2. شاهد السجلات تظهر في "📝 سجل العمليات"
3. تحقق من ظهور النتائج في ورقة "نتائج_الاستعلام" في Google Sheets

### 5.3 فحص السجلات

في Render Dashboard:
- اضغط على اسم الـ Web Service
- افتح تبويب **"Logs"**
- ستظهر جميع سجلات التطبيق والأخطاء

---

## 🔧 استكشاف الأخطاء

### ❌ المشكلة: "Address already in use"
**الحل**: تأكد من أن `dashboard.py` يستخدم `PORT` من متغير البيئة:
```python
port = int(os.environ.get('PORT', 10000))
```

### ❌ المشكلة: Chrome/ChromeDriver لا يعمل
**الحل**: تأكد من استخدام الإعدادات الصحيحة في `main.py`:
```python
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
```

### ❌ المشكلة: لا يمكن الاتصال بـ Google Sheets
**الحل**: 
1. تحقق من `GOOGLE_APPLICATION_CREDENTIALS_JSON` في متغيرات البيئة
2. تأكد من منح Service Account صلاحيات الوصول للـ Sheet
3. شارك الـ Sheet مع البريد الإلكتروني للـ Service Account

### ❌ المشكلة: التطبيق ينام بعد 15 دقيقة
**الحل**: تأكد من:
1. إعداد UptimeRobot بشكل صحيح
2. الرابط صحيح: `https://your-app.onrender.com/health`
3. الفترة: كل 5 دقائق

---

## 🎊 مبروك! 🎊

تطبيقك الآن يعمل على Render بشكل مستمر 24/7!

### 📍 الروابط المهمة

| الخدمة | الرابط |
|--------|--------|
| **لوحة التحكم** | `https://your-app.onrender.com` |
| **Health Check** | `https://your-app.onrender.com/health` |
| **Render Dashboard** | [dashboard.render.com](https://dashboard.render.com) |
| **UptimeRobot** | [uptimerobot.com](https://uptimerobot.com) |

---

## 🔄 التحديثات المستقبلية

عند تعديل الكود:

```bash
# في Replit Shell
git add .
git commit -m "وصف التحديث"
git push github main
```

Render سيكتشف التغييرات تلقائياً ويعيد النشر! 🚀

---

## 💰 ملاحظات حول الخطة المجانية

### حدود Render Free Tier:
- ✅ **750 ساعة/شهر** (كافية للعمل 24/7 = ~720 ساعة)
- ✅ بناء مجاني (Build time مجاني)
- ⚠️ ينام بعد 15 دقيقة (لكن UptimeRobot يحل هذا!)
- ⚠️ تشغيل بطيء بعد النوم (30-60 ثانية للاستيقاظ)

### الترقية إلى Paid Plan ($7/شهر):
- ⚡ لا ينام أبداً
- ⚡ أداء أسرع
- ⚡ موارد أكثر

---

## 📞 الدعم الفني

إذا واجهت أي مشكلة:
1. راجع **"استكشاف الأخطاء"** أعلاه
2. افحص السجلات في Render Dashboard
3. تحقق من متغيرات البيئة

---

**تم إعداد هذا الدليل بعناية لضمان نشر ناجح! 🎯**
