import imp
from re import T
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

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
                request.session['id_empresa'] = request.POST['codigo'] 
                print(request.POST['codigo'])
                print(request.session['id_empresa'])
                # print(user.pk)
                # print(user.tipo)
                return redirect('agenda:home')
    else:
        form = AuthenticationForm()
    return render(request, 'agenda/login.html', {'form': form})

def logout_view(request):
    auth.logout(request)
    return redirect('agenda:login')

@login_required(login_url='agenda:login')
def home(request):
    print(request.session['id_empresa'])
    empresa = models.Empresa.objects.get(pk=request.session['id_empresa'])
    empresas = models.Empresa.objects.filter(gerente_id=empresa.gerente_id)

    return render(request, 'agenda/home.html',{'empresas': empresas})


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

@login_required(login_url='agenda:login')
def perfil(request):
    if request.method == 'POST':
        print(request.POST)
        username = request.POST['username'] 
        email = request.POST['email']
        password = request.POST['password']
        confirmar_senha = request.POST['confirmar_senha']
        
        status = True
        passwordErros = []
        user = models.User.objects.get(pk=request.user.pk)
        
        if username != '':
            user.username = username
        
        if password != '':
            if password != confirmar_senha:
                status = False
                passwordErros.append('As senhas não conferem.') 
            else:
                user.set_password(password)
        
        if(status):
            user.save()
            return redirect('agenda:logout_view')
            
        
        return render(request, 'agenda/perfil.html', {'passwordErros': passwordErros, 'user': request.user})
                    
    else:
        return render(request, 'agenda/perfil.html', {'user': request.user})
    
    
@login_required(login_url='agenda:login')
def empresa(request):
    return render(request, 'agenda/empresa.html')


def servico(request):
    if request.method == 'POST':
        id_empresa = request.POST['id_empresa'] 
        empresa = models.Empresa.objects.get(pk=id_empresa)
        servicos = models.Servico.objects.filter(empresa_id=id_empresa)
        print(servicos)
        return render(request, 'agenda/servico.html', {'servicos': servicos, 'empresa': empresa})
    return redirect('agenda:home')

def agenda(request):
    if request.method == 'POST':
        id_servico = request.POST['id_servico'] 
        id_empresa = request.POST['id_empresa'] 
        data = datetime.strptime(request.POST['data'], '%Y-%m-%d')
        servico = models.Servico.objects.get(pk=id_servico)
        
        funcionarios = models.ServicoFuncionario.objects.filter(
            servico_id=id_servico,
            funcionario__diasemanafuncionario__dia__pk=data.weekday()+1).values_list('funcionario', flat=True)

        agendamentos = models.Agenda.objects.filter(
            servico__servicofuncionario__funcionario__pk__in=funcionarios,
            data_inicio__date=data.date()).values_list('data_inicio', 'data_final')

        horarios_trabalho = models.DiaSemanaFuncionario.objects.filter(
            funcionario__pk__in=funcionarios,  
            dia = data.weekday()+1
        ).values_list('horaIncial', 'horaFinal')
        
        tempo_servico = models.Servico.objects.get(pk=id_servico).tempoSevico
        
        print(tempo_servico )
        print(funcionarios)
        print(agendamentos)
        print(horarios_trabalho)
        
        # Suponha que você tenha o horário de início e o horário final
        hora_inicial = datetime.strptime('08:00', '%H:%M')
        hora_final = datetime.strptime('18:00', '%H:%M')

        # Lista para armazenar os intervalos de uma hora
        horarios_divididos = []

        # Iterar sobre os intervalos de uma hora
        horario_atual = hora_inicial
        while horario_atual < hora_final:
            proximo_horario = horario_atual + timedelta(hours=1)
            horarios_divididos.append((horario_atual.time(), proximo_horario.time()))
            horario_atual = proximo_horario

        # Imprimir os intervalos de uma hora
        for inicio, fim in horarios_divididos:
            print(f"Início: {inicio}, Fim: {fim}")
            
        return render(request, 'agenda/agenda.html', {'servico': servico, 'data': request.POST['data']})        
    return redirect('agenda:home')

