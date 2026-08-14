import streamlit as st
import pandas as pd
import plotly.express as px
import json

# 1. Configuração da Página
st.set_page_config(
    page_title="Credit & Commercial Intelligence",
    page_icon="⚡",
    layout="wide"
)

# Estilo personalizado simples
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. Carregar Dados
@st.cache_data
def carregar_dados():
    try:
        # Tenta carregar do arquivo JSON
        with open('base_score.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    except FileNotFoundError:
        # Fallback para o CSV caso o JSON não esteja na raiz
        df = pd.read_csv('base_score_powerbi.csv', sep=';')
    
    # Tratamento de colunas numéricas
    cols_num = ['Limite_Atual', 'Limite_Recomendado', 'Score_Credito', 'Compra_Media', 'Probabilidade_Risco_Perc']
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

df = carregar_dados()

# 3. Barra Lateral (Filtros Global)
st.sidebar.header("🔍 Filtros de Operação")

cidades = ["Todas"] + sorted(df['Cidade'].astype(str).unique().tolist())
cidade_sel = st.sidebar.selectbox("Cidade", cidades)

setores = ["Todos"] + sorted(df['Cod_Setor'].astype(str).unique().tolist())
setor_sel = st.sidebar.selectbox("Setor Comercial", setores)

faixas = ["Todas"] + sorted(df['Faixa_Score'].astype(str).unique().tolist())
faixa_sel = st.sidebar.selectbox("Faixa de Score", faixas)

acoes = ["Todas"] + sorted(df['Acao_Recomendada'].astype(str).unique().tolist())
acao_sel = st.sidebar.selectbox("Ação Recomendada", acoes)

# Aplicar Filtros
df_filtrado = df.copy()
if cidade_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Cidade'] == cidade_sel]
if setor_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Cod_Setor'] == setor_sel]
if faixa_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Faixa_Score'] == faixa_sel]
if acao_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Acao_Recomendada'] == acao_sel]

# 4. Cabeçalho e KPIs
st.title("⚡ Credit & Commercial Intelligence")
st.caption("Painel Preditivo de Risco e Concessão de Crédito")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_clientes = len(df_filtrado)
limite_atual = df_filtrado['Limite_Atual'].sum()
limite_rec = df_filtrado['Limite_Recomendado'].sum()
score_medio = df_filtrado['Score_Credito'].mean() if total_clientes > 0 else 0

kpi1.metric("Total de Clientes", f"{total_clientes:,}")
kpi2.metric("Limite Atual Total", f"R$ {limite_atual:,.2f}")
kpi3.metric("Limite Recomendado", f"R$ {limite_rec:,.2f}", delta=f"R$ {limite_rec - limite_atual:,.2f}")
kpi4.metric("Score Médio", f"{score_medio:.1f} / 100")

st.divider()

# 5. Gráficos Interativos (Plotly)
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Distribuição por Faixa de Score")
    fig_score = px.pie(
        df_filtrado, 
        names='Faixa_Score', 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_score, use_container_width=True)

with col_g2:
    st.subheader("Limite Atual vs. Recomendado por Ação")
    df_acao = df_filtrado.groupby('Acao_Recomendada')[['Limite_Atual', 'Limite_Recomendado']].sum().reset_index()
    fig_bar = px.bar(
        df_acao, 
        x='Acao_Recomendada', 
        y=['Limite_Atual', 'Limite_Recomendado'],
        barmode='group',
        labels={'value': 'R$', 'variable': 'Tipo de Limite'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# 6. Tabela Operacional Detalhada
st.subheader("📋 Matriz Operacional de Clientes")

colunas_tabela = [
    'Cod_Cliente', 'Nome_Fantasia', 'Cidade', 'Cod_Setor', 
    'Faixa_Score', 'Score_Credito', 'Limite_Atual', 
    'Limite_Recomendado', 'Acao_Recomendada'
]

st.dataframe(
    df_filtrado[colunas_tabela],
    use_container_width=True,
    hide_index=True
)