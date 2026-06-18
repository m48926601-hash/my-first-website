from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from django.templatetags.static import static
from django.utils import timezone
import json
from datetime import timedelta
from .models import Trainee, DietProgram, TrainingProgram, ChatMessage

# ====================================================
# 1. الصفحات العامة وتسجيل الدخول والخروج
# ====================================================

def home_page(request):
    return render(request, 'athletes/home.html')

def coach_login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('coach_dashboard')
        else:
            return render(request, 'athletes/coach_login.html', {'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'})
    return render(request, 'athletes/coach_login.html')

def coach_logout_view(request):
    logout(request)
    return redirect('home')

# دالة تسجيل دخول المتدرب (محدثة لتعمل برقم الجوال)
def trainee_login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number') # استلام رقم الجوال
        p = request.POST.get('password')
        
        # المصادقة باستخدام رقم الجوال كأنه username
        user = authenticate(request, username=phone, password=p)
        
        if user is not None:
            login(request, user)
            return redirect('trainee_dashboard')
        else:
            return render(request, 'athletes/trainee_login.html', {'error': 'رقم الجوال أو كلمة المرور غير صحيحة'})
            
    return render(request, 'athletes/trainee_login.html')
def trainee_logout_view(request):
    logout(request)
    return redirect('home')

# ====================================================
# 2. لوحات التحكم (Dashboards)
# ====================================================

@login_required(login_url='coach_login')
def coach_dashboard(request):
    # إحصائيات عامة للكابتن
    total_trainees = Trainee.objects.count()
    active_trainees = Trainee.objects.filter(end_date__gte=timezone.now().date()).count()
    total_diet = DietProgram.objects.count()
    total_training = TrainingProgram.objects.count()
    latest_trainees = Trainee.objects.all().order_by('-id')[:5]

    # دارة التنبيهات الذكية (المتدربين اللي اشتراكهم بيخلص قريباً)
    today = timezone.now().date()
    next_week = today + timedelta(days=7)
    expiring_trainees = Trainee.objects.filter(end_date__lte=next_week, end_date__gte=today).order_by('end_date')

    context = {
        'total_trainees': total_trainees,
        'active_trainees': active_trainees,
        'total_diet': total_diet,
        'total_training': total_training,
        'latest_trainees': latest_trainees,
        'expiring_trainees': expiring_trainees,
    }
    return render(request, 'athletes/coach_dashboard.html', context)

@login_required(login_url='trainee_login')
def trainee_dashboard_view(request):
    try:
        # استدعاء ملف المتدرب وبرامجه تلقائياً حسب حسابه المسجل الدخول فيه
        trainee = request.user.trainee
        training_programs = TrainingProgram.objects.filter(trainee=trainee)
        diet_programs = DietProgram.objects.filter(trainee=trainee)
    except Trainee.DoesNotExist:
        return redirect('coach_dashboard') # حماية من دخول الكابتن لهون بالخطأ

    coach_user = User.objects.filter(is_staff=True).exclude(id=request.user.id).first()
        
    context = {
        'trainee': trainee,
        'training_programs': training_programs,
        'diet_programs': diet_programs,
        'coach_user': coach_user,
    }
    return render(request, 'athletes/trainee_dashboard.html', context)

# ====================================================
# 3. إدارة المتدربين (إضافة، تعديل، عرض)
# ====================================================

@login_required(login_url='coach_login')
def trainees_list_view(request):
    all_trainees = Trainee.objects.all().order_by('-start_date')
    return render(request, 'athletes/coach_trainees.html', {'all_trainees': all_trainees})

