#!/usr/bin/env python3
"""
Command Line Interface for AI Workflow Builder
واجهة سطر الأوامر للنظام
"""

import click
import asyncio
import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from rich import print as rprint

from main import AIWorkflowBuilder, TaskType
from config import Config, MESSAGES

console = Console()

@click.group()
@click.version_option(version="1.0.0", prog_name="AI Workflow Builder")
def cli():
    """🤖 AI Workflow Builder - نظام أتمتة المهام باستخدام الذكاء الاصطناعي"""
    if not Config.validate():
        console.print("[red]❌ يرجى إعداد OpenAI API key في متغيرات البيئة[/red]")
        sys.exit(1)

@cli.command()
@click.option('--type', 'task_type', type=click.Choice([t.value for t in TaskType]), required=True, help='نوع المهمة')
@click.option('--title', required=True, help='عنوان المهمة')
@click.option('--description', required=True, help='وصف المهمة')
@click.option('--input', 'input_file', type=click.Path(exists=True), help='ملف البيانات المدخلة (JSON)')
@click.option('--execute', is_flag=True, help='تنفيذ المهمة فوراً')
def create_task(task_type, title, description, input_file, execute):
    """إنشاء مهمة جديدة"""
    
    try:
        # قراءة بيانات الإدخال
        if input_file:
            with open(input_file, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
        else:
            input_data = get_interactive_input(TaskType(task_type))
        
        # إنشاء المهمة
        workflow_builder = AIWorkflowBuilder()
        task_id = workflow_builder.add_task(
            TaskType(task_type),
            title,
            description,
            input_data
        )
        
        console.print(f"[green]✅ تم إنشاء المهمة: {task_id}[/green]")
        
        # تنفيذ المهمة إذا طُلب ذلك
        if execute:
            console.print("[yellow]🚀 بدء تنفيذ المهمة...[/yellow]")
            asyncio.run(execute_task_by_id(workflow_builder, task_id))
            
    except Exception as e:
        console.print(f"[red]❌ خطأ: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.option('--workflow-file', type=click.Path(exists=True), required=True, help='ملف تعريف سير العمل (JSON)')
@click.option('--execute', is_flag=True, help='تنفيذ سير العمل فوراً')
def create_workflow(workflow_file, execute):
    """إنشاء سير عمل من ملف تعريف"""
    
    try:
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow_config = json.load(f)
        
        workflow_builder = AIWorkflowBuilder()
        
        # إنشاء المهام
        task_ids = []
        for task_config in workflow_config['tasks']:
            task_id = workflow_builder.add_task(
                TaskType(task_config['type']),
                task_config['title'],
                task_config['description'],
                task_config['input_data']
            )
            task_ids.append(task_id)
        
        # إنشاء سير العمل
        workflow_name = workflow_config['name']
        workflow_builder.create_workflow(workflow_name, task_ids)
        
        console.print(f"[green]✅ تم إنشاء سير العمل: {workflow_name}[/green]")
        console.print(f"[blue]📝 المهام: {len(task_ids)}[/blue]")
        
        # تنفيذ سير العمل
        if execute:
            console.print(f"[yellow]🔄 بدء تنفيذ سير العمل: {workflow_name}[/yellow]")
            asyncio.run(execute_workflow_by_name(workflow_builder, workflow_name))
            
    except Exception as e:
        console.print(f"[red]❌ خطأ: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'detailed']), default='table', help='تنسيق الإخراج')
def list_tasks(output_format):
    """عرض قائمة المهام"""
    
    try:
        workflow_builder = AIWorkflowBuilder()
        tasks = workflow_builder.list_tasks()
        
        if not tasks:
            console.print("[yellow]📝 لا توجد مهام[/yellow]")
            return
        
        if output_format == 'json':
            print(json.dumps(tasks, ensure_ascii=False, indent=2, default=str))
        elif output_format == 'detailed':
            for task in tasks:
                panel = Panel(
                    f"""[bold]{task['title']}[/bold]
                    
الوصف: {task['description']}
النوع: {task['type']}
الحالة: {task['status']}
تاريخ الإنشاء: {task['created_at']}
تاريخ الإكمال: {task.get('completed_at', 'غير مكتمل')}""",
                    title=f"مهمة: {task['id']}",
                    expand=False
                )
                console.print(panel)
        else:  # table format
            table = Table(title="📋 قائمة المهام")
            table.add_column("ID", style="cyan")
            table.add_column("العنوان", style="magenta")
            table.add_column("النوع", style="blue")
            table.add_column("الحالة", style="green")
            table.add_column("تاريخ الإنشاء", style="yellow")
            
            for task in tasks:
                status_color = {
                    'pending': '⏳',
                    'running': '🚀',
                    'completed': '✅',
                    'failed': '❌'
                }.get(task['status'], '❓')
                
                table.add_row(
                    task['id'][:8] + "...",
                    task['title'],
                    task['type'],
                    f"{status_color} {task['status']}",
                    task['created_at'][:10]
                )
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[red]❌ خطأ: {str(e)}[/red]")

@cli.command()
@click.argument('task_id')
def execute_task(task_id):
    """تنفيذ مهمة محددة"""
    
    try:
        workflow_builder = AIWorkflowBuilder()
        asyncio.run(execute_task_by_id(workflow_builder, task_id))
        
    except Exception as e:
        console.print(f"[red]❌ خطأ: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('workflow_name')
def execute_workflow(workflow_name):
    """تنفيذ سير عمل محدد"""
    
    try:
        workflow_builder = AIWorkflowBuilder()
        asyncio.run(execute_workflow_by_name(workflow_builder, workflow_name))
        
    except Exception as e:
        console.print(f"[red]❌ خطأ: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('task_id')
@click.option('--output', type=click.Path(), help='مسار حفظ النتائج')
def get_results(task_id, output):
    """الحصول على نتائج مهمة"""
    
    try:
        workflow_builder = AIWorkflowBuilder()
        task_status = workflow_builder.get_task_status(task_id)
        
        if not task_status:
            console.print(f"[red]❌ المهمة غير موجودة: {task_id}[/red]")
            return
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(task_status, f, ensure_ascii=False, indent=2, default=str)
            console.print(f"[green]💾 تم حفظ النتائج في: {output}[/green]")
        else:
            if task_status.get('output_data'):
                console.print("\n[bold blue]📊 نتائج المهمة:[/bold blue]")
                rprint(task_status['output_data'])
            else:
                console.print("[yellow]⏳ المهمة لم تكتمل بعد[/yellow]")
                
    except Exception as e:
        console.print(f"[red]❌ خطأ: {str(e)}[/red]")

@cli.command()
@click.option('--task-type', type=click.Choice([t.value for t in TaskType]), help='نوع المهمة')
def interactive():
    """الوضع التفاعلي لإنشاء المهام"""
    
    console.print(Panel.fit("🤖 مرحباً بك في الوضع التفاعلي لـ AI Workflow Builder", style="bold blue"))
    
    try:
        workflow_builder = AIWorkflowBuilder()
        
        while True:
            console.print("\n[bold]اختر العملية:[/bold]")
            console.print("1. إنشاء مهمة جديدة")
            console.print("2. عرض المهام")
            console.print("3. تنفيذ مهمة")
            console.print("4. إنشاء سير عمل")
            console.print("5. الخروج")
            
            choice = click.prompt("\nاختيارك", type=int)
            
            if choice == 1:
                create_interactive_task(workflow_builder)
            elif choice == 2:
                show_interactive_tasks(workflow_builder)
            elif choice == 3:
                execute_interactive_task(workflow_builder)
            elif choice == 4:
                create_interactive_workflow(workflow_builder)
            elif choice == 5:
                console.print("[green]👋 وداعاً![/green]")
                break
            else:
                console.print("[red]❌ اختيار غير صحيح[/red]")
                
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 تم إيقاف البرنامج بواسطة المستخدم[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ خطأ: {str(e)}[/red]")

def create_interactive_task(workflow_builder):
    """إنشاء مهمة في الوضع التفاعلي"""
    
    console.print("\n[bold blue]✨ إنشاء مهمة جديدة[/bold blue]")
    
    # اختيار نوع المهمة
    task_types = list(TaskType)
    console.print("\nأنواع المهام المتاحة:")
    for i, task_type in enumerate(task_types, 1):
        type_names = {
            TaskType.CONTENT_WRITING: "📝 كتابة المحتوى",
            TaskType.DATA_ANALYSIS: "📊 تحليل البيانات",
            TaskType.TEXT_SUMMARIZATION: "📄 تلخيص النصوص",
            TaskType.EMAIL_GENERATION: "📧 كتابة الإيميلات",
            TaskType.TRANSLATION: "🌐 الترجمة",
            TaskType.CODE_GENERATION: "💻 توليد الكود"
        }
        console.print(f"{i}. {type_names[task_type]}")
    
    type_choice = click.prompt("اختر نوع المهمة", type=int) - 1
    if type_choice < 0 or type_choice >= len(task_types):
        console.print("[red]❌ اختيار غير صحيح[/red]")
        return
    
    selected_type = task_types[type_choice]
    
    # معلومات المهمة
    title = click.prompt("عنوان المهمة")
    description = click.prompt("وصف المهمة")
    
    # بيانات الإدخال حسب نوع المهمة
    input_data = get_interactive_input(selected_type)
    
    # إنشاء المهمة
    task_id = workflow_builder.add_task(selected_type, title, description, input_data)
    console.print(f"[green]✅ تم إنشاء المهمة: {task_id}[/green]")
    
    # سؤال عن التنفيذ الفوري
    if click.confirm("هل تريد تنفيذ المهمة الآن؟"):
        asyncio.run(execute_task_by_id(workflow_builder, task_id))

def get_interactive_input(task_type):
    """الحصول على بيانات الإدخال في الوضع التفاعلي"""
    
    if task_type == TaskType.CONTENT_WRITING:
        return {
            "prompt": click.prompt("المطلوب كتابته"),
            "content_type": click.prompt("نوع المحتوى", default="مقال"),
            "language": click.prompt("اللغة", default="arabic"),
            "tone": click.prompt("النبرة", default="professional")
        }
    
    elif task_type == TaskType.DATA_ANALYSIS:
        data_path = click.prompt("مسار ملف البيانات")
        return {
            "data_path": data_path,
            "analysis_type": click.prompt("نوع التحليل", default="basic"),
            "include_charts": click.confirm("تضمين الرسوم البيانية؟", default=True)
        }
    
    elif task_type == TaskType.TEXT_SUMMARIZATION:
        return {
            "text": click.prompt("النص المراد تلخيصه"),
            "max_length": click.prompt("الحد الأقصى للكلمات", type=int, default=150),
            "language": click.prompt("لغة الملخص", default="arabic")
        }
    
    elif task_type == TaskType.EMAIL_GENERATION:
        return {
            "purpose": click.prompt("الغرض من الإيميل"),
            "recipient": click.prompt("المستلم"),
            "tone": click.prompt("النبرة", default="professional"),
            "language": click.prompt("اللغة", default="arabic")
        }
    
    elif task_type == TaskType.TRANSLATION:
        return {
            "text": click.prompt("النص المراد ترجمته"),
            "source_language": click.prompt("اللغة المصدر", default="auto"),
            "target_language": click.prompt("اللغة المستهدفة", default="arabic")
        }
    
    elif task_type == TaskType.CODE_GENERATION:
        return {
            "description": click.prompt("وصف الكود المطلوب"),
            "programming_language": click.prompt("لغة البرمجة", default="python"),
            "include_comments": click.confirm("تضمين التعليقات؟", default=True)
        }
    
    return {}

def show_interactive_tasks(workflow_builder):
    """عرض المهام في الوضع التفاعلي"""
    
    tasks = workflow_builder.list_tasks()
    
    if not tasks:
        console.print("[yellow]📝 لا توجد مهام[/yellow]")
        return
    
    table = Table(title="📋 قائمة المهام الحالية")
    table.add_column("#", style="cyan", width=3)
    table.add_column("العنوان", style="magenta")
    table.add_column("النوع", style="blue")
    table.add_column("الحالة", style="green")
    
    for i, task in enumerate(tasks, 1):
        status_icon = {
            'pending': '⏳',
            'running': '🚀',
            'completed': '✅',
            'failed': '❌'
        }.get(task['status'], '❓')
        
        table.add_row(
            str(i),
            task['title'][:30] + ("..." if len(task['title']) > 30 else ""),
            task['type'],
            f"{status_icon} {task['status']}"
        )
    
    console.print(table)

def execute_interactive_task(workflow_builder):
    """تنفيذ مهمة في الوضع التفاعلي"""
    
    tasks = workflow_builder.list_tasks()
    
    if not tasks:
        console.print("[yellow]📝 لا توجد مهام لتنفيذها[/yellow]")
        return
    
    show_interactive_tasks(workflow_builder)
    
    task_index = click.prompt("اختر رقم المهمة للتنفيذ", type=int) - 1
    
    if task_index < 0 or task_index >= len(tasks):
        console.print("[red]❌ رقم غير صحيح[/red]")
        return
    
    task_id = tasks[task_index]['id']
    asyncio.run(execute_task_by_id(workflow_builder, task_id))

def create_interactive_workflow(workflow_builder):
    """إنشاء سير عمل في الوضع التفاعلي"""
    
    tasks = workflow_builder.list_tasks()
    
    if not tasks:
        console.print("[yellow]📝 لا توجد مهام لإنشاء سير عمل[/yellow]")
        return
    
    console.print("\n[bold blue]🔄 إنشاء سير عمل جديد[/bold blue]")
    
    workflow_name = click.prompt("اسم سير العمل")
    
    show_interactive_tasks(workflow_builder)
    
    selected_tasks = []
    console.print("\nاختر المهام (أدخل أرقام المهام مفصولة بفواصل):")
    task_numbers = click.prompt("أرقام المهام").split(',')
    
    for num_str in task_numbers:
        try:
            task_index = int(num_str.strip()) - 1
            if 0 <= task_index < len(tasks):
                selected_tasks.append(tasks[task_index]['id'])
            else:
                console.print(f"[yellow]⚠️ تم تجاهل الرقم غير الصحيح: {num_str.strip()}[/yellow]")
        except ValueError:
            console.print(f"[yellow]⚠️ تم تجاهل القيمة غير الصحيحة: {num_str.strip()}[/yellow]")
    
    if not selected_tasks:
        console.print("[red]❌ لم يتم اختيار أي مهام صحيحة[/red]")
        return
    
    workflow_builder.create_workflow(workflow_name, selected_tasks)
    console.print(f"[green]✅ تم إنشاء سير العمل: {workflow_name}[/green]")
    console.print(f"[blue]📝 المهام المختارة: {len(selected_tasks)}[/blue]")
    
    if click.confirm("هل تريد تنفيذ سير العمل الآن؟"):
        asyncio.run(execute_workflow_by_name(workflow_builder, workflow_name))

async def execute_task_by_id(workflow_builder, task_id):
    """تنفيذ مهمة بواسطة معرفها"""
    
    tasks = workflow_builder.list_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        console.print(f"[red]❌ المهمة غير موجودة: {task_id}[/red]")
        return
    
    task_obj = None
    for t in workflow_builder.tasks:
        if t.id == task_id:
            task_obj = t
            break
    
    if not task_obj:
        console.print(f"[red]❌ خطأ في العثور على المهمة[/red]")
        return
    
    try:
        with console.status(f"[bold green]🚀 جارِ تنفيذ المهمة: {task['title']}"):
            result = await workflow_builder.execute_task(task_obj)
        
        console.print(f"[green]✅ تم إكمال المهمة بنجاح[/green]")
        
        # عرض النتائج
        if result:
            console.print("\n[bold blue]📊 النتائج:[/bold blue]")
            if isinstance(result, dict):
                for key, value in result.items():
                    if key == 'content' and len(str(value)) > 200:
                        console.print(f"[cyan]{key}:[/cyan] {str(value)[:200]}...")
                    else:
                        console.print(f"[cyan]{key}:[/cyan] {value}")
            else:
                console.print(result)
                
    except Exception as e:
        console.print(f"[red]❌ فشل في تنفيذ المهمة: {str(e)}[/red]")

async def execute_workflow_by_name(workflow_builder, workflow_name):
    """تنفيذ سير عمل بواسطة اسمه"""
    
    try:
        console.print(f"[yellow]🔄 بدء تنفيذ سير العمل: {workflow_name}[/yellow]")
        
        with console.status(f"[bold green]جارِ تنفيذ سير العمل: {workflow_name}"):
            results = await workflow_builder.execute_workflow(workflow_name)
        
        console.print(f"[green]🎉 تم إكمال سير العمل بنجاح[/green]")
        console.print(f"[blue]📊 تم إنتاج {len(results)} نتيجة[/blue]")
        
        # تصدير النتائج
        export_path = workflow_builder.export_workflow_results(workflow_name)
        console.print(f"[green]💾 تم حفظ النتائج في: {export_path}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ فشل في تنفيذ سير العمل: {str(e)}[/red]")

@cli.command()
def generate_config():
    """إنشاء ملف إعداد نموذجي"""
    
    workflow_config = {
        "name": "مثال_سير_عمل",
        "description": "مثال على سير عمل للمحتوى والتحليل",
        "tasks": [
            {
                "type": "content_writing",
                "title": "كتابة مقال عن الذكاء الاصطناعي",
                "description": "كتابة مقال شامل عن تطبيقات الذكاء الاصطناعي",
                "input_data": {
                    "prompt": "اكتب مقالاً عن فوائد الذكاء الاصطناعي في التعليم",
                    "content_type": "مقال",
                    "language": "arabic",
                    "tone": "professional"
                }
            },
            {
                "type": "text_summarization",
                "title": "تلخيص المقال",
                "description": "إنشاء ملخص للمقال المكتوب",
                "input_data": {
                    "text": "سيتم استخدام نتيجة المهمة السابقة",
                    "max_length": 100,
                    "language": "arabic"
                }
            }
        ]
    }
    
    config_file = "workflow_example.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(workflow_config, f, ensure_ascii=False, indent=2)
    
    console.print(f"[green]✅ تم إنشاء ملف الإعداد النموذجي: {config_file}[/green]")
    console.print("[blue]يمكنك تعديل الملف واستخدامه مع الأمر create-workflow[/blue]")

if __name__ == "__main__":
    cli()