import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURAÇÃO DA PÁGINA E UI ---
st.set_page_config(page_title="Dashboard de Resultados", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Painel de Resultados Dinâmico")
st.markdown("Acompanhe as métricas e gerencie os cadastros em tempo real.")
st.divider()

# --- 2. CARREGAMENTO DE DADOS ---
@st.cache_data(ttl=60)
def carregar_dados():
    url_planilha = "https://docs.google.com/spreadsheets/d/1lT12_cI5O0H2PI2jkWbCmzHECBYgh4FGnZQI7C_CbqY/export?format=csv"
    df = pd.read_csv(url_planilha)
    
    primeira_coluna = df.columns[0]
    if "data" in primeira_coluna.lower() or "carimbo" in primeira_coluna.lower():
        try:
            df[primeira_coluna] = pd.to_datetime(df[primeira_coluna])
        except:
            pass
    return df

try:
    with st.spinner("Sincronizando dados com a base..."):
        df = carregar_dados()
        df_filtrado = df.copy()

    # --- 3. BARRA LATERAL (APENAS 2 FILTROS) ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2040/2040504.png", width=60)
        st.header("🔍 Filtros")
        st.markdown("Refine sua busca abaixo:")
        
        coluna_cidade = next((col for col in df.columns if "cidade" in col.lower()), None)
        coluna_mei = next((col for col in df.columns if "mei" in col.lower() and "cnpj" not in col.lower()), None) 
        
        if coluna_cidade:
            valores_cidade = sorted(df[coluna_cidade].dropna().unique().tolist())
            selecao_cidade = st.multiselect(f"📍 {coluna_cidade}", valores_cidade)
            if selecao_cidade:
                df_filtrado = df_filtrado[df_filtrado[coluna_cidade].isin(selecao_cidade)]
                
        if coluna_mei:
            valores_mei = sorted(df[coluna_mei].dropna().unique().tolist())
            selecao_mei = st.multiselect(f"🏢 {coluna_mei}", valores_mei)
            if selecao_mei:
                df_filtrado = df_filtrado[df_filtrado[coluna_mei].isin(selecao_mei)]
                
        if not coluna_cidade and not coluna_mei:
            st.warning("⚠️ Colunas de Cidade e MEI não encontradas para gerar os filtros.")
            
        st.divider()
        st.caption("A base atualiza automaticamente a cada 60 segundos.")

    # --- 4. MÉTRICAS GLOBAIS ---
    col1, col2, col3 = st.columns(3)
    
    col1.metric("📌 Total Filtrado", f"{len(df_filtrado)} registros")
    
    primeira_col = df_filtrado.columns[0]
    if pd.api.types.is_datetime64_any_dtype(df_filtrado[primeira_col]) and len(df_filtrado) > 0:
        ultima_resposta = df_filtrado[primeira_col].max().strftime("%d/%m/%Y às %H:%M")
        col2.metric("⏱️ Última Atualização", ultima_resposta)
    else:
        col2.metric("🗃️ Total na Base", f"{len(df)} registros")
        
    col3.metric("📡 Status", "Sincronizado", delta="Online", delta_color="normal")

    st.write("") 

    # --- 5. ABAS DE NAVEGAÇÃO ---
    aba_graficos, aba_dados = st.tabs(["📈 Visão Geral", "👥 Cadastros e Base de Dados"])

    # ==========================================
    # ABA 1: GRÁFICOS
    # ==========================================
    with aba_graficos:
        if len(df_filtrado) > 0:
            todas_as_colunas = df_filtrado.columns.tolist()
            graf_col1, graf_col2 = st.columns(2)
            
            with graf_col1:
                st.markdown("#### 📊 Distribuição Principal")
                pergunta_barras = st.selectbox("Eixo X (Barras):", todas_as_colunas, index=1 if len(todas_as_colunas)>1 else 0)
                
                fig_barras = px.histogram(df_filtrado, x=pergunta_barras, color=pergunta_barras, text_auto=True)
                fig_barras.update_layout(
                    showlegend=False, 
                    xaxis_title="", 
                    yaxis_title="Quantidade",
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig_barras, use_container_width=True)

            with graf_col2:
                st.markdown("#### 🍕 Proporções")
                pergunta_pizza = st.selectbox("Categoria (Pizza):", todas_as_colunas, index=2 if len(todas_as_colunas)>2 else 0)
                
                contagem_pizza = df_filtrado[pergunta_pizza].value_counts().reset_index()
                contagem_pizza.columns = [pergunta_pizza, 'Quantidade']
                fig_pizza = px.pie(contagem_pizza, names=pergunta_pizza, values='Quantidade', hole=0.45)
                fig_pizza.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=0)))
                fig_pizza.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig_pizza, use_container_width=True)
        else:
            st.warning("⚠️ Nenhum dado encontrado. Ajuste os filtros na barra lateral.")

    # ==========================================
    # ABA 2: DADOS E TABELAS
    # ==========================================
    with aba_dados:
        st.markdown("#### 📋 Cadastros Principais")
        st.markdown("Visualização rápida dos dados de identificação, localização e contato.")
        
        # 1. O que eu QUERO que apareça:
        termos_desejados = ["nome", "mei", "cnpj", "cidade", "bairro", "telefone", "whatsapp", "whats", "recado"]
        
        # 2. O que eu NÃO QUERO que apareça de jeito nenhum:
        termos_proibidos = ["mãe", "mae", "pai"]
        
        colunas_encontradas = []
        for coluna in df_filtrado.columns:
            coluna_min = coluna.lower()
            
            # Verifica se tem alguma palavra proibida na coluna (ex: "nome da mãe")
            tem_proibido = any(proibido in coluna_min for proibido in termos_proibidos)
            
            # Se não tiver palavra proibida, ele vê se tem as palavras desejadas
            if not tem_proibido:
                for termo in termos_desejados:
                    if termo in coluna_min and coluna not in colunas_encontradas:
                        colunas_encontradas.append(coluna)
        
        if colunas_encontradas:
            st.dataframe(df_filtrado[colunas_encontradas], use_container_width=True, hide_index=True)
        else:
            st.info("Colunas essenciais não encontradas com esses nomes exatos.")

        st.divider()
        
        with st.expander("🔍 Ver Base de Dados Completa (Todas as colunas, incluindo nomes dos pais)"):
            st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error("⚠️ Ocorreu um erro ao conectar com a base de dados.")
    st.caption(f"Detalhes técnicos: {e}")
