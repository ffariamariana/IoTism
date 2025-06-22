import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uuid
from pymongo import MongoClient
from datetime import datetime

# Inicialização da API com o título final
app = FastAPI(
    title="IoTism API",
    description="API para prever o risco de sobrecarga sensorial com base em dados de sensores.",
    version="1.0.0"
)

# Configuração do CORS para permitir a comunicação com o front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexão com DB e Carregamento do Modelo
MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
DATABASE_NAME = "teasense_db"
MODEL_FILENAME = 'teasense_model.pkl'

try:
    modelo = joblib.load(MODEL_FILENAME)
    mongo_client = MongoClient(MONGO_CONNECTION_STRING)
    db = mongo_client[DATABASE_NAME]
    feedback_collection = db["feedback_data"]
    print("INFO:     Modelo e conexão com MongoDB carregados com sucesso.")
except Exception as e:
    print(f"ERRO:     Falha na inicialização. Detalhes: {e}")
    modelo = None


# Modelos de Dados Pydantic para validação de entrada
class SensorData(BaseModel):
    batimento_cardiaco: int
    temperatura_corporal: float
    temperatura_ambiente: float
    nivel_ruido_db: int
    luminosidade_lux: int


class FeedbackData(BaseModel):
    prediction_id: str
    tipo_feedback: str


# Endpoints da API
@app.get("/")
def read_root():
    return {"status": "API do IoTism está no ar!"}


@app.post("/predict")
async def predict(data: SensorData):
    """Recebe dados dos sensores e retorna uma previsão de risco com um ID único."""
    if modelo is None:
        return {"erro": "Modelo não carregado. Verifique o terminal para erros na inicialização."}

    dados_df = pd.DataFrame([data.dict()])

    previsao_array = modelo.predict(dados_df)
    probabilidade_array = modelo.predict_proba(dados_df)

    previsao = int(previsao_array[0])
    probabilidade_crise = float(probabilidade_array[0][1])

    return {
        "prediction_id": str(uuid.uuid4()),
        "previsao_crise": previsao,
        "risco_detectado": "Sim" if previsao == 1 else "Não",
        "probabilidade_de_crise": round(probabilidade_crise * 100, 2)
    }


@app.post("/feedback")
async def receive_feedback(data: FeedbackData):
    """Recebe e armazena o feedback do usuário no banco de dados."""
    try:
        documento_feedback = {
            "prediction_id": data.prediction_id,
            "tipo_feedback": data.tipo_feedback,
            "timestamp_feedback": datetime.now()
        }
        feedback_collection.insert_one(documento_feedback)
        return {"status": "sucesso", "mensagem": "Feedback recebido com sucesso!"}
    except Exception as e:
        return {"status": "erro", "mensagem": f"Falha ao salvar o feedback: {e}"}