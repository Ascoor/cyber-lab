# حالة مشروع Cyber Lab Control Panel

## آخر حالة للمشروع
المشروع انتقل إلى `0.5.0 - Scan History + Reports Viewer`. تمت إضافة سجل فحوصات داخل SQLite وقارئ تقارير من الواجهة دون إضافة أي فحص جديد ودون تغيير أمر Nmap Basic.

## ما تم إنجازه
- إضافة جدول `scans` في SQLite.
- تسجيل كل تشغيل Nmap Basic في جدول `scans`.
- إضافة endpoints: `GET /scans` و`GET /scans/{scan_id}` و`GET /scans/{scan_id}/report`.
- إضافة Scan History إلى واجهة `/ui`.
- إضافة Report Viewer لعرض JSON التقرير المحفوظ.
- الإبقاء على Nmap Basic عبر `target_id` فقط، دون flags/options ودون `shell=True`.

## ما يعمل الآن
- `/health` و`/ui` يعملان.
- Target Management يعمل.
- Nmap Basic يعمل للأهداف المصرح بها عبر `target_id` فقط.
- كل فحص Nmap Basic ينشئ scan record.
- يمكن عرض السجل والتقرير من API ومن الواجهة.

## ما لم يتم تنفيذه بعد
- ZAP.
- SSL scan.
- Headers scan.
- MobSF.
- Job Queue.
- Docker Compose جاهز للتشغيل.

## الخطوة التالية المقترحة
تنفيذ Job Queue أو Report Builder موحد قبل إضافة فحوصات جديدة.

## آخر مراجعة
- التاريخ: 2026-06-18
- نتيجة المراجعة: تم تنفيذ Scan History وReports Viewer دون تغيير أمر Nmap ودون قبول target مباشر أو flags/options.

## حالة 0.6.0 - Domain Archive Intelligence

تم إضافة Domain Archive Intelligence كموديول دفاعي وقراءة فقط للدومينات.

ما يعمل الآن:
- endpoint جديد `POST /scans/domain/archive` يعتمد على `target_id` فقط.
- دعم أهداف `domain` و`url` المصرح بها فقط.
- استخراج hostname من URL قبل بناء التقرير.
- رفض أهداف `ip` و`localhost` برسالة واضحة.
- DNS current resolution باستخدام مكتبة Python القياسية `socket`.
- توليد روابط Wayback وcrt.sh وRDAP وWHOIS/DNS history للفتح اليدوي.
- حفظ تقارير JSON داخل `reports/domain_archive/`.
- عرض زر Domain Archive ونتيجته في Admin Web UI.

ما لم ينفذ بعد:
- لا يوجد scraping للمصادر الأرشيفية.
- لا يوجد تكامل API مدفوع أو مفاتيح WHOIS/RDAP خارجية.
- لا يوجد subdomain enumeration أو wordlists.

الخطوة التالية المقترحة:
- إضافة إعدادات اختيارية آمنة عبر environment variables لتكامل RDAP/WHOIS API رسمي عند الحاجة، مع rate limiting وتوثيق واضح.

## حالة 0.6.1 - Archive Fetch Lite

تم إنجاز مرحلة Archive Fetch Lite لموديول Domain Archive Intelligence:

- إضافة جلب RDAP JSON summary من مصدر عام منظم وبمهلة قصيرة.
- إضافة جلب Wayback CDX lite summary بحد أقصى 20 capture.
- تحديث تقرير JSON ليشمل `current_dns` و`rdap_summary` و`wayback_summary` و`source_links`.
- تحديث واجهة Admin Web UI لعرض RDAP وWayback captures بوضوح مع روابط قابلة للضغط.
- الإبقاء على `crt.sh` كرابط فقط بدون جلب في هذه المرحلة.
- استمرار endpoint `POST /scans/domain/archive` في قبول `target_id` فقط.

الخطوة التالية المقترحة: تحسين التحليلات الدفاعية داخل التقرير مثل تصنيف أنواع الملفات التاريخية وتلخيص تغيّر سجلات RDAP بدون إضافة scraping أو enumeration.

## حالة 0.6.2 - Network Connectivity Diagnostics + Documentation Cleanup

تمت إضافة تشخيص اتصال شبكي محدود لمساعدة المستخدم على معرفة ما إذا كانت البيئة المحلية قادرة على الوصول إلى مصادر Domain Archive الخارجية.

ما يعمل الآن:
- endpoint جديد `GET /diagnostics/network`.
- فحص DNS ثابت لكل من `rdap.org` و`web.archive.org`.
- فحص HTTP ثابت لكل من RDAP وWayback CDX باستخدام `example.com` فقط.
- عرض نتيجة التشخيص داخل Admin Web UI.
- لا يقبل التشخيص أي target أو URL من المستخدم.
- لا يتم تشغيل shell ولا حفظ scan record لهذا التشخيص.
- تحديث README وحالة المشروع وسجل التغييرات والقرارات لتوضيح نسخة 0.6.2.

الخطوة التالية المقترحة: توحيد report builder أو إضافة Job Queue قبل توسيع الموديولات.
