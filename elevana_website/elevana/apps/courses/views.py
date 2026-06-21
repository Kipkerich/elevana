from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Department  
from .forms import CourseForm

def staff_only(user):
    return user.is_staff

@login_required
@user_passes_test(staff_only)
def manage_course(request, slug=None):
    course = get_object_or_404(Course, slug=slug) if slug else None
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('courses')
    else:
        form = CourseForm(instance=course)
        
    return render(request, 'courses/manage_course.html', {'form': form})

def course_list(request):
    # Retrieve all departments with their courses pre-loaded
    departments = Department.objects.prefetch_related('courses').all()
    return render(request, 'courses/course_list.html', {'departments': departments})

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    return render(request, 'courses/course_detail.html', {'course': course})

def delete_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        course.delete()
        return redirect('courses')
    return render(request, 'courses/confirm_delete.html', {'course': course})

#View to show all courses in one department
def department_detail(request, slug):
    department = get_object_or_404(Department, slug=slug)
    courses = department.courses.all() # related_name='courses' from the model
    return render(request, 'courses/department_detail.html', {
        'department': department,
        'courses': courses
    })

# View to show the details of ONE specific course
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    return render(request, 'courses/course_detail.html', {'course': course})