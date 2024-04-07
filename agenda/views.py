import imp
from re import T
from traceback import print_tb
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from agenda.util import encontrar_menor_maior_hora, dividir_horarios, filtrar_horarios_nao_ocupados
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
        
        # Obter os funcionários que prestam o serviço no dia da semana
        funcionarios = models.ServicoFuncionario.objects.filter(
            servico_id=id_servico,
            funcionario__diasemanafuncionario__dia__pk=data.weekday()+1).values_list('funcionario', flat=True)
        
        lista_funcionarios = models.User.objects.filter(pk__in=funcionarios)

        agendamentos = models.Agenda.objects.filter(
            funcionario__id__in=funcionarios,
            data_inicio__date=data.date()).values_list('data_inicio', 'data_final')

        horarios_trabalho = models.DiaSemanaFuncionario.objects.filter(
            funcionario__pk__in=funcionarios,  
            dia = data.weekday()+1
        ).values_list('horaInicial', 'horaFinal')
        
        menor_hora, maior_hora = encontrar_menor_maior_hora(horarios_trabalho)
        
        tempo_servico = models.Servico.objects.get(pk=id_servico).tempoServico
                
        # horário de início e o horário final
        hora_inicial = datetime.combine(datetime.today(), menor_hora)
        hora_final = datetime.combine(datetime.today(), maior_hora)

        # Lista para armazenar os intervalos de uma hora
        horarios_divididos = dividir_horarios(hora_inicial, hora_final, tempo_servico)
            
        horarios_divididos_nao_ocupados = filtrar_horarios_nao_ocupados(horarios_divididos, agendamentos)
        
        lista_agendamentos = []
        for funcionario in lista_funcionarios:
            print("="*50)
            print(funcionario.pk)
            print("="*50)
            lista_agendamentos.append((funcionario.pk, bucas_agendamentos(funcionario.pk, data, id_servico)))
        
        print("="*50)
        print(lista_agendamentos)
        print("="*50)
        return render(request, 'agenda/agenda.html', {
            'servico': servico,
            'lista_funcionarios': lista_funcionarios,
            'horarios_divididos_nao_ocupados': horarios_divididos_nao_ocupados,
            'lista_agendamentos': lista_agendamentos,
            'data': request.POST['data']
            })        
    return redirect('agenda:home')


def bucas_agendamentos(funcionario, data, id_servico):
    # Obtenha os horários de trabalho do funcionário
    horarios_trabalho = models.DiaSemanaFuncionario.objects.filter(
        funcionario=funcionario,
        dia=data.weekday() + 1
    ).values_list('horaInicial', 'horaFinal')

    # Encontre a menor e a maior hora dos horários de trabalho do funcionário
    menor_hora, maior_hora = encontrar_menor_maior_hora(horarios_trabalho)
    
    # Obtenha os agendamentos do funcionário para o dia especificado
    agendamentos = models.Agenda.objects.filter(
        funcionario=funcionario,
        data_inicio__date=data.date()
    ).values_list('data_inicio', 'data_final')

    # Calcule os horários divididos não ocupados pelo funcionário
    tempo_servico = models.Servico.objects.get(pk=id_servico).tempoServico
    hora_inicial = datetime.combine(data.date(), menor_hora)
    hora_final = datetime.combine(data.date(), maior_hora)
    horarios_divididos = dividir_horarios(hora_inicial, hora_final, tempo_servico)
    horarios_divididos_nao_ocupados = filtrar_horarios_nao_ocupados(horarios_divididos, agendamentos)

    return horarios_divididos_nao_ocupados


