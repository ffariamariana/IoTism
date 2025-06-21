import pymongo
import random
from datetime import datetime, timedelta

# --- Configurações Geraais ---
MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
DATABASE_NAME = "teasense_db"
COLLECTION_NAME = "sensor_data_v6"

# --- Definições dos Perfis de Sensibilidade ---
PERFIS = {
    "padrao": {"zona_conforto_temp": (21.0, 24.0), "zona_conforto_ruido": (40, 55), "zona_conforto_luz": (150, 500),
               "multiplicador_stress": 1.0, "limiar_crise": 100.0},
    "hiper-reativo": {"zona_conforto_temp": (22.0, 23.0), "zona_conforto_ruido": (35, 45),
                      "zona_conforto_luz": (200, 400), "multiplicador_stress": 1.5, "limiar_crise": 80.0},
    "hipo-reativo": {"zona_conforto_temp": (20.0, 26.0), "zona_conforto_ruido": (40, 65),
                     "zona_conforto_luz": (100, 700), "multiplicador_stress": 0.7, "limiar_crise": 130.0}
}

# --- Definições dos Cenários Ambientais ---
CENARIOS = {
    "casa": {"temp_range": (19, 25), "ruido_range": (30, 50), "luz_range": (50, 400)},
    "escritorio": {"temp_range": (21, 24), "ruido_range": (45, 60), "luz_range": (400, 600)},
    "shopping": {"temp_range": (23, 45), "ruido_range": (60, 100), "luz_range": (500, 1200)}
}

# --- Parâmetros Fisiológicos e de Crise ---
TEMP_CORPORAL_NORMAL = (36.1, 37.2)
CHANCE_DE_FEBRE = 0.1
LIMITES_ABSOLUTOS = {"temp_ambiente_max": 38.0, "ruido_db_max": 95, "temp_corporal_max": 38.5}
LIMITES_DE_VARIACAO = {"ruido_delta_max": 30, "luz_delta_max": 500}


def calcular_indice_sobrecarga(perfil, temp_amb, ruido, luz, temp_corp):
    """Calcula o índice de sobrecarga sensorial com base em fatores externos e internos."""
    indice = 0.0
    p_config = PERFIS[perfil]

    # Contribuições cumulativas
    if temp_amb > p_config["zona_conforto_temp"][1]:
        indice += (temp_amb - p_config["zona_conforto_temp"][1]) * 15
    elif temp_amb < p_config["zona_conforto_temp"][0]:
        indice += (p_config["zona_conforto_temp"][0] - temp_amb) * 10
    if ruido > p_config["zona_conforto_ruido"][1]: indice += ((ruido - p_config["zona_conforto_ruido"][1]) ** 1.5)
    if luz > p_config["zona_conforto_luz"][1]: indice += (luz - p_config["zona_conforto_luz"][1]) * 0.1
    if temp_corp > TEMP_CORPORAL_NORMAL[1]: indice += 30 + ((temp_corp - TEMP_CORPORAL_NORMAL[1]) * 50)

    return round(indice * p_config["multiplicador_stress"], 2)


