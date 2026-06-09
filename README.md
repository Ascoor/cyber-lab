# Cyber Lab Control Panel

Cyber Lab Control Panel هو مشروع محلي داخل WSL2 Ubuntu لتنظيم فحوصات أمن سيبراني دفاعية ومصرح بها فقط. يعتمد Backend الحالي على FastAPI، ويهدف إلى بناء لوحة تحكم قابلة للتوسع مع توثيق عربي واضح للنطاق، المنهجية، التقارير، والمراجعة المستمرة.

## تحذير قانوني واضح

استخدم هذا المشروع فقط على أنظمة تملكها أو لديك إذن مكتوب لاختبارها. لا تستخدمه لفحص أهداف عامة، شبكات خارج النطاق، أشخاص، أرقام هاتف، حسابات، كلمات مرور، أو أي نشاط استغلالي. أي فحص لاحق يجب أن يكون محدودًا، دفاعيًا، موثقًا، ويتطلب تصريحًا صريحًا مثل `authorized=true`.

## الحالة الحالية

- Backend يعمل عبر FastAPI.
- endpoint `/` موجود للتحقق العام.
- endpoint `/health` موجود للتحقق السريع.
- ملفات موديولات الفحص موجودة مبدئيًا داخل `backend/app/modules/`.
- ملف `backend/app/modules/nmap_scan.py` موجود لكنه فارغ في المراجعة الحالية، لذلك لا يوجد تنفيذ Nmap فعلي موثق بعد.
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
7. المرحلة 6: Simple UI.
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
