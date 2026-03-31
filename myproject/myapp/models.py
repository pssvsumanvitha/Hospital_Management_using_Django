# myapp/models.py

from django.db import models


class Users(models.Model):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor',  'Doctor'),
        ('admin',   'Admin'),
    ]

    fullname = models.CharField(max_length=100, default='')
    username = models.CharField(max_length=50, unique=True, default='')
    email    = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    role     = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_admin_or_doctor(self):
        return self.role in ('admin', 'doctor')

    class Meta:
        verbose_name        = 'User'
        verbose_name_plural = 'Users'


class Appointment(models.Model):

    DEPARTMENT_CHOICES = [
        ('cardiology',   'Cardiology'),
        ('neurology',    'Neurology'),
        ('dentistry',    'General Dentistry'),
        ('laboratory',   'Laboratory Testing'),
        ('health_check', 'Health Check-Up'),
        ('pharmacy',     'Pharmacy'),
        ('general',      'General / Other'),
    ]

    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    # Patient details
    user       = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='appointments')
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    email      = models.EmailField()
    phone      = models.CharField(max_length=15)

    # Patient describes their issue
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='general')
    issue      = models.TextField(blank=True, default='')

    # Admin fills these in when confirming
    assigned_doctor  = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_appointments',
        limit_choices_to={'role__in': ['doctor', 'admin']},
    )
    appointment_date = models.DateField(null=True, blank=True)
    appointment_time = models.TimeField(null=True, blank=True)
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_notes      = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.get_department_display()} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class Prescription(models.Model):
    user         = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='prescriptions')
    patient_name = models.CharField(max_length=100)
    doctor_name  = models.CharField(max_length=100)

    file_name         = models.CharField(max_length=255, default='')
    file_data         = models.BinaryField(null=True, blank=True)
    file_content_type = models.CharField(max_length=100, default='application/octet-stream')

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} — {self.file_name}"

    class Meta:
        ordering = ['-uploaded_at']