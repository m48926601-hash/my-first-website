from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Trainee
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Trainee, DietProgram, TrainingProgram
from django.utils import timezone
from datetime import timedelta

def home_page(request):
    return render(request, 'athletes/home.html')

# دالة التحقق من تسجيل الدخول
def coach_login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('coach_dashboard') # إذا صح، فوت عاللوحة
        else:
            # إذا غلط، ارجع طلع الشاشة مع رسالة خطأ
            return render(request, 'athletes/coach_login.html', {'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'})
    
    return render(request, 'athletes/coach_login.html')

# هاد السطر هو القفل! بيمنع أي حدا يفوت عاللوحة بدون تسجيل دخول
@login_required(login_url='coach_login')
def coach_dashboard(request):
    # إحصائيات عامة
    total_trainees = Trainee.objects.count()
    active_trainees = Trainee.objects.filter(end_date__gte=timezone.now().date()).count()
    total_diet = DietProgram.objects.count()
    total_training = TrainingProgram.objects.count()
    latest_trainees = Trainee.objects.all().order_by('-id')[:5]

    # --- دارة التنبيهات الذكية ---
    today = timezone.now().date()
    next_week = today + timedelta(days=7) # بنضيف 7 أيام لتاريخ اليوم
    
    # منجيب كل المتدربين اللي تاريخ نهاية اشتراكهم أصغر أو يساوي تاريخ الأسبوع القادم
    expiring_trainees = Trainee.objects.filter(end_date__lte=next_week, end_date__gte=today).order_by('end_date')

    context = {
        'total_trainees': total_trainees,
        'active_trainees': active_trainees,
        'total_diet': total_diet,
        'total_training': total_training,
        'latest_trainees': latest_trainees,
        'expiring_trainees': expiring_trainees, # بعتنا قائمة التنبيهات للشاشة
    }
    return render(request, 'athletes/coach_dashboard.html', context)

# دالة تسجيل الخروج الآمن
def coach_logout_view(request):
    logout(request)
    return redirect('home') # بترجعك للصفحة الرئيسية للموقع

# دالة صفحة قائمة المتدربين
@login_required(login_url='coach_login')
def trainees_list_view(request):
    # سحب كل المتدربين من قاعدة البيانات
    all_trainees = Trainee.objects.all().order_by('-start_date')
    return render(request, 'athletes/coach_trainees.html', {'all_trainees': all_trainees})
