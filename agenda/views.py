from calendar import c
from cgi import print_arguments
from turtle import mode
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from agenda.util import encontrar_menor_maior_hora, dividir_horarios, filtrar_horarios_nao_ocupados
from agenda import models
from django.urls import resolve
from django.utils import timezone
from django.core.mail import send_mail



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
                request.session['id_empresa'] = 11
                request.session['statusAgenda'] = 'M'
                request.session['id_cidade'] = request.POST['idCidade'] 

                if user.tipo == 'C':
                    return redirect('agenda:home')
                
                return redirect('agenda:perfil')
    else:
        form = AuthenticationForm()
        
    cidades = models.Cidade.objects.all()
    return render(request, 'agenda/login.html', {'form': form, 'cidades': cidades})


def logout_view(request):
    auth.logout(request)
    return redirect('agenda:login')

@login_required(login_url='agenda:login')
def home(request):
    empresa = models.Empresa.objects.get(pk=request.session['id_empresa'], cidade_id=request.session['id_cidade'])
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
        
        return redirect('agenda:cadastrarFuncionario')
                    
    dias = models.Dia.objects.all()
    empresas = models.Empresa.objects.filter(gerente_id=request.user.pk, status=True)
    servicos = models.Servico.objects.filter(empresa_id__in=empresas, status=True)
    funcionarios = models.EmpresaFuncionario.objects.filter(empresa_id__in=empresas, funcionario__status=True)
    return render(request, 'agenda/cadastrar-funcionario.html', {
        'empresas': empresas,
        'dias': dias,
        'servicos': servicos,
        'funcionarios': funcionarios})

def updateFuncionario(request):
    if request.method == 'POST':
        username = request.POST['nome'] 
        email = request.POST['email']
        id_funcionario = request.POST['id_funcionario']
        idEmpresa = request.POST.getlist('idEmpresa')
        idServico = request.POST.getlist('idServico')
        idDias = request.POST.getlist('idDia')
        horaInicial = request.POST['horaInicial']
        horaFinal = request.POST['horaFinal']
        foto = request.FILES['foto']  
       
        funcionario, _ = models.User.objects.update_or_create(pk=id_funcionario, defaults= {'username':username, 'email':email, 'foto':foto})
        # Supondo que idEmpresa seja uma lista de IDs de empresas
        for empresa_id in idEmpresa:
            models.EmpresaFuncionario.objects.update_or_create(
                empresa_id=empresa_id, funcionario_id=funcionario.pk,
                defaults={'empresa_id':empresa_id, 'funcionario_id':funcionario.pk})

        # Supondo que idServico seja uma lista de IDs de serviços
        for servico_id in idServico:
            models.ServicoFuncionario.objects.update_or_create(
                servico_id=servico_id, funcionario_id=funcionario.pk,
                defaults={'servico_id':servico_id, 'funcionario_id':funcionario.pk})
            
        for dia_id in idDias:
            models.DiaSemanaFuncionario.objects.update_or_create(dia_id=dia_id, funcionario_id=funcionario.pk, horaInicial=horaInicial, horaFinal=horaFinal)
        
        return redirect('agenda:cadastrarFuncionario')

    idFuncionario = request.GET['id_funcionario'] 
    funcionario = models.User.objects.get(pk=idFuncionario, status=True)
    
    diasFun = models.DiaSemanaFuncionario.objects.filter(funcionario_id=funcionario.pk)
    diasFunHora = models.DiaSemanaFuncionario.objects.filter(funcionario_id=funcionario.pk).first()
    dias = models.Dia.objects.all().exclude(id__in=diasFun.values_list('dia_id', flat=True))
    
    empresasFun =  models.EmpresaFuncionario.objects.filter(funcionario_id=funcionario.pk)
    empresas = models.Empresa.objects.filter(gerente_id=request.user.pk, status=True).exclude(id__in=empresasFun.values_list('empresa_id', flat=True))
    
    servicosFun = models.ServicoFuncionario.objects.filter(funcionario_id=funcionario.pk)
    servicos = models.Servico.objects.filter(empresa_id__in=empresas, status=True).exclude(id__in=servicosFun.values_list('servico_id', flat=True))

    return render(request, 'agenda/update-funcionario.html',{
        'empresas': empresas,
        'empresasFun': empresasFun,
        'dias': dias,
        'diasFun': diasFun,
        'funcionario': funcionario,
        'diasFunHora': diasFunHora,
        'servicos': servicos,
        'servicosFun': servicosFun})
    
