import json
import hmac
import hashlib
import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Course, Department, CourseApplication
from .forms import CourseForm, CourseApplicationForm


PAYSTACK_API = "https://api.paystack.co"


def staff_only(user):
    return user.is_staff


# ---------------------------------------------------------------------------
# Course management (staff only)
# ---------------------------------------------------------------------------

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


def delete_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        course.delete()
        return redirect('courses')
    return render(request, 'courses/confirm_delete.html', {'course': course})


# ---------------------------------------------------------------------------
# Public course views
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
# Application & payment flow
# ---------------------------------------------------------------------------

def apply_course(request, slug):
    """
    Step 1 — Display and process the application form.
    On valid POST: save as draft, redirect to payment page.
    """
    course = get_object_or_404(Course, slug=slug)

    if request.method == 'POST':
        form = CourseApplicationForm(request.POST, request.FILES, course=course)
        if form.is_valid():
            application = form.save(commit=False)
            application.status = 'draft'
            application.payment_status = 'unpaid'
            application.save()
            # Store the application id in session so payment page can retrieve it
            request.session['pending_application_id'] = application.id
            return redirect('payment_page', ref=application.payment_reference)
    else:
        form = CourseApplicationForm(course=course)

    return render(request, 'courses/apply.html', {'form': form, 'course': course})


def payment_page(request, ref):
    """
    Step 2 — Show payment summary and trigger Paystack popup.
    """
    application = get_object_or_404(CourseApplication, payment_reference=ref)

    # Guard: if already paid, skip to success
    if application.payment_status == 'paid':
        return redirect('application_success')

    # Amount in kobo (Paystack uses smallest currency unit)
    # Course price is in KES — Paystack Kenya uses KES, amount in cents (x100)
    amount_kobo = int(application.course.price * 100)

    context = {
        'application': application,
        'course': application.course,
        'amount_kobo': amount_kobo,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
        'callback_url': request.build_absolute_uri(
            reverse('payment_callback', args=[ref])
        ),
    }
    return render(request, 'courses/payment.html', context)


def payment_callback(request, ref):
    """
    Step 3 — Paystack redirects back here after the popup closes.
    We verify the transaction server-side with the secret key.
    """
    application = get_object_or_404(CourseApplication, payment_reference=ref)

    trxref = request.GET.get('trxref') or request.GET.get('reference') or ref

    # Verify with Paystack API
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
        messages.error(request, 'Could not verify payment. Please contact support.')
        return redirect('payment_page', ref=ref)

    if data.get('status') and data['data']['status'] == 'success':
        # Confirm amount matches to prevent price tampering
        paid_amount = data['data']['amount']  # in kobo
        expected_amount = int(application.course.price * 100)

        if paid_amount >= expected_amount:
            application.payment_status = 'paid'
            application.status = 'pending'
            application.save()
            # Clear session
            request.session.pop('pending_application_id', None)
            return redirect('application_success')
        else:
            messages.warning(
                request,
                'Payment amount mismatch. Please contact support with reference: '
                f'{ref}'
            )
            return redirect('payment_page', ref=ref)
    else:
        application.payment_status = 'failed'
        application.save()
        messages.error(
            request,
            'Payment was not completed. You can try again below.'
        )
        return redirect('payment_page', ref=ref)


@csrf_exempt
@require_POST
def paystack_webhook(request):
    """
    Paystack webhook — secondary/backup confirmation.
    Paystack signs the payload with HMAC-SHA512 using your secret key.
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


def application_success(request):
    return render(request, 'courses/application_success.html')
