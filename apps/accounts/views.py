from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import ProfileForm, RegisterForm
from .models import Profile

def register(request):
    if request.user.is_authenticated:
        return redirect("book_list")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Profile.objects.create(user=user)
        login(request, user)
        messages.success(request, "Your account has been created.")
        return redirect("book_list")
    return render(request, "accounts/register.html", {"form": form})

@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile_obj, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("profile")
    return render(request, "accounts/profile.html", {"form": form})
