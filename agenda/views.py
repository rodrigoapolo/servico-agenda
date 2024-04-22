from http import client
import imp
from pydoc import cli
from re import T
import re
import stat
from traceback import print_tb
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from agenda.util import encontrar_menor_maior_hora, dividir_horarios, filtrar_horarios_nao_ocupados
from agenda import models
from django.utils import timezone

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
                return redirect('agenda:perfil')
    else:
        form = AuthenticationForm()
    return render(request, 'agenda/login.html', {'form': form})

def logout_view(request):
    auth.logout(request)
    return redirect('agenda:login')

@login_required(login_url='agenda:login')
def home(request):
    empresa = models.Empresa.objects.get(pk=request.session['id_empresa'])
    empresas = models.Empresa.objects.filter(gerente_id=empresa.gerente_id, status=True)

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
    
    
def cadastrarFuncionario(request):
    if request.method == 'POST':
        username = request.POST['nome'] 
        email = request.POST['email']
        password = request.POST['password']
        idEmpresa = request.POST.getlist('idEmpresa')
        idServico = request.POST.getlist('idServico')
        idDias = request.POST.getlist('idDia')
        horaInicial = request.POST['horaInicial']
        horaFinal = request.POST['horaFinal']
        foto = request.FILES['foto']  
       
        funcionario = models.User.objects.create_user(username=username, email=email, password=password, foto=foto, tipo='F')
        # Supondo que idEmpresa seja uma lista de IDs de empresas
        for empresa_id in idEmpresa:
            models.EmpresaFuncionario.objects.create(empresa_id=empresa_id, funcionario_id=funcionario.pk)

        # Supondo que idServico seja uma lista de IDs de serviços
        for servico_id in idServico:
            models.ServicoFuncionario.objects.create(servico_id=servico_id, funcionario_id=funcionario.pk)
            
        for dia_id in idDias:
            models.DiaSemanaFuncionario.objects.create(dia_id=dia_id, funcionario_id=funcionario.pk, horaInicial=horaInicial, horaFinal=horaFinal)

        print("="*50)
        print(username)
        print(email)
        print(password)
        print(idEmpresa)
        print(idServico)
        print("="*50)
                    
    dias = models.Dia.objects.all()
    empresas = models.Empresa.objects.filter(gerente_id=request.user.pk, status=True)
    servicos = models.Servico.objects.filter(empresa_id__in=empresas, status=True)
    funcionarios = models.EmpresaFuncionario.objects.filter(empresa_id__in=empresas)
    return render(request, 'agenda/cadastrar-funcionario.html', {
        'empresas': empresas,
        'dias': dias,
        'servicos': servicos,
        'funcionarios': funcionarios})


def deletarFuncionario(request):
    if request.method == 'POST':
        idServico = request.POST['idServico'] 
        models.Servico.objects.filter(pk=idServico).update(status=False)
        
    return redirect('agenda:cadastrarFuncionario')

@login_required(login_url='agenda:login')
def perfil(request):
    
    agendaHistorico = models.Agenda.objects.filter(cliente_id=request.user.pk, status='E')[:3]
    agendaMarcada = models.Agenda.objects.filter(cliente_id=request.user.pk, status='M')[:4]
    agendaProgramada = models.Agenda.objects.filter(cliente_id=request.user.pk, status='P')[:4]
    
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
            
        
        return render(request, 'agenda/perfil.html', {
            'passwordErros': passwordErros,
            'user': request.user,
            'agendaHistorico': agendaHistorico,
            'agendaMarcada': agendaMarcada,
            'agendaProgramada': agendaProgramada})
                    
    else:
        return render(request, 'agenda/perfil.html', {
            'user': request.user,
            'agendaHistorico': agendaHistorico,
            'agendaMarcada': agendaMarcada,
            'agendaProgramada': agendaProgramada})
    
    
@login_required(login_url='agenda:login')
def empresa(request):
    empresaupdate = None
    if request.GET.get('id_empresa', None) is not None:
        empresaupdate = models.Empresa.objects.get(pk=request.GET['id_empresa'], status=True)
            
    if request.method == 'POST':
        nome = request.POST['nome']
        cep = request.POST['cep']
        numero = request.POST['numero']
        descricao = request.POST['descricao']
        complemento = request.POST['complemento']
        logradouro = request.POST['logradouro']
        foto = request.FILES['foto']  
        
        if request.POST.get('id_empresaupdate', None) is "":
            models.Empresa.objects.create(
                nome=nome,
                logradouro=logradouro,
                cep=cep,
                descricao=descricao,
                numero=numero,
                complemento=complemento,
                foto=foto,
                gerente_id=request.user.pk
            )
        else:
            models.Empresa.objects.update_or_create(
                pk=request.POST['id_empresaupdate'],
                defaults={
                'nome':nome,
                'logradouro':logradouro,
                'cep':cep,
                'descricao':descricao,
                'numero':numero,
                'complemento':complemento,
                'foto':foto,
                'gerente_id':request.user.pk}
            )
        
    
    empresas = models.Empresa.objects.filter(gerente_id=request.user.pk, status=True)
    return render(request, 'agenda/empresa.html', {'empresas': empresas, 'empresaupdate': empresaupdate})
    
