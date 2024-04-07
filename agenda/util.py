from datetime import datetime, timedelta

def encontrar_menor_maior_hora(horarios_trabalho):
    menor_hora = None
    maior_hora = None

    # Iterar sobre a lista de intervalos de tempo
    for inicio, fim in horarios_trabalho:
        # Verifique a menor hora (hora de início)
        if menor_hora is None or inicio < menor_hora:
            menor_hora = inicio
        
        # Verifique a maior hora (hora final)
        if maior_hora is None or fim > maior_hora:
            maior_hora = fim
    
    return menor_hora, maior_hora


def dividir_horarios(hora_inicial, hora_final, tempo_servico):
    # Lista para armazenar os intervalos de uma hora
    horarios_divididos = []

    # Iterar sobre os intervalos de uma hora
    horario_atual = hora_inicial
    while horario_atual < hora_final:
        proximo_horario = horario_atual + timedelta(hours=tempo_servico.hour, minutes=tempo_servico.minute)
        horarios_divididos.append((horario_atual.time(), proximo_horario.time()))
        horario_atual = proximo_horario

    return horarios_divididos


def filtrar_horarios_nao_ocupados(horarios_divididos, agendamentos):
    horarios_divididos_nao_ocupados = []

    for inicio, fim in horarios_divididos:
        ocupado = False
        for agendamento_inicio, agendamento_fim in agendamentos:
            if inicio < agendamento_fim.time() and fim > agendamento_inicio.time():
                ocupado = True
                break
        if not ocupado:
            horarios_divididos_nao_ocupados.append((inicio, fim))

    return horarios_divididos_nao_ocupados