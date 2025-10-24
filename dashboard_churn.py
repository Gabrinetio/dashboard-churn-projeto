
import streamlit as st
import pandas as pd
import joblib # Usaremos joblib para carregar nosso modelo e dados pré-processados

# --- Configuração da Página ---
st.set_page_config(layout="wide")
st.title('Dashboard Preditivo de Risco de Churn')

# --- Carregamento dos Dados e Modelo (Simulado) ---
# Em um projeto real, você salvaria seu modelo treinado e os dados
# usando joblib e os carregaria aqui. Para simplificar, vamos
# carregar o CSV e simular a parte da previsão.

@st.cache_data # Cache para performance
def carregar_dados():
    # Carrega o CSV original
    df = pd.read_csv('WA_Fn-UseC_-Telco-Customer-Churn.csv')

    # Adiciona uma coluna de probabilidade simulada (como se o modelo tivesse rodado)
    # Apenas para fins de visualização no dashboard
    probabilidades_simuladas = abs(df['TotalCharges'].fillna(0).astype(float) / 10000 + df['tenure'] / 100 - (df['Contract'] == 'Month-to-month') * 0.3)
    probabilidades_simuladas = (probabilidades_simuladas - probabilidades_simuladas.min()) / (probabilidades_simuladas.max() - probabilidades_simuladas.min())
    df['Probabilidade_Churn'] = probabilidades_simuladas.clip(0.05, 0.95)

    return df.sort_values(by='Probabilidade_Churn', ascending=False)

df_resultados = carregar_dados()
mrr_em_risco = df_resultados[df_resultados['Probabilidade_Churn'] > 0.5]['MonthlyCharges'].sum()

# --- Construção do Dashboard ---
st.header('Indicadores Chave de Risco')

col1, col2, col3 = st.columns(3)
col1.metric("Taxa de Churn Geral", f"{df_resultados[df_resultados['Churn'] == 'Yes'].shape[0] / df_resultados.shape[0]:.1%}")
col2.metric("MRR em Risco (Prob > 50%)", f"R$ {mrr_em_risco:,.2f}")
col3.metric("Clientes em Estado Crítico (>70%)",
            df_resultados[df_resultados['Probabilidade_Churn'] > 0.7].shape[0])

st.markdown("---")

st.header('Ferramenta de Análise e Ação')

# Filtro de probabilidade
prob_slider = st.slider(
    'Filtre clientes por nível de risco (Probabilidade de Churn):',
    min_value=0.0, max_value=1.0, value=(0.7, 1.0) # Um slider de intervalo
)

# Filtro por tipo de contrato
contrato_filtro = st.multiselect(
    'Filtre por Tipo de Contrato:',
    options=df_resultados['Contract'].unique(),
    default=df_resultados['Contract'].unique()
)

# Aplicar os filtros
df_filtrado = df_resultados[
    (df_resultados['Probabilidade_Churn'] >= prob_slider[0]) &
    (df_resultados['Probabilidade_Churn'] <= prob_slider[1]) &
    (df_resultados['Contract'].isin(contrato_filtro))
]

st.write(f"Exibindo {df_filtrado.shape[0]} clientes com base nos filtros selecionados.")

# Exibir a tabela com os clientes filtrados
st.dataframe(df_filtrado[[
    'customerID',
    'Probabilidade_Churn',
    'tenure',
    'Contract',
    'MonthlyCharges',
    'TotalCharges'
]])

