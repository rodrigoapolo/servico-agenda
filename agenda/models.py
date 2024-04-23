from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):   
    TIPO_ADM_CHOICES = (('G', 'Gerente'), ('F', 'Funcionario'), ('C', 'Cliente'))
    
    id = models.AutoField(primary_key=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)
    tipo = models.CharField(max_length=1, choices=TIPO_ADM_CHOICES)
    foto = models.ImageField(upload_to='imagens/', null=True, blank=True)
    status = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
    
class Dia(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=30)

class DiaSemanaFuncionario(models.Model):
    id = models.AutoField(primary_key=True)
    horaInicial = models.TimeField()
    horaFinal = models.TimeField()
    dia = models.ForeignKey(Dia, on_delete=models.SET_NULL, blank=True, null=True)
    funcionario = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    
class Empresa(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=200, blank=True, null=True)
    logradouro = models.CharField(max_length=200, blank=True, null=True)
    foto = models.ImageField(upload_to='imagens/', null=True, blank=True)
    descricao = models.CharField(max_length=200, blank=True, null=True)
    cep = models.CharField(max_length=200, blank=True, null=True)
    numero = models.CharField(max_length=200, blank=True, null=True)
    complemento = models.CharField(max_length=200, blank=True, null=True)
    status = models.BooleanField(default=True)
    gerente = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
            
class Servico(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=200, blank=True, null=True)
    descricao = models.CharField(max_length=200, blank=True, null=True)
    valor = models.FloatField()
    tempoServico = models.TimeField()
    intervalo = models.TimeField(blank=True, null=True)
    status = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='imagens/', null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, blank=True, null=True)
    
class ServicoFuncionario(models.Model):
    id = models.AutoField(primary_key=True)
    funcionario = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    servico = models.ForeignKey(Servico, on_delete=models.SET_NULL, blank=True, null=True)
    
        
class Agenda(models.Model):
    STATUS = (('M', 'Marcado'),('P', 'Programado'), ('E', 'Executado'), ('C', 'Cancelado'))
    id = models.AutoField(primary_key=True)
    create_data = models.DateTimeField(auto_now_add=True)
    data_inicio = models.DateTimeField()
    data_final = models.DateTimeField()
    status = models.CharField(max_length=1, choices=STATUS)
    servico = models.ForeignKey(Servico, on_delete=models.SET_NULL, blank=True, null=True)
    cliente = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='agendas_cliente')
    funcionario = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='agendas_funcionario')
    
class EmpresaFuncionario(models.Model):
    id = models.AutoField(primary_key=True)
    funcionario = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, blank=True, null=True)
    