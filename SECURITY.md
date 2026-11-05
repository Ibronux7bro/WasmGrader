# معايير وسياسات الأمان والعزل (Security & Sandboxing Architecture)

يقدم هذا المستند تحليلاً لنموذج التهديدات (Threat Model) وكيفية تصدي نظام **Moodle WASM Evaluator** لهجمات واختراقات الأكواد البرمجية الضارة للطلاب.

---

## 1. نموذج التهديدات وآليات الحماية (Threat Model & Mitigations)

| نوع التهديد (Threat Vector) | آلية الهجوم المحتملة | الحل الهندسي المطبق في النظام (Mitigation) |
| :--- | :--- | :--- |
| **الهروب من البيئة المعزولة (Sandbox Escape)** | استدعاء دوال النظام المضيف `system()`, `fork()`, قراءة `/etc/passwd`. | **Wasmtime Zero-Trust WASI**: الكود لا يتصل بالنظام المضيف مباشرة. دوال WASI مقيدة ومحجوبة بالكامل، والوصول للقرص أو العمليات المجاورة غير موجود في جدول الدوال (Linker). |
| **الحلقات اللانهائية واستنزاف المعالج (CPU Exhaustion / DoS)** | كود يحتوي على `while(1){}` أو خوارزميات غير منتهية لتعطيل الخادم. | **Fuel Metering**: يستهلك كل أمر في WebAssembly عدداً محدداً من وحدات الوقود. بمجرد نفاد الوقود المقدر بالـ `timeout_ms`، يقاطع محرك Wasmtime المعالجة فوراً بنمط `Trap::OutOfFuel`. |
| **قنابل الذاكرة (Memory Exhaustion / Fork Bombs)** | كود يحجز غيغابايت من الذاكرة (`malloc(1024*1024*1024)`). | **Wasmtime ResourceLimiter**: يحدد سقفاً أعلى (Upper Bound) للـ Linear Memory (افتراضياً 64MB). أي طلب لتوسيع الذاكرة يتجاوز هذا الحد يُرفض في الحال وتتوقف العملية بـ `MemoryLimitExceeded`. |
| **تسريب البيانات وسرقة المفاتيح (Data Exfiltration / Network Egress)** | محاولة الكود فتح اتصال شبكي (Sockets/HTTP) لإرسال بيانات حساسة للخارج. | **شبكة معطلة بالكامل**: إعدادات بيئة التشغيل `WasiCtx` لا تملك أي واجهات شبكية (No Sockets / No TCP/UDP bindings). |
| **فيضان المخرجات (Stdout/Stderr Flooding)** | طباعة مليارات الحروف لملء قرص السيرفر أو استهلاك ذاكرة الـ RAM. | **In-Memory Pipe Caps**: توجيه المخرجات إلى `MemoryOutputPipe` بحد أقصى (1MB). أي بيانات إضافية يتم قطعها فوراً. |

---

## 2. أفضل ممارسات النشر والتشغيل (Deployment Best Practices)

1. **تشغيل الخادم كـ Non-root User:**
   - الحاوية في Docker تعمل بصلاحيات مستخدم مقيد دون امتيازات root.
2. **استخدام شبكة داخلية خاصة (Private Docker Network):**
   - يجب حصر الوصول لمنفذ السيرفر `8080` داخل الشبكة الافتراضية لحاويات Docker، بحيث لا يمكن إلا لسيرفر Moodle التخاطب معه.
3. **تفعيل مفتاح المصادقة (API Bearer Token):**
   - تعيين قيمة `assignsubmission_wasmcode/api_key` في إعدادات Moodle وربطها في الخادم لحماية الـ endpoints من الاستدعاء غير المصرح به.
