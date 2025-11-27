# بوت "كورسات مجانية ومدفوعة" - نشر على Render (FastAPI + webhook)

## خطوات جاهزة للنشر
1. انسخ الملفات إلى مستودع GitHub.
2. املأ ملف `.env` بالقيم الحقيقية (انظر `.env.example`).
3. على Render:
   - أنشئ Web Service وربطه بالمستودع.
   - اعداد Build command: `pip install -r requirements.txt`
   - اعداد Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - أضف متغيرات البيئة من `.env` في لوحة Render
4. شغّل الخدمة. Render ينشر التطبيق ويجعل `APP_URL` جاهز.
5. تأكد أن `APP_URL` هو نفس القيمة في `.env` ثم أعد النشر إذا عدلتها.

## ملاحظات
- تأكد من أن `DATABASE_URL` لقاعدة PostgreSQL صحيحة (يمكنك استخدام Render PostgreSQL).
- لتفعيل Webhook، الكود يقوم تلقائياً بوضع webhook عند التشغيل.
- الأدمن (ADMIN_ID) سيستقبل إشعارات الطلبات وعمليات الشحن.

## صيانة
- لتفعيل وضع الصيانة: اتصل بالأدمن وادع `maintenance.enable(reason)`
- لإيقاف: `maintenance.disable()`