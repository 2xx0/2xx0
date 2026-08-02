# طريقة تفعيل البروفايل

## 1. سوي الريبو الخاص (نفس اسم اليوزرنيم بالضبط)
```
gh repo create 2xx0 --public --clone
```
أو من الموقع: New Repository → الاسم لازم يكون `2xx0` بالضبط → Public.

## 2. انسخ كل ملفات هالمجلد جوا الريبو
انسخ:
- `README.md`
- `ascii-logo.svg`
- `info-card.svg`
- `contrib-heatmap.svg`
- `scripts/` (كل الملفات)
- `data/contributions.json`
- `.github/workflows/update-profile-art.yml`

## 3. ادفعها لـ GitHub
```
git add .
git commit -m "init profile"
git push origin main
```

## 4. فعّل الـ Action يدوياً أول مرة
روح على تبويب **Actions** بالريبو → اختر **Update profile art** → **Run workflow**.
هاد بيتأكد إنه فعلاً قادر يعمل commit ويحدّث الـ heatmap.

## 5. تأكد إنه الـ Actions permissions مضبوطة
Settings → Actions → General → Workflow permissions → اختر **Read and write permissions**.
(لو مو مفعّلة هيك، الـ Action رح يفشل بمحاولة الـ commit التلقائي.)

## بعدها
كل يوم الساعة ~06:17 UTC (~09:17 بتوقيت الأردن) الـ workflow رح يسحب بيانات مساهماتك الحقيقية من GitHub ويحدّث `contrib-heatmap.svg` تلقائياً بدون ما تحرك إصبع.

## تخصيص لاحق
- عدّل الأسطر بـ `scripts/make_info_card.py` (متغير `ROWS`) لما تضيف مشروع أو تغيّر status.
- لو بدك تغيّر نص الشعار، بدّل `LOGO_TEXT` بأعلى `scripts/make_ascii_logo_svg.py` وشغّله من جديد.
