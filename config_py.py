"""
Configuration settings for AI Workflow Builder
إعدادات التطبيق
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# المسارات الأساسية
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATES_DIR = BASE_DIR / "templates"

# إنشاء المجلدات إذا لم تكن موجودة
for directory in [DATA_DIR, RESULTS_DIR, LOGS_DIR, TEMPLATES_DIR]:
    directory.mkdir(exist_ok=True)

class Config:
    """فئة الإعدادات الرئيسية"""
    
    # إعدادات API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    # إعدادات النموذج
    DEFAULT_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7
    
    # إعدادات المهام
    MAX_CONCURRENT_TASKS = 5
    TASK_TIMEOUT = 300  # 5 دقائق
    RETRY_ATTEMPTS = 3
    
    # إعدادات الملفات
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    SUPPORTED_FILE_FORMATS = ['.txt', '.csv', '.json', '.xlsx', '.docx', '.pdf']
    
    # إعدادات التسجيل
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "{time} | {level} | {message}"
    
    # إعدادات واجهة المستخدم
    STREAMLIT_THEME = "dark"
    UI_TITLE = "🤖 AI Workflow Builder"
    
    @classmethod
    def validate(cls) -> bool:
        """التحقق من صحة الإعدادات"""
        if not cls.OPENAI_API_KEY:
            print("⚠️ تحذير: OpenAI API key غير موجود")
            return False
        return True
    
    @classmethod
    def get_model_config(cls, model_name: str = None) -> Dict[str, Any]:
        """الحصول على إعدادات النموذج"""
        return {
            "model": model_name or cls.DEFAULT_MODEL,
            "max_tokens": cls.MAX_TOKENS,
            "temperature": cls.TEMPERATURE
        }

# قوالب المهام الافتراضية
TASK_TEMPLATES = {
    "content_writing": {
        "system_prompt": "أنت كاتب محتوى محترف باللغة العربية. اكتب محتوى جذاب ومفيد وواضح.",
        "default_params": {
            "language": "arabic",
            "tone": "professional",
            "length": "medium"
        }
    },
    
    "data_analysis": {
        "system_prompt": "أنت محلل بيانات خبير. قم بتحليل البيانات وتقديم رؤى مفيدة باللغة العربية.",
        "default_params": {
            "chart_types": ["bar", "line", "pie"],
            "include_insights": True
        }
    },
    
    "email_generation": {
        "system_prompt": "أنت مساعد كتابة رسائل إلكترونية محترف. اكتب رسائل واضحة ومؤثرة.",
        "default_params": {
            "language": "arabic",
            "tone": "professional",
            "include_signature": True
        }
    },
    
    "translation": {
        "system_prompt": "أنت مترجم محترف. قم بالترجمة مع الحفاظ على المعنى والسياق.",
        "default_params": {
            "preserve_formatting": True,
            "cultural_adaptation": True
        }
    },
    
    "summarization": {
        "system_prompt": "أنت خبير في تلخيص النصوص. اكتب ملخصات دقيقة ومفيدة.",
        "default_params": {
            "language": "arabic",
            "style": "bullet_points",
            "max_length": 200
        }
    },
    
    "code_generation": {
        "system_prompt": "أنت مطور برمجيات خبير. اكتب كود نظيف ومعلق باللغة العربية.",
        "default_params": {
            "language": "python",
            "include_comments": True,
            "include_tests": False
        }
    }
}

# إعدادات قواعد البيانات (اختيارية)
DATABASE_CONFIG = {
    "type": "sqlite",
    "path": BASE_DIR / "workflow_builder.db",
    "tables": {
        "tasks": "tasks",
        "workflows": "workflows",
        "results": "results",
        "logs": "execution_logs"
    }
}

# إعدادات الواجهة الرسومية
UI_CONFIG = {
    "sidebar_width": 300,
    "main_area_padding": 20,
    "theme_colors": {
        "primary": "#1f77b4",
        "secondary": "#ff7f0e",
        "success": "#2ca02c",
        "error": "#d62728",
        "warning": "#ff7f0e"
    },
    "icons": {
        "task_pending": "⏳",
        "task_running": "🚀",
        "task_completed": "✅",
        "task_failed": "❌",
        "workflow": "🔄",
        "data": "📊",
        "content": "📝",
        "email": "📧"
    }
}

# رسائل النظام
MESSAGES = {
    "welcome": "🤖 مرحباً بك في نظام AI Workflow Builder",
    "task_created": "✨ تم إنشاء المهمة بنجاح",
    "task_failed": "❌ فشل في تنفيذ المهمة",
    "workflow_completed": "🎉 تم إكمال سير العمل بنجاح",
    "api_key_missing": "⚠️ مفتاح API مفقود",
    "file_uploaded": "📁 تم رفع الملف بنجاح",
    "results_exported": "💾 تم تصدير النتائج"
}