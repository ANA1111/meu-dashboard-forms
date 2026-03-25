import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página (Layout Largo)
st.set_page_config(page_title="Dashboard de Resultados", page_icon="📊", layout="wide")

# Estilização básica para ocultar o menu padrão do Streamlit e deixar mais limpo
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Painel de Resultados do Formulário")
st.markdown("Visão geral e análise das respostas submetidas.")
st.divider()

# 2. Carregamento dos Dados
@st.cache_data(ttl=60)
def carregar_dados():
    url_planilha = "https://docs.google.com/spreadsheets/d/1lT12_cI5O0H2PI2jkWbCmzHECBYgh4FGnZQI7C_CbqY/export?format=csv"
    df = pd.read_csv(url_planilha)
    
    # Tenta identificar a coluna de data (geralmente a primeira no Google Forms)
    primeira_coluna = df.columns[0]
    if "data" in primeira_coluna.lower() or "carimbo" in primeira_coluna.lower():
        try:
            df[primeira_coluna] = pd.to_datetime(df[primeira_coluna])
        except:
            pass
            
    return df

try:
    df = carregar_dados()
    df_filtrado = df.copy()

    # --- 3. BARRA LATERAL (FILTROS) ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/263/263074.png", width=50) # Ícone decorativo
    st.sidebar.header("🔍 Filtros Dinâmicos")
    
    # Pula a primeira coluna se for a data/hora do Google Forms para não criar um filtro gigante
    colunas_para_filtro = df.columns[1:] if "data" in df.columns[0].lower() or "carimbo" in df.columns[0].lower() else df.columns
    
    for coluna in colunas_para_filtro:
        valores_unicos = df[coluna].dropna().unique().tolist()
        # Só cria filtro se a coluna tiver menos de 30 opções únicas (evita travar com textos long