def deletarFuncionario(request):
    if request.method == 'POST':
        idFuncionario = request.POST['idFuncionario'] 
        models.User.objects.filter(pk=idFuncionario).update(status=False)
        
    return redirect('agenda:cadastrarFuncionario')

@login_required(login_url='agenda:login')
def perfil(request):
    
    if request.user.tipo == 'F':
        agendaHistorico = models.Agenda.objects.filter(funcionario=request.user.pk, servico__empresa__pk= request.session['id_empresa'], status='E')[:3]
    else:
        agendaHistorico = models.Agenda.objects.filter(cliente_id=request.user.pk, servico__empresa__pk= request.session['id_empresa'], status='E')[:3]
        
    agendaMarcada = models.Agenda.objects.filter(cliente_id=request.user.pk, servico__empresa__pk= request.session['id_empresa'], status='M')[:4]
    agendaProgramada = models.Agenda.objects.filter(cliente_id=request.user.pk, servico__empresa__pk= request.session['id_empresa'], status='P')[:4]
    

    primeiro_dia_mes_atual = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    primeiro_dia_proximo_mes = (primeiro_dia_mes_atual + timedelta(days=32)).replace(day=1)
    servicoRealizadoFunc = models.Agenda.objects.filter(
        data_inicio__gte=primeiro_dia_mes_atual,
        data_inicio__lt=primeiro_dia_proximo_mes,
        status='E',
        servico__empresa__pk= request.session['id_empresa'])
    
    func = servicoRealizadoFunc.values_list('funcionario', flat=True).distinct()
    countServicoRealizadoFunc = []
    for fu in func:
        countServicoRealizadoFunc.append(
            {
                'funcionario': (servicoRealizadoFunc.filter(funcionario__pk=fu).values_list('funcionario__username', flat=True).first()),
                'quantidade': (servicoRealizadoFunc.filter(funcionario__pk=fu).count())
            }
        )
        
    servicoRealizadoMes = models.Agenda.objects.filter(
    data_inicio__gte=primeiro_dia_mes_atual,
    data_inicio__lt=primeiro_dia_proximo_mes,
    status='E',
    servico__empresa__pk= request.session['id_empresa'])
    servicos = servicoRealizadoMes.values_list('servico', flat=True).distinct()
    countServicoRealizadoMes = []
    for serv in servicos:
        countServicoRealizadoMes.append(
            {
                'servico': (servicoRealizadoMes.filter(servico__pk=serv).values_list('servico__nome', flat=True).first()),
                'quantidade': (servicoRealizadoMes.filter(servico__pk=serv).count())
            }
        )
        
    servicoCanceladoMes = models.Agenda.objects.filter(
    data_inicio__gte=primeiro_dia_mes_atual,
    data_inicio__lt=primeiro_dia_proximo_mes,
    status='C',
    servico__empresa__pk= request.session['id_empresa'])
    servicosCancelados = servicoCanceladoMes.values_list('servico', flat=True).distinct()
    countServicoCanceladosMes = []
    for serv in servicosCancelados:
        countServicoCanceladosMes.append(
            {
                'servico': (servicoCanceladoMes.filter(servico__pk=serv).values_list('servico__nome', flat=True).first()),
                'quantidade': (servicoCanceladoMes.filter(servico__pk=serv).count())
            }
        )
    print('='*50)
    print(servicosCancelados)
    print(countServicoCanceladosMes)
    print('='*50)
        
    if request.method == 'POST':
        print(request.POST)
        username = request.POST['username'] 
        email = request.POST['email']
        password = request.POST['password']
        confirmar_senha = request.POST['confirmar_senha']
        
        status = True
        passwordErros = []
        user = models.User.objects.get(pk=request.user.pk, status=True)
        
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
            'agendaProgramada': agendaProgramada,
            'countServicoRealizadoFunc': countServicoRealizadoFunc,
            'countServicoRealizadoMes': countServicoRealizadoMes,
            'countServicoCanceladosMes': countServicoCanceladosMes})
                    
    else:
        return render(request, 'agenda/perfil.html', {
            'user': request.user,
            'agendaHistorico': agendaHistorico,
            'agendaMarcada': agendaMarcada,
            'agendaProgramada': agendaProgramada,
            'countServicoRealizadoFunc': countServicoRealizadoFunc,
            'countServicoRealizadoMes': countServicoRealizadoMes,
            'countServicoCanceladosMes': countServicoCanceladosMes})
    
    
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
        cidade, _ = models.Cidade.objects.update_or_create(
                nome=request.POST['idCidade'],
                defaults={
                'nome':request.POST['idCidade'],})
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
                cidade=cidade,
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
                'cidade':cidade,
                'gerente_id':request.user.pk}
            )
        
    cidades = models.Cidade.objects.all()
    empresas = models.Empresa.objects.filter(gerente_id=request.user.pk, status=True)
    return render(request, 'agenda/empresa.html', {'empresas': empresas, 'empresaupdate': empresaupdate, 'cidades': cidades})
    
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
    servicoupdate = None
    if request.GET.get('id_servico', None) is not None:
        servicoupdate = models.Servico.objects.get(pk=request.GET['id_servico'], status=True)
        
    if request.method == 'POST':
        nome = request.POST['nome'] 
        valor = request.POST['valor'] 
        tempoServico = request.POST['tempoServico'] 
        idempresa = request.POST['idempresa'] 
        descricao = request.POST['descricao'] 
        foto = request.FILES['foto']
        
        valor = valor.replace(',', '.')
        
        if request.POST.get('id_servicoupdate', None) is "":
            models.Servico.objects.create(
                nome=nome,
                valor=valor,
                tempoServico=tempoServico,
                descricao=descricao,
                foto=foto,
                empresa_id=idempresa
            )
        else:
            models.Servico.objects.update_or_create(
                pk=request.POST['id_servicoupdate'],
                defaults={
                'nome':nome,
                'valor':valor,
                'tempoServico':tempoServico,
                'descricao':descricao,
                'foto':foto,
                'empresa_id':idempresa}
            )
        
    
    empresas = models.Empresa.objects.filter(gerente_id=request.user.pk, status=True)
    servicos = models.Servico.objects.filter(empresa_id__in=empresas, status=True)
    return render(request, 'agenda/cadastrar-servico.html', {
        'empresas': empresas,
        'servicos': servicos,
        'servicoupdate': servicoupdate})

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
        
        lista_funcionarios = models.User.objects.filter(pk__in=funcionarios, status=True)

        
        lista_agendamentos = []
        for funcionario in lista_funcionarios:
            lista_agendamentos.append((funcionario.pk, bucas_agendamentos(funcionario.pk, data, id_servico,request.session['statusAgenda'])))
        
        return render(request, 'agenda/agenda.html', {
            'servico': servico,
            'lista_funcionarios': lista_funcionarios,
            'lista_agendamentos': lista_agendamentos,
            'data': request.POST['data']
            })        
    return redirect('agenda:home')


