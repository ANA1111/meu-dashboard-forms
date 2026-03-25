import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Resultados do Forms", page_icon="📊", layout="wide")
st.title("📊 Dashboard de Resultados do Formulário")
st.markdown("Acompanhamento dinâmico das respostas submetidas.")

# 2. Carregamento dos Dados
@st.cache_data(ttl=60) # Atualiza os dados a cada 60 segundos automaticamente
def carregar_dados():
    # Aqui está o seu link já modificado para leitura direta pelo Pandas
    url_planilha = "https://docs.google.com/spreadsheets/d/1lT12_cI5O0H2PI2jkWbCmzHECBYgh4FGnZQI7C_CbqY/export?format=csv"
    df = pd.read_csv(url_planilha)
    return df

try:
    # Tenta carregar os dados da sua planilha
    df = carregar_dados()
    
    # 3. Métrica Rápida
    st.subheader("Resumo")
    st.metric("Total de Respostas Recebidas", len(df))
    st.divider()

    # 4. Gráfico Dinâmico (Lê as suas colunas automaticamente!)
    st.subheader("Análise Visual")
    st.markdown("Escolha uma das perguntas do seu formulário abaixo para gerar o gráfico:")
    
    # Pega o nome de todas as colunas (perguntas) da sua planilha
    todas_as_colunas = df.columns.tolist()
    
    # Cria um seletor para você escolher qual pergunta quer analisar
    pergunta_selecionada = st.selectbox("Selecione a pergunta para visualizar:", todas_as_colunas)
    
    # Gera um gráfico de barras com a contagem de respostas para a pergunta selecionada
    fig = px.histogram(df, x=pergunta_selecionada, color=pergunta_selecionada, text_auto=True)
    fig.update_layout(showlegend=False, xaxis_title="Respostas", yaxis_title="Quantidade")
    
    # Mostra o gráfico na tela
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 5. Tabela de Dados Brutos
    with st.expander("Ver base de dados completa (Planilha)"):
        st.dataframe(df)

except Exception as e:
    # Se algo der errado (ex: planilha não estiver pública), ele avisa de forma elegante
    st.error("⚠️ Não foi possível carregar a planilha.")
    st.write(f"Verifique se o link está correto e se o acesso geral está marcado como 'Qualquer pessoa com o link'. Detalhe do erro: {e}")
