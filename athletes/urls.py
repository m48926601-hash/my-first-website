from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    
    # مسارات الكوتش
    path('coach/login/', views.coach_login_view, name='coach_login'),
    path('coach/logout/', views.coach_logout_view, name='coach_logout'),
    path('coach/trainees/', views.trainees_list_view, name='trainees_list'),
    path('coach/trainees/add/', views.add_trainee_view, name='add_trainee'),
    path('coach/training/', views.add_training_view, name='add_training'), 
    path('coach/diet/', views.add_diet_view, name='add_diet'),
    path('coach/trainees/<int:trainee_id>/', views.trainee_profile_view, name='trainee_profile'),
    path('coach/', views.coach_dashboard, name='coach_dashboard'),
    
    # مسارات المتدرب الجديدة
    path('trainee/login/', views.trainee_login_view, name='trainee_login'),
    path('trainee/dashboard/', views.trainee_dashboard_view, name='trainee_dashboard'),
    path('trainee/logout/', views.trainee_logout_view, name='trainee_logout'),
    # السلك الجديد للتعديل:
    path('coach/trainees/<int:trainee_id>/edit/', views.edit_trainee_view, name='edit_trainee'),
]