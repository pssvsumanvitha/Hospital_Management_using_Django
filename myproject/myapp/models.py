from django.db import models

class Users(models.Model):
    email = models.EmailField(max_length=30, unique=True)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.email
    
class Appointment(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name

class Prescription(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    doctor_name = models.CharField(max_length=100)
    file = models.FileField(upload_to="prescriptions/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.patient_name


