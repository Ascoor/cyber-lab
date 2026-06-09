# نظرة عامة على المشروع

## اسم المشروع
Cyber Lab Control Panel

## وصف مختصر
لوحة تحكم محلية مبنية حول FastAPI لتنظيم فحوصات أمن سيبراني دفاعية ومصرح بها فقط، مع توثيق واضح للنطاق، الاختبارات، التقارير، وخطوات التطوير اللاحقة.

## الهدف الدفاعي
الهدف هو مساعدة الفريق على تنفيذ فحوصات تحقق أساسية على الأصول المملوكة أو المصرح باختبارها، وتوثيق النتائج بشكل قابل للمراجعة دون تحويل المشروع إلى أداة هجومية أو أداة استغلال.

## ما الذي يفعله المشروع
- يوفر Backend أوليًا باستخدام FastAPI.
- يوفر endpoint رئيسيًا `/` للتحقق من جاهزية اللوحة.
- يوفر endpoint `/health` للتحقق السريع من صحة الخدمة.
- يحتوي على هيكل مبدئي لوحدات فحص مثل Nmap وSSL وHeaders وZAP وMobSF وOSINT.
- يضع أساسًا لتخزين التقارير والسجلات والنتائج محليًا.
- يفرض منهجية تطوير دفاعية محدودة النطاق قبل إضافة أي فحص جديد.

## ما الذي لا يفعله المشروع
- لا ينفذ فحوصات هجومية أو استغلال ثغرات فعليًا.
- لا يسمح بفحص أهداف خارج النطاق أو بدون تصريح.
- لا يسمح بفحص شبكات كاملة أو نطاقات CIDR في النسخة الأولى.
- لا يسمح بتتبع أشخاص أو أرقام هواتف أو حسابات شخصية.
- لا يسمح بهجمات كلمات مرور أو credential attacks.
- لا يوفر أدوات تجاوز صلاحيات أو persistence أو post-exploitation.

## بيئة التشغيل الحالية
- النظام المقصود: WSL2 Ubuntu محليًا.
- Backend: FastAPI.
- خادم التطوير: Uvicorn.
- إدارة الحزم: `backend/requirements.txt`.
- Docker: توجد ملفات `backend/Dockerfile` و`docker-compose.yml`، لكن `docker-compose.yml` فارغ حاليًا ويحتاج ضبطًا لاحقًا قبل الاعتماد عليه.

## بنية المشروع الحالية
```text
cyber-lab/
├── README.md
├── PROJECT_STATUS_AR.md
├── REVIEW_AFTER_EACH_CHANGE_AR.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── auth.py
│       ├── database.py
│       ├── jobs.py
│       ├── models.py
│       ├── modules/
│       │   ├── __init__.py
│       │   ├── headers_scan.py
│       │   ├── mobsf_scan.py
│       │   ├── nmap_scan.py
│       │   ├── osint_check.py
│       │   ├── ssl_scan.py
│       │   └── zap_scan.py
│       └── reports/
│           ├── __init__.py
│           └── report_builder.py
├── docs/
├── frontend/
│   └── simple_ui/
├── data/
├── logs/
├── reports/
├── scans/
└── docker-compose.yml
```

## الحالة الحالية
- Backend يعمل مبدئيًا من خلال `backend/app/main.py`.
- endpoint `/` موجود ويعيد حالة تشغيل عامة.
- endpoint `/health` موجود ويعيد `status=ok`.
- وحدة `backend/app/modules/nmap_scan.py` موجودة كملف، لكنها فارغة في المراجعة الحالية؛ لذلك فإن Nmap Basic غير موثق كتنفيذ فعلي داخل الملف حتى الآن.
- `docker-compose.yml` فارغ في المراجعة الحالية؛ لذلك مرحلة Docker Compose لم تكتمل بعد.
- لا توجد إضافة أدوات فحص جديدة في هذه المرحلة؛ التركيز على التوثيق والمنهجية والمراجعة.

## ملاحظات مراجعة الملفات الحالية
- `backend/app/main.py`: يحتوي على إعداد FastAPI وCORS وendpoint `/` و`/health`. لا توجد حاليًا حماية نطاق أو تسجيل تقارير داخل هذا الملف.
- `backend/app/modules/nmap_scan.py`: الملف موجود لكنه فارغ، ويجب تنفيذ أي فحص Nmap لاحقًا وفق سياسة التصريح ومنع CIDR والـ timeout وعدم استخدام `shell=True`.
- `README.md`: كان يحتوي وصفًا مختصرًا وتحذيرًا قانونيًا عامًا، وتم توسيعه ليربط بالتوثيق العربي وخريطة الطريق.
- `backend/requirements.txt`: يحتوي dependencies أساسية مناسبة للمرحلة الحالية دون إضافة حزم كبيرة.
- `docker-compose.yml`: فارغ حاليًا، ولا يجب اعتباره وسيلة تشغيل جاهزة حتى مرحلة Packaging with Docker Compose.
