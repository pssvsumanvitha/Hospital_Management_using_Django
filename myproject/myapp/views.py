from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Users, Prescription, Appointment

# Home page
def home(request): 
    return render(request, "home.html")


# Show all users (test purpose)
def alluser(request):
    return HttpResponse("Returning all User")

# Prescription page
def prescription(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    if request.method == "POST":
        user = Users.objects.get(id=user_id)

        Prescription.objects.create(
            user=user,
            patient_name=request.POST.get("patient_name"),
            doctor_name=request.POST.get("doctor_name"),
            file=request.FILES.get("file")
        )

        messages.success(request, "Prescription uploaded successfully!")

    return render(request, "prescription.html")

# Login page + validation
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = Users.objects.get(email=email, password=password)

            # ✅ SAVE SESSION DATA
            request.session["user_id"] = user.id
            request.session["username"] = user.email.split("@")[0]  # OR use name if you have it

            messages.success(request, "Login successful!")
            return redirect("home")


        except Users.DoesNotExist:
            messages.error(request, "Invalid email or password")

    return render(request, "login.html")

def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # save user
        from .models import Users
        Users.objects.create(email=email, password=password)

        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "register.html")

def book_appointment(request):
    if request.method == "POST":
        user_id = request.session.get("user_id")

        if not user_id:
            messages.error(request, "Please login to book an appointment.")
            return redirect("login")

        user = Users.objects.get(id=user_id)

        Appointment.objects.create(
            user=user,
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone")
        )

        messages.success(request, "Appointment booked successfully!")

    return redirect("home")

def logout_view(request):
    request.session.flush()
    messages.success(request, "Logged out successfully!")
    return redirect("login")


