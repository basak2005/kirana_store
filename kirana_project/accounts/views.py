from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password.")
        # If form is not valid, it will be passed to the template with errors
    else:
        form = AuthenticationForm()
    return render(request=request, template_name="accounts/login.html", context={"login_form": form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("accounts:login")

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New account created: {username}")
            login(request, user)
            return redirect("dashboard")
        # If form is not valid, it will be passed to the template with errors
    else:
        form = UserCreationForm()
    return render(request=request, template_name="accounts/register.html", context={"register_form": form})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

@login_required
def settings_view(request):
    return render(request, 'accounts/settings.html')