@login_required(login_url='coach_login')
def add_trainee_view(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        pass_word = request.POST.get('password')
        
        # حماية ضد تكرار اسم الحساب
        if User.objects.filter(username=user_name).exists():
            return render(request, 'athletes/add_trainee.html', {
                'error': 'اسم المستخدم هذا محجوز مسبقاً! الرجاء كتابة اسم مستخدم آخر فريد للمتدرب الجديد.'
            })

        new_user = User.objects.create_user(username=user_name, password=pass_word)
        
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        Trainee.objects.create(
            user=new_user, 
            name=request.POST.get('name'),
            phone_number=request.POST.get('phone_number'),
            height=request.POST.get('height') or 0,
            current_weight=request.POST.get('current_weight') or 0,
            target_weight=request.POST.get('target_weight') or 0,
            start_date=start_date if start_date else timezone.now().date(),
            end_date=end_date if end_date else timezone.now().date(),
            monthly_cost=request.POST.get('monthly_cost') or 0,
            coach_notes=request.POST.get('notes')
        )
        return redirect('coach_dashboard')
        
    return render(request, 'athletes/add_trainee.html')

@login_required(login_url='coach_login')
def trainee_profile_view(request, trainee_id):
    trainee = Trainee.objects.get(id=trainee_id)
    training_programs = TrainingProgram.objects.filter(trainee=trainee)
    diet_programs = DietProgram.objects.filter(trainee=trainee)
    
    context = {
        'trainee': trainee,
        'training_programs': training_programs,
        'diet_programs': diet_programs,
    }
    return render(request, 'athletes/trainee_profile.html', context)

@login_required(login_url='coach_login')
def edit_trainee_view(request, trainee_id):
    trainee = Trainee.objects.get(id=trainee_id)
    
    if request.method == 'POST':
        trainee.name = request.POST.get('name')
        trainee.phone_number = request.POST.get('phone_number')
        trainee.height = request.POST.get('height')
        trainee.current_weight = request.POST.get('current_weight')
        trainee.target_weight = request.POST.get('target_weight')
        trainee.monthly_cost = request.POST.get('monthly_cost')
        
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        if start: trainee.start_date = start
        if end: trainee.end_date = end
        
        trainee.coach_notes = request.POST.get('coach_notes')
        trainee.save()
        return redirect('trainee_profile', trainee_id=trainee.id)
        
    return render(request, 'athletes/edit_trainee.html', {'trainee': trainee})

# ====================================================
# 4. إدارة البرامج (التدريبية والغذائية)
# ====================================================

@login_required(login_url='coach_login')
def add_training_view(request):
    all_trainees = Trainee.objects.all()
    
    if request.method == 'POST':
        trainee_id = request.POST.get('trainee_id')
        title = request.POST.get('title')
        exercises_details = request.POST.get('exercises_details')
        media_file = request.FILES.get('media_file')
        
        # حماية ضد إرسال قائمة فارغة
        if not trainee_id:
            return render(request, 'athletes/add_training.html', {
                'all_trainees': all_trainees, 
                'error': 'يرجى اختيار المتدرب من القائمة المنسدلة أولاً!'
            })
            
        try:
            selected_trainee = Trainee.objects.get(id=trainee_id)
            TrainingProgram.objects.create(
                trainee=selected_trainee,
                title=title,
                exercises_details=exercises_details,
                media_file=media_file
            )
            return redirect('coach_dashboard')
        except Trainee.DoesNotExist:
            return render(request, 'athletes/add_training.html', {
                'all_trainees': all_trainees, 
                'error': 'حدث خطأ: المتدرب المحدد غير موجود في النظام.'
            })
        
    return render(request, 'athletes/add_training.html', {'all_trainees': all_trainees})

@login_required(login_url='coach_login')
def add_diet_view(request):
    all_trainees = Trainee.objects.all()
    
    if request.method == 'POST':
        trainee_id = request.POST.get('trainee_id')
        title = request.POST.get('title')
        meals_details = request.POST.get('meals_details')
        media_file = request.FILES.get('media_file')
        
        # حماية ضد إرسال قائمة فارغة
        if not trainee_id:
            return render(request, 'athletes/add_diet.html', {
                'all_trainees': all_trainees, 
                'error': 'يرجى اختيار المتدرب من القائمة المنسدلة أولاً!'
            })
            
        try:
            selected_trainee = Trainee.objects.get(id=trainee_id)
            DietProgram.objects.create(
                trainee=selected_trainee,
                title=title,
                meals_details=meals_details,
                media_file=media_file
            )
            return redirect('coach_dashboard')
        except Trainee.DoesNotExist:
            return render(request, 'athletes/add_diet.html', {
                'all_trainees': all_trainees, 
                'error': 'حدث خطأ: المتدرب المحدد غير موجود في النظام.'
            })
        
    return render(request, 'athletes/add_diet.html', {'all_trainees': all_trainees})

# دالة تسجيل المتدرب (محدثة لاستقبال التواريخ والصور)
def trainee_register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone_number').strip()
        password = request.POST.get('password')
        
        height = request.POST.get('height') or 0
        current_weight = request.POST.get('current_weight') or 0
        target_weight = request.POST.get('target_weight') or 0
        
        # سحب التواريخ من الواجهة
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if User.objects.filter(username=phone).exists():
            return render(request, 'athletes/trainee_register.html', {
                'error': 'رقم الجوال هذا مسجل مسبقاً! الرجاء تسجيل الدخول أو استخدام رقم آخر.'
            })

        new_user = User.objects.create_user(username=phone, password=password)
        
        # حفظ المتدرب مع استقبال الصور من request.FILES
        Trainee.objects.create(
            user=new_user, 
            name=name,
            phone_number=phone,
            height=height,
            current_weight=current_weight,
            target_weight=target_weight,
            start_date=start_date if start_date else timezone.now().date(),
            end_date=end_date if end_date else timezone.now().date(),
            monthly_cost=0,
            coach_notes="تسجيل ذاتي من الموقع - بانتظار تفعيل الكابتن.",
            front_image=request.FILES.get('front_image'), # الصورة الأمامية
            side_image=request.FILES.get('side_image'),   # الصورة الجانبية
            back_image=request.FILES.get('back_image')    # الصورة الخلفية
        )
        
        login(request, new_user)
        return redirect('trainee_dashboard')
        
    return render(request, 'athletes/trainee_register.html')


@login_required
def chat_room(request, other_user_id):
    other_user = get_object_or_404(User, id=other_user_id)
    
    # 1. معالجة إرسال رسالة جديدة (POST) عن طريق AJAX
    if request.method == 'POST':
        message_text = request.POST.get('message_text', '').strip()
        media_file = request.FILES.get('media_file', None)
        
        if message_text or media_file:
            msg = ChatMessage.objects.create(
                sender=request.user,
                receiver=other_user,
                message_text=message_text,
                media_file=media_file
            )
            return JsonResponse({
                'status': 'success',
                'message_text': msg.message_text,
                'media_url': msg.media_file.url if msg.media_file else '',
                'sender_id': msg.sender.id,
                'timestamp': msg.timestamp.strftime('%H:%M')
            })
        return JsonResponse({'status': 'error', 'message': 'رسالة فارغة'}, status=400)

    # 2. تحويل الرسائل المستقبلة إلى "مقروءة" بمجرد فتح الغرفة
    ChatMessage.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    # 3. جلب التاريخ الكامل للمحادثة (الصادرة والواردة معاً)
    chat_history = ChatMessage.objects.filter(
        Q(sender=request.user, receiver=other_user) | 
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    # 4. تحديد اسم وصورة الترويسة ديناميكياً حسب من يفتح الشات
    # 4. تحديد اسم وصورة الترويسة ديناميكياً حسب من يفتح الشات
    if request.user.is_superuser or hasattr(request.user, 'coach'):
        try:
            chat_header_name = other_user.trainee.name if other_user.trainee.name else other_user.get_full_name() or other_user.username
            
            # 💡 التعديل هنا: استخدام front_image بدل profile_image
            if hasattr(other_user.trainee, 'front_image') and other_user.trainee.front_image:
                chat_header_image_url = other_user.trainee.front_image.url
            else:
                chat_header_image_url = '/static/images/trainee.jpg' # أو صورة افتراضية
        except:
            chat_header_name = other_user.username
            chat_header_image_url = '/static/images/coach3.PNG'
            
        chat_header_subtitle = "متدرب مشترك"
    else:
        # الحالي هو المتدرب -> يعرض دائماً الكابتن طارق
        chat_header_name = "الكابتن طارق راشد"
        chat_header_image_url = '/static/images/coach3.PNG'
        chat_header_subtitle = "المدرب الشخصي"

    return render(request, 'athletes/chat_room.html', {
        'other_user': other_user,
        'chat_history': chat_history,
        'chat_header_name': chat_header_name,
        'chat_header_image_url': chat_header_image_url,
        'chat_header_subtitle': chat_header_subtitle,
    })


@login_required
# ضف هذا التابع في نهاية ملف views.py
def check_unread_messages(request):
    if request.user.is_authenticated:
        # حساب عدد الرسائل التي لم تُقرأ وموجهة للمستخدم الحالي
        count = ChatMessage.objects.filter(receiver=request.user, is_read=False).count()
        return JsonResponse({'unread_count': count})
    return JsonResponse({'unread_count': 0})