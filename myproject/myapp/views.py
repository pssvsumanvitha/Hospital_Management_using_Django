import functools

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Appointment, Prescription, Users


# ─── Helpers ────────────────────────────────────────────────────────────────

def get_logged_in_user(request):
    """Return Users instance if session is valid, else None."""
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return None


def login_required_view(func):
    """Decorator: redirect to login if not authenticated."""
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
        return func(request, *args, **kwargs)
    return wrapper


def admin_or_doctor_required(func):
    """Decorator: only allow admin/doctor roles."""
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        user = get_logged_in_user(request)
        if not user:
            return redirect('login')
        if not user.is_admin_or_doctor:
            messages.error(request, "Access denied. Doctors/Admins only.")
            return redirect('home')
        return func(request, *args, **kwargs)
    return wrapper


# ─── Auth ────────────────────────────────────────────────────────────────────

VALID_ROLES = {'patient', 'doctor', 'admin'}


def register_view(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        username = request.POST.get('username', '').strip()
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm  = request.POST.get('confirm_password', '')
        role     = request.POST.get('role', 'patient')

        if role not in VALID_ROLES:
            role = 'patient'

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if Users.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        if Users.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        Users.objects.create(
            fullname=fullname,
            username=username,
            email=email,
            password=make_password(password),
            role=role,
        )
        messages.success(request, "Account created! Please log in.")
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

        if not check_password(password, user.password):
            messages.error(request, "Invalid email or password.")
            return redirect('login')

        request.session['user_id']  = user.id
        request.session['username'] = user.username or user.fullname
        request.session['role']     = user.role
        messages.success(request, f"Welcome back, {user.fullname}!")
        return redirect('home')

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('login')


# ─── Home ────────────────────────────────────────────────────────────────────

def home_view(request):
    return render(request, 'home.html')


# ─── Appointment (patient books) ──────────────────────────────────────────────

@login_required_view
def appointment_view(request):
    if request.method == 'POST':
        user = get_logged_in_user(request)
        Appointment.objects.create(
            user=user,
            first_name=request.POST.get('first_name', '').strip(),
            last_name=request.POST.get('last_name', '').strip(),
            email=request.POST.get('email', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            department=request.POST.get('department', 'general'),
            issue=request.POST.get('issue', '').strip(),
            status='pending',
        )
        messages.success(
            request,
            "Appointment request submitted! You will receive a confirmation email "
            "once a doctor has been assigned."
        )
        return redirect('home')
    messages.error(request, "Invalid request.")
    return redirect('home')


# ─── Appointment Confirm (admin/doctor assigns doctor + date/time) ─────────────

@admin_or_doctor_required
def confirm_appointment(request, pk):
    """
    Admin/doctor fills in: assigned_doctor, appointment_date, appointment_time,
    admin_notes — then saves and emails the patient.
    """
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == 'POST':
        doctor_id        = request.POST.get('assigned_doctor')
        appointment_date = request.POST.get('appointment_date', '').strip()
        appointment_time = request.POST.get('appointment_time', '').strip()
        admin_notes      = request.POST.get('admin_notes', '').strip()
        action           = request.POST.get('action', 'confirm')  # 'confirm' or 'cancel'

        if action == 'cancel':
            appointment.status = 'cancelled'
            appointment.save()
            messages.success(request, "Appointment cancelled.")
            return redirect('dashboard')

        # Validate required fields for confirmation
        if not doctor_id or not appointment_date or not appointment_time:
            messages.error(request, "Please fill in doctor, date, and time before confirming.")
            return redirect('confirm_appointment', pk=pk)

        try:
            doctor = Users.objects.get(id=doctor_id, role__in=['doctor', 'admin'])
        except Users.DoesNotExist:
            messages.error(request, "Selected doctor not found.")
            return redirect('confirm_appointment', pk=pk)

        appointment.assigned_doctor  = doctor
        appointment.appointment_date = appointment_date
        appointment.appointment_time = appointment_time
        appointment.admin_notes      = admin_notes
        appointment.status           = 'confirmed'
        appointment.save()

        # ── Send confirmation email to patient ──────────────────────────────
        _send_confirmation_email(appointment)

        messages.success(
            request,
            f"Appointment confirmed and confirmation email sent to {appointment.email}."
        )
        return redirect('dashboard')

    # GET — show the confirm form
    doctors = Users.objects.filter(role__in=['doctor', 'admin']).order_by('fullname')
    return render(request, 'confirm_appointment.html', {
        'appointment': appointment,
        'doctors':     doctors,
    })


def _send_confirmation_email(appointment):
    """Send a nicely formatted confirmation email to the patient."""
    doctor_name = (
        appointment.assigned_doctor.fullname
        if appointment.assigned_doctor
        else "our medical team"
    )

    date_str = appointment.appointment_date.strftime("%A, %d %B %Y")
    time_str = appointment.appointment_time.strftime("%I:%M %p")

    subject = f"[HealthCare] Your Appointment is Confirmed — {date_str}"

    body = f"""Dear {appointment.first_name} {appointment.last_name},

Your appointment at HealthCare has been confirmed. Here are your details:

  Department  : {appointment.get_department_display()}
  Doctor      : Dr. {doctor_name}
  Date        : {date_str}
  Time        : {time_str}
  Your Issue  : {appointment.issue or 'Not specified'}

{'Admin Notes : ' + appointment.admin_notes if appointment.admin_notes else ''}

Please arrive 10 minutes before your scheduled time and bring a valid ID
and any previous medical records relevant to your visit.

If you need to reschedule or have any questions, contact us at:
  Email : support@care.com
  Phone : (+91) 93456 87989

We look forward to seeing you.

Warm regards,
HealthCare Team
Redfort Bridge Street, Delhi
"""

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.email],
            fail_silently=False,
        )
    except Exception:
        # Log but don't crash — appointment is already saved
        pass


