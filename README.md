# Cyber Lab Control Panel

## 0.6.2 - Network Connectivity Diagnostics + Documentation Cleanup

- إضافة endpoint تشخيصي ثابت `GET /diagnostics/network` للتحقق من اتصال البيئة بمصادر RDAP وWayback المستخدمة في Domain Archive Intelligence.
- التشخيص لا يقبل target أو URL من المستخدم ولا يشغل shell ولا يحفظ تقرير scan.
- واجهة `/ui` تعرض قسم Network Connectivity Diagnostics لتسهيل تمييز مشاكل الشبكة عن مشاكل الموديول.
- تنظيف التوثيق الحالي ليعكس نسخة `0.6.2` وحالة موديول Domain Archive بعد Archive Fetch Lite.
- لا تزال Nmap Basic وDomain Archive تعملان عبر `target_id` فقط للأهداف المخزنة والمصرح بها.


Cyber Lab Control Panel هو مشروع محلي داخل WSL2 Ubuntu لتنظيم فحوصات أمن سيبراني دفاعية ومصرح بها فقط. يعتمد Backend الحالي على FastAPI، ويهدف إلى بناء لوحة تحكم قابلة للتوسع مع توثيق عربي واضح للنطاق، المنهجية، التقارير، والمراجعة المستمرة.

## تحذير قانوني واضح

استخدم هذا المشروع فقط على أنظمة تملكها أو لديك إذن مكتوب لاختبارها. لا تستخدمه لفحص أهداف عامة، شبكات خارج النطاق، أشخاص، أرقام هاتف، حسابات، كلمات مرور، أو أي نشاط استغلالي. أي فحص لاحق يجب أن يكون محدودًا، دفاعيًا، موثقًا، ويتطلب تصريحًا صريحًا مثل `authorized=true`.

## الحالة الحالية

- Backend يعمل عبر FastAPI.
- endpoint `/` موجود للتحقق العام.
- endpoint `/health` موجود للتحقق السريع.
- endpoint `/diagnostics/network` موجود لتشخيص اتصال البيئة بمصادر RDAP وWayback الثابتة دون فحص أهداف المستخدم.
- نظام Target Management مضاف لإدارة الأهداف محليًا قبل أي فحص.
- SQLite يستخدم ملف `data/cyber_lab.db` محليًا ويُنشئ جدول `targets` تلقائيًا عند تشغيل التطبيق.
- ملفات موديولات الفحص موجودة داخل `backend/app/modules/`، ويعمل منها حاليًا Nmap Basic فقط وفق قواعد محدودة.
- ملف `backend/app/modules/nmap_scan.py` ينفذ Nmap Basic بأمر ثابت عبر `target_id` للأهداف المصرح بها فقط.
- واجهة Admin Web UI متاحة عبر `/ui` لإدارة الأهداف وتشغيل Nmap Basic وDomain Archive من الجدول فقط، وتشغيل تشخيص اتصال الشبكة من زر مستقل.
- ملف `docker-compose.yml` فارغ حاليًا، وسيتم ضبطه في مرحلة Docker Compose لاحقًا.

## طريقة التشغيل الحالية

### 1. تثبيت المتطلبات

```bash
python -m pip install -r backend/requirements.txt
```

### 2. تشغيل Backend

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

أثناء التطوير يمكن استخدام:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. اختبار endpoints الحالية

```bash
curl http://localhost:8000/
```

```bash
curl http://localhost:8000/health
```

## أمثلة curl الحالية

### فحص الصفحة الرئيسية

```bash
curl http://localhost:8000/
```

النتيجة المتوقعة:

```json
{
  "status": "running",
  "message": "Cyber Lab Control Panel is ready"
}
```

### فحص الصحة

```bash
curl http://localhost:8000/health
```

النتيجة المتوقعة:

```json
{
  "status": "ok"
}
```

## التوثيق العربي الأساسي

التوثيق العربي داخل `docs/` هو المرجع الأساسي للتطوير القادم. يجب قراءة هذه الملفات قبل إضافة أي ميزة أو موديول فحص:

- [نظرة عامة على المشروع](docs/00_PROJECT_OVERVIEW_AR.md)
- [خريطة الطريق](docs/01_ROADMAP_AR.md)
- [سياسة الأمان والنطاق](docs/02_SECURITY_AND_SCOPE_POLICY_AR.md)
- [منهجية التطوير](docs/03_DEVELOPMENT_METHODOLOGY_AR.md)
- [قائمة المراجعة](docs/04_REVIEW_CHECKLIST_AR.md)
- [سجل التغييرات](docs/05_CHANGELOG_AR.md)
- [سجل القرارات المعمارية](docs/06_DECISION_LOG_AR.md)
- [الاختبار والتحقق](docs/07_TESTING_AND_VALIDATION_AR.md)
- [قالب مواصفة موديول](docs/08_MODULE_SPECIFICATION_TEMPLATE_AR.md)
- [معيار التقارير](docs/09_REPORTING_STANDARD_AR.md)

ملفات حالة ومراجعة سريعة:

