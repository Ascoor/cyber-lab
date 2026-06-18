# حالة مشروع Cyber Lab Control Panel

## آخر حالة للمشروع
المشروع انتقل إلى `0.3.0 - Nmap Basic Scan`. أصبح Backend يحتوي على فحص Nmap Basic محدود ودفاعي مرتبط بالأهداف المخزنة في SQLite فقط، ولا يقبل target مباشر أو flags/options من المستخدم.

## ما تم إنجازه
- تحديث إصدار FastAPI إلى `0.3.0`.
- إضافة endpoint جديد: `POST /scans/nmap/basic`.
- إضافة موديل request للفحص يحتوي على `target_id` فقط.
- ربط فحص Nmap Basic بجدول `targets` عبر `get_target`.
- رفض `target_id` غير الموجود قبل أي فحص.
- رفض `authorized=false` قبل تشغيل Nmap.
- إعادة التحقق من الهدف المخزن عبر `target_validation.py` قبل التشغيل.
- تشغيل أمر ثابت فقط: `nmap -sV -T3 --top-ports 100 <target>`.
- استخدام `subprocess.run` بقائمة command وبدون `shell=True`.
- إضافة timeout واضح لمدة 180 ثانية.
- حفظ تقارير JSON داخل `reports/nmap_basic/` مع `target_id` وtimestamp.

## ما يعمل الآن
- endpoint `/` يعمل.
- endpoint `/health` يعمل.
- endpoints Target Management تعمل كما هي:
  - `POST /targets`
  - `GET /targets`
  - `GET /targets/{target_id}`
  - `PATCH /targets/{target_id}/authorization`
  - `DELETE /targets/{target_id}`
- endpoint `POST /scans/nmap/basic` يعمل باستخدام `target_id` فقط.
- يتم حفظ `stdout` و`stderr` و`command_used` و`started_at` و`finished_at` في تقرير الفحص.

## ما لم يتم تنفيذه بعد
- Web Security Baseline.
- SSL/TLS & Headers.
- Report builder موحد لكل أنواع الفحوصات.
- Audit Log.
- UI مرتبطة فعليًا بالـ backend.
- Job Queue للفحوصات الطويلة.
- Docker Compose جاهز للتشغيل.
- تكامل ZAP أو MobSF، وهي خارج نطاق المرحلة 2.

## الخطوة التالية المقترحة
تنفيذ المرحلة 3: Web Security Baseline بشكل دفاعي ومحدود، مع الاستمرار في الاعتماد على الأهداف المخزنة والمصرح بها فقط، وعدم قبول flags أو options مباشرة من المستخدم.

## آخر مراجعة
- التاريخ: 2026-06-18
- نتيجة المراجعة: تم تنفيذ Nmap Basic Scan محدود، مربوط بـ Target Management، ويحفظ تقارير داخل `reports/nmap_basic/` دون استخدام `shell=True`.

## قائمة أوامر تحقق سريعة
```bash
python3 -m compileall backend/app
rg "shell=True|os.system|eval|exec" backend/app || true
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/health
curl http://localhost:8000/targets
```
