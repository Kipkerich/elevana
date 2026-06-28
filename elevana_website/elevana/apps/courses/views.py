import hashlib
import hmac
import json

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import CourseApplicationForm, CourseForm, DepartmentForm
from .models import Course, CourseApplication, Department

PAYSTACK_API = "https://api.paystack.co"


def staff_only(user):
    return user.is_staff


def send_application_status_email(application):
    subject = f"Your Elevana application has been {application.get_status_display().lower()}"
    if application.status == 'accepted':
        message = (
            f"Dear applicant,\n\n"
            f"Congratulations. Your application for {application.course.title} has been approved.\n"
            "Our admissions team will contact you with the next steps.\n\n"
            "Kind regards,\n"
            "Elevana Professional Training Institute"
        )
    else:
        message = (
            f"Dear applicant,\n\n"
            f"Thank you for applying for {application.course.title}. "
            "After review, your application was not approved at this time.\n\n"
            "Kind regards,\n"
            "Elevana Professional Training Institute"
        )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else settings.EMAIL_HOST_USER,
        [application.email],
        fail_silently=False,
    )


# ---------------------------------------------------------------------------
# Staff: course management
# ---------------------------------------------------------------------------

@login_required(login_url='admin_login')
@user_passes_test(staff_only, login_url='admin_login')
def admin_course_dashboard(request):
    course_form = CourseForm()
    department_form = DepartmentForm()

    if request.method == 'POST':
        form_action = request.POST.get('form_action')
        if form_action == 'create_department':
            department_form = DepartmentForm(request.POST)
            if department_form.is_valid():
                department = department_form.save()
                messages.success(request, f'{department.name} department was created successfully.')
                return redirect('admin_course_dashboard')
        else:
            course_form = CourseForm(request.POST, request.FILES)
            if course_form.is_valid():
                course = course_form.save()
                messages.success(request, f'{course.title} was created successfully.')
                return redirect('admin_course_dashboard')

    courses = Course.objects.select_related('department').prefetch_related('applications').order_by('department__name', 'title')
    departments = Department.objects.prefetch_related('courses').order_by('name')
    applications = CourseApplication.objects.select_related('course', 'course__department').all()
    stats = {
        'courses': courses.count(),
        'departments': departments.count(),
        'applications': applications.count(),
        'pending': applications.filter(status='pending').count(),
        'accepted': applications.filter(status='accepted').count(),
        'rejected': applications.filter(status='rejected').count(),
    }

    return render(request, 'courses/admin_dashboard.html', {
        'course_form': course_form,
        'department_form': department_form,
        'courses': courses,
        'departments': departments,
        'applications': applications,
        'stats': stats,
    })


@login_required(login_url='admin_login')
@user_passes_test(staff_only, login_url='admin_login')
def manage_course(request, slug=None):
    course = get_object_or_404(Course, slug=slug) if slug else None
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'{course.title} was saved successfully.')
            return redirect('admin_course_dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/manage_course.html', {'form': form})


@login_required(login_url='admin_login')
@user_passes_test(staff_only, login_url='admin_login')
def delete_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        course.delete()
        messages.success(request, f'{course.title} was deleted successfully.')
        return redirect('admin_course_dashboard')
    return render(request, 'courses/confirm_delete.html', {'course': course})


@login_required(login_url='admin_login')
@user_passes_test(staff_only, login_url='admin_login')
@require_POST
def update_application_status(request, pk, decision):
    application = get_object_or_404(
        CourseApplication.objects.select_related('course'),
        pk=pk,
    )
    status_by_decision = {
        'approve': 'accepted',
        'reject': 'rejected',
    }
    new_status = status_by_decision.get(decision)
    if not new_status:
        messages.error(request, 'Invalid application decision.')
        return redirect('admin_course_dashboard')

    application.status = new_status
    application.save(update_fields=['status'])

    try:
        send_application_status_email(application)
        messages.success(
            request,
            f'{application.email} was {application.get_status_display().lower()} and notified by email.',
        )
    except Exception as exc:
        messages.warning(
            request,
            f'{application.email} was {application.get_status_display().lower()}, but the email could not be sent: {exc}',
        )

    return redirect('admin_course_dashboard')


# ---------------------------------------------------------------------------
# Public: course browsing
# ---------------------------------------------------------------------------

def course_list(request):
    departments = Department.objects.prefetch_related('courses').all()
    return render(request, 'courses/course_list.html', {'departments': departments})


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    return render(request, 'courses/course_detail.html', {'course': course})


