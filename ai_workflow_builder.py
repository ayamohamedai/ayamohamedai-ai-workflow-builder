#!/usr/bin/env python3
"""
AI Workflow Builder
نظام أتمتة المهام باستخدام الذكاء الاصطناعي
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import openai
from pathlib import Path

# إعداد OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

class TaskType(Enum):
    CONTENT_WRITING = "content_writing"
    DATA_ANALYSIS = "data_analysis"
    TEXT_SUMMARIZATION = "text_summarization"
    EMAIL_GENERATION = "email_generation"
    TRANSLATION = "translation"
    CODE_GENERATION = "code_generation"

@dataclass
class Task:
    """فئة لتمثيل مهمة واحدة"""
    id: str
    type: TaskType
    title: str
    description: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"
    created_at: str = ""
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class AIWorkflowBuilder:
    """الفئة الرئيسية لبناء وتنفيذ سير العمل الذكي"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        openai.api_key = self.api_key
        self.tasks: List[Task] = []
        self.workflows: Dict[str, List[str]] = {}
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
    def add_task(self, task_type: TaskType, title: str, description: str, 
                 input_data: Dict[str, Any]) -> str:
        """إضافة مهمة جديدة"""
        task_id = f"task_{len(self.tasks)}_{datetime.now().strftime('%H%M%S')}"
        task = Task(
            id=task_id,
            type=task_type,
            title=title,
            description=description,
            input_data=input_data
        )
        self.tasks.append(task)
        return task_id
    
    def create_workflow(self, workflow_name: str, task_ids: List[str]):
        """إنشاء سير عمل من مهام متعددة"""
        self.workflows[workflow_name] = task_ids
        
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """تنفيذ مهمة واحدة"""
        try:
            task.status = "running"
            print(f"🚀 تنفيذ المهمة: {task.title}")
            
            if task.type == TaskType.CONTENT_WRITING:
                result = await self._generate_content(task.input_data)
            elif task.type == TaskType.DATA_ANALYSIS:
                result = await self._analyze_data(task.input_data)
            elif task.type == TaskType.TEXT_SUMMARIZATION:
                result = await self._summarize_text(task.input_data)
            elif task.type == TaskType.EMAIL_GENERATION:
                result = await self._generate_email(task.input_data)
            elif task.type == TaskType.TRANSLATION:
                result = await self._translate_text(task.input_data)
            elif task.type == TaskType.CODE_GENERATION:
                result = await self._generate_code(task.input_data)
            else:
                raise ValueError(f"نوع المهمة غير مدعوم: {task.type}")
            
            task.output_data = result
            task.status = "completed"
            task.completed_at = datetime.now().isoformat()
            
            # حفظ النتائج
            await self._save_results(task)
            
            print(f"✅ تم إكمال المهمة: {task.title}")
            return result
            
        except Exception as e:
            task.status = "failed"
            task.output_data = {"error": str(e)}
            print(f"❌ فشل في المهمة {task.title}: {str(e)}")
            raise
    
    async def _generate_content(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """توليد محتوى نصي"""
        prompt = input_data.get('prompt', '')
        content_type = input_data.get('content_type', 'article')
        language = input_data.get('language', 'arabic')
        
        system_prompt = f"""أنت كاتب محتوى محترف. اكتب {content_type} باللغة {language} 
        بناءً على الطلب التالي. اجعل المحتوى جذاباً ومفيداً ومنظماً."""
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        
        return {
            "content": content,
            "word_count": len(content.split()),
            "content_type": content_type,
            "language": language
        }
    
    async def _analyze_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """تحليل البيانات"""
        data_path = input_data.get('data_path')
        analysis_type = input_data.get('analysis_type', 'general')
        
        if not data_path or not Path(data_path).exists():
            raise ValueError("ملف البيانات غير موجود")
        
        # قراءة البيانات
        if data_path.endswith('.csv'):
            df = pd.read_csv(data_path)
        elif data_path.endswith('.json'):
            df = pd.read_json(data_path)
        else:
            raise ValueError("نوع ملف غير مدعوم")
        
        # إجراء التحليل الأساسي
        analysis = {
            "rows_count": len(df),
            "columns_count": len(df.columns),
            "columns": list(df.columns),
            "data_types": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "basic_stats": df.describe().to_dict() if df.select_dtypes(include=['number']).shape[1] > 0 else {}
        }
        
        # توليد تقرير ذكي باستخدام GPT
        data_summary = f"""
        البيانات تحتوي على {len(df)} صف و {len(df.columns)} عمود.
        الأعمدة: {', '.join(df.columns)}
        القيم المفقودة: {df.isnull().sum().sum()}
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت محلل بيانات خبير. قم بتحليل البيانات وتقديم رؤى مفيدة باللغة العربية."},
                {"role": "user", "content": f"حلل هذه البيانات: {data_summary}"}
            ],
            max_tokens=1000
        )
        
        analysis["ai_insights"] = response.choices[0].message.content
        
        return analysis
    
    async def _summarize_text(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """تلخيص النصوص"""
        text = input_data.get('text', '')
        max_length = input_data.get('max_length', 150)
        language = input_data.get('language', 'arabic')
        
        prompt = f"لخص النص التالي في {max_length} كلمة أو أقل باللغة {language}:\n\n{text}"
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"أنت خبير في تلخيص النصوص باللغة {language}"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_length * 2
        )
        
        summary = response.choices[0].message.content
        
        return {
            "original_length": len(text.split()),
            "summary": summary,
            "summary_length": len(summary.split()),
            "compression_ratio": len(summary.split()) / len(text.split()) if text else 0
        }
    
    async def _generate_email(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """توليد رسائل بريد إلكتروني"""
        purpose = input_data.get('purpose', '')
        recipient = input_data.get('recipient', '')
        tone = input_data.get('tone', 'professional')
        language = input_data.get('language', 'arabic')
        
        prompt = f"""
        اكتب رسالة بريد إلكتروني باللغة {language} بنبرة {tone}
        الغرض: {purpose}
        المستلم: {recipient}
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"أنت مساعد كتابة رسائل إلكترونية محترف"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )
        
        email_content = response.choices[0].message.content
        
        return {
            "email_content": email_content,
            "purpose": purpose,
            "tone": tone,
            "language": language
        }
    
    async def _translate_text(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """ترجمة النصوص"""
        text = input_data.get('text', '')
        source_lang = input_data.get('source_language', 'auto')
        target_lang = input_data.get('target_language', 'arabic')
        
        prompt = f"ترجم النص التالي من {source_lang} إلى {target_lang}:\n\n{text}"
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مترجم محترف"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=len(text.split()) * 2
        )
        
        translation = response.choices[0].message.content
        
        return {
            "original_text": text,
            "translated_text": translation,
            "source_language": source_lang,
            "target_language": target_lang
        }
    
    async def _generate_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """توليد الكود"""
        description = input_data.get('description', '')
        language = input_data.get('programming_language', 'python')
        
        prompt = f"اكتب كود {language} لتنفيذ المطلوب التالي:\n{description}\n\nأضف تعليقات باللغة العربية"
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"أنت مطور برمجيات خبير في {language}"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )
        
        code = response.choices[0].message.content
        
        return {
            "code": code,
            "programming_language": language,
            "description": description
        }
    
    async def _save_results(self, task: Task):
        """حفظ نتائج المهمة"""
        filename = f"{task.id}_{task.type.value}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(task), f, ensure_ascii=False, indent=2, default=str)
    
    async def execute_workflow(self, workflow_name: str):
        """تنفيذ سير عمل كامل"""
        if workflow_name not in self.workflows:
            raise ValueError(f"سير العمل '{workflow_name}' غير موجود")
        
        task_ids = self.workflows[workflow_name]
        tasks_to_execute = [t for t in self.tasks if t.id in task_ids]
        
        print(f"🔄 بدء تنفيذ سير العمل: {workflow_name}")
        print(f"📝 المهام: {len(tasks_to_execute)}")
        
        results = []
        for task in tasks_to_execute:
            result = await self.execute_task(task)
            results.append(result)
        
        print(f"🎉 تم إكمال سير العمل: {workflow_name}")
        return results
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """الحصول على حالة المهمة"""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return {"error": "المهمة غير موجودة"}
        
        return asdict(task)
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """عرض قائمة المهام"""
        return [asdict(task) for task in self.tasks]
    
    def export_workflow_results(self, workflow_name: str, format: str = 'json') -> str:
        """تصدير نتائج سير العمل"""
        if workflow_name not in self.workflows:
            raise ValueError(f"سير العمل '{workflow_name}' غير موجود")
        
        task_ids = self.workflows[workflow_name]
        workflow_tasks = [t for t in self.tasks if t.id in task_ids]
        
        results = {
            "workflow_name": workflow_name,
            "execution_date": datetime.now().isoformat(),
            "tasks": [asdict(task) for task in workflow_tasks]
        }
        
        if format == 'json':
            filename = f"{workflow_name}_results.json"
            filepath = self.results_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        return str(filepath)


