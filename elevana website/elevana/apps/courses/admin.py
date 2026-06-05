from django.contrib import admin
from .models import Category, Course

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'instructor', 'is_active')
    list_filter = ('category', 'is_active')
    prepopulated_fields = {'slug': ('title',)}