def bucas_agendamentos(funcionario, data, id_servico, status):
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
        status='M',
        data_inicio__date=data.date()
    ).values_list('data_inicio', 'data_final')

    # Calcule os horários divididos não ocupados pelo funcionário
    tempo_servico = models.Servico.objects.get(pk=id_servico, status=True).tempoServico
    hora_inicial = datetime.combine(data.date(), menor_hora)
    hora_final = datetime.combine(data.date(), maior_hora)
    horarios_divididos = dividir_horarios(hora_inicial, hora_final, tempo_servico)
    if status == 'M':
        horarios_divididos_nao_ocupados = filtrar_horarios_nao_ocupados(horarios_divididos, agendamentos)
    else:
        horarios_divididos_nao_ocupados = horarios_divididos
        
    return horarios_divididos_nao_ocupados

@login_required(login_url='agenda:login')
def gerarAgendamento(request):
    if request.method == 'POST':
        data = request.POST['data']
        hora_inicio = request.POST['hora_inicio'].strip()
        hora_final = request.POST['hora_final'].strip()
        idFuncionario = request.POST['idFuncionario'] 
        idServico = request.POST['idServico']
        status = request.session['statusAgenda']
      
        hora_inicio = datetime.strptime(data + ' ' + hora_inicio+ ':' + '00 +0000', '%Y-%m-%d %H:%M:%S %z')
        hora_final = datetime.strptime(data + ' ' + hora_final+ ':' + '00 +0000', '%Y-%m-%d %H:%M:%S %z')

        models.Agenda(
            data_inicio=hora_inicio,
            data_final=hora_final,
            status=status,
            cliente_id=request.user.pk,
            funcionario_id=idFuncionario,
            servico_id=idServico
        ).save()
        
        request.session['statusAgenda'] = 'M'
    return redirect('agenda:perfil')