- [حالة المشروع](PROJECT_STATUS_AR.md)
- [مراجعة بعد كل تعديل](REVIEW_AFTER_EACH_CHANGE_AR.md)

## خريطة الطريق المختصرة

1. المرحلة 0: التأسيس والتوثيق.
2. المرحلة 1: Target Management.
3. المرحلة 2: Nmap Basic Scan مضبوط.
4. المرحلة 3: Web Security Baseline.
5. المرحلة 4: SSL/TLS & Headers.
6. المرحلة 5: Reports.
7. المرحلة 6: Simple UI / Admin Web UI.
8. المرحلة 7: Job Queue.
9. المرحلة 8: MobSF Integration.
10. المرحلة 9: Audit Log.
11. المرحلة 10: Packaging with Docker Compose.

## قواعد تطوير مختصرة

- لا تضف ميزة خارج المرحلة الحالية في Roadmap.
- لا تستخدم `shell=True`.
- لا تسمح بتمرير أوامر أو flags مباشرة من المستخدم.
- ارفض `authorized=false` قبل أي فحص.
- ارفض CIDR/ranges في النسخة الأولى عند الفحص.
- أضف timeout لأي أداة خارجية.
- احفظ تقريرًا لكل فحص عند تنفيذ موديولات الفحص.
- حدث `docs/05_CHANGELOG_AR.md` بعد كل تعديل مهم.
- حدث `docs/06_DECISION_LOG_AR.md` عند وجود قرار معماري أو أمني.

## Docker Compose

`docker-compose.yml` موجود لكنه فارغ حاليًا، ولا يعتبر طريقة تشغيل جاهزة. سيتم ضبطه في المرحلة 10 فقط بعد استقرار Backend والتقارير والسجلات.

## Target Management - المرحلة 1

تمت إضافة Target Management كمرحلة مستقلة لإدارة الأهداف المصرح بها قبل تشغيل أي فحص. هذه المرحلة لا تشغل Nmap أو ZAP أو MobSF أو أي أداة خارجية، ولا تضيف أي وظيفة فحص جديدة.

### التخزين المحلي

تستخدم المرحلة الحالية SQLite بسيطًا داخل:

```text
data/cyber_lab.db
```

يتم إنشاء جدول `targets` تلقائيًا عند تشغيل FastAPI ويحتوي على الحقول الأساسية التالية:

- `id`
- `name`
- `target`
- `target_type`
- `authorized`
- `scope_notes`
- `created_at`
- `updated_at`

### صيغ الأهداف المقبولة

يقبل النظام فقط:

- IPv4 واحد مثل `127.0.0.1`.
- Domain واحد مثل `example.com`.
- URL واحد يبدأ بـ `http://` أو `https://`.
- `localhost`.

ويرفض صراحةً:

- CIDR مثل `192.168.1.0/24`.
- IP ranges مثل `192.168.1.1-192.168.1.50`.
- Wildcards مثل `*.example.com`.
- بروتوكولات URL غير `http` و`https` مثل `ftp` و`file` و`javascript`.
- الرموز الخطيرة في shell مثل `;` و`&` و`|` و`$` وbackticks و`>` و`<` والأسطر الجديدة.

### أمثلة تشغيل واختبار

تشغيل السيرفر:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

فحص الصحة:

```bash
curl http://localhost:8000/health
```

إنشاء target صحيح:

```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Localhost Test","target":"127.0.0.1","authorized":true,"scope_notes":"Local machine only"}'
```

عرض كل الأهداف:

```bash
curl http://localhost:8000/targets
```

عرض target واحد:

```bash
curl http://localhost:8000/targets/1
```

تغيير حالة التصريح:

```bash
curl -X PATCH http://localhost:8000/targets/1/authorization \
  -H "Content-Type: application/json" \
  -d '{"authorized":false}'
```

حذف target:

```bash
curl -X DELETE http://localhost:8000/targets/1
```

اختبار رفض CIDR:

```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Bad CIDR","target":"192.168.1.0/24","authorized":true,"scope_notes":"Should be rejected"}'
```

اختبار رفض wildcard:

```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Bad Wildcard","target":"*.example.com","authorized":true,"scope_notes":"Should be rejected"}'
```

## Nmap Basic Scan - المرحلة 2

تمت إضافة فحص Nmap Basic محدود ودفاعي في الإصدار `0.3.0`. هذا الفحص مرتبط مباشرةً بـ Target Management ولا يقبل هدفًا مباشرًا من المستخدم.

### قواعد الفحص

- endpoint الفحص يقبل `target_id` فقط عبر `POST /scans/nmap/basic`.
- يجب أن يكون الهدف موجودًا مسبقًا في SQLite داخل `data/cyber_lab.db`.
- يجب أن تكون قيمة `authorized=true` قبل تشغيل Nmap.
- لا يتم قبول أي `flags` أو `options` أو target مباشر داخل request الفحص.
- الأمر المستخدم ثابت فقط:

```bash
nmap -sV -T3 --top-ports 100 <target>
```

- التقارير تحفظ داخل:

