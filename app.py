import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Resultados do Forms", page_icon="📊", layout="wide")
st.title("📊 Dashboard de Resultados do Formulário")
st.markdown("Acompanhamento em tempo real das respostas submetidas.")

# 2. Carregamento dos Dados
# O @st.cache_data faz com que o app não recarregue a planilha toda vez que alguém clicar na tela, melhorando a performance.
@st.cache_data
def carregar_dados():
    # -------------------------------------------------------------------------
    # PARA USAR SEUS DADOS REAIS, DESCOMENTE A LINHA ABAIXO:
    # df = pd.read_csv("caminho_para_seu_arquivo.csv") 
    # ou use gspread/st.connection para ler direto do Google Sheets.
    # -------------------------------------------------------------------------
    
    # DADOS FALSOS APENAS PARA DEMONSTRAÇÃO DO VISUAL
    dados_mock = {
        "Data": ["2023-10-01", "2023-10-01", "2023-10-02", "2023-10-02", "2023-10-03", "2023-10-03"],
        "Departamento": ["Vendas", "TI", "Marketing", "Vendas", "TI", "TI"],
        "Nota de Satisfação": [5, 4, 3, 5, 5, 4],
        "Recomenda a empresa?": ["Sim", "Sim", "Não", "Sim", "Sim", "Sim"]
    }
    return pd.DataFrame(dados_mock)

df = carregar_dados()

# 3. Filtros na Barra Lateral (Sidebar)
st.sidebar.header("Filtros")
departamentos_unicos = df["Departamento"].unique().tolist()
departamento_selecionado = st.sidebar.multiselect("Filtrar por Departamento", departamentos_unicos, default=departamentos_unicos)

# Aplicando o filtro
df_filtrado = df[df["Departamento"].isin(departamento_selecionado)]

# 4. Métricas Rápidas (Cards no topo)
col1, col2, col3 = st.columns(3)
col1.metric("Total de Respostas", len(df_filtrado))
col2.metric("Média de Satisfação", round(df_filtrado["Nota de Satisfação"].mean(), 1))
col3.metric("Promotores (Recomendam)", f"{(df_filtrado['Recomenda a empresa?'] == 'Sim').sum()}")

st.divider() # Linha divisória

# 5. Gráficos Visuais
grafico_col1, grafico_col2 = st.columns(2)

with grafico_col1:
    st.subheader("Respostas por Departamento")
    # Gráfico de barras
    fig_barras = px.histogram(df_filtrado, x="Departamento", color="Departamento", text_auto=True)
    st.plotly_chart(fig_barras, use_container_width=True)

with grafico_col2:
    st.subheader("Distribuição de Notas")
    # Gráfico de pizza (rosca)
    fig_pizza = px.pie(df_filtrado, names="Nota de Satisfação", hole=0.4)
    st.plotly_chart(fig_pizza, use_container_width=True)

# 6. Tabela de Dados Brutos Oculta
with st.expander("Ver base de dados completa (Respostas Cruas)"):
    st.dataframe(df_filtrado)