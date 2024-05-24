from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('login/', views.login_in, name='login'),
    path('logout/', views.logout_view, name='logout_view'),
    path('login/create-cliente', views.create_cliente, name='create_cliente'),
    path('perfil/', views.perfil, name='perfil'),
    path('empresa/', views.empresa, name='empresa'),
    path('servico/', views.servico, name='servico'),
    path('agenda/', views.agenda, name='agenda'),
    path('agendamento/', views.agendamento, name='agendamento'),
    path('gerarAgendamento/', views.gerarAgendamento, name='gerarAgendamento'),
    path('gerar-agendamento-programado/', views.gerarAgendamentoProgramado, name='gerarAgendamentoProgramado'),
    path('cancelar-agendamento/', views.cancelarAgendamento, name='cancelarAgendamento'),
    path('cadastrar-servico/', views.cadastrarServico, name='cadastrarServico'),
    path('cadastrar-funcionario/', views.cadastrarFuncionario, name='cadastrarFuncionario'),
    path('update-funcionario/', views.updateFuncionario, name='updateFuncionario'),
    path('deletar-servico/', views.deletarServico, name='deletarServico'),
    path('deletar-empresa/', views.deletarEmpresa, name='deletarEmpresa'),
    path('deletar-funcionario/', views.deletarFuncionario, name='deletarFuncionario'),
]