```text
reports/nmap_basic/
```

### أمثلة curl للمرحلة 2

إنشاء target مصرح:

```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Localhost Nmap","target":"127.0.0.1","authorized":true,"scope_notes":"Localhost Nmap test"}'
```

تشغيل Nmap باستخدام `target_id` فقط:

```bash
curl -X POST http://localhost:8000/scans/nmap/basic \
  -H "Content-Type: application/json" \
  -d '{"target_id":1}'
```

تجربة target غير موجود:

```bash
curl -X POST http://localhost:8000/scans/nmap/basic \
  -H "Content-Type: application/json" \
  -d '{"target_id":99999}'
```

إنشاء target موجود لكنه غير مصرح:

```bash
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"name":"Unauthorized Localhost","target":"127.0.0.1","authorized":false,"scope_notes":"Should be blocked"}'
```

تجربة فحص target غير مصرح:

```bash
curl -X POST http://localhost:8000/scans/nmap/basic \
  -H "Content-Type: application/json" \
  -d '{"target_id":2}'
```

عرض مكان التقارير:

```bash
find reports/nmap_basic -maxdepth 1 -type f
```

## 0.4.0 - Admin Web UI

تمت إضافة واجهة إدارة بسيطة داخل `frontend/simple_ui/` ويتم تقديمها مباشرة من FastAPI عبر المسار:

```text
http://localhost:8000/ui
```

### ما توفره الواجهة

- عرض حالة الـ Backend عبر زر **Check Health** الذي يستدعي `/health`.
- إضافة الأهداف من الواجهة باستخدام الحقول: `name` و`target` و`authorized` و`scope_notes`.
- عرض الأهداف المخزنة في جدول واضح مع `id` و`name` و`target` و`target_type` و`authorized` و`scope_notes` و`created_at`.
- تغيير حالة `authorized` من زر **Toggle Authorized**.
- حذف target بعد تأكيد المستخدم عبر `confirm`.
- تشغيل **Nmap Basic** من زر **Run Nmap Basic** على `target_id` الموجود في الجدول فقط.
- عرض نتيجة الفحص، بما في ذلك `target` و`command_used` و`report_file` و`stdout` و`stderr`.

### قيود أمان الواجهة

- الواجهة لا تقبل أي `flags` أو `options` لفحص Nmap.
- لا يوجد input مباشر لتشغيل Nmap على target جديد أو نص حر.
- تشغيل Nmap يتم فقط عبر `target_id` من الأهداف المخزنة.
- زر **Run Nmap Basic** يكون معطلًا عندما يكون `authorized=false`.
- قواعد Nmap الحالية لم تتغير: الأمر ثابت ومحدود، ولا يوجد استخدام لـ `shell=True`.

## 0.6.0 - Domain Archive Intelligence

تمت إضافة موديول دفاعي وقراءة فقط لجمع مؤشرات أرشيفية وعلنية منظمة عن الدومينات من خلال `POST /scans/domain/archive`.

- الفحص يستخدم `target_id` فقط من Target Management ولا يقبل هدفًا مباشرًا من المستخدم.
- يعمل فقط مع أهداف `domain` و`url` المصرح بها، ويستخرج `hostname` من URL تلقائيًا.
- يرفض أهداف `ip` و`localhost` برسالة واضحة لأن Domain Archive يحتاج domain/URL.
- لا يستخدم scraping، ولا brute force، ولا wordlists، ولا قواعد بيانات مسربة، ولا أوامر shell.
- يحاول DNS الحالي باستخدام `socket.gethostbyname_ex` فقط، وفشل DNS لا يفشل التقرير.
- يولد روابط يفتحها الباحث يدويًا: Wayback وcrt.sh وRDAP وروابط WHOIS/DNS history من WhoisFreaks، مع ملاحظة عن خدمات WHOIS history المدفوعة.
- يحفظ تقرير JSON داخل:

```text
reports/domain_archive/
```

مثال تشغيل:

```bash
curl -X POST http://localhost:8000/scans/domain/archive \
  -H "Content-Type: application/json" \
  -d '{"target_id":4}'
```

## 0.6.1 - Archive Fetch Lite

تم تطوير Domain Archive Intelligence ليجلب ملخصًا خفيفًا وآمنًا من مصادر عامة منظمة عبر `POST /scans/domain/archive` مع استمرار الاعتماد على `target_id` فقط.

- يجلب RDAP JSON summary من `https://rdap.org/domain/{domain}` بمهلة قصيرة وبدون حفظ الخام الكامل عند كبر الحجم.
- يجلب Wayback CDX lite summary من `https://web.archive.org/cdx` بحد أقصى 20 capture وبدون scraping.
- لا يستخدم scraping، ولا shell، ولا wordlists.
- لا ينفذ subdomain enumeration.
- لا يقبل target مباشر من المستخدم؛ الطلب يبقى بالشكل: `{ "target_id": 4 }`.
- يبقى `crt.sh` رابطًا فقط ضمن `source_links` في هذه المرحلة ولا يتم الجلب منه.
