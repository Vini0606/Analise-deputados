import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="VHL - Gêmeo Digital Legislativo",
    page_icon="🏛️",
    layout="wide"
)

# --- GERADOR DE DADOS SIMULADOS (ONTOLOGIA) ---
@st.cache_data
def load_simulated_data():
    dates = pd.date_range(start="2024-01-01", periods=30, freq='D')
    
    # Simulação de Performance das Redes Sociais
    social_data = pd.DataFrame({
        'Data': dates,
        'Engajamento': np.random.randint(1000, 5000, size=30),
        'Sentimento': np.random.uniform(0.4, 0.9, size=30),
        'Novos_Seguidores': np.random.randint(50, 200, size=30)
    })
    
    # Simulação de Pautas e Impacto
    pautas = ['Reforma Tributária', 'Segurança Pública', 'Educação', 'Agro', 'Saúde']
    pautas_data = pd.DataFrame({
        'Pauta': pautas,
        'Mencões': np.random.randint(100, 1000, size=5),
        'Sentimento_Base': [0.8, 0.45, 0.7, 0.9, 0.6], # 0 a 1
        'Risco_Politico': ['Baixo', 'Alto', 'Baixo', 'Muito Baixo', 'Médio']
    })
    
    return social_data, pautas_data

social_df, pautas_df = load_simulated_data()

# --- SIDEBAR DE FILTROS ---
st.sidebar.image("https://via.placeholder.com/150x50?text=VHL+AGENCY", use_container_width=True)
st.sidebar.title("Configurações do Gêmeo")
deputado_selecionado = st.sidebar.selectbox("Parlamentar", ["Dep. Vinícius Ribeiro", "Dep. Exemplo B"])
periodo = st.sidebar.slider("Período de Análise (Dias)", 7, 30, 15)

# --- HEADER ---
st.title(f"🏛️ Painel Operacional: {deputado_selecionado}")
st.markdown(f"**Status:** Ativo | **Última Atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# --- TABELAS DE NAVEGAÇÃO ---
tab1, tab2, tab3 = st.tabs(["📊 Visão de Comando", "🔮 Simulador What-if", "🧠 Biblioteca RAG"])

# --- TAB 1: VISÃO DE COMANDO ---
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Score de Influência", "82/100", "+5%")
    col2.metric("Engajamento Médio", f"{social_df['Engajamento'].mean():.0f}", "-2.1%")
    col3.metric("Sentimento da Base", "Positivo (72%)", "+12%")
    col4.metric("Pautas Ativas", "14", "Reforma Tributária")

    st.divider()
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Tendência de Capital Político vs. Eventos Legislativos")
        
        # Garantimos que os dados estão no formato correto
        plot_df = social_df.tail(periodo).copy()
        
        fig = px.line(plot_df, x='Data', y='Engajamento', 
                    title="Correlação: Postagens vs. Impacto Digital")
        
        # Pegamos a data do evento
        data_evento = plot_df['Data'].iloc[-5]

        # Em vez de add_vline com anotação (que buga o sum interno), 
        # adicionamos a linha e a anotação separadamente
        fig.add_shape(
            type="line",
            x0=data_evento, x1=data_evento,
            y0=0, y1=1,
            yref="paper",
            line=dict(color="Red", width=2, dash="dash")
        )
        
        # Adicionamos o texto manualmente para evitar o erro de soma do Plotly
        fig.add_annotation(
            x=data_evento,
            y=1,
            yref="paper",
            text="Votação PEC 45",
            showarrow=False,
            yshift=10
        )

        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Aderência por Pauta")
        fig_pie = px.pie(pautas_df, values='Mencões', names='Pauta', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 2: SIMULADOR WHAT-IF ---
with tab2:
    st.header("🔮 Simulador de Impacto Narrativo")
    st.info("Utilize este módulo para prever a reação da base antes de um posicionamento oficial.")
    
    col_sim1, col_sim2 = st.columns([1, 1])
    
    with col_sim1:
        pauta_sim = st.selectbox("Selecione a Pauta para Simulação", pautas_df['Pauta'])
        posicao = st.radio("Posicionamento do Deputado", ["A Favor", "Contra", "Abstenção / Neutro"])
        intensidade = st.select_slider("Intensidade da Comunicação", ["Baixa (1 post)", "Média (Campanha)", "Alta (Live + Ads)"])
        
        if st.button("Executar Simulação de Cenário"):
            with st.spinner('Processando via Ontologia...'):
                import time; time.sleep(1.5) # Simulação de processamento
                st.success("Simulação Concluída!")
                
    with col_sim2:
        st.subheader("Resultado da Projeção")
        # Lógica simulada de "What-if"
        risco = "Alto" if posicao == "Contra" and pauta_sim == "Segurança Pública" else "Baixo"
        
        st.write(f"**Risco de Perda de Base:** {risco}")
        st.progress(85 if risco == "Alto" else 15)
        
        st.markdown("""
        **Recomendações da IA (VHL Agent):**
        * O público desta pauta reage melhor a conteúdos em formato de 'Explainer' (Carrossel).
        * Evite termos técnicos; foque no impacto econômico local.
        * **Vacina de Conteúdo:** Publique um vídeo de 30s nos Stories antes da votação.
        """)

# --- TAB 3: BIBLIOTECA RAG ---
with tab3:
    st.header("🧠 Memória Técnica (RAG)")
    query = st.text_input("Buscar histórico de posicionamentos ou discursos:", placeholder="Ex: O que eu disse sobre o agro no semestre passado?")
    
    if query:
        st.markdown("---")
        st.markdown("**Resultado da Busca Vetorial (Simulado):**")
        st.info(f"Encontramos 3 trechos de discursos em plenário sobre '{query}'")
        
        with st.expander("Discurso na Comissão de Finanças - 12/10/2025"):
            st.write("'...é fundamental que o pequeno produtor tenha acesso ao crédito sem a burocracia dos grandes bancos...'")
            if st.button("Transformar em Legenda"):
                st.code("O crédito para o pequeno produtor não pode ser um privilégio, mas um direito! 🚜🇧🇷 #AgroForte #MandatoAtivo")

# --- FOOTER ---
st.divider()
st.caption("VHL Comunicação Política - Inteligência Operacional baseada em Palantir Foundry Architecture.")