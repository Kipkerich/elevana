from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import ContactForm

def home(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def contact(request):
    return render(request, 'main/contact.html')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Extract data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            # Send Email
            send_mail(
                f'New Inquiry from {name}: {form.cleaned_data["inquiry_type"]}',
                message,
                email, # From
                ['info@elevanatraininginstitute.com'], # To (Use your official email)
            )
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'main/contact.html', {'form': form})


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_course_dashboard')

    next_url = request.GET.get('next') or request.POST.get('next') or ''
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                return redirect('admin_course_dashboard')

            messages.error(request, 'This account does not have admin access.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'main/admin_login.html', {
        'form': form,
        'next': next_url,
    })


def admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('admin_login')
