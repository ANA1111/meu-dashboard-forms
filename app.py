import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard de Resultados", page_icon="📊", layout="wide")

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
    
    # Tentativa de formatar a data, se existir
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
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/263/263074.png", width=50)
    st.sidebar.header("🔍 Filtros Dinâmicos")
    
    colunas_para_filtro = df.columns[1:] if "data" in df.columns[0].lower() or "carimbo" in df.columns[0].lower() else df.columns
    
    for coluna in colunas_para_filtro:
        valores_unicos = df[coluna].dropna().unique().tolist()
        if len(valores_unicos) < 30:
            selecao = st.sidebar.multiselect(f"{coluna}", valores_unicos)
            if selecao:
                df_filtrado = df_filtrado[df_filtrado[coluna].isin(selecao)]

    # --- 4. MÉTRICAS PRINCIPAIS ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Cadastros Filtrados", len(df_filtrado))
    with col2:
        primeira_col = df_filtrado.columns[0]
        if pd.api.types.is_datetime64_any_dtype(df_filtrado[primeira_col]):
            ultima_resposta = df_filtrado[primeira_col].max().strftime("%d/%m/%Y")
            st.metric("Última Atualização", ultima_resposta)
        else:
            st.metric("Total na Base", len(df))
    with col3:
        st.metric("Status", "Online 🟢")

    st.divider()

    # --- 5. GRÁFICOS LADO A LADO ---
    if len(df_filtrado) > 0:
        todas_as_colunas = df_filtrado.columns.tolist()
        graf_col1, graf_col2 = st.columns(2)
        
        with graf_col1:
            st.subheader("Análise de Distribuição (Barras)")
            pergunta_barras = st.selectbox("Escolha a pergunta para o Gráfico de Barras:", todas_as_colunas, index=1 if len(todas_as_colunas)>1 else 0)
            fig_barras = px.histogram(df_filtrado, x=pergunta_barras, color=pergunta_barras, text_auto=True)
            fig_barras.update_layout(showlegend=False, xaxis_title="", yaxis_title="Quantidade")
            st.plotly_chart(fig_barras, use_container_width=True)

        with graf_col2:
            st.subheader("Análise de Proporção (Pizza)")
            pergunta_pizza = st.selectbox("Escolha a pergunta para o Gráfico de Pizza:", todas_as_colunas, index=2 if len(todas_as_colunas)>2 else 0)
            contagem_pizza = df_filtrado[pergunta_pizza].value_counts().reset_index()
            contagem_pizza.columns = [pergunta_pizza, 'Quantidade']
            fig_pizza = px.pie(contagem_pizza, names=pergunta_pizza, values='Quantidade', hole=0.4)
            fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pizza, use_container_width=True)
            
        st.divider()

        # --- NOVO: 6. LISTA DOS DADOS PRINCIPAIS ---
        st.subheader("👥 Detalhes dos Cadastros")
        st.markdown("Lista rápida com os principais dados das respostas filtradas acima.")
        
        # Lista com as palavras-chave que você quer buscar nas colunas
        termos_desejados = ["nome", "mei", "cnpj", "cidade", "bairro"]
        
        # O código procura na sua planilha colunas que contenham essas palavras
        colunas_encontradas = []
        for coluna in df_filtrado.columns:
            for termo in termos_desejados:
                # Transforma tudo em minúsculo para comparar sem erro
                if termo in coluna.lower() and coluna not in colunas_encontradas:
                    colunas_encontradas.append(coluna)
        
        # Se ele encontrar as colunas, ele mostra uma tabela só com elas
        if colunas_encontradas:
            # Oculta o índice (aquela coluna com números 0, 1, 2...) para ficar mais limpo
            st.dataframe(df_filtrado[colunas_encontradas], use_container_width=True, hide_index=True)
        else:
            st.info("As colunas de Nome, MEI, CNPJ, Cidade ou Bairro não foram encontradas com esses nomes exatos.")

    else:
        st.warning("⚠️ Nenhum dado encontrado com os filtros atuais. Limpe os filtros na barra lateral.")

    st.divider()

    # --- 7. DADOS BRUTOS (TABELA COMPLETA) ---
    with st.expander("📋 Clique aqui para visualizar a planilha COMPLETA com todas as colunas"):
        st.dataframe(df_filtrado, use_container_width=True)

except Exception as e:
    st.error("⚠️ Erro ao processar os dados.")
    st.write(f"Detalhe: {e}")
