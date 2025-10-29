# 🚀 دليل النشر السريع على Render

## ✅ تم إصلاح المشكلة!

تم تحديث ملف `Dockerfile` لحل مشكلة `apt-key: not found` باستخدام الطريقة الحديثة لتثبيت Google Chrome و ChromeDriver.

---

## 📋 خطوات النشر (5 دقائق)

### 1️⃣ رفع المشروع على GitHub

```bash
# في Shell الخاص بـ Replit
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"

# إضافة GitHub remote
git remote add github https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# رفع الكود
git add .
git commit -m "Ready for Render deployment"
git push github main
```

**💡 ملاحظة**: إذا طلب كلمة مرور، استخدم [GitHub Personal Access Token](https://github.com/settings/tokens)

---

### 2️⃣ النشر على Render

1. سجل دخول في [Render.com](https://dashboard.render.com)
2. اضغط **New +** → **Web Service**
3. اختر **Build and deploy from a Git repository**
4. اضغط **Connect GitHub** ووافق على الصلاحيات
5. اختر المشروع من القائمة

**إعدادات Web Service:**
- **Name**: `egyptian-voter-bot` (أو أي اسم تريده)
- **Region**: `Frankfurt` (أو الأقرب لك)
- **Branch**: `main`
- **Runtime**: `Docker` ✅ (سيتم اكتشافه تلقائياً)
- **Plan**: `Free`

---

### 3️⃣ إضافة متغيرات البيئة (مهم جداً!)

في صفحة الإعدادات، اضغط **Environment** وأضف المتغيرات التالية:

| المفتاح | القيمة | ملاحظات |
|---------|--------|---------|
| `SPREADSHEET_ID` | `1-rCGPx6vyE...` | من رابط Google Sheet |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | `{محتوى ملف JSON كامل}` | **مهم!** انظر الشرح بالأسفل |
| `PYTHONUNBUFFERED` | `1` | لعرض السجلات مباشرة |
| `PORT` | `10000` | يستخدمه Render تلقائياً |

#### 📋 كيفية الحصول على المتغيرات:

**1. SPREADSHEET_ID:**
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
                                      ↑↑↑↑↑↑↑↑↑↑↑↑
                              انسخ هذا الجزء
```

**2. GOOGLE_APPLICATION_CREDENTIALS_JSON:**
1. افتح ملف `credentials.json` أو `service_account.json`
2. انسخ **المحتوى الكامل** للملف (يبدأ بـ `{` وينتهي بـ `}`)
3. الصق المحتوى كامل في قيمة المتغير

**مثال على شكل المحتوى:**
```json
{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "your-service-account@....iam.gserviceaccount.com",
  ...
}
```

⚠️ **ملاحظة**: تأكد من مشاركة Google Sheet مع البريد الإلكتروني `client_email` الموجود في ملف JSON!

---

### 4️⃣ 🔥 منع النوم بعد 15 دقيقة (مهم جداً!)

**المشكلة**: الخطة المجانية تُنام التطبيق بعد 15 دقيقة من عدم النشاط

**الحل**: استخدام **UptimeRobot** (مجاني 100%)

#### خطوات الإعداد:

1. سجل في [UptimeRobot.com](https://uptimerobot.com) (مجاناً)
2. اضغط **+ Add New Monitor**
3. أدخل المعلومات:

| الحقل | القيمة |
|-------|--------|
| **Monitor Type** | `HTTP(s)` |
| **Friendly Name** | `Voter Bot Keep-Alive` |
| **URL** | `https://your-app.onrender.com/health` |
| **Monitoring Interval** | `Every 5 minutes` |

4. اضغط **Create Monitor**

**✅ الآن التطبيق سيعمل 24/7 بدون توقف!**

---

### 5️⃣ التحقق من العمل

1. افتح رابط التطبيق: `https://your-app.onrender.com`
2. يجب أن ترى لوحة التحكم باللغة العربية
3. اضغط **▶️ بدء العملية** للاختبار
4. راقب السجلات في لوحة التحكم

---

## 🔧 حل المشاكل الشائعة

### ❌ Build fails: "apt-key: not found"
**✅ تم الإصلاح!** قم برفع ملف `Dockerfile` المحدث إلى GitHub:
```bash
git add Dockerfile
git commit -m "Fix apt-key issue"
git push github main
```

### ❌ لا يمكن الاتصال بـ Google Sheets
1. تحقق من `SPREADSHEET_ID` في متغيرات البيئة
2. تحقق من `GOOGLE_APPLICATION_CREDENTIALS_JSON`:
   - يجب أن يكون JSON صحيح (يبدأ بـ `{` وينتهي بـ `}`)
   - يحتوي على جميع المفاتيح المطلوبة
3. **مهم**: شارك Google Sheet مع البريد الإلكتروني `client_email` الموجود في ملف JSON:
   - افتح Google Sheet
   - اضغط **Share** (مشاركة)
   - أضف البريد الإلكتروني من ملف JSON (ينتهي بـ `.iam.gserviceaccount.com`)
   - امنحه صلاحية **Editor** (محرر)

### ❌ التطبيق ينام رغم UptimeRobot
- تأكد من الرابط صحيح: `/health` في آخر الرابط
- تأكد من الفترة: كل 5 دقائق (ليس أكثر)

---

## 📊 مراقبة التطبيق

### في Render Dashboard:
- **Logs** → لعرض سجلات التطبيق الكاملة
- **Metrics** → لمراقبة استهلاك الموارد
- **Events** → لرؤية تاريخ النشر والتحديثات

### Endpoints المهمة:
- `/` → لوحة التحكم الرئيسية
- `/health` → للتحقق من حالة التطبيق
- `/api/status` → معلومات التقدم (JSON)

---

## 🔄 التحديثات المستقبلية

عند تعديل الكود:

```bash
git add .
git commit -m "وصف التحديث"
git push github main
```

**Render سيعيد النشر تلقائياً في 3-5 دقائق!** 🚀

---

## 💰 ملاحظات الخطة المجانية

### ✅ الإيجابيات:
- 750 ساعة شهرياً (كافية للعمل 24/7)
- بناء مجاني
- SSL مجاني
- نطاق فرعي مجاني

### ⚠️ القيود:
- ينام بعد 15 دقيقة (حل: UptimeRobot ✅)
- بطء عند الاستيقاظ (30-60 ثانية)
- 512 MB RAM فقط

### 💎 الترقية ($7/شهر):
- لا ينام أبداً
- أداء أسرع
- 512 MB → 2 GB RAM

---

## 🎉 تهانينا!

تطبيقك الآن على Render ويعمل 24/7! 🎊

### الروابط المهمة:
- **لوحة التحكم**: `https://your-app.onrender.com`
- **Health Check**: `https://your-app.onrender.com/health`
- **Render Dashboard**: [dashboard.render.com](https://dashboard.render.com)
- **UptimeRobot**: [uptimerobot.com/dashboard](https://uptimerobot.com/dashboard)

---

**آخر تحديث**: تم إصلاح مشكلة `apt-key` ✅
