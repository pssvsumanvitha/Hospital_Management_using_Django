from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Users

# Home page
def home(request):
    return render(request, "home.html")

# Show all users (test purpose)
def alluser(request):
    return HttpResponse("Returning all User")

# Prescription page
def prescription(request):
    return render(request, "prescription.html")

# Login page + validation
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # check in Users table
        try:
            user = Users.objects.get(email=email, password=password)
            messages.success(request, "Login successful!")
            return redirect("home")   # go to home.html
        except Users.DoesNotExist:
            messages.error(request, "Invalid email or password")

    return render(request, "login.html")   # show login form
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