# ─── Prescription Upload ──────────────────────────────────────────────────────

@login_required_view
def prescription_view(request):
    user = get_logged_in_user(request)
    is_privileged = user.is_admin_or_doctor

    if request.method == 'POST':
        patient_name  = request.POST.get('patient_name', '').strip()
        doctor_name   = request.POST.get('doctor_name', '').strip()
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            messages.error(request, "Please select a file to upload.")
            return redirect('prescription')

        file_bytes   = uploaded_file.read()
        content_type = uploaded_file.content_type or 'application/octet-stream'

        Prescription.objects.create(
            user=user,
            patient_name=patient_name,
            doctor_name=doctor_name,
            file_name=uploaded_file.name,
            file_data=file_bytes,
            file_content_type=content_type,
        )
        messages.success(request, "Prescription uploaded successfully!")
        return redirect('prescription')

    if is_privileged:
        prescriptions = Prescription.objects.select_related('user').order_by('-uploaded_at')
    else:
        prescriptions = Prescription.objects.filter(user=user).order_by('-uploaded_at')

    return render(request, 'prescription.html', {
        'prescriptions': prescriptions,
        'is_privileged': is_privileged,
    })


# ─── Prescription Download ───────────────────────────────────────────────────

@login_required_view
def download_prescription(request, pk):
    user         = get_logged_in_user(request)
    prescription = get_object_or_404(Prescription, pk=pk)

    if not user.is_admin_or_doctor and prescription.user != user:
        raise Http404("File not found.")

    safe_name = prescription.file_name.replace('"', '').replace('\n', '').replace('\r', '')
    response  = HttpResponse(bytes(prescription.file_data), content_type=prescription.file_content_type)
    response['Content-Disposition'] = f'attachment; filename="{safe_name}"'
    return response


# ─── Admin Dashboard ─────────────────────────────────────────────────────────

@admin_or_doctor_required
def admin_dashboard(request):
    all_users         = Users.objects.filter(role='patient')
    all_appointments  = Appointment.objects.select_related(
        'user', 'assigned_doctor'
    ).order_by('-created_at')
    all_prescriptions = Prescription.objects.select_related('user').order_by('-uploaded_at')

    # Counts for summary cards
    pending_count   = all_appointments.filter(status='pending').count()
    confirmed_count = all_appointments.filter(status='confirmed').count()
    cancelled_count = all_appointments.filter(status='cancelled').count()

    return render(request, 'dashboard.html', {
        'all_users':         all_users,
        'all_appointments':  all_appointments,
        'all_prescriptions': all_prescriptions,
        'pending_count':     pending_count,
        'confirmed_count':   confirmed_count,
        'cancelled_count':   cancelled_count,
    })