# دالة إضافة متدرب جديد وتوليد حسابه تلقائياً
@login_required(login_url='coach_login')
def add_trainee_view(request):
    if request.method == 'POST':
        # 1. سحب بيانات الحساب أولاً لإنشائه بنظام جانغو
        user_name = request.POST.get('username')
        pass_word = request.POST.get('password')
        
        # إنشاء حساب مستخدم حقيقي في النظام للمتدرب
        new_user = User.objects.create_user(username=user_name, password=pass_word)
        
        # 2. سحب باقي بيانات المتدرب من الاستمارة
        Trainee.objects.create(
            user=new_user, # ربط ملف المتدرب بحسابه الجديد فوراً
            name=request.POST.get('name'),
            phone_number=request.POST.get('phone_number'),
            height=request.POST.get('height'),
            current_weight=request.POST.get('current_weight'),
            target_weight=request.POST.get('target_weight'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            monthly_cost=request.POST.get('monthly_cost'),
            coach_notes=request.POST.get('coach_notes')
        )
        # بعد الحفظ بنجاح، أرجع الكوتش للوحة التحكم الرئيسية
        return redirect('coach_dashboard')
        
    return render(request, 'athletes/add_trainee.html')
@login_required(login_url='coach_login')
def add_training_view(request):
    # سحب كل المتدربين لنعرضهم بقائمة منسدلة ليختار الكوتش لمين البرنامج
    all_trainees = Trainee.objects.all()
    
    if request.method == 'POST':
        trainee_id = request.POST.get('trainee_id')
        title = request.POST.get('title')
        exercises_details = request.POST.get('exercises_details')
        
        # نجلب ملف المتدرب بناءً على اختياره من القائمة
        selected_trainee = Trainee.objects.get(id=trainee_id)
        
        # إنشاء البرنامج التدريبي وربطه بالمتدرب
        TrainingProgram.objects.create(
            trainee=selected_trainee,
            title=title,
            exercises_details=exercises_details
        )
        return redirect('coach_dashboard') # العودة للوحة بعد الحفظ
        
    return render(request, 'athletes/add_training.html', {'all_trainees': all_trainees})
# دالة عرض ملف المتدرب المفصل للكوتش
@login_required(login_url='coach_login')
# دالة عرض ملف المتدرب المفصل للكوتش (محدثة لتشمل الغذاء)
@login_required(login_url='coach_login')
def trainee_profile_view(request, trainee_id):
    trainee = Trainee.objects.get(id=trainee_id)
    training_programs = TrainingProgram.objects.filter(trainee=trainee)
    # السطر الجديد: سحب البرامج الغذائية
    diet_programs = DietProgram.objects.filter(trainee=trainee)
    
    context = {
        'trainee': trainee,
        'training_programs': training_programs,
        'diet_programs': diet_programs, # تمريرها للشاشة
    }
    return render(request, 'athletes/trainee_profile.html', context)


# دالة إضافة برنامج غذائي سردي
@login_required(login_url='coach_login')
def add_diet_view(request):
    all_trainees = Trainee.objects.all()
    
    if request.method == 'POST':
        trainee_id = request.POST.get('trainee_id')
        title = request.POST.get('title')
        meals_details = request.POST.get('meals_details')
        
        selected_trainee = Trainee.objects.get(id=trainee_id)
        
        DietProgram.objects.create(
            trainee=selected_trainee,
            title=title,
            meals_details=meals_details
        )
        return redirect('coach_dashboard')
        
    return render(request, 'athletes/add_diet.html', {'all_trainees': all_trainees})
# دالة تسجيل دخول المتدرب
def trainee_login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('trainee_dashboard') # التوجيه للوحة المتدرب
        else:
            return render(request, 'athletes/trainee_login.html', {'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'})
            
    return render(request, 'athletes/trainee_login.html')

# دالة لوحة تحكم المتدرب (للقراءة فقط وبالمؤشرات الحقيقية)
@login_required(login_url='trainee_login')
def trainee_dashboard_view(request):
    try:
        # النظام بيعرف تلقائياً مين اللاعب اللي مسجل دخول هلق وبيجيب ملفه
        trainee = request.user.trainee
        training_programs = TrainingProgram.objects.filter(trainee=trainee)
        diet_programs = DietProgram.objects.filter(trainee=trainee)
    except Trainee.DoesNotExist:
        # حماية: إذا الكوتش حاول يدخل لهون بالغلط، بنرجعه للوحة التحكم تبعه
        return redirect('coach_dashboard')
        
    context = {
        'trainee': trainee,
        'training_programs': training_programs,
        'diet_programs': diet_programs,
    }
    return render(request, 'athletes/trainee_dashboard.html', context)

# دالة تسجيل خروج المتدرب
def trainee_logout_view(request):
    logout(request)
    return redirect('home')
# دالة تعديل بيانات وتحديث وزن المتدرب
@login_required(login_url='coach_login')
def edit_trainee_view(request, trainee_id):
    # جلب اللاعب المطلوب بناءً على رقمه
    trainee = Trainee.objects.get(id=trainee_id)
    
    if request.method == 'POST':
        # سحب البيانات الجديدة من الفورم وتحديثها
        trainee.name = request.POST.get('name')
        trainee.phone_number = request.POST.get('phone_number')
        trainee.height = request.POST.get('height')
        trainee.current_weight = request.POST.get('current_weight')
        trainee.target_weight = request.POST.get('target_weight')
        trainee.monthly_cost = request.POST.get('monthly_cost')
        
        # التأكد من عدم مسح التواريخ إذا لم يتم إدخال جديد
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        if start: trainee.start_date = start
        if end: trainee.end_date = end
        
        trainee.coach_notes = request.POST.get('coach_notes')
        
        # حفظ التعديلات في قاعدة البيانات
        trainee.save()
        
        # إرجاع الكوتش لملف اللاعب ليشوف التعديلات فوراً
        return redirect('trainee_profile', trainee_id=trainee.id)
        
    return render(request, 'athletes/edit_trainee.html', {'trainee': trainee})