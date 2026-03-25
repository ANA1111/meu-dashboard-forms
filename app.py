import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Resultados do Forms", page_icon="📊", layout="wide")
st.title("📊 Dashboard de Resultados do Formulário")
st.markdown("Filtre os dados na barra lateral à esquerda e visualize os resultados dinamicamente.")

# 2. Carregamento dos Dados
@st.cache_data(ttl=60)
def carregar_dados():
    url_planilha = "https://docs.google.com/spreadsheets/d/1lT12_cI5O0H2PI2jkWbCmzHECBYgh4FGnZQI7C_CbqY/export?format=csv"
    df = pd.read_csv(url_planilha)
    return df

try:
    df = carregar_dados()
    
    # Criamos uma cópia dos dados para aplicar os filtros em cima dela
    df_filtrado = df.copy()

    # --- 3. BARRA LATERAL COM FILTROS PARA TODAS AS COLUNAS ---
    st.sidebar.header("🔍 Filtros Avançados")
    st.sidebar.markdown("Use as caixas abaixo para filtrar:")

    # O código passa por cada coluna da sua planilha e cria um filtro no menu lateral
    for coluna in df.columns:
        # Pega todas as opções únicas de resposta daquela coluna (ignorando espaços vazios)
        valores_unicos = df[coluna].dropna().unique().tolist()
        
        # Cria a caixa de múltipla escolha. Ela começa vazia.
        selecao = st.sidebar.multiselect(f"{coluna}", valores_unicos)
        
        # Se você selecionar algo no filtro, ele corta a planilha para mostrar só aquilo
        if selecao:
            df_filtrado = df_filtrado[df_filtrado[coluna].isin(selecao)]

    # --- 4. MÉTRICA RÁPIDA (Atualizada com o Filtro) ---
    st.subheader("Resumo")
    # Mostra quantas respostas sobraram após aplicar os filtros
    st.metric("Total de Respostas (Filtradas)", len(df_filtrado))
    st.divider()

    # --- 5. GRÁFICO DINÂMICO (Atualizado com o Filtro) ---
    st.subheader("Análise Visual")
    
    todas_as_colunas = df.columns.tolist()
    pergunta_selecionada = st.selectbox("Selecione qual pergunta você quer ver no gráfico:", todas_as_colunas)
    
    # Prevenção de erro: só desenha o gráfico se sobrar algum dado após os filtros
    if len(df_filtrado) > 0:
        fig = px.histogram(df_filtrado, x=pergunta_selecionada, color=pergunta_selecionada, text_auto=True)
        fig.update_layout(showlegend=False, xaxis_title="Respostas", yaxis_title="Quantidade")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados. Tente limpar alguns filtros na barra lateral.")

    st.divider()

    # --- 6. TABELA DE DADOS BRUTOS ---
    with st.expander("Ver base de dados (Planilha Filtrada)"):
        st.dataframe(df_filtrado)

except Exception as e:
    st.error("⚠️ Não foi possível carregar a planilha.")
    st.write(f"Verifique se o link está correto e público. Detalhe do erro: {e}")
