from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate,logout
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import render_to_response
from .forms import SignUpForm,LoginForm
from .tokens import account_activation_token
from django.contrib.auth.forms import PasswordChangeForm


from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
#from settings import DEFAULT_FROM_EMAIL
from django.views.generic import *
#from utils.forms.reset_password_form import PasswordResetRequestForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.query_utils import Q

@login_required
def home(request):
    return render(request, 'apikey/credentials.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


def user_login(request,**kwargs):
    if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request,user)           
                    return HttpResponseRedirect(reverse('home'))
                else:
                    messages.error(request,"Your account was inactive.")
            else:
                print("Someone tried to login and failed.")
                print("They used username: {} and password: {}".format(username,password))
                messages.error(request,"Invalid login details given")
        else:
            return render(request, 'accounts/login.html', {})
    return render(request, 'accounts/login.html', {})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your VeriDoc Developer Account'
            message = render_to_string('accounts/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token':account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            from_email = settings.EMAIL_HOST_USER
            to_email = form.cleaned_data.get('username')
            email = EmailMessage(
                        subject, message,from_email, to=[to_email]
            )
            email.send()
            messages.success(request, 'Please confirm your email address to complete the registration.')
        else:
            messages.error(request,'')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def account_activation_sent(request):
    return render(request, 'accounts/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        #login(request, user)
        messages.success(request, " Thanks for Activating your account...!!please Login here..")
        return redirect('user_login')
    else:
        return render(request, 'accounts/account_activation_invalid.html')

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })
