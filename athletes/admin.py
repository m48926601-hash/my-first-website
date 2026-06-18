from django.contrib import admin
from .models import Trainee, WeightRecord, ChatMessage

admin.site.register(Trainee)
admin.site.register(WeightRecord)
admin.site.register(ChatMessage)