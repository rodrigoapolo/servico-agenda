import imp
from re import T
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from agenda import models

def index(request):
    return render(request, 'agenda/index.html')

def login_in(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            print(user)
            if user is not None:
                login(request, user)
                # print(user.pk)
                # print(user.tipo)
                return redirect('agenda:index')
    else:
        form = AuthenticationForm()
    return render(request, 'agenda/login.html', {'form': form})

@login_required(login_url='agenda:index')
def logout_view(request):
    auth.logout(request)
    return redirect('agenda:index')

@login_required(login_url='agenda:index')
def home(request):
    return render(request, 'agenda/home.html')


def create_cliente(request):
    if request.method == 'POST':
        username = request.POST['username'] 
        email = request.POST['email']
        password = request.POST['password']
        confirmar_senha = request.POST['confirmar_senha']
        
        status = True
        usernameErros = []
        emailErros = []
        passwordErros = []
        
        if username == '':
            status = False
            usernameErros.append('Este campo é obrigatório.')
        
        if email == '':
            status = False
            emailErros.append('Este campo é obrigatório.')
            
        if password == '':
            status = False
            passwordErros.append('Este campo é obrigatório.')
            
        if password != confirmar_senha:
            status = False
            passwordErros.append('As senhas não conferem.')
            
        if models.User.objects.filter(email=email).exists():
            status = False
            emailErros.append('Este e-mail já está cadastrado.')
            
        
        if(status):
            user = models.User.objects.create_user(username=username, email=email, password=password, tipo='C')
            return redirect('agenda:home')
        
        return render(request, 'agenda/create-cliente.html', {
            'usernameErros': usernameErros, 'emailErros': emailErros, 'passwordErros': passwordErros,
            'username': username, 'email': email, 'password': password, 'confirmar_senha': confirmar_senha
            })
        
    else:
        return render(request, 'agenda/create-cliente.html')
    