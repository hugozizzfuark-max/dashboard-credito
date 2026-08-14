import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# ---------------------------------------------------------
# 1. Configuração da Página e Tema Executive Dark
# ---------------------------------------------------------
st.set_page_config(
    page_title="Credit & Commercial Intelligence | Executive Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Personalizada
st.markdown("""
    <style>
    /* Fundo geral e fontes */
    .stApp { background-color: #0b0f19; color: #f8fafc; }
    
    /* Customização dos Cards de KPI */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
    }
    [data-testid="stMetric"] {
        background-color: #1e293b;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    /* Abas estilizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 10px 20px;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Carregamento e Tratamento de Dados
# ---------------------------------------------------------
@st.cache_data
def carregar_dados():
    try:
        with open('base_score.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    except Exception:
        df = pd.read_csv('base_score_powerbi.csv', sep=';')

    # Garantir conversão correta de tipos numéricos
    cols_numericas = [
        'Limite_Atual', 'Limite_Usado', 'Limite_Disponivel', 'Compra_Media',
        'Maior_Compra', 'Acumulado_Vendas', 'Atraso_Medio_Historico',
        'Perc_Utilizacao_Limite', 'Razao_Compra_Limite', 'Dias_Sem_Comprar',
        'Qtd_Titulos_Pendentes', 'Valor_Total_Pendente', 'Maior_Atraso_Dias_Pendente',
        'Target_Inadimplente', 'Probabilidade_Risco_Perc', 'Score_Credito',
        'Limite_Recomendado'
    ]
    
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Criar coluna combinada de PDV para busca fácil
    if 'Cod_Cliente' in df.columns and 'Nome_Fantasia' in df.columns:
        df['PDV_Label'] = df['Cod_Cliente'].astype(str) + " - " + df['Nome_Fantasia'].astype(str)
    else:
        df['PDV_Label'] = df['Cod_Cliente'].astype(str)

    return df

df = carregar_dados()

# ---------------------------------------------------------
# 3. Sidebar (Filtros Globais + Filtro por PDV)
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/shield-with-sign.png", width=60)
st.sidebar.title("🎛️ Filtros da Operação")

# Filtro por PDV / Cliente
pdvs = ["Todos os PDVs"] + sorted(df['PDV_Label'].unique().tolist())
pdv_sel = st.sidebar.selectbox("🔎 Filtrar por PDV / Cliente", pdvs)

# Demais Filtros
cidades = ["Todas"] + sorted(df['Cidade'].astype(str).unique().tolist())
cidade_sel = st.sidebar.selectbox("📍 Cidade", cidades)

setores = ["Todos"] + sorted(df['Cod_Setor'].astype(str).unique().tolist())
setor_sel = st.sidebar.selectbox("🏬 Setor Comercial", setores)

faixas = ["Todas"] + sorted(df['Faixa_Score'].astype(str).unique().tolist())
faixa_sel = st.sidebar.selectbox("⭐ Faixa de Score", faixas)

acoes = ["Todas"] + sorted(df['Acao_Recomendada'].astype(str).unique().tolist())
acao_sel = st.sidebar.selectbox("🎯 Ação Recomendada", acoes)

# Aplicação dos Filtros
df_filtrado = df.copy()

if pdv_sel != "Todos os PDVs":
    df_filtrado = df_filtrado[df_filtrado['PDV_Label'] == pdv_sel]
if cidade_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Cidade'] == cidade_sel]
if setor_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Cod_Setor'] == setor_sel]
if faixa_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Faixa_Score'] == faixa_sel]
if acao_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Acao_Recomendada'] == acao_sel]

# ---------------------------------------------------------
# 4. Cabeçalho Principal e KPIs
# ---------------------------------------------------------
st.title("🛡️ Credit & Commercial Intelligence")
st.caption("Sistema de Análise Preditiva de Risco e Expansão Comercial")

# Métricas Principais
k1, k2, k3, k4, k5 = st.columns(5)

total_pdvs = len(df_filtrado)
lim_atual = df_filtrado['Limite_Atual'].sum()
lim_rec = df_filtrado['Limite_Recomendado'].sum()
risco_medio = df_filtrado['Probabilidade_Risco_Perc'].mean() * 100 if total_pdvs > 0 else 0
val_pendente = df_filtrado['Valor_Total_Pendente'].sum()

k1.metric("Total de PDVs", f"{total_pdvs:,}")
k2.metric("Limite Atual Total", f"R$ {lim_atual:,.2f}")
k3.metric("Limite Recomendado", f"R$ {lim_rec:,.2f}", delta=f"R$ {lim_rec - lim_atual:,.2f}")
k4.metric("Probab. Risco Média", f"{risco_medio:.1f}%")
k5.metric("Total Pendente (Inad.)", f"R$ {val_pendente:,.2f}", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. Organização em Painéis (Tabs)
# ---------------------------------------------------------
tab_macro, tab_matriz, tab_custom = st.tabs([
    "📊 Visão Geral & Score", 
    "📋 Matriz Operacional Completa", 
    "🛠️ Construtor de Gráficos"
])

# =========================================================
# ABA 1: Visão Geral & Score
# =========================================================
with tab_macro:
    c_g1, c_g2 = st.columns(2)

    with c_g1:
        st.subheader("📊 Distribuição de Clientes por Faixa de Score")
        df_faixa = df_filtrado['Faixa_Score'].value_counts().reset_index()
        df_faixa.columns = ['Faixa_Score', 'Quantidade']
        
        # Gráfico de Barras Horizontais (Substituindo o gráfico de pizza)
        fig_score_bar = px.bar(
            df_faixa,
            x='Quantidade',
            y='Faixa_Score',
            orientation='h',
            text='Quantidade',
            color='Faixa_Score',
            color_discrete_sequence=px.colors.qualitative.Dark24,
            template="plotly_dark"
        )
        fig_score_bar.update_layout(showlegend=False, xaxis_title="Nº de Clientes", yaxis_title="")
        st.plotly_chart(fig_score_bar, use_container_width=True)

    with c_g2:
        st.subheader("⚖️ Limite Atual vs. Recomendado por Ação")
        df_acao_lim = df_filtrado.groupby('Acao_Recomendada')[['Limite_Atual', 'Limite_Recomendado']].sum().reset_index()
        fig_bar_lim = px.bar(
            df_acao_lim,
            x='Acao_Recomendada',
            y=['Limite_Atual', 'Limite_Recomendado'],
            barmode='group',
            labels={'value': 'R$ Total', 'variable': 'Tipo de Limite'},
            template="plotly_dark",
            color_discrete_map={'Limite_Atual': '#64748b', 'Limite_Recomendado': '#10b981'}
        )
        st.plotly_chart(fig_bar_lim, use_container_width=True)

    st.divider()

    c_g3, c_g4 = st.columns(2)

    with c_g3:
        st.subheader("🔴 Risco % vs. Score de Crédito")
        fig_scatter = px.scatter(
            df_filtrado,
            x='Score_Credito',
            y='Probabilidade_Risco_Perc',
            size='Valor_Total_Pendente',
            color='Acao_Recomendada',
            hover_name='Nome_Fantasia',
            labels={'Probabilidade_Risco_Perc': 'Probab. Risco (%)', 'Score_Credito': 'Score de Crédito'},
            template="plotly_dark"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with c_g4:
        st.subheader("⏳ Atraso Médio Histórico por Cidade (Dias)")
        df_atraso_cid = df_filtrado.groupby('Cidade')['Atraso_Medio_Historico'].mean().reset_index().sort_values(by='Atraso_Medio_Historico', ascending=False).head(10)
        fig_atraso = px.bar(
            df_atraso_cid,
            x='Atraso_Medio_Historico',
            y='Cidade',
            orientation='h',
            color='Atraso_Medio_Historico',
            color_continuous_scale='Reds',
            template="plotly_dark"
        )
        fig_atraso.update_layout(xaxis_title="Dias Média", yaxis_title="")
        st.plotly_chart(fig_atraso, use_container_width=True)


# =========================================================
# ABA 2: Matriz Operacional Completa
# =========================================================
with tab_matriz:
    st.subheader("📋 Matriz Detalhada de Risco e Concessão de Crédito")
    st.caption("Esta tabela contém todas as métricas detalhadas solicitadas para auditoria e tomada de decisão.")

    cols_matriz = [
        'Cod_Cliente', 'Nome_Fantasia', 'Cidade', 'Cod_Setor',
        'Score_Credito', 'Faixa_Score', 'Acao_Recomendada', 'Limite_Recomendado',
        'Limite_Atual', 'Valor_Total_Pendente', 'Qtd_Titulos_Pendentes',
        'Maior_Atraso_Dias_Pendente', 'Atraso_Medio_Historico', 'Dias_Sem_Comprar',
        'Probabilidade_Risco_Perc', 'Perc_Utilizacao_Limite', 'Razao_Compra_Limite',
        'Target_Inadimplente'
    ]

    # Filtrar apenas colunas existentes no dataset
    cols_existentes = [c for c in cols_matriz if c in df_filtrado.columns]

    st.dataframe(
        df_filtrado[cols_existentes],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cod_Cliente": st.column_config.TextColumn("Código"),
            "Nome_Fantasia": st.column_config.TextColumn("Nome / PDV"),
            "Score_Credito": st.column_config.NumberColumn("Score", format="%d"),
            "Limite_Recomendado": st.column_config.NumberColumn("Lim. Recomendado", format="R$ %.2f"),
            "Limite_Atual": st.column_config.NumberColumn("Lim. Atual", format="R$ %.2f"),
            "Valor_Total_Pendente": st.column_config.NumberColumn("Total Pendente", format="R$ %.2f"),
            "Probabilidade_Risco_Perc": st.column_config.NumberColumn("Risco %", format="%.2f%%"),
            "Perc_Utilizacao_Limite": st.column_config.NumberColumn("% Utiliz. Limite", format="%.2f%%"),
            "Razao_Compra_Limite": st.column_config.NumberColumn("Razão Compra/Limite", format="%.2f"),
            "Target_Inadimplente": st.column_config.CheckboxColumn("Inadimplente?")
        }
    )

# =========================================================
# ABA 3: Construtor de Gráficos Customizados
# =========================================================
with tab_custom:
    st.subheader("🛠️ Monte o Seu Próprio Gráfico de Análise")
    st.write("Escolha as variáveis do dataset para criar cruzamentos específicos sob demanda.")

    col_eixo_x, col_eixo_y, col_tipo, col_cor = st.columns(4)

    # Seleção de Colunas Numéricas/Categóricas
    todas_colunas = df_filtrado.columns.tolist()
    colunas_num = df_filtrado.select_dtypes(include=['float64', 'int64']).columns.tolist()

    with col_eixo_x:
        eixo_x = st.selectbox("Eixo X (Categorias ou Números)", todas_colunas, index=todas_colunas.index('Acao_Recomendada') if 'Acao_Recomendada' in todas_colunas else 0)
    
    with col_eixo_y:
        eixo_y = st.selectbox("Eixo Y (Valores)", colunas_num, index=colunas_num.index('Valor_Total_Pendente') if 'Valor_Total_Pendente' in colunas_num else 0)

    with col_tipo:
        tipo_grafico = st.selectbox("Tipo de Gráfico", ["Barras", "Dispersão (Scatter)", "Linhas", "Boxplot"])

    with col_cor:
        cor_agrup = st.selectbox("Agrupar/Colorir por", ["Nenhum"] + todas_colunas)

    cor_param = None if cor_agrup == "Nenhum" else cor_agrup

    # Renderização Dinâmica
    if tipo_grafico == "Barras":
        fig_custom = px.bar(df_filtrado, x=eixo_x, y=eixo_y, color=cor_param, template="plotly_dark", barmode="group")
    elif tipo_grafico == "Dispersão (Scatter)":
        fig_custom = px.scatter(df_filtrado, x=eixo_x, y=eixo_y, color=cor_param, template="plotly_dark")
    elif tipo_grafico == "Linhas":
        fig_custom = px.line(df_filtrado, x=eixo_x, y=eixo_y, color=cor_param, template="plotly_dark")
    else:
        fig_custom = px.box(df_filtrado, x=eixo_x, y=eixo_y, color=cor_param, template="plotly_dark")

    st.plotly_chart(fig_custom, use_container_width=True)
