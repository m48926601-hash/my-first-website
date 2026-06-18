from django.db import models
from django.contrib.auth.models import User # استيراد نظام الحسابات لتوليد يوزر وباسورد للمتدرب

class Trainee(models.Model):
    # ربط المتدرب بحساب تسجيل دخول
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="حساب الدخول")
    
    name = models.CharField(max_length=100, verbose_name="الاسم الكامل")
    phone_number = models.CharField(max_length=20, verbose_name="رقم الجوال", null=True, blank=True)
    height = models.FloatField(verbose_name="الطول (سم)")
    current_weight = models.FloatField(verbose_name="الوزن الحالي (كغ)")
    target_weight = models.FloatField(verbose_name="الوزن المستهدف (كغ)")
    start_date = models.DateField(verbose_name="تاريخ البدء بالتسجيل")
    end_date = models.DateField(verbose_name="تاريخ الانتهاء")
    monthly_cost = models.FloatField(verbose_name="التكلفة شهرياً", null=True, blank=True)
    
    coach_notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات المدرب (سرية)")
    # حقول الصور الاختيارية (مسموح تكون فاضية null=True, blank=True)
    front_image = models.ImageField(upload_to='trainees_images/', null=True, blank=True)
    side_image = models.ImageField(upload_to='trainees_images/', null=True, blank=True)
    back_image = models.ImageField(upload_to='trainees_images/', null=True, blank=True)
    
    class Meta:
        verbose_name = "متدرب"
        verbose_name_plural = "المتدربون"

    def __str__(self):
        return self.name

class WeightRecord(models.Model):
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, verbose_name="المتدرب")
    weight = models.FloatField(verbose_name="الوزن المسجل (كغ)")
    date_recorded = models.DateField(auto_now_add=True, verbose_name="تاريخ التسجيل")

    class Meta:
        verbose_name = "سجل وزن"
        verbose_name_plural = "سجلات الأوزان"

    def __str__(self):
        return f"{self.trainee.name} - {self.weight} kg"

# --- الجداول الجديدة الخاصة بالبرامج ---

class DietProgram(models.Model):
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, verbose_name="المتدرب")
    title = models.CharField(max_length=100, verbose_name="عنوان اليوم (مثال: اليوم الأول)")
    meals_details = models.TextField(verbose_name="تفاصيل الوجبات")
    media_file = models.FileField(upload_to='diet_media/', blank=True, null=True)
    
    class Meta:
        verbose_name = "برنامج غذائي"
        verbose_name_plural = "البرامج الغذائية"

    def __str__(self):
        return f"{self.trainee.name} - {self.title}"

class TrainingProgram(models.Model):
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, verbose_name="المتدرب")
    title = models.CharField(max_length=100, verbose_name="عنوان اليوم (مثال: يوم الظهر والبايسبس)")
    exercises_details = models.TextField(verbose_name="تفاصيل التمارين")
    media_file = models.FileField(upload_to='training_media/', blank=True, null=True)
    
    class Meta:
        verbose_name = "برنامج تدريبي"
        verbose_name_plural = "البرامج التدريبية"

    def __str__(self):
        return f"{self.trainee.name} - {self.title}"


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_chat_messages", verbose_name="المرسل")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_chat_messages", verbose_name="المستقبل")
    message_text = models.TextField(blank=True, null=True, verbose_name="نص الرسالة")
    media_file = models.FileField(upload_to='chat_media/', blank=True, null=True, verbose_name="ملف مرفق")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="وقت الإرسال")
    is_read = models.BooleanField(default=False, verbose_name="تمت القراءة")

    class Meta:
        verbose_name = "رسالة محادثة"
        verbose_name_plural = "رسائل المحادثة"
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender} -> {self.receiver} @ {self.timestamp:%Y-%m-%d %H:%M}"