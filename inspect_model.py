# Script: inspect_model.py
import joblib
import pandas as pd

# O nome do arquivo que queremos inspecionar
NOME_ARQUIVO_MODELO = 'teasense_model.pkl'


def inspecionar_modelo():
    """
    Carrega um modelo salvo de um arquivo .pkl e mostra suas informações.
    """
    print(f"--- Inspecionando o arquivo '{NOME_ARQUIVO_MODELO}' ---")

    try:
        # Passo 1: Carregar o modelo do arquivo
        modelo = joblib.load(NOME_ARQUIVO_MODELO)
        print("Arquivo carregado com sucesso!\n")

        # Passo 2: Mostrar o objeto do modelo
        # Isso imprimirá a estrutura completa do modelo XGBoost com todos os seus parâmetros.
        print("1. Configuração do Objeto do Modelo:")
        print(modelo)

        # Passo 3: Mostrar a "Importância das Features"
        # Esta é a parte mais interessante! Ela nos diz quais dados de sensores o modelo
        # considerou mais importantes para fazer suas previsões.
        print("\n" + "=" * 50 + "\n")
        print("2. Importância das Features (O que o modelo aprendeu?):")

        if hasattr(modelo, 'feature_importances_'):
            # Precisamos saber os nomes das features na ordem em que o modelo foi treinado
            features = [
                'batimento_cardiaco',
                'temperatura_corporal',
                'temperatura_ambiente',
                'nivel_ruido_db',
                'luminosidade_lux'
            ]

            # Criamos um DataFrame para visualizar melhor
            importancias = pd.DataFrame({
                'Feature': features,
                'Importancia': modelo.feature_importances_
            }).sort_values(by='Importancia', ascending=False)

            print(importancias)
            print(
                "\nAnálise: Quanto maior o valor da 'Importância', mais peso essa variável teve na decisão do modelo.")
        else:
            print("Não foi possível encontrar os dados de importância das features neste modelo.")

    except FileNotFoundError:
        print(f"ERRO: O arquivo '{NOME_ARQUIVO_MODELO}' não foi encontrado.")
        print("Certifique-se de executar primeiro o script 'train_and_save_model.py'.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


# Ponto de entrada do script
if __name__ == "__main__":
    inspecionar_modelo()