# سجل التغييرات

## 0.5.0 - Scan History + Reports Viewer

- إضافة جدول scans في SQLite.
- تسجيل فحوصات Nmap Basic في قاعدة البيانات.
- إضافة GET /scans.
- إضافة GET /scans/{scan_id}.
- إضافة GET /scans/{scan_id}/report.
- إضافة Scan History إلى الواجهة.
- إضافة Report Viewer إلى الواجهة.
- عدم تغيير قواعد Nmap أو قبول flags/options.


## 0.4.0 - Admin Web UI

- إضافة واجهة إدارة بسيطة.
- عرض وإضافة وحذف الأهداف.
- تغيير authorized من الواجهة.
- تشغيل Nmap Basic من الواجهة على target_id فقط.
- عرض نتيجة الفحص والتقرير.

## 0.3.0 - Nmap Basic Scan

- إضافة endpoint `POST /scans/nmap/basic`.
- ربط Nmap بالأهداف المخزنة فقط عبر `target_id`.
- رفض `authorized=false` قبل تشغيل Nmap.
- منع قبول target مباشر من المستخدم داخل endpoint الفحص.
- حفظ التقارير داخل `reports/nmap_basic/`.
- تشغيل الأمر الثابت فقط `nmap -sV -T3 --top-ports 100 <target>`.
- عدم استخدام `shell=True`.

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

## 0.6.0 - Domain Archive Intelligence

- إضافة فحص أرشيفي للدومينات.
- دعم domain/url targets فقط.
- استخراج hostname من URL.
- إضافة روابط Wayback وcrt.sh وRDAP ومصادر WHOIS/DNS History.
- حفظ تقارير داخل `reports/domain_archive/`.
- عدم استخدام scraping أو shell أو flags.
