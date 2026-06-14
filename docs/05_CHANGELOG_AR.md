# سجل التغييرات

## 0.2.0 - Target Management

- إضافة نظام إدارة أهداف مستقل قبل تشغيل أي فحص.
- إضافة SQLite محلي داخل `data/cyber_lab.db` وجدول `targets`.
- إضافة endpoints: `POST /targets` و`GET /targets` و`GET /targets/{target_id}` و`PATCH /targets/{target_id}/authorization` و`DELETE /targets/{target_id}`.
- إضافة تحقق صارم للأهداف يقبل IPv4 واحدًا أو domain واحدًا أو URL يبدأ بـ `http://` أو `https://` أو `localhost` فقط.
- رفض CIDR وIP ranges وwildcards والرموز الخطيرة مثل `;` و`&` و`|` و`$` وbackticks و`>` و`<` والأسطر الجديدة.
- الإبقاء على Target Management مستقلًا دون ربطه بأي فحص أو أداة خارجية.

## 0.1.0 - التأسيس الأولي

- إنشاء هيكل المشروع.
- إنشاء FastAPI backend.
- إضافة endpoint رئيسي `/`.
- إضافة endpoint `/health`.
- إضافة ملفات مبدئية لوحدات الفحص.
- إضافة وحدة Nmap Basic كمسار ملف مبدئي يحتاج استكمالًا آمنًا.
- إضافة سياسة بداية للتصريح قبل الفحص ضمن التوثيق.
- إنشاء نظام توثيق ومراجعة عربي داخل `docs/`.
- تحديث `README.md` ليكون مدخلًا للتشغيل والتوثيق.
- إضافة `PROJECT_STATUS_AR.md` و`REVIEW_AFTER_EACH_CHANGE_AR.md` في جذر المشروع.

## القادم

- تنفيذ Target Management قبل توسيع الفحوصات.
- تنفيذ Nmap Basic مضبوط ومحدود بعد توثيق مواصفته.
- توحيد report builder وحفظ التقارير وفق معيار التقارير.
- إضافة Audit Log للفحوصات والرفض.
