# Moodle WASM Evaluator & Sandbox Plugin

نظام متكامل لتقييم وفحص الأكواد البرمجية للطلاب في منصة موودل (Moodle) عبر تجميع الأكواد إلى WebAssembly (WASM) وتنفيذها داخل بيئة معزولة (Sandbox) فائقة الأمان والسرعة باستخدام **Rust** و **Wasmtime**، مع توليد حالات الاختبار آلياً بالذكاء الاصطناعي.

---

## 🏗️ مكونات المشروع (Components)

1. **الخادم الخلفي (Rust Backend - `backend/`):**
   - **`crates/common`**: تعريف بنى البيانات والـ DTOs للأوامر والنتائج.
   - **`crates/engine`**: محرك التنفيذ المعزول المبني على `Wasmtime` مع تقييد الذاكرة (Memory Limits)، تقييد استهلاك الوقود (Fuel Metering لمنع الحلقات اللانهائية)، وعزل الـ IO عبر In-Memory Pipes، والتنفيذ المتوازي عبر `Rayon`.
   - **`crates/compiler`**: أنابيب التجميع للغات البرمجة المختلفة (C/C++ عبر `clang` و `wasi-sdk`، Rust عبر `rustc`، Python عبر بيئات تشغيل WASM).
   - **`crates/ai-generator`**: وحدة توليد حالات الاختبار آلياً باستخدام نماذج الذكاء الاصطناعي (مثل Google Gemini) بصيغة JSON مهيكلة.
   - **`crates/server`**: خادم REST API مبني بواسطة إطار `Axum`.

2. **إضافة موودل (Moodle PHP Plugin - `moodle_plugin/`):**
   - إضافة فرعية لنظام الواجبات (`assignsubmission_wasmcode`).
   - تتيح للطالب إدخال وحل الواجب البرمجي، وللمعلم تحديد معايير التقييم وتوليد الاختبارات.
   - ترتبط بسيرفر التقييم وتُسجل النتائج والدرجات تلقائياً في Moodle Gradebook.

---

## 🚀 التشغيل السريع باستخدام Docker

لتشغيل السيرفر ومنصة Moodle متصلين معاً بضغطة زر واحدة:

```bash
# قم بإدخال مفتاح الذكاء الاصطناعي (اختياري)
export GEMINI_API_KEY="your_api_key_here"

# تشغيل بيئة العمل المتكاملة
docker compose up -d
```

سيكون الخادم متاحاً على:
- **سيرفر التقييم (Rust Evaluator):** `http://localhost:8080`
- **منصة موودل (Moodle):** `http://localhost`

---

## 📡 واجهات برمجة التطبيقات (API Endpoints)

### 1. تقييم كود الطالب (Evaluate Code)
`POST /api/v1/evaluate`

```json
{
  "language": "c",
  "source_code": "#include <stdio.h>\nint main() { int a, b; scanf(\"%d %d\", &a, &b); printf(\"%d\\n\", a + b); return 0; }",
  "limits": {
    "timeout_ms": 2000,
    "memory_limit_mb": 64
  },
  "test_cases": [
    {
      "id": 1,
      "name": "Basic Addition",
      "input": "4 5\n",
      "expected_output": "9\n",
      "is_hidden": false,
      "weight": 10.0
    }
  ]
}
```

### 2. توليد الاختبارات بالذكاء الاصطناعي (AI Test Generation)
`POST /api/v1/tests/generate`

```json
{
  "assignment_title": "Sum of Two Numbers",
  "assignment_description": "Read two integers from stdin and print their sum.",
  "language": "c",
  "number_of_tests": 5
}
```
