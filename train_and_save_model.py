import pandas as pd
import xgboost as xgb
import joblib
from pymongo import MongoClient
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Configurações ---
MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
DATABASE_NAME = "teasense_db"
COLLECTION_NAME = "sensor_data_v6"
MODEL_FILENAME = 'teasense_model.pkl'


def carregar_dados_do_mongodb():
    """Carrega os dados da coleção especificada no MongoDB."""
    print(f"Carregando dados da coleção '{COLLECTION_NAME}'...")
    try:
        client = MongoClient(MONGO_CONNECTION_STRING)
        dados = list(client[DATABASE_NAME][COLLECTION_NAME].find({}))
        client.close()

        if len(dados) == 0:
            print("ERRO: Nenhum dado encontrado. Execute o coletor de dados primeiro.")
            return None
        return pd.DataFrame(dados)
    except Exception as e:
        print(f"ERRO ao carregar dados do MongoDB: {e}")
        return None


def preparar_dados_para_treino(df):
    """Prepara os dados para o treinamento final, selecionando features e target."""
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
    return X, y


if __name__ == "__main__":
    print("\n--- Iniciando Treinamento e Salvamento do Modelo Definitivo ---")

    dataframe = carregar_dados_do_mongodb()

    if dataframe is not None:
        X, y = preparar_dados_para_treino(dataframe)

        if X is not None:
            # Para o modelo final, usamos todos os dados para o treinamento
            modelo_final = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')

            print("Treinando o modelo final com todo o dataset...")
            modelo_final.fit(X, y)

            joblib.dump(modelo_final, MODEL_FILENAME)
            print(f"\nModelo salvo com sucesso no arquivo: '{MODEL_FILENAME}'")