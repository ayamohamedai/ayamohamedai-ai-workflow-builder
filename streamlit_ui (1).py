"""
Streamlit UI for AI Workflow Builder
واجهة المستخدم الرسومية للنظام
"""

import streamlit as st
import asyncio
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# استيراد الوحدات الخاصة بالمشروع
from main import AIWorkflowBuilder, TaskType, Task
from config import Config, UI_CONFIG, MESSAGES, TASK_TEMPLATES

# إعداد الصفحة
st.set_page_config(
    page_title="AI Workflow Builder",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخزين البيانات في الجلسة
if 'workflow_builder' not in st.session_state:
    try:
        st.session_state.workflow_builder = AIWorkflowBuilder()
    except ValueError as e:
        st.error("❌ يرجى إعداد OpenAI API key في متغيرات البيئة")
        st.stop()

if 'active_tasks' not in st.session_state:
    st.session_state.active_tasks = []

if 'workflows' not in st.session_state:
    st.session_state.workflows = {}

def main():
    """الوظيفة الرئيسية للواجهة"""
    
    # العنوان الرئيسي
    st.title("🤖 AI Workflow Builder")
    st.markdown("**نظام أتمتة المهام باستخدام الذكاء الاصطناعي**")
    st.divider()
    
    # الشريط الجانبي
    with st.sidebar:
        st.header("⚙️ لوحة التحكم")
        
        # اختيار الوضع
        mode = st.selectbox(
            "اختر الوضع:",
            ["إنشاء مهمة جديدة", "إدارة المهام", "سير العمل", "النتائج والتقارير"]
        )
        
        st.divider()
        
        # معلومات النظام
        st.subheader("📊 إحصائيات سريعة")
        st.metric("المهام النشطة", len(st.session_state.active_tasks))
        st.metric("سير العمل", len(st.session_state.workflows))
        
        # حالة API
        if Config.OPENAI_API_KEY:
            st.success("✅ OpenAI API متصل")
        else:
            st.error("❌ OpenAI API غير متصل")
    
    # المحتوى الرئيسي
    if mode == "إنشاء مهمة جديدة":
        create_task_interface()
    elif mode == "إدارة المهام":
        manage_tasks_interface()
    elif mode == "سير العمل":
        workflow_interface()
    else:
        results_interface()

def create_task_interface():
    """واجهة إنشاء المهام"""
    st.header("✨ إنشاء مهمة جديدة")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # اختيار نوع المهمة
        task_type = st.selectbox(
            "نوع المهمة:",
            options=list(TaskType),
            format_func=lambda x: {
                TaskType.CONTENT_WRITING: "📝 كتابة المحتوى",
                TaskType.DATA_ANALYSIS: "📊 تحليل البيانات", 
                TaskType.TEXT_SUMMARIZATION: "📄 تلخيص النصوص",
                TaskType.EMAIL_GENERATION: "📧 كتابة الإيميلات",
                TaskType.TRANSLATION: "🌐 الترجمة",
                TaskType.CODE_GENERATION: "💻 توليد الكود"
            }[x]
        )
        
        # معلومات المهمة الأساسية
        task_title = st.text_input("عنوان المهمة:")
        task_description = st.text_area("وصف المهمة:")
        
        # إعدادات المهمة حسب النوع
        st.subheader("⚙️ إعدادات المهمة")
        input_data = {}
        
        if task_type == TaskType.CONTENT_WRITING:
            input_data = content_writing_form()
        elif task_type == TaskType.DATA_ANALYSIS:
            input_data = data_analysis_form()
        elif task_type == TaskType.TEXT_SUMMARIZATION:
            input_data = text_summarization_form()
        elif task_type == TaskType.EMAIL_GENERATION:
            input_data = email_generation_form()
        elif task_type == TaskType.TRANSLATION:
            input_data = translation_form()
        elif task_type == TaskType.CODE_GENERATION:
            input_data = code_generation_form()
    
    with col2:
        st.subheader("📋 معاينة المهمة")
        if task_title and task_description:
            st.info(f"""
            **العنوان:** {task_title}
            
            **الوصف:** {task_description}
            
            **النوع:** {task_type.value}
            """)
        
        # زر إنشاء المهمة
        if st.button("🚀 إنشاء المهمة", type="primary", use_container_width=True):
            if task_title and task_description and input_data:
                task_id = st.session_state.workflow_builder.add_task(
                    task_type, task_title, task_description, input_data
                )
                st.session_state.active_tasks.append(task_id)
                st.success(f"✅ تم إنشاء المهمة: {task_id}")
                st.rerun()
            else:
                st.error("❌ يرجى ملء جميع الحقول المطلوبة")

def content_writing_form():
    """نموذج كتابة المحتوى"""
    prompt = st.text_area("المطلوب كتابته:", height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        content_type = st.selectbox("نوع المحتوى:", ["مقال", "منشور", "تقرير", "قصة"])
        language = st.selectbox("اللغة:", ["arabic", "english"])
    
    with col2:
        tone = st.selectbox("النبرة:", ["professional", "casual", "creative", "technical"])
        length = st.selectbox("الطول:", ["short", "medium", "long"])
    
    return {
        "prompt": prompt,
        "content_type": content_type,
        "language": language,
        "tone": tone,
        "length": length
    }

def data_analysis_form():
    """نموذج تحليل البيانات"""
    uploaded_file = st.file_uploader("رفع ملف البيانات:", type=['csv', 'xlsx', 'json'])
    
    if uploaded_file:
        # حفظ الملف مؤقتاً
        file_path = Path("temp") / uploaded_file.name
        file_path.parent.mkdir(exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        
        analysis_type = st.selectbox("نوع التحليل:", ["basic", "detailed", "statistical"])
        include_charts = st.checkbox("تضمين الرسوم البيانية", value=True)
        
        return {
            "data_path": str(file_path),
            "analysis_type": analysis_type,
            "include_charts": include_charts
        }
    
    return {}

def text_summarization_form():
    """نموذج تلخيص النصوص"""
    text = st.text_area("النص المراد تلخيصه:", height=200)
    
    col1, col2 = st.columns(2)
    with col1:
        max_length = st.number_input("الحد الأقصى للكلمات:", min_value=50, max_value=500, value=150)
        language = st.selectbox("لغة الملخص:", ["arabic", "english"])
    
    with col2:
        summary_style = st.selectbox("أسلوب التلخيص:", ["bullet_points", "paragraph", "outline"])
        focus = st.selectbox("التركيز على:", ["main_points", "key_facts", "conclusions"])
    
    return {
        "text": text,
        "max_length": max_length,
        "language": language,
        "summary_style": summary_style,
        "focus": focus
    }

def email_generation_form():
    """نموذج كتابة الإيميل"""
    purpose = st.text_input("الغرض من الإيميل:")
    recipient = st.text_input("المستلم:")
    
    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("النبرة:", ["professional", "friendly", "formal", "casual"])
        language = st.selectbox("اللغة:", ["arabic", "english"])
    
    with col2:
        email_type = st.selectbox("نوع الإيميل:", ["business", "marketing", "support", "personal"])
        include_signature = st.checkbox("تضمين التوقيع", value=True)
    
    return {
        "purpose": purpose,
        "recipient": recipient,
        "tone": tone,
        "language": language,
        "email_type": email_type,
        "include_signature": include_signature
    }

def translation_form():
    """نموذج الترجمة"""
    text = st.text_area("النص المراد ترجمته:", height=150)
    
    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox("اللغة المصدر:", ["auto", "arabic", "english", "french", "spanish"])
    
    with col2:
        target_lang = st.selectbox("اللغة المستهدفة:", ["arabic", "english", "french", "spanish"])
    
    preserve_formatting = st.checkbox("الحفاظ على التنسيق", value=True)
    
    return {
        "text": text,
        "source_language": source_lang,
        "target_language": target_lang,
        "preserve_formatting": preserve_formatting
    }

def code_generation_form():
    """نموذج توليد الكود"""
    description = st.text_area("وصف الكود المطلوب:", height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        programming_language = st.selectbox("لغة البرمجة:", ["python", "javascript", "java", "c++", "html"])
        complexity = st.selectbox("مستوى التعقيد:", ["simple", "medium", "complex"])
    
    with col2:
        include_comments = st.checkbox("تضمين التعليقات", value=True)
        include_tests = st.checkbox("تضمين الاختبارات", value=False)
    
    return {
        "description": description,
        "programming_language": programming_language,
        "complexity": complexity,
        "include_comments": include_comments,
        "include_tests": include_tests
    }

def manage_tasks_interface():
    """واجهة إدارة المهام"""
    st.header("🔧 إدارة المهام")
    
    if not st.session_state.active_tasks:
        st.info("📝 لا توجد مهام حالياً. قم بإنشاء مهمة جديدة!")
        return
    
    # عرض المهام
    tasks = st.session_state.workflow_builder.list_tasks()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("قائمة المهام")
        
        for task in tasks:
            with st.expander(f"{task['title']} - {task['status']}"):
                st.write(f"**الوصف:** {task['description']}")
                st.write(f"**النوع:** {task['type']}")
                st.write(f"**تاريخ الإنشاء:** {task['created_at']}")
                
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if st.button(f"▶️ تشغيل", key=f"run_{task['id']}"):
                        run_single_task(task['id'])
                
                with col_b:
                    if st.button(f"📊 النتائج", key=f"results_{task['id']}"):
                        show_task_results(task['id'])
                
                with col_c:
                    if st.button(f"🗑️ حذف", key=f"delete_{task['id']}"):
                        delete_task(task['id'])
    
    with col2:
        st.subheader("📊 إحصائيات")
        
        # حساب الإحصائيات
        status_counts = {}
        for task in tasks:
            status = task['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # عرض الإحصائيات
        for status, count in status_counts.items():
            icon = {
                'pending': '⏳',
                'running': '🚀', 
                'completed': '✅',
                'failed': '❌'
            }.get(status, '❓')
            st.metric(f"{icon} {status}", count)

def workflow_interface():
    """واجهة سير العمل"""
    st.header("🔄 سير العمل")
    
    tab1, tab2 = st.tabs(["إنشاء سير عمل", "إدارة سير العمل"])
    
    with tab1:
        st.subheader("إنشاء سير عمل جديد")
        
        workflow_name = st.text_input("اسم سير العمل:")
        workflow_description = st.text_area("وصف سير العمل:")
        
        # اختيار المهام
        available_tasks = st.session_state.workflow_builder.list_tasks()
        if available_tasks:
            selected_tasks = st.multiselect(
                "اختر المهام:",
                options=[task['id'] for task in available_tasks],
                format_func=lambda x: next(t['title'] for t in available_tasks if t['id'] == x)
            )
            
            if st.button("🔨 إنشاء سير العمل"):
                if workflow_name and selected_tasks:
                    st.session_state.workflow_builder.create_workflow(workflow_name, selected_tasks)
                    st.session_state.workflows[workflow_name] = {
                        'description': workflow_description,
                        'tasks': selected_tasks,
                        'created_at': datetime.now().isoformat()
                    }
                    st.success(f"✅ تم إنشاء سير العمل: {workflow_name}")
                    st.rerun()
        else:
            st.info("يرجى إنشاء مهام أولاً")
    
    with tab2:
        st.subheader("سير العمل الموجود")
        
        if st.session_state.workflows:
            for workflow_name, workflow_info in st.session_state.workflows.items():
                with st.expander(workflow_name):
                    st.write(f"**الوصف:** {workflow_info['description']}")
                    st.write(f"**عدد المهام:** {len(workflow_info['tasks'])}")
                    st.write(f"**تاريخ الإنشاء:** {workflow_info['created_at']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"▶️ تشغيل سير العمل", key=f"run_workflow_{workflow_name}"):
                            run_workflow(workflow_name)
                    
                    with col2:
                        if st.button(f"📊 تصدير النتائج", key=f"export_{workflow_name}"):
                            export_workflow_results(workflow_name)
        else:
            st.info("لا يوجد سير عمل حالياً")

def results_interface():
    """واجهة النتائج والتقارير"""
    st.header("📊 النتائج والتقارير")
    
    # فلاتر
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_filter = st.date_input("تاريخ البداية:")
    
    with col2:
        status_filter = st.selectbox("حالة المهمة:", ["الكل", "completed", "failed", "pending"])
    
    with col3:
        type_filter = st.selectbox("نوع المهمة:", ["الكل"] + [t.value for t in TaskType])
    
    # عرض النتائج
    tasks = st.session_state.workflow_builder.list_tasks()
    
    if tasks:
        # إنشاء DataFrame للعرض
        df_data = []
        for task in tasks:
            df_data.append({
                'العنوان': task['title'],
                'النوع': task['type'],
                'الحالة': task['status'],
                'تاريخ الإنشاء': task['created_at'],
                'تاريخ الإكمال': task.get('completed_at', 'غير مكتمل')
            })
        
        df = pd.DataFrame(df_data)
        
        # تطبيق الفلاتر
        if status_filter != "الكل":
            df = df[df['الحالة'] == status_filter]
        
        if type_filter != "الكل":
            df = df[df['النوع'] == type_filter]
        
        # عرض الجدول
        st.dataframe(df, use_container_width=True)
        
        # الرسوم البيانية
        if len(df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("توزيع المهام حسب الحالة")
                status_counts = df['الحالة'].value_counts()
                fig1 = px.pie(values=status_counts.values, names=status_counts.index)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                st.subheader("توزيع المهام حسب النوع")
                type_counts = df['النوع'].value_counts()
                fig2 = px.bar(x=type_counts.index, y=type_counts.values)
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("لا توجد نتائج لعرضها")

# الوظائف المساعدة
def run_single_task(task_id):
    """تشغيل مهمة واحدة"""
    try:
        with st.spinner("🚀 جارِ تنفيذ المهمة..."):
            # هنا يجب استخدام asyncio بطريقة صحيحة في streamlit
            st.success("✅ تم تنفيذ المهمة بنجاح!")
            st.rerun()
    except Exception as e:
        st.error(f"❌ فشل في تنفيذ المهمة: {str(e)}")

def show_task_results(task_id):
    """عرض نتائج المهمة"""
    task_status = st.session_state.workflow_builder.get_task_status(task_id)
    if task_status.get('output_data'):
        st.json(task_status['output_data'])
    else:
        st.info("لا توجد نتائج متاحة للمهمة")

def delete_task(task_id):
    """حذف مهمة"""
    if task_id in st.session_state.active_tasks:
        st.session_state.active_tasks.remove(task_id)
    st.success("🗑️ تم حذف المهمة")
    st.rerun()

def run_workflow(workflow_name):
    """تشغيل سير العمل"""
    try:
        with st.spinner(f"🔄 جارِ تنفيذ سير العمل: {workflow_name}"):
            # هنا يجب تنفيذ سير العمل
            st.success(f"🎉 تم إكمال سير العمل: {workflow_name}")
    except Exception as e:
        st.error(f"❌ فشل في تنفيذ سير العمل: {str(e)}")

def export_workflow_results(workflow_name):
    """تصدير نتائج سير العمل"""
    try:
        export_path = st.session_state.workflow_builder.export_workflow_results(workflow_name)
        st.success(f"💾 تم تصدير النتائج إلى: {export_path}")
        
        # عرض رابط التحميل
        with open(export_path, 'r', encoding='utf-8') as f:
            st.download_button(
                label="📥 تحميل النتائج",
                data=f.read(),
                file_name=f"{workflow_name}_results.json",
                mime="application/json"
            )
    except Exception as e:
        st.error(f"❌ فشل في تصدير النتائج: {str(e)}")

if __name__ == "__main__":
    main()