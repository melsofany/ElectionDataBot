# 🚀 إعداد المتغيرات البيئية على Render

## المتغيرات المطلوبة

عند النشر على Render، يجب إضافة المتغيرات التالية في **Environment Variables**:

### 1. SPREADSHEET_ID
معرّف Google Sheet الخاص بك.

**كيفية الحصول عليه:**
```
https://docs.google.com/spreadsheets/d/1-rCGPx6vyEMm3zmR7ks3xZh63XcJk4ks78e5e9jfuyo/edit
                                      ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                                      هذا هو SPREADSHEET_ID
```

### 2. GOOGLE_APPLICATION_CREDENTIALS_JSON ⭐ (الأهم)

محتوى ملف Google Service Account JSON **كاملاً**.

**الخطوات:**

1. **احصل على ملف Service Account من Google Cloud:**
   - افتح [Google Cloud Console](https://console.cloud.google.com)
   - اذهب إلى **IAM & Admin** → **Service Accounts**
   - أنشئ Service Account جديد أو استخدم موجود
   - اضغط على **Keys** → **Add Key** → **Create New Key**
   - اختر **JSON** وحمّل الملف

2. **افتح الملف وانسخ محتواه:**
   
   الملف يبدو كالتالي:
   ```json
   {
     "type": "service_account",
     "project_id": "your-project-12345",
     "private_key_id": "abc123...",
     "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBg...",
     "client_email": "your-bot@your-project.iam.gserviceaccount.com",
     "client_id": "123456789",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "https://www.googleapis.com/..."
   }
   ```

3. **في Render Dashboard:**
   - افتح Web Service الخاص بك
   - اذهب إلى **Environment**
   - اضغط **Add Environment Variable**
   - **Key**: `GOOGLE_APPLICATION_CREDENTIALS_JSON`
   - **Value**: **الصق محتوى الملف كاملاً** (من `{` إلى `}`)

⚠️ **مهم جداً**: انسخ JSON كاملاً بما فيه الأقواس `{` و `}`

### 3. PYTHONUNBUFFERED
لعرض السجلات مباشرة في Render.

**القيمة**: `1`

### 4. PORT (اختياري)
Render يعيّنه تلقائياً، لكن يمكنك تحديده.

**القيمة الافتراضية**: `10000`

---

## ✅ التحقق من الإعداد الصحيح

### خطوة إضافية مهمة: مشاركة Google Sheet

1. افتح Google Sheet الخاص بك
2. اضغط على زر **Share** (مشاركة)
3. أضف البريد الإلكتروني من ملف JSON:
   - ابحث عن `"client_email"` في ملف JSON
   - انسخ القيمة (مثل: `your-bot@your-project.iam.gserviceaccount.com`)
   - أضفها في خانة المشاركة
4. امنحه صلاحية **Editor** (محرر)

---

## 🎯 مثال كامل للمتغيرات

```
SPREADSHEET_ID=1-rCGPx6vyEMm3zmR7ks3xZh63XcJk4ks78e5e9jfuyo

GOOGLE_APPLICATION_CREDENTIALS_JSON={
  "type": "service_account",
  "project_id": "voters-bot-123",
  "private_key_id": "abc123def456...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBA...",
  "client_email": "voters-bot@voters-bot-123.iam.gserviceaccount.com",
  "client_id": "112233445566",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/..."
}

PYTHONUNBUFFERED=1

PORT=10000
```

---

## 🔧 استكشاف الأخطاء

### خطأ: "لم يتم العثور على طريقة للاتصال"

**الحل:**
1. تأكد من إضافة `GOOGLE_APPLICATION_CREDENTIALS_JSON` في متغيرات البيئة
2. تحقق من أن JSON صحيح (استخدم [JSONLint](https://jsonlint.com) للتحقق)
3. تأكد من نسخ المحتوى كاملاً من `{` إلى `}`

### خطأ: "Permission denied" أو "403 Forbidden"

**الحل:**
- شارك Google Sheet مع `client_email` الموجود في ملف JSON
- امنح صلاحية **Editor** (ليس Viewer)

---

## 📌 ملاحظات أمان

- ✅ **آمن**: وضع محتوى JSON في متغيرات البيئة على Render آمن ومشفر
- ⚠️ **لا تنشر**: لا ترفع ملف `credentials.json` إلى GitHub (موجود في `.gitignore`)
- 🔐 **الحفاظ على السرية**: لا تشارك محتوى JSON مع أحد

---

**آخر تحديث**: تم تحديث الكود ليقرأ من `GOOGLE_APPLICATION_CREDENTIALS_JSON` تلقائياً ✅
