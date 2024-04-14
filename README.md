1. **Instale as Dependências:**
   ```bash
   python -m pip install --upgrade pip --user
   python3 -m pip install --upgrade pip --user
   ```

2. **Primeiro, instale o venv, caso ainda não o tenha feito. Você pode instalá-lo usando pip::**
   ```bash
   pip install virtualenv
   ```

3. **Agora, crie um ambiente virtual na sua pasta de projeto:**
   ```bash
   python3 -m venv venv
   ou
   python -m venv venv
   ```

4. **Agora, crie um ambiente virtual na sua pasta de projeto:**
   ```bash
   linux:
   source venv/bin/activate
   Windows:
   venv\\Scripts\\activate
   ```
5. **Instale as Dependências:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Instale as Dependências:** Pula essa etapa por agora
   ```bash
   python manage.py makemigrations
   ```

8. **Configure o Banco de Dados:** Pula essa etapa por agora
   ```bash
   python manage.py migrate
   ```

9. **Execute o Servidor Local:**
   ```bash
   python manage.py runserver
   ```

10. **Acesse a Aplicação:**
   - Abra o navegador e vá para [http://localhost:8000](http://localhost:8000)

## GitHub Repository

O código fonte deste projeto está disponível no repositório do GitHub. Você pode conferir e clonar o repositório [aqui]().

## Considerações Finais

Agradeço pela oportunidade de participar deste desafio. Estou satisfeito em informar que todos os requisitos foram atendidos integralmente. Estou aberto a feedbacks construtivos e disposto a continuar aprimorando o projeto conforme necessário.