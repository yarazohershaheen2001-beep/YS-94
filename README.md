# YS | 94 — Telegram Bot

> بوت تيليجرام احترافي لخدمات السوشيال ميديا مع لوحة تحكم إدارية كاملة.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-green)](https://docs.aiogram.dev)
[![Railway](https://img.shields.io/badge/Deploy-Railway-purple)](https://railway.app)

---

## ✨ المميزات

| الميزة | الوصف |
|--------|-------|
| 🔒 نظام الاشتراك الإجباري | يتحقق من اشتراك المستخدم في @shaheen_ys و @fi1_oo قبل الدخول |
| 🎬 شاشة ترحيب بالفيديو | فيديو ترحيب مع قائمة رئيسية |
| 📱 6 منصات | TikTok, Instagram, Telegram, Snapchat, Facebook, YouTube |
| 📦 30 باقة | 5 باقات لكل منصة بأسعار متدرجة |
| 💳 4 طرق دفع | Orange Money, ila bank, نجوم تيليجرام, PayPal |
| 📸 نظام الإيصالات | FSM يقبل الصور فقط ويرسلها للمشرف |
| ✅❌ موافقة المشرف | أزرار قبول/رفض مع إشعار فوري للمستخدم |
| 🛡️ لوحة تحكم إدارية | 8 أوامر شاملة للإحصاء والرسائل الجماعية |
| 🗄️ قاعدة بيانات SQLite | 3 جداول: users, orders, payments |
| 📋 سجل أخطاء | ملفات logs/ تلقائية مع دوران عند الامتلاء |

---

## 🗂️ هيكل المشروع

```
telegram-bot/
├── bot.py                  # نقطة الانطلاق — تسجيل الـ Routers وبدء التشغيل
├── config.py               # جميع الثوابت تُقرأ من .env
├── .env                    # المتغيرات الحساسة (لا ترفعه على GitHub)
├── requirements.txt        # المكتبات المطلوبة بإصداراتها
├── Procfile                # أمر تشغيل Railway
├── railway.json            # إعدادات Railway
│
├── database/
│   ├── __init__.py
│   └── db.py               # دوال SQLite لجداول users/orders/payments
│
├── handlers/
│   ├── __init__.py
│   ├── start.py            # /start + التحقق من الاشتراك
│   ├── menu.py             # التنقل بين الشاشات
│   ├── platforms.py        # اختيار المنصة والباقة
│   ├── payment.py          # اختيار الدفع + رفع الإيصال
│   └── admin.py            # أوامر الإدارة + أزرار القبول/الرفض
│
├── keyboards/
│   ├── __init__.py
│   ├── callbacks.py        # جميع كلاسات CallbackData
│   ├── main.py             # لوحات المفاتيح الرئيسية
│   └── packages.py         # لوحات باقات المنصات الست
│
├── states/
│   ├── __init__.py
│   ├── order.py            # OrderStates (FSM للطلبات)
│   └── admin.py            # AdminStates (FSM للرسائل الجماعية)
│
├── utils/
│   ├── __init__.py
│   ├── subscription.py     # check_subscription() — get_chat_member()
│   └── admin_filter.py     # IsAdmin() — فلتر التحقق من صلاحية المشرف
│
└── logs/                   # يُنشأ تلقائياً عند التشغيل
    ├── bot.log             # سجل عام (5MB دوار)
    └── errors.log          # أخطاء فقط (2MB دوار)
```

---

## ⚙️ الإعداد المحلي

### 1 — المتطلبات

- Python **3.11** أو أحدث
- `pip` محدَّث

### 2 — استنساخ المستودع

```bash
git clone https://github.com/<username>/<repo>.git
cd <repo>/telegram-bot
```

### 3 — إنشاء البيئة الافتراضية (اختياري لكن مُوصى به)

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 4 — تثبيت المكتبات

```bash
pip install -r requirements.txt
```

### 5 — إعداد ملف `.env`

افتح ملف `.env` الموجود في المجلد وأدخل القيم:

```env
# توكن البوت من @BotFather
BOT_TOKEN=123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ

# المعرف الرقمي لقناة الإدارة (يبدأ بـ -100)
ADMIN_CHANNEL_ID=-1001234567890

# معرفات المشرفين مفصولة بفاصلة
ADMIN_IDS=123456789,987654321

# قنوات الاشتراك الإجباري (القيم الافتراضية صحيحة)
SUPPORT_CHANNEL=@shaheen_ys
GIFT_CHANNEL=@fi1_oo
```

### 6 — تشغيل البوت

```bash
python bot.py
```

---

## 🛡️ متطلبات البوت في تيليجرام

| الشرط | السبب |
|-------|-------|
| البوت مشرف في `ADMIN_CHANNEL_ID` | لإرسال الإيصالات وقراءة ردود الأزرار |
| البوت عضو في `@shaheen_ys` | لاستخدام `get_chat_member()` للتحقق من الاشتراك |
| البوت عضو في `@fi1_oo` | نفس السبب |

---

## 🛡️ أوامر الإدارة

أضف معرّفك في `ADMIN_IDS` بملف `.env` للوصول إلى الأوامر التالية:

| الأمر | الوظيفة |
|-------|---------|
| `/admin` | لوحة التحكم مع إحصائيات سريعة |
| `/stats` | إحصائيات تفصيلية |
| `/users` | عدد المستخدمين المسجلين |
| `/orders` | آخر 20 طلب |
| `/pending` | الطلبات المعلقة |
| `/approved` | الطلبات المقبولة |
| `/rejected` | الطلبات المرفوضة |
| `/broadcast` | رسالة جماعية لجميع المستخدمين |
| `/helpadmin` | شرح كامل للأوامر |

---

## 🚀 النشر على Railway

### الطريقة الأولى — ربط GitHub مع Railway (مُوصى به)

**خطوة 1 — رفع المشروع إلى GitHub**

```bash
cd telegram-bot        # المجلد الذي يحتوي bot.py

git init
git add .
git commit -m "Initial commit — YS | 94 bot"
git branch -M main
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```

> ⚠️ **تأكد من إضافة `.env` في `.gitignore` حتى لا تُرفع بياناتك الحساسة:**
> ```
> echo ".env" >> .gitignore
> echo "database/" >> .gitignore
> echo "logs/" >> .gitignore
> git add .gitignore
> git commit -m "Add gitignore"
> git push
> ```

**خطوة 2 — إنشاء مشروع على Railway**

1. سجّل دخولك على [railway.app](https://railway.app)
2. اضغط **New Project → Deploy from GitHub repo**
3. اختر المستودع
4. Railway سيكتشف `Procfile` و `railway.json` تلقائياً

**خطوة 3 — إضافة المتغيرات البيئية**

في لوحة Railway اذهب إلى **Variables** وأضف:

```
BOT_TOKEN        = <توكن البوت>
ADMIN_CHANNEL_ID = <معرف القناة>
ADMIN_IDS        = <معرفات المشرفين>
SUPPORT_CHANNEL  = @shaheen_ys
GIFT_CHANNEL     = @fi1_oo
```

**خطوة 4 — تشغيل المشروع**

اضغط **Deploy** — سيبدأ البوت خلال ثوانٍ.

---

### الطريقة الثانية — Railway CLI

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

ثم أضف المتغيرات:

```bash
railway variables set BOT_TOKEN=<value>
railway variables set ADMIN_CHANNEL_ID=<value>
railway variables set ADMIN_IDS=<value>
```

---

## 🗄️ قاعدة البيانات

البيانات محفوظة في `database/orders.db` (SQLite).

| الجدول | المحتوى |
|--------|---------|
| `users` | معلومات كل مستخدم بدأ البوت |
| `orders` | تفاصيل كل طلب مع حالته |
| `payments` | سجل رفع الإيصالات مع معرّفات الصور |

---

## 📋 السجلات (Logs)

ينشئ البوت تلقائياً مجلد `logs/`:

- `logs/bot.log` — سجل كامل (حد 5MB، 3 نسخ احتياطية)
- `logs/errors.log` — الأخطاء فقط (حد 2MB، نسختان)

---

## 🤝 المساهمة

1. Fork المستودع
2. أنشئ فرعاً جديداً: `git checkout -b feature/new-feature`
3. ادفع التغييرات: `git push origin feature/new-feature`
4. افتح Pull Request

---

## 📄 الترخيص

MIT License — يمكنك الاستخدام والتعديل والتوزيع بحرية.
