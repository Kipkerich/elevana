from django.contrib import admin
from .models import Department, Course, CourseApplication


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'price')
    list_filter = ('department',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(CourseApplication)
class CourseApplicationAdmin(admin.ModelAdmin):
    list_display = ('email', 'id_number', 'course', 'status', 'payment_status', 'submitted_at')
    list_filter = ('status', 'payment_status', 'course', 'submitted_at')
    search_fields = ('email', 'id_number', 'transaction_code', 'payment_reference')
    readonly_fields = ('submitted_at', 'payment_reference')
    list_editable = ('status',)
    ordering = ('-submitted_at',)