# OZONE LUACRYPT
واجهة عربية للجوال وAPI لتشفير Roblox Luau باستخدام محرك Obscura المفتوح المصدر.

## النشر
1. ارفع محتويات هذا المجلد إلى مستودع GitHub.
2. أنشئ Web Service على استضافة تدعم Python وGit والاتصال الخارجي.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app --workers 1 --threads 4 --timeout 90`
5. أول تشغيل يحاول تنزيل Obscura ومتطلباته تلقائيًا.

## API
`POST /api/obfuscate`
```json
{"code":"print('Hello')","mode":"vm"}
```
الأوضاع: `lightweight`, `rename`, `native`, `vm`.
النتيجة: JSON يحتوي على `result`.

مهم: بعض صيغ Luau غير مدعومة؛ اختبر الناتج داخل Roblox Studio. الاستضافات المجانية قد تنام أو تفرض حدودًا. حد الطلبات الحالي بسيط وليس بديلًا عن حماية إنتاجية. لا ترسل أسرارًا داخل السكربت. محرك Obscura: https://github.com/vo3pal/obscura
