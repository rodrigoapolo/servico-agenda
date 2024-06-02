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
    mensagem['Subject'] = "Venha novamente nos encontrar! Estamos te esperando para atendê-lo na Barbearia Tech!"

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
    message = f"Prezado(a),{servicoCliente[4]}\nEspero que esta mensagem o(a) encontre bem."
    "Há algum tempo, tivemos o prazer de prestar nossos serviços a você na Barbearia Tech e ficamos muito satisfeitos com a oportunidade de atendê-lo(a). Gostaríamos de lembrá-lo(a) sobre o serviço que realizamos para você e reforçar o quanto valorizamos sua confiança em nossa empresa. Seja para um corte de cabelo estiloso, uma barba impecável ou qualquer outro tratamento, estamos à disposição para ajudar. A Barbearia Tech é pioneira no mercado e oferece uma plataforma para atender às suas necessidades. Nossos profissionais qualificados estão prontos para proporcionar a melhor experiência possível. Se você deseja agendar um novo serviço ou simplesmente reviver a experiência incrível que tivemos anteriormente, não hesite em entrar em contato conosco. Estamos ansiosos para tê-lo(a) novamente como nosso cliente! Atenciosamente, Barbearia Tech"
    #munda o parametro de enviarEmail para o email do cliente servicoCliente[3]
    enviarEmail('rodrigoapolodev@gmail.com', servicoCliente[1], message)