def department_detail(request, slug):
    department = get_object_or_404(Department, slug=slug)
    courses = department.courses.all()
    return render(request, 'courses/department_detail.html', {
        'department': department,
        'courses': courses,
    })


# ---------------------------------------------------------------------------
# Application + Paystack payment flow
#
#  Step 1 — apply_course    : user fills form → saved as draft → redirect to payment_page
#  Step 2 — payment_page    : shows order summary + triggers Paystack popup
#  Step 3 — payment_callback: Paystack redirects here → we verify server-side → success
#  Step 4 — application_success : confirmation page
#
#  Bonus  — paystack_webhook: backup HMAC-signed event from Paystack servers
# ---------------------------------------------------------------------------

def apply_course(request, slug):
    """Step 1 — application form."""
    course = get_object_or_404(Course, slug=slug)

    if request.method == 'POST':
        form = CourseApplicationForm(request.POST, request.FILES, course=course)
        if form.is_valid():
            application = form.save(commit=False)
            application.status = 'draft'
            application.payment_status = 'unpaid'
            application.save()
            return redirect('payment_page', ref=application.payment_reference)
    else:
        form = CourseApplicationForm(course=course)

    return render(request, 'courses/apply.html', {'form': form, 'course': course})


def payment_page(request, ref):
    """Step 2 — payment summary + Paystack inline popup."""
    application = get_object_or_404(CourseApplication, payment_reference=ref)

    # Already paid? Skip straight to success.
    if application.payment_status == 'paid':
        return redirect('application_success')

    # Paystack expects the smallest currency unit.
    # KES on Paystack = kobo-equivalent (multiply by 100).
    amount_kobo = int(application.course.price * 100)

    callback_url = request.build_absolute_uri(
        reverse('payment_callback', args=[ref])
    )

    context = {
        'application': application,
        'course': application.course,
        'amount_kobo': amount_kobo,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
        'callback_url': callback_url,
    }
    return render(request, 'courses/payment.html', context)


def payment_callback(request, ref):
    """
    Step 3 — Paystack redirects here after popup closes successfully.
    We verify the transaction with the Paystack API before marking it paid.
    """
    application = get_object_or_404(CourseApplication, payment_reference=ref)

    # Paystack sends ?trxref=xxx&reference=xxx in the redirect
    trxref = request.GET.get('trxref') or request.GET.get('reference') or ref

    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.get(
            f"{PAYSTACK_API}/transaction/verify/{trxref}",
            headers=headers,
            timeout=15,
        )
        data = response.json()
    except requests.RequestException:
        messages.error(request, 'Network error while verifying payment. Please contact support.')
        return redirect('payment_page', ref=ref)

    if data.get('status') and data['data']['status'] == 'success':
        paid_amount = data['data']['amount']          # in kobo
        expected_amount = int(application.course.price * 100)

        if paid_amount >= expected_amount:
            application.payment_status = 'paid'
            application.status = 'pending'            # now awaiting staff review
            application.save()
            return redirect('application_success')
        else:
            messages.warning(
                request,
                f'Payment amount mismatch. Please contact support quoting reference: {ref}'
            )
            return redirect('payment_page', ref=ref)
    else:
        # Payment failed or was abandoned
        application.payment_status = 'failed'
        application.save()
        messages.error(request, 'Payment was not completed. Please try again.')
        return redirect('payment_page', ref=ref)


def application_success(request):
    """Step 4 — confirmation page."""
    return render(request, 'courses/application_success.html')


# ---------------------------------------------------------------------------
# Paystack webhook — backup server-to-server confirmation
# ---------------------------------------------------------------------------

@csrf_exempt
@require_POST
def paystack_webhook(request):
    """
    Paystack POSTs signed events here.
    Used as a backup — catches cases where the callback redirect was interrupted.
    """
    paystack_signature = request.headers.get('X-Paystack-Signature', '')
    secret = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
    computed = hmac.new(secret, request.body, hashlib.sha512).hexdigest()

    if not hmac.compare_digest(computed, paystack_signature):
        return HttpResponse(status=400)

    payload = json.loads(request.body)
    event = payload.get('event')

    if event == 'charge.success':
        reference = payload['data']['reference']
        paid_amount = payload['data']['amount']

        try:
            application = CourseApplication.objects.get(payment_reference=reference)
        except CourseApplication.DoesNotExist:
            return HttpResponse(status=200)

        expected_amount = int(application.course.price * 100)
        if paid_amount >= expected_amount and application.payment_status != 'paid':
            application.payment_status = 'paid'
            application.status = 'pending'
            application.save()

    return HttpResponse(status=200)