# مثال على الاستخدام
async def main():
    """مثال على استخدام النظام"""
    
    # إنشاء مثيل من النظام
    workflow_builder = AIWorkflowBuilder()
    
    print("🤖 مرحباً بك في نظام AI Workflow Builder")
    print("=" * 50)
    
    # إضافة مهام مختلفة
    
    # 1. مهمة كتابة محتوى
    content_task = workflow_builder.add_task(
        TaskType.CONTENT_WRITING,
        "كتابة مقال عن الذكاء الاصطناعي",
        "كتابة مقال شامل عن تطبيقات الذكاء الاصطناعي",
        {
            "prompt": "اكتب مقالاً عن تطبيقات الذكاء الاصطناعي في التعليم",
            "content_type": "مقال",
            "language": "arabic"
        }
    )
    
    # 2. مهمة تلخيص نص
    summary_task = workflow_builder.add_task(
        TaskType.TEXT_SUMMARIZATION,
        "تلخيص نص طويل",
        "تلخيص مقال أكاديمي",
        {
            "text": """
            الذكاء الاصطناعي هو مجال واسع في علوم الحاسوب يهدف إلى إنشاء أنظمة قادرة على أداء مهام تتطلب ذكاءً بشرياً.
            يشمل ذلك التعلم، والتفكير، وحل المشكلات، والإدراك، واستخدام اللغة. تطور هذا المجال بشكل سريع في العقود الأخيرة
            مع ظهور تقنيات جديدة مثل التعلم العميق والشبكات العصبية. تطبيقات الذكاء الاصطناعي موجودة الآن في كل مكان،
            من السيارات ذاتية القيادة إلى مساعدات الصوت الذكية، ومن أنظمة التشخيص الطبي إلى خوارزميات التوصية في منصات التواصل الاجتماعي.
            """,
            "max_length": 50,
            "language": "arabic"
        }
    )
    
    # 3. مهمة توليد بريد إلكتروني
    email_task = workflow_builder.add_task(
        TaskType.EMAIL_GENERATION,
        "كتابة بريد إلكتروني تجاري",
        "كتابة بريد ترحيبي للعملاء الجدد",
        {
            "purpose": "ترحيب بعميل جديد وتقديم الخدمات",
            "recipient": "عميل جديد",
            "tone": "ودود ومهني",
            "language": "arabic"
        }
    )
    
    # إنشاء سير عمل
    workflow_builder.create_workflow("content_workflow", [content_task, summary_task, email_task])
    
    # تنفيذ سير العمل
    try:
        results = await workflow_builder.execute_workflow("content_workflow")
        print(f"\n📊 تم إنتاج {len(results)} نتيجة")
        
        # تصدير النتائج
        export_path = workflow_builder.export_workflow_results("content_workflow")
        print(f"📁 تم حفظ النتائج في: {export_path}")
        
    except Exception as e:
        print(f"❌ خطأ في التنفيذ: {str(e)}")
    
    # عرض حالة المهام
    print("\n📋 حالة المهام:")
    for task in workflow_builder.list_tasks():
        print(f"- {task['title']}: {task['status']}")


if __name__ == "__main__":
    asyncio.run(main())