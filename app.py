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
        # Só cria filtro se a coluna tiver menos de 30 opções únicas (evita travar com textos longos abertos)
        if len(valores_unicos) < 30:
            selecao = st.sidebar.multiselect(f"{coluna}", valores_unicos)
            if selecao:
                df_filtrado = df_filtrado[df_filtrado[coluna].isin(selecao)]

    # --- 4. MÉTRICAS PRINCIPAIS (KPIs) No topo ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Respostas", len(df_filtrado))
    with col2:
        # Se houver uma coluna de data, mostra a data da última resposta
        primeira_col = df_filtrado.columns[0]
        if pd.api.types.is_datetime64_any_dtype(df_filtrado[primeira_col]):
            ultima_resposta = df_filtrado[primeira_col].max().strftime("%d/%m/%Y")
            st.metric("Última Resposta", ultima_resposta)
        else:
            st.metric("Colunas Analisadas", len(df_filtrado.columns))
    with col3:
        st.metric("Status da Conexão", "Ativa 🟢")

    st.divider()

    # --- 5. GRÁFICOS ESTRUTURADOS (LADO A LADO) ---
    if len(df_filtrado) > 0:
        todas_as_colunas = df_filtrado.columns.tolist()
        
        # Criando duas colunas para os gráficos
        graf_col1, graf_col2 = st.columns(2)
        
        with graf_col1:
            st.subheader("Análise de Distribuição (Barras)")
            # Deixa o usuário escolher a pergunta para o gráfico 1
            pergunta_barras = st.selectbox("Escolha a pergunta para o Gráfico de Barras:", todas_as_colunas, index=1 if len(todas_as_colunas)>1 else 0)
            
            fig_barras = px.histogram(df_filtrado, x=pergunta_barras, color=pergunta_barras, text_auto=True)
            fig_barras.update_layout(showlegend=False, xaxis_title="", yaxis_title="Quantidade")
            st.plotly_chart(fig_barras, use_container_width=True)

        with graf_col2:
            st.subheader("Análise de Proporção (Pizza)")
            # Deixa o usuário escolher a pergunta para o gráfico 2
            pergunta_pizza = st.selectbox("Escolha a pergunta para o Gráfico de Pizza:", todas_as_colunas, index=2 if len(todas_as_colunas)>2 else 0)
            
            # Conta os valores para fazer o gráfico de pizza
            contagem_pizza = df_filtrado[pergunta_pizza].value_counts().reset_index()
            contagem_pizza.columns = [pergunta_pizza, 'Quantidade']
            
            fig_pizza = px.pie(contagem_pizza, names=pergunta_pizza, values='Quantidade', hole=0.4) # hole=0.4 faz virar um gráfico de "rosca"
            fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pizza, use_container_width=True)
    else:
        st.warning("⚠️ Nenhum dado encontrado com os filtros atuais. Limpe os filtros na barra lateral.")

    st.divider()

    # --- 6. DADOS BRUTOS (TABELA) ---
    st.subheader("📋 Base de Dados Completa")
    with st.expander("Clique aqui para visualizar a planilha em formato de tabela"):
        st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error("⚠️ Erro ao processar os dados.")
    st.write(f"Detalhe: {e}")
