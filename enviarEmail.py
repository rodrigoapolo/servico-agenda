#pip install db-sqlite3
#pip install python-dotenv

from calendar import c
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

banco = sqlite3.connect('db.sqlite3')

cursor = banco.cursor()

cursor.execute("SELECT DISTINCT c.id, c.email, c.username FROM agenda_agenda aa INNER JOIN agenda_user c ON aa.cliente_id = c.id;")
# Obtendo todos os resultados da consulta

# Extraindo os valores únicos de cliente_id
ids_clientes = cursor.fetchall()

servicoClientes = []
for cliente in ids_clientes:
    cursor.execute("SELECT DISTINCT aa.cliente_id, s.nome, s.descricao FROM agenda_agenda aa INNER JOIN agenda_servico s ON aa.servico_id = s.id WHERE cliente_id = ? LIMIT 1;", (cliente[0],))
    resultado = cursor.fetchone()
    
    resultado_com_cliente = (resultado[0], resultado[1], resultado[2], cliente[1], cliente[2])
    servicoClientes.append(resultado_com_cliente)

# Fechando a conexão com o banco de dados
banco.close()


print(servicoClientes)


load_dotenv()
# Configurações do servidor SMTP do Gmail
smtp_server = 'smtp.gmail.com'
smtp_port = 587

# Seu endereço de e-mail e senha do Gmail
email = os.getenv('EMAIL_HOST_USER')
senha = os.getenv('EMAIL_HOST_PASSWORD')

def enviarEmail(destinatario, assunto, corpo):
    # Criar uma mensagem multipart
    mensagem = MIMEMultipart()
    mensagem['From'] = email
    mensagem['To'] = destinatario
    mensagem['Subject'] = assunto

    # Adicionar o corpo do e-mail à mensagem
    mensagem.attach(MIMEText(corpo, 'plain'))

    # Iniciar uma conexão SMTP com o servidor
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()

    # Faça login na conta do Gmail
    server.login(email, senha)

    # Envie o e-mail
    texto_do_email = mensagem.as_string()
    server.sendmail(email, destinatario, texto_do_email)

    # Fechar a conexão com o servidor SMTP
    server.quit()


for servicoCliente in servicoClientes:
    message = f"Olá {servicoCliente[4]}! Não se esqueça de agendar novamente o serviço {servicoCliente[1]}, onde {servicoCliente[2]} \n\n\nEstamos ansiosos para vê-lo em breve!"
    #munda o parametro de enviarEmail para o email do cliente servicoCliente[3]
    enviarEmail('rodrigoapolodev@gmail.com', servicoCliente[1], message)

