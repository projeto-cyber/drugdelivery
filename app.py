import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA (MOBILE HEALTH)
# ==========================================
st.set_page_config(
    page_title="PharmaCare - Atenção & Saúde",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Customização visual para um app de atenção farmacêutica
st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; }
    
    .health-header {
        background: linear-gradient(135deg, #0d5c75, #1988a6);
        color: white;
        padding: 22px;
        border-radius: 0 0 20px 20px;
        margin: -60px -20px 20px -20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .pharmacy-card {
        background: white;
        padding: 16px;
        border-radius: 12px;
        border-left: 5px solid #1988a6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    
    .alert-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #ffeeba;
        font-size: 13px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DADOS COM PANDAS (SIMULAÇÃO DA REDE)
# ==========================================
@st.cache_data
def carregar_dados():
    # Base de Medicamentos cadastrados
    medicamentos = pd.DataFrame([
        {"id": 101, "nome": "Amoxicilina 500mg (21 Cáp.)", "classe": "Antibiótico", "retencao": True, "orientacao": "Tomar de 8 em 8 horas. Concluir todo o tratamento."},
        {"id": 102, "nome": "Dipirona Monoidratada 1g (10 Comp.)", "classe": "Analgésico/Antitérmico", "retencao": False, "orientacao": "Tomar em caso de dor ou febre de 6 em 6 horas."},
        {"id": 103, "nome": "Losartana Potássica 50mg (30 Comp.)", "classe": "Anti-hipertensivo", "retencao": True, "orientacao": "Uso contínuo conforme indicação médica. Medir pressão regularmente."},
        {"id": 104, "nome": "Omeprazol 20mg (28 Cáp.)", "classe": "Antiácido", "retencao": False, "orientacao": "Ingerir em jejum, 30 minutos antes do café da manhã."}
    ])
    
    # Base de Farmácias Parceiras e Preços (com coordenadas de GPS)
    estoque_farmacias = pd.DataFrame([
        {"med_id": 101, "farmacia": "Drogaria São Paulo - Centro", "distancia_km": 0.8, "preco": 24.90, "lat": -23.5505, "lon": -46.6333},
        {"med_id": 101, "farmacia": "Droga Raia - Jardins", "distancia_km": 2.3, "preco": 28.50, "lat": -23.5615, "lon": -46.6559},
        {"med_id": 102, "farmacia": "Drogaria São Paulo - Centro", "distancia_km": 0.8, "preco": 8.50, "lat": -23.5505, "lon": -46.6333},
        {"med_id": 102, "farmacia": "Farmácia Pague Menos - Bairro", "distancia_km": 1.4, "preco": 6.90, "lat": -23.5430, "lon": -46.6410},
        {"med_id": 103, "farmacia": "Droga Raia - Jardins", "distancia_km": 2.3, "preco": 12.00, "lat": -23.5615, "lon": -46.6559},
        {"med_id": 104, "farmacia": "Farmácia Pague Menos - Bairro", "distancia_km": 1.4, "preco": 18.90, "lat": -23.5430, "lon": -46.6410}
    ])
    
    return medicamentos, estoque_farmacias

df_meds, df_estoque = carregar_dados()

# Sessão do Carrinho
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# ==========================================
# 3. CABEÇALHO DO APLICATIVO
# ==========================================
st.markdown("""
<div class="health-header">
    <small>🩺 Atenção Farmacêutica & Segurança</small>
    <h3 style="margin:0; font-weight:600;">Busca de Medicamentos</h3>
</div>
""", unsafe_allow_html=True)

# Navegação por Abas
tab_busca, tab_carrinho = st.tabs(["🔍 Pesquisar Medicamento", f"🛒 Meu Carrinho ({len(st.session_state.carrinho)})"])

# ==========================================
# 4. ABA 1: BUSCA PREDITIVA E COMPARATIVO DE DISTÂNCIA
# ==========================================
with tab_busca:
    st.caption("Digite o nome do medicamento para verificar a disponibilidade nas farmácias próximas:")
    
    # Seleção digitável (Selectbox com busca por texto)
    opcoes_meds = ["Selecione ou digite..."] + list(df_meds["nome"].unique())
    med_selecionado = st.selectbox("Nome do Medicamento:", opcoes_meds, index=0)
    
    if med_selecionado != "Selecione ou digite...":
        # Filtro Pandas
        info_med = df_meds[df_meds["nome"] == med_selecionado].iloc[0]
        resultados = pd.merge(df_estoque, df_meds, left_on="med_id", right_on="id")
        resultados_filtrados = resultados[resultados["nome"] == med_selecionado].sort_values(by="distancia_km")
        
        # Painel de Atenção Farmacêutica
        st.subheader("📋 Informações de Segurança")
        st.info(f"**Classe:** {info_med['classe']}\n\n**Orientação de Uso:** {info_med['orientacao']}")
        
        if info_med['retencao']:
            st.markdown("""
            <div class="alert-box">
                <b>⚠️ Medicamento Sujeito a Controle Especial (RDC 344/98):</b><br>
                Este item exige a apresentação de receita médica válida e retenção no momento da retirada ou entrega.
            </div><br>
            """, unsafe_allow_html=True)
            
        st.subheader("🏪 Disponibilidade e Distância")
        
        # Exibição dos resultados encontrados nas farmácias
        for _, row in resultados_filtrados.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="pharmacy-card">
                    <b>{row['farmacia']}</b><br>
                    <span style="color:#555; font-size:13px;">📍 Distância: <b>{row['distancia_km']} km</b> da sua localização</span><br>
                    <span style="color:#0d5c75; font-weight:bold; font-size:16px;">R$ {row['preco']:.2f}</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Adicionar da {row['farmacia']}", key=f"btn_{row['farmacia']}_{row['id']}"):
                    item_carrinho = {
                        "medicamento": row['nome'],
                        "farmacia": row['farmacia'],
                        "preco": row['preco'],
                        "distancia": row['distancia_km'],
                        "retencao": row['retencao']
                    }
                    st.session_state.carrinho.append(item_carrinho)
                    st.success("Item adicionado ao carrinho de atenção!")
                    st.rerun()

        # Mapa com as Farmácias que possuem o medicamento
        st.subheader("🗺️ Localização das Unidades")
        mapa = folium.Map(location=[-23.5505, -46.6333], zoom_start=13)
        
        for _, farm in resultados_filtrados.iterrows():
            folium.Marker(
                location=[farm['lat'], farm['lon']],
                popup=f"{farm['farmacia']} - R$ {farm['preco']:.2f} ({farm['distancia_km']} km)",
                tooltip=farm['farmacia'],
                icon=folium.Icon(color="green", icon="plus-sign")
            ).add_to(mapa)
            
        st_folium(mapa, width=700, height=280)

# ==========================================
# 5. ABA 2: CARRINHO DE ATENÇÃO FARMACÊUTICA
# ==========================================
with tab_carrinho:
    st.subheader("Resumo do Pedido")
    
    if not st.session_state.carrinho:
        st.write("Seu carrinho está vazio. Busque por um medicamento para iniciar.")
    else:
        df_carrinho = pd.DataFrame(st.session_state.carrinho)
        
        for idx, item in df_carrinho.iterrows():
            st.write(f"**{item['medicamento']}**")
            st.caption(f"Retirada/Entrega: {item['farmacia']} ({item['distancia']} km) — R$ {item['preco']:.2f}")
            if item['retencao']:
                st.warning(" Exige Envio de Receita Médica")
            st.divider()
            
        total = df_carrinho["preco"].sum()
        st.markdown(f"### Total: **R$ {total:.2f}**")
        
        # Envio de receita
        if any(df_carrinho["retencao"]):
            st.file_uploader(" Anexar Foto da Receita Médica (Obrigatório)", type=["jpg", "png", "pdf"])
            
        if st.button("Confirmar e Enviar para Validação Farmacêutica", type="primary"):
            st.success("Pedido enviado! O farmacêutico responsável pela unidade analisará sua receita antes da liberação.")
            st.balloons()
            st.session_state.carrinho = []
