import pandas as pd
import xgboost as xgb
import joblib
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Configurações ---
MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
DATABASE_NAME = "teasense_db"
COLLECTION_NAME = "sensor_data_v6"  # Usando nosso melhor dataset
MODEL_FILENAME = 'teasense_model.pkl'


def carregar_dados_do_mongodb():
    """Carrega os dados da coleção especificada no MongoDB."""
    print(f"Carregando dados da coleção '{COLLECTION_NAME}'...")
    try:
        client = MongoClient(MONGO_CONNECTION_STRING)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        dados = list(collection.find({}))
        client.close()

        if len(dados) == 0:
            print(f"ERRO: Nenhum dado encontrado na coleção. Execute o 'coletor_de_dados_v6.py' primeiro.")
            return None
        print(f"{len(dados)} registros carregados com sucesso.")
        return pd.DataFrame(dados)
    except Exception as e:
        print(f"ERRO ao carregar dados do MongoDB: {e}")
        return None


def preparar_dados(df):
    """Prepara os dados, selecionando as colunas de features e o alvo (target)."""
    print("Preparando dados para o treinamento...")
    features = [
        'batimento_cardiaco',
        'temperatura_corporal',
        'temperatura_ambiente',
        'nivel_ruido_db',
        'luminosidade_lux'
    ]
    target = 'crise'

    if target not in df.columns or not all(f in df.columns for f in features):
        print("ERRO: O DataFrame não contém as colunas necessárias.")
        return None, None

    X = df[features]
    y = df[target]
    print("Dados prontos.")
    return X, y


if __name__ == "__main__":
    print("\n--- Iniciando Ciclo Final de Treinamento e Avaliação ---")

    dataframe = carregar_dados_do_mongodb()

    if dataframe is not None:
        X, y = preparar_dados(dataframe)

        if X is not None:
            # --- FASE 1: AVALIAÇÃO ---
            print("\n[FASE 1 de 2] Avaliando a performance do modelo...")

            # Separa os dados em treino e teste para uma avaliação honesta
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

            # Treina o modelo APENAS com os dados de treino
            modelo_para_avaliacao = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
            modelo_para_avaliacao.fit(X_train, y_train)

            # Avalia o modelo nos dados de teste que ele nunca viu
            predicoes = modelo_para_avaliacao.predict(X_test)
            print("\n--- Relatório de Performance em Dados de Teste ---")
            print(classification_report(y_test, predicoes, target_names=['Sem Crise (0)', 'Crise (1)']))
            print("--------------------------------------------------\n")

            # --- FASE 2: TREINAMENTO PARA PRODUÇÃO ---
            print("[FASE 2 de 2] Treinando o modelo final com TODOS os dados...")

            # Cria e treina o modelo final com 100% dos dados (X e y)
            modelo_final_producao = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
            modelo_final_producao.fit(X, y)

            # Salva ESTE modelo final, o mais completo, no arquivo
            joblib.dump(modelo_final_producao, MODEL_FILENAME)
            print(f"\nModelo final (treinado com todos os dados) foi salvo com sucesso em: '{MODEL_FILENAME}'")

    print("\n--- Processo Finalizado ---")