# IoTism - Prevenção Inteligente de Sobrecarga Sensorial

Um protótipo funcional inicial para demonstrar a viabilidade de um sistema de previsão de crises sensoriais em indivíduos no espectro autista, utilizando Machine Learning e uma arquitetura preparada para IoT.

**Status do Projeto:** Protótipo Inicial Concluído ✅ (Junho de 2025)

---

### Visão Geral do Projeto

Este projeto nasceu como a primeira fase de um projeto de extensão, partindo da pergunta: "e se a tecnologia pudesse oferecer um pouco mais de previsibilidade para o dia a dia de pessoas autistas que lidam com a sobrecarga sensorial?".

O objetivo deste protótipo foi construir e validar uma prova de conceito. O sistema analisa uma combinação de dados fisiológicos e ambientais (atualmente simulados) através de um modelo de Machine Learning (XGBoost) e retorna um alerta de risco em tempo real através de uma interface interativa.

É crucial ressaltar que esta é a **primeira versão de um protótipo**, cuja função principal foi validar a arquitetura de software e a viabilidade da inteligência artificial para este problema complexo.

### O Processo de Desenvolvimento

O desenvolvimento foi um processo iterativo para criar uma base de dados simulada que fosse o mais realista possível para treinar um modelo inicial eficaz. A simulação evoluiu para incluir:

* **Carga Cumulativa:** O acúmulo de múltiplos estressores leves.
* **Limites Absolutos:** O impacto de um único estímulo extremo.
* **Variação Brusca:** O "choque" de mudanças repentinas no ambiente.

Para permitir essa evolução rápida, a arquitetura foi baseada em um banco de dados **NoSQL (MongoDB)**, cuja flexibilidade foi essencial para a prototipagem. O backend foi construído com **FastAPI** em Python, e o frontend com **HTML/CSS/JS** e **ApexCharts** para visualização.

### Arquitetura do Protótipo

* `coletor_de_dados_v4.py`: Script para simulação e geração do dataset.
* `train_and_save_model.py`: Script para treinamento do modelo e serialização.
* `main.py`: A API Backend (FastAPI).
* `index.html`: O Dashboard Frontend para interação.
* `requirements.txt`: Lista de dependências Python.
* `teasense_model.pkl`: (Gerado) O modelo treinado.

---

### Como Executar o Protótipo

**(As instruções de execução permanecem as mesmas: Preparar ambiente com `pip install -r requirements.txt`, gerar dados, treinar modelo, iniciar API e abrir o `index.html`)**

---

### Próximos Passos: O Início dos Testes com IoT

Com a viabilidade do protótipo confirmada, o próximo passo imediato do projeto é **iniciar a fase de testes com dispositivos IoT do mundo real**, saindo do ambiente de simulação.

O plano é:

1.  **Coleta de Dados Reais:** Substituir a simulação pela integração com:
    * **Wearables (Smartwatches):** Para capturar métricas fisiológicas em tempo real (Batimento Cardíaco, Variabilidade da Frequência Cardíaca - HRV).
    * **Sensores do Smartphone:** Para utilizar o microfone e o sensor de luz do próprio celular como fontes de dados do ambiente imediato (Nível de Ruído e Luminosidade).

2.  **Validação e Refinamento do Modelo:** Comparar as previsões do modelo com os dados reais coletados e, fundamentalmente, com o **feedback dos usuários**, para entender as limitações atuais e refinar a lógica de detecção.

3.  **Futuro (Pós-Validação):** A visão de longo prazo, após a validação com dados reais, continua sendo a integração com sistemas de automação residencial (luzes, som, climatização) para criar um ambiente que se adapta proativamente ao usuário, prevenindo ativamente as crises.
