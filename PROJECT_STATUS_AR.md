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
