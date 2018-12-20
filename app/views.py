""" All view logic for the app """

from uuid import uuid4
import requests, json

from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from app.models import CustomUser, SuperSecretCode


# Get the API key and site id
with open('solar/secrets.json', 'r') as f:
    API_KEY = json.load(f)['SOLAREDGE']['API_KEY']
with open('solar/secrets.json', 'r') as f:
    SITE_ID = json.load(f)['SOLAREDGE']['SITE_ID']


@login_required
def index_view(request):
    """ Main page of the app """
    url = f'https://monitoringapi.solaredge.com/site/{SITE_ID}/overview?api_key={API_KEY}'
    response = requests.get(url)
    data = json.loads(response.content)['overview']
    context = {
        'last_updated': data['lastUpdateTime'],
        'energy_total': int(data['lifeTimeData']['energy'] / 1000),
        'energy_year': int(data['lastYearData']['energy'] / 1000),
        'energy_month': int(data['lastMonthData']['energy'] / 1000),
        'energy_day': round(data['lastDayData']['energy'] / 1000, 1),
        'current_power': int(data['currentPower']['power'])
    }
    print(data)
    return render(request, 'app/index.html', context)


def login_view(request):
    """ Login and register page """
    if request.method == 'POST':
        form = request.POST.dict()
        if 'super-secret-code' in form:
            message = ''
            code = SuperSecretCode.objects.filter(code=form['super-secret-code'])
            if form['password'] != form['password-check']:
                message = 'Passwords do not match.'
            elif CustomUser.objects.filter(email=form['email']).exists():
                message = 'This e-mail address already has an account.'
            elif not code.exists():
                message = 'This super secret code does not exist.'
            elif code.first().activated:
                message = 'This super secret code has already been used.'
            if message != '':
                return render(request, 'app/login.html', {'message': message, 'register': True})
            new_user = CustomUser.objects.create_user(email=form['email'],\
                first_name=form['first-name'],\
                password=form['password'],\
                username=uuid4())
            new_user.save()
            code.first().activated = True
            code.first().user = new_user
            code.first().save()
            user = authenticate(request, email=form['email'], password=form['password'])
            if user is None:
                message = "Something went wrong while creating your account. Please try again."
                return render(request, "app/login.html", {"message": message})
        else:
            user = authenticate(request, email=form['email'], password=form['password'])
            if user is None:
                return render(request, 'app/login.html', {'message': 'Invalid credentials.'})
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, 'app/login.html')


@login_required
def logout_view(request):
    """ Log the user out """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def password_reset_view(request):
    """ TODO: Create the password reset logic """
    return render(request, 'app/login.html', {'message': 'Hahaha, too bad...'})


@login_required
def user_settings_view(request):
    """ Returns the settings page """
    first_name = request.user.first_name
    last_name = request.user.last_name
    email = request.user.email
    message = None
    if request.method == 'POST':
        user = CustomUser.objects.filter(email=request.user).first()
        code = request.POST['code']
        content = request.POST['content']
        if code == 'first name':
            user.first_name = content
            first_name = content
        elif code == 'last name':
            user.last_name = content
            last_name = content
        elif code == 'e-mail':
            user.email = content
            email = content
        elif code == 'password':
            user.set_password(content)
            login(request, user)
        message = code.capitalize() + ' has been succesfully updated!'
        user.save()
    context = {
        'message': message,
        'tab': 'settings',
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
    }
    return render(request, 'app/user_settings.html', context)


@login_required
def chart_settings_view(request):
    return render(request, 'app/chart_settings.html', {'tab': 'settings'})
