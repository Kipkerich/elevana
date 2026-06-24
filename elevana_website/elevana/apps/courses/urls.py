from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='courses'),
    path('manage/', views.manage_course, name='add_course'),
    path('manage/<slug:slug>/', views.manage_course, name='edit_course'),
    path('apply/success/', views.application_success, name='application_success'),
    path('department/<slug:slug>/', views.department_detail, name='department_detail'),
    path('details/<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/apply/', views.apply_course, name='apply_course'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
]