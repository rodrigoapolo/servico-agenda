from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_in, name='login'),
    path('logout/', views.logout_view, name='logout_view'),
    path('login/create-cliente', views.create_cliente, name='create_cliente'),
    path('perfil/', views.perfil, name='perfil'),
    path('home/', views.home, name='home'),
]
