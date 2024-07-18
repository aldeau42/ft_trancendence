from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .utils import send_otp
from datetime import datetime
from .forms import RegisterForm
from .models import UserProfile
import pyotp

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect(f'/users/success/?username={user.username}')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def success_view(request):
    username = request.GET.get('username')
    user = User.objects.get(username=username)
    user_profile = UserProfile.objects.get(user=user)
    context = {
        'user': user,
        'user_profile': user_profile,
        'phone_number': user_profile.phone_number,
    }
    return render(request, 'users/success.html', context)

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, form.get_user())
            send_otp(request)
            request.session['username'] = user.username
            return redirect('/users/otp/')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', { "form":form })


def otp_view(request):
    if request.method == "POST":
        user_otp = request.POST.get('otp')
        otp_secret_key = request.session.get('otp_secret_key')
        otp_valid_date = request.session.get('otp_valid_date')

        if otp_secret_key and otp_valid_date:
            valid_until = datetime.fromisoformat(otp_valid_date)

            if valid_until > datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=60)
                if totp.verify(user_otp):
                    username = request.session.get('username')
                    user = get_object_or_404(User, username=username)
                    login(request, user)

                    # Clear session data
                    del request.session['otp_secret_key']
                    del request.session['otp_valid_date']
                    del request.session['username']

                    return redirect('/about/')
            else:
                return render(request, 'users/otp.html', {'error': 'OTP has expired'})

        return render(request, 'users/otp.html', {'error': 'Invalid OTP'})

    return render(request, 'users/otp.html')