def simular_passo_de_tempo(perfil_nome, cenario_nome, estado_anterior, timestamp):
    """Simula um único passo no tempo, considerando o estado anterior para calcular variações."""
    perfil_config = PERFIS[perfil_nome]
    cenario_config = CENARIOS[cenario_nome]

    temperatura_ambiente = round(random.uniform(*cenario_config["temp_range"]), 1)
    ruido = random.randint(*cenario_config["ruido_range"])
    luminosidade = random.randint(*cenario_config["luz_range"])

    # Simula estado febril
    temperatura_corporal = estado_anterior.get('temperatura_corporal', round(random.uniform(*TEMP_CORPORAL_NORMAL), 1))
    if random.random() < 0.05:
        if random.random() < CHANCE_DE_FEBRE:
            temperatura_corporal = round(random.uniform(37.3, 39.0), 1)
        else:
            temperatura_corporal = round(random.uniform(*TEMP_CORPORAL_NORMAL), 1)

    # Lógica de Crise: Combina 3 fatores (cumulativo, absoluto e variação)
    indice_sobrecarga = calcular_indice_sobrecarga(perfil_nome, temperatura_ambiente, ruido, luminosidade,
                                                   temperatura_corporal)

    # Fator 1: Carga Cumulativa
    crise = 1 if indice_sobrecarga > perfil_config["limiar_crise"] else 0

    # Fator 2: Limites Absolutos (Nocaute)
    if (temperatura_ambiente > LIMITES_ABSOLUTOS["temp_ambiente_max"] or
            ruido > LIMITES_ABSOLUTOS["ruido_db_max"] or
            temperatura_corporal > LIMITES_ABSOLUTOS["temp_corporal_max"]):
        crise = 1

    # Fator 3: Variação Brusca (Choque)
    indice_choque = 0
    delta_ruido = ruido - estado_anterior.get('nivel_ruido_db', ruido)
    delta_luz = luminosidade - estado_anterior.get('luminosidade_lux', luminosidade)
    if delta_ruido > LIMITES_DE_VARIACAO["ruido_delta_max"]: indice_choque += delta_ruido * 2
    if delta_luz > LIMITES_DE_VARIACAO["luz_delta_max"]: indice_choque += delta_luz * 0.2
    if indice_choque > 50:
        crise = 1

    batimento_cardiaco = int(
        estado_anterior.get('batimento_cardiaco', 70) + (indice_sobrecarga + indice_choque) * 0.1 + random.randint(-2,
                                                                                                                   2))

    dados = {
        'perfil_usuario': perfil_nome, 'cenario_ambiental': cenario_nome, 'batimento_cardiaco': batimento_cardiaco,
        'temperatura_corporal': temperatura_corporal, 'temperatura_ambiente': temperatura_ambiente,
        'nivel_ruido_db': ruido, 'luminosidade_lux': luminosidade, 'indice_sobrecarga_calculado': indice_sobrecarga,
        'indice_choque_calculado': indice_choque, 'crise': crise, 'timestamp': timestamp
    }
    return dados


if __name__ == "__main__":
    from pymongo import MongoClient

    print("--- Iniciando Simulador de Dados Avançado (v6 - Temporal) ---")

    try:
        mongo_client = MongoClient(MONGO_CONNECTION_STRING)
        mongo_client.admin.command('ping')
        print(f"Limpando a coleção '{COLLECTION_NAME}'...")
        mongo_client[DATABASE_NAME][COLLECTION_NAME].delete_many({})
    except Exception as e:
        print(f"ERRO: Não foi possível conectar ou limpar o MongoDB. Verifique se ele está rodando. \nDetalhes: {e}")
        exit()

    NUM_JORNADAS = 15
    DURACAO_JORNADA_MIN = 60
    total_registros = NUM_JORNADAS * DURACAO_JORNADA_MIN
    print(f"Simulando {NUM_JORNADAS} jornadas de {DURACAO_JORNADA_MIN} minutos ({total_registros} registros)...")

    for j in range(NUM_JORNADAS):
        perfil_sorteado = random.choice(list(PERFIS.keys()))
        cenario_sorteado = random.choice(list(CENARIOS.keys()))
        estado_atual = {}
        timestamp_atual = datetime.now() - timedelta(minutes=DURACAO_JORNADA_MIN)

        for i in range(DURACAO_JORNADA_MIN):
            estado_atual = simular_passo_de_tempo(perfil_sorteado, cenario_sorteado, estado_atual, timestamp_atual)
            mongo_client[DATABASE_NAME][COLLECTION_NAME].insert_one(estado_atual)
            timestamp_atual += timedelta(minutes=1)

    mongo_client.close()
    print(f"\n--- Simulação Finalizada. {total_registros} registros foram gerados. ---")