def deletarEmpresa(request):
    if request.method == 'POST':
        idEmpresa = request.POST['idempresa'] 
        models.Empresa.objects.filter(pk=idEmpresa).update(status=False)
        
    return redirect('agenda:empresa')    

def servico(request):
    if request.method == 'POST':
        id_empresa = request.POST['id_empresa'] 
        empresa = models.Empresa.objects.get(pk=id_empresa, status=True)
        servicos = models.Servico.objects.filter(empresa_id=id_empresa, status=True)
        return render(request, 'agenda/servico.html', {'servicos': servicos, 'empresa': empresa})
    return redirect('agenda:home')

def cadastrarServico(request):
    if request.method == 'POST':
        nome = request.POST['nome'] 
        valor = request.POST['valor'] 
        tempoServico = request.POST['tempoServico'] 
        idempresa = request.POST['idempresa'] 
        descricao = request.POST['descricao'] 
        
        valor = valor.replace(',', '.')
        
        models.Servico.objects.update_or_create(
            pk=request.POST['idservico'],
            defaults={
            'nome':nome,
            'valor':valor,
            'tempoServico':tempoServico,
            'descricao':descricao,
            'empresa_id':idempresa}
        )
        
    
    empresas = models.Empresa.objects.filter(gerente_id=request.user.pk, status=True)
    servicos = models.Servico.objects.filter(empresa_id__in=empresas, status=True)
    return render(request, 'agenda/cadastrar-servico.html', {'empresas': empresas, 'servicos': servicos})

def deletarServico(request):
    if request.method == 'POST':
        idServico = request.POST['idServico'] 
        models.Servico.objects.filter(pk=idServico).update(status=False)
        
    return redirect('agenda:cadastrarServico')

def agenda(request):
    if request.method == 'POST':
        id_servico = request.POST['id_servico'] 
        id_empresa = request.POST['id_empresa'] 
        data = datetime.strptime(request.POST['data'], '%Y-%m-%d')
        servico = models.Servico.objects.get(pk=id_servico, status=True)
        
        # Obter os funcionários que prestam o serviço no dia da semana
        funcionarios = models.ServicoFuncionario.objects.filter(
            servico_id=id_servico,
            funcionario__diasemanafuncionario__dia__pk=data.weekday()+1).values_list('funcionario', flat=True)
        
        lista_funcionarios = models.User.objects.filter(pk__in=funcionarios)

        
        lista_agendamentos = []
        for funcionario in lista_funcionarios:
            lista_agendamentos.append((funcionario.pk, bucas_agendamentos(funcionario.pk, data, id_servico)))
        
        return render(request, 'agenda/agenda.html', {
            'servico': servico,
            'lista_funcionarios': lista_funcionarios,
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
    tempo_servico = models.Servico.objects.get(pk=id_servico, status=True).tempoServico
    hora_inicial = datetime.combine(data.date(), menor_hora)
    hora_final = datetime.combine(data.date(), maior_hora)
    horarios_divididos = dividir_horarios(hora_inicial, hora_final, tempo_servico)
    horarios_divididos_nao_ocupados = filtrar_horarios_nao_ocupados(horarios_divididos, agendamentos)

    return horarios_divididos_nao_ocupados

@login_required(login_url='agenda:login')
def gerarAgendamento(request):
    if request.method == 'POST':
        data = request.POST['data']
        hora_inicio = request.POST['hora_inicio'].strip()
        hora_final = request.POST['hora_final'].strip()
        idFuncionario = request.POST['idFuncionario'] 
        idServico = request.POST['idServico']
      
        hora_inicio = datetime.strptime(data + ' ' + hora_inicio+ ':' + '00 +0000', '%Y-%m-%d %H:%M:%S %z')
        hora_final = datetime.strptime(data + ' ' + hora_final+ ':' + '00 +0000', '%Y-%m-%d %H:%M:%S %z')

        models.Agenda(
            data_inicio=hora_inicio,
            data_final=hora_final,
            status='M',
            cliente_id=request.user.pk,
            funcionario_id=idFuncionario,
            servico_id=idServico
        ).save()
        
    return redirect('agenda:perfil')