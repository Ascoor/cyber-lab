# الاختبار والتحقق

## تشغيل السيرفر محليًا
من جذر المشروع:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

للتشغيل أثناء التطوير مع إعادة التحميل:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## اختبار endpoint الرئيسي
```bash
curl http://localhost:8000/
```

النتيجة المتوقعة حاليًا:
```json
{
  "status": "running",
  "message": "Cyber Lab Control Panel is ready"
}
```

## اختبار health
```bash
curl http://localhost:8000/health
```

النتيجة المتوقعة حاليًا:
```json
{
  "status": "ok"
}
```

## اختبار Nmap على 127.0.0.1
حاليًا ملف `backend/app/modules/nmap_scan.py` فارغ في المراجعة الحالية، لذلك لا يوجد endpoint موثق لفحص Nmap داخل الكود الحالي. عند تنفيذ المرحلة 2، يجب أن يكون الاختبار على هدف محلي واحد ومصرح مثل:

```bash
curl -X POST http://localhost:8000/scans/nmap/basic \
  -H "Content-Type: application/json" \
  -d '{"target":"127.0.0.1","authorized":true}'
```

## اختبار رفض authorized=false
عند تنفيذ أي endpoint فحص، يجب أن يرفض الطلب التالي قبل تشغيل أي أداة خارجية:

```bash
curl -X POST http://localhost:8000/scans/nmap/basic \
  -H "Content-Type: application/json" \
  -d '{"target":"127.0.0.1","authorized":false}'
```

النتيجة المتوقعة لاحقًا: HTTP 400 أو 403 مع رسالة توضح أن التصريح مطلوب.

## اختبار رفض CIDR/ranges
عند تنفيذ أي endpoint فحص في المراحل الأولى، يجب رفض CIDR مثل:

```bash
curl -X POST http://localhost:8000/scans/nmap/basic \
  -H "Content-Type: application/json" \
  -d '{"target":"192.168.1.0/24","authorized":true}'
```

النتيجة المتوقعة لاحقًا: رفض الطلب وعدم تشغيل Nmap.

## فحص Python syntax
```bash
python -m compileall backend/app
```

يجب تشغيله بعد أي تعديل على Python backend.

## أين تحفظ التقارير
- التقارير العامة: `reports/`.
- نتائج أو artifacts فحص مؤقتة: `scans/` عند الحاجة.
- السجلات: `logs/`.

## ملاحظات تحقق مهمة
- لا تفترض نجاح أي endpoint دون تشغيله فعليًا.
- إذا تعذر تشغيل السيرفر بسبب البيئة، وثق السبب بوضوح.
- كل فحص جديد يجب أن يختبر الحالة المسموحة والحالة المرفوضة.
