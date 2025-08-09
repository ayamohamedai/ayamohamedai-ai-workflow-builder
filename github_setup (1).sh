# خطوات نشر المشروع على GitHub

# 1. إنشاء مستودع محلي
git init

# 2. إضافة جميع الملفات
git add .

# 3. أول commit
git commit -m "🎉 Initial commit: AI Workflow Builder

- ✨ نظام شامل لأتمتة المهام باستخدام الذكاء الاصطناعي
- 📝 دعم كتابة المحتوى وتحليل البيانات
- 🔄 إنشاء سير العمل المتقدم
- 🖥️ واجهتان: سطر الأوامر وواجهة ويب
- 🌐 دعم اللغة العربية والإنجليزية
- 🐳 دعم Docker والحاويات
- 🧪 اختبارات شاملة"

# 4. إنشاء مستودع على GitHub (عبر الموقع أو CLI)
# إذا كان لديك GitHub CLI:
gh repo create ai-workflow-builder --public --description "🤖 نظام أتمتة المهام باستخدام الذكاء الاصطناعي"

# أو قم بإنشاء المستودع يدوياً على github.com

# 5. ربط المستودع المحلي بـ GitHub
git remote add origin https://github.com/yourusername/ai-workflow-builder.git

# 6. رفع الملفات
git branch -M main
git push -u origin main

# 7. إنشاء العلامات (Tags) للإصدارات
git tag -a v1.0.0 -m "🚀 الإصدار الأول من AI Workflow Builder"
git push origin v1.0.0

# 8. إنشاء فروع للتطوير
git checkout -b development
git push -u origin development

git checkout -b features/new-ai-models
git push -u origin features/new-ai-models

# 9. إعداد GitHub Actions للـ CI/CD (اختياري)
mkdir -p .github/workflows

cat > .github/workflows/ci.yml << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [ main, development ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov black flake8 mypy

    - name: Run black code formatter check
      run: black --check .

    - name: Run flake8 linter
      run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

    - name: Run type checker
      run: mypy . --ignore-missing-imports

    - name: Run tests with pytest
      run: |
        pytest tests/ --cov=. --cov-report=xml
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build-docker:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Build Docker image
      run: |
        docker build -t ai-workflow-builder:latest -f docker/Dockerfile .

    - name: Test Docker image
      run: |
        docker run --rm ai-workflow-builder:latest python -c "import main; print('✅ Docker image works')"
EOF

# 10. إنشاء Issue Templates
mkdir -p .github/ISSUE_TEMPLATE

cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug Report
about: تقرير خطأ في النظام
title: '[BUG] '
labels: bug
assignees: ''
---

## 🐛 وصف الخطأ
وصف واضح وموجز للخطأ.

## 🔄 خطوات إعادة الإنتاج
1. اذهب إلى '...'
2. اضغط على '....'
3. مرر لأسفل إلى '....'
4. ستظهر الرسالة

## ✅ السلوك المتوقع
وصف واضح وموجز لما توقعت حدوثه.

## 📱 لقطات الشاشة
إذا أمكن، أضف لقطات شاشة لشرح المشكلة.

## 🖥️ معلومات البيئة:
 - نظام التشغيل: [e.g. Windows, macOS, Linux]
 - إصدار Python: [e.g. 3.9]
 - إصدار المتصفح: [e.g. Chrome 96]

## 📋 معلومات إضافية
أي معلومات إضافية حول المشكلة.
EOF

cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
---
name: Feature Request
about: اقتراح ميزة جديدة
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## 🚀 طلب الميزة
وصف واضح وموجز للميزة المطلوبة.

## 💡 الحل المقترح
وصف واضح وموجز لما تريد حدوثه.

## 🔄 البدائل المدروسة
وصف واضح وموجز لأي حلول أو ميزات بديلة فكرت فيها.

## 📋 معلومات إضافية
أي معلومات إضافية أو لقطات شاشة حول طلب الميزة.
EOF

# 11. إنشاء Pull Request Template
cat > .github/PULL_REQUEST_TEMPLATE.md << 'EOF'
## 📝 وصف التغييرات
وصف واضح للتغييرات التي تم إجراؤها.

## 🔄 نوع التغيير
- [ ] إصلاح خطأ (bug fix)
- [ ] ميزة جديدة (new feature)
- [ ] تغيير جذري (breaking change)
- [ ] تحديث الوثائق

## 🧪 الاختبار
- [ ] تم اختبار التغييرات محلياً
- [ ] تم إضافة اختبارات جديدة (إذا لزم الأمر)
- [ ] جميع الاختبارات تمر بنجاح

## 📋 قائمة المراجعة
- [ ] تم مراجعة الكود
- [ ] تم تحديث الوثائق
- [ ] تم اتباع معايير الترميز
- [ ] لا توجد console.log أو print غير ضرورية

## 📷 لقطات الشاشة
إذا كانت هناك تغييرات في واجهة المستخدم، أضف لقطات الشاشة.
EOF

# 12. إضافة الملفات الجديدة و commit
git add .github/
git commit -m "🔧 إضافة GitHub Actions و Issue Templates"