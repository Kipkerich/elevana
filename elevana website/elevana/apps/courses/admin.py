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
    list_display = ('first_name', 'last_name', 'email', 'course', 'status', 'submitted_at')
    list_filter = ('status', 'course', 'submitted_at')
    search_fields = ('first_name', 'last_name', 'email', 'id_passport_number')
    readonly_fields = ('submitted_at',)
    list_editable = ('status',)
    ordering = ('-submitted_at',)