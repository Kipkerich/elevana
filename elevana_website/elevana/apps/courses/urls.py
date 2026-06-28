from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='courses'),
    path('dashboard/', views.admin_course_dashboard, name='admin_course_dashboard'),
    path('manage/', views.manage_course, name='add_course'),
    path('manage/<slug:slug>/', views.manage_course, name='edit_course'),
    path('manage/<slug:slug>/delete/', views.delete_course, name='delete_course'),
    path('dashboard/applications/<int:pk>/<str:decision>/', views.update_application_status, name='update_application_status'),

    # Application & payment
    path('apply/success/', views.application_success, name='application_success'),
    path('apply/payment/<str:ref>/', views.payment_page, name='payment_page'),
    path('apply/callback/<str:ref>/', views.payment_callback, name='payment_callback'),
    path('apply/webhook/', views.paystack_webhook, name='paystack_webhook'),

    # Course browsing — specific paths before the slug catch-all
    path('department/<slug:slug>/', views.department_detail, name='department_detail'),
    path('details/<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/apply/', views.apply_course, name='apply_course'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
]
