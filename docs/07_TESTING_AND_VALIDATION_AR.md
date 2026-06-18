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
يجب إنشاء هدف مصرح أولًا عبر Target Management، ثم تشغيل Nmap Basic باستخدام `target_id` فقط:

```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Localhost Nmap","target":"127.0.0.1","authorized":true,"scope_notes":"Localhost only"}'
```

```bash
curl -X POST http://localhost:8000/scans/nmap/basic \
  -H "Content-Type: application/json" \
  -d '{"target_id":1}'
```

## اختبار رفض authorized=false
يجب أن يرفض endpoint الفحص أي هدف مخزن غير مصرح قبل تشغيل Nmap:

```bash
curl -X POST http://localhost:8000/scans/nmap/basic \
  -H "Content-Type: application/json" \
  -d '{"target_id":2}'
```

النتيجة المتوقعة: HTTP 403 مع رسالة توضح أن الهدف غير مصرح للفحص.

## اختبار رفض CIDR/ranges
يتم رفض CIDR/ranges عند إضافة الهدف إلى Target Management قبل أن يصل إلى أي فحص:

```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Bad CIDR","target":"192.168.1.0/24","authorized":true}'
```

النتيجة المتوقعة: HTTP 400 وعدم تخزين الهدف أو تشغيل Nmap.

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

## اختبار Target Management

> هذه الاختبارات تخص المرحلة 1 فقط، ولا تشغل أي فحص أو أداة خارجية.

### إنشاء target صحيح 127.0.0.1
```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Localhost Test","target":"127.0.0.1","authorized":true,"scope_notes":"Local machine only"}'
```

### إنشاء target domain صحيح
```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Example Domain","target":"example.com","authorized":false,"scope_notes":"Documentation example domain"}'
```

### رفض CIDR
```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Bad CIDR","target":"192.168.1.0/24","authorized":true,"scope_notes":"Should be rejected"}'
```

النتيجة المتوقعة: HTTP 400 مع رسالة توضح أن CIDR غير مسموح في هذه النسخة.

### رفض wildcard
```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Bad Wildcard","target":"*.example.com","authorized":true,"scope_notes":"Should be rejected"}'
```

النتيجة المتوقعة: HTTP 400 مع رسالة توضح أن wildcards غير مسموحة.

### عرض كل الأهداف
```bash
curl http://localhost:8000/targets
```

### عرض target واحد
```bash
curl http://localhost:8000/targets/1
```

### تغيير authorized
```bash
curl -X PATCH http://localhost:8000/targets/1/authorization \
  -H "Content-Type: application/json" \
  -d '{"authorized":false}'
```

### حذف target
```bash
curl -X DELETE http://localhost:8000/targets/1
```

## اختبار المرحلة 2: Nmap Basic Scan

### فحص Python syntax
```bash
python3 -m compileall backend/app
```

### فحص عدم وجود أوامر خطرة
```bash
rg "shell=True|os.system|eval|exec" backend/app || true
```

### تشغيل السيرفر
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### فحص health
```bash
curl http://localhost:8000/health
```

### إنشاء target مصرح
```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Localhost Nmap","target":"127.0.0.1","authorized":true,"scope_notes":"Localhost Nmap test"}'
```

### تشغيل Nmap على target_id
```bash
curl -X POST http://localhost:8000/scans/nmap/basic \
  -H "Content-Type: application/json" \
  -d '{"target_id":1}'
```

### إنشاء target غير مصرح
```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Unauthorized Localhost","target":"127.0.0.1","authorized":false,"scope_notes":"Should be blocked"}'
```

### تجربة Nmap على target غير مصرح
```bash
curl -X POST http://localhost:8000/scans/nmap/basic \
  -H "Content-Type: application/json" \
  -d '{"target_id":2}'
```

### تجربة target_id غير موجود
```bash
curl -X POST http://localhost:8000/scans/nmap/basic \
  -H "Content-Type: application/json" \
  -d '{"target_id":99999}'
```

### التحقق من التقارير
```bash
find reports/nmap_basic -maxdepth 1 -type f
```

## اختبار المرحلة 0.4.0: Admin Web UI

### فتح واجهة الإدارة
```bash
curl http://localhost:8000/ui
```
النتيجة المتوقعة: إرجاع صفحة HTML تحتوي على `Cyber Lab Control Panel`.

### Check Health من الواجهة
افتح المتصفح على:

```text
http://localhost:8000/ui
```
ثم اضغط زر **Check Health**.

النتيجة المتوقعة: ظهور نتيجة `/health` وتحديث حالة Backend إلى `ok`.

### إضافة Target من الواجهة
من قسم **Add Target** أدخل بيانات مثل:

```text
name: Localhost UI
 target: 127.0.0.1
 authorized: true
 scope_notes: Local UI validation
```

ثم اضغط **Add Target**.

النتيجة المتوقعة: ظهور رسالة نجاح وتحديث جدول الأهداف تلقائيًا.

### التأكد من ظهوره في الجدول
بعد الإضافة، يجب أن يظهر الهدف في جدول **Targets** مع `id` و`target_type` و`authorized` و`created_at`.

### تغيير authorized
اضغط زر **Toggle Authorized** للهدف.

النتيجة المتوقعة: تتغير قيمة `authorized` في الجدول بعد إعادة التحميل.

### تشغيل Nmap على authorized target
تأكد أن الهدف `authorized=true` ثم اضغط **Run Nmap Basic**.

النتيجة المتوقعة: ظهور حالة loading ثم نتيجة الفحص في قسم **Nmap Result**.

### التأكد من ظهور report_file
بعد انتهاء الفحص يجب أن يظهر حقل `report_file` ضمن نتيجة Nmap.

### التأكد من منع Nmap على target غير مصرح
اجعل الهدف `authorized=false` من زر **Toggle Authorized**.

النتيجة المتوقعة: زر **Run Nmap Basic** يكون disabled ولا يمكن تشغيل Nmap من الواجهة على هذا الهدف.

### فحص عدم وجود shell=True أو أوامر خطرة
```bash
rg "shell=True|os.system|eval|exec" backend/app || true
```