def gerarAgendamentoProgramado(request):
    request.session['statusAgenda'] = 'P'
    return redirect('agenda:home')

def cancelarAgendamento(request):
    if request.method == 'POST':
        idAgenda = request.POST['idAgenda']
        agenda = models.Agenda.objects.get(pk=idAgenda)
        agenda.status = 'C'
        agenda.save()
                
        
    if request.POST['path'] == '/perfil/':
        agendas = models.Agenda.objects.filter(
        data_inicio__date=agenda.data_inicio,
        data_inicio__gte=agenda.data_inicio,
        data_final__lte=agenda.data_final,
        status='P',
        funcionario_id=agenda.funcionario.pk).first()
        
        if agendas is not None:
            agendas.status = 'M'
            agendas.save()
            
            assunto = 'Serviço Programado Agendado'
            mensagem = agenda.cliente.username+', você tem um novo serviço programado agendado. Confira em sua agenda.'
            remetente = 'gogaragedev@gmail.com'
            destinatario = []
            destinatario.append(agenda.cliente.email)
    
            send_mail(assunto, mensagem, remetente, destinatario)
            
        return redirect('agenda:perfil')

    if request.POST['path'] == '/agendamento/':
        return redirect('agenda:agendamento')

def agendamento(request):
    if request.method == 'POST':
        idAgenda = request.POST['id_agenda']
        models.Agenda.objects.filter(pk=idAgenda).update(status='E')
        return redirect('agenda:agendamento')
    
    
    if request.GET.get('data', None) is None:
        data_hoje = datetime.now().date()
        agendas = models.Agenda.objects.filter(funcionario_id=request.user.pk, servico__empresa__pk= request.session['id_empresa'], status='M', data_inicio__date=data_hoje)
        return render(request, 'agenda/agendamento.html',{'agendas': agendas, 'data': data_hoje})
    else:
        data_hoje = request.GET.get('data', None)
        agendas = models.Agenda.objects.filter(funcionario_id=request.user.pk, servico__empresa__pk= request.session['id_empresa'], status='M', data_inicio__date=data_hoje)        
        return render(request, 'agenda/agendamento.html',{'agendas': agendas, 'data': data_hoje})