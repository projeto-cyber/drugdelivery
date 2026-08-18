import streamlit as st
import pandas as pd

# Tenta importar o streamlit_option_menu; se não estiver instalado, usa o componente nativo do Streamlit
try:
    from streamlit_option_menu import option_menu
    HAS_OPTION_MENU = True
except ImportError:
    HAS_OPTION_MENU = False

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA (MOBILE HEALTH)
# ==========================================
st.set_page_config(
    page_title="PharmaCare - Atenção & Saúde",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização CSS profissional estilo App Farmacêutico
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    
    .health-header {
        background: linear-gradient(135deg, #0d5c75, #1988a6);
        color: white;
        padding: 20px;
        border-radius: 0 0 20px 20px;
        margin: -60px -20px 15px -20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .promo-card {
        background: linear-gradient(135deg, #28a745, #218838);
        color: white;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 12px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.1);
    }
    
    .pharmacy-card {
        background: white;
        padding: 14px;
        border-radius: 12px;
        border-left: 4px solid #1988a6;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        margin-bottom: 10px;
    }
    
    .badge-portaria {
        background-color: #dc3545;
        color: white;
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    .badge-mip {
        background-color: #17a2b8;
        color: white;
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    .badge-suplemento {
        background-color: #28a745;
        color: white;
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BANCO DE DADOS DIVERSIFICADO (PANDAS)
# ==========================================
@st.cache_data
def carregar_banco_dados():
    cat_meds = pd.DataFrame([
        # --- MEDICAMENTOS SUJEITOS À PORTARIA 344/98 ---
        {"id": 201, "nome_principio": "Clonazepam", "apresentacao": "2,5mg/mL Gotas (20mL)", "categoria": "Portaria 344/98 (Lista B1)", "classe": "Ansiolítico / Anticonvulsivante", "retencao": True, "orientacao": "Notificação de Receita B (Azul). Causa dependência. Uso conforme orientação médica."},
        {"id": 202, "nome_principio": "Zolpidem", "apresentacao": "10mg (30 Comprimidos)", "categoria": "Portaria 344/98 (Lista B1)", "classe": "Indutor do Sono", "retencao": True, "orientacao": "Notificação de Receita B (Azul). Ingerir imediatamente antes de deitar."},
        {"id": 203, "nome_principio": "Sertralina (Cloridrato)", "apresentacao": "50mg (30 Comprimidos)", "categoria": "Portaria 344/98 (Lista C1)", "classe": "Antidepressivo (ISRS)", "retencao": True, "orientacao": "Receita de Controle Especial em 2 vias. Não interromper o tratamento sem orientação."},

        # --- MEDICAMENTOS ISENTOS DE PRESCRIÇÃO (MIPs) ---
        {"id": 301, "nome_principio": "Dipirona Monoidratada", "apresentacao": "1g (10 Comprimidos)", "categoria": "MIP (Isento de Prescrição)", "classe": "Analgésico e Antitérmico", "retencao": False, "orientacao": "Uso adulto. Respeitar o intervalo mínimo de 6 horas entre as doses."},
        {"id": 302, "nome_principio": "Paracetamol", "apresentacao": "750mg (20 Comprimidos)", "categoria": "MIP (Isento de Prescrição)", "classe": "Analgésico e Antitérmico", "retencao": False, "orientacao": "Atenção: Não ultrapassar 4g diárias para evitar hepatotoxicidade."},
        {"id": 303, "nome_principio": "Ibuprofeno", "apresentacao": "600mg (20 Comprimidos)", "categoria": "MIP (Isento de Prescrição)", "classe": "Anti-inflamatório", "retencao": False, "orientacao": "Tomar preferencialmente após as refeições para proteger o estômago."},

        # --- SUPLEMENTOS ALIMENTARES E VITAMINAS ---
        {"id": 401, "nome_principio": "Vitamina C + Zinco", "apresentacao": "1000mg (10 Comp. Efervescentes)", "categoria": "Suplemento Alimentar", "classe": "Imunidade", "retencao": False, "orientacao": "Dissolver 1 comprimido em um copo de água ao dia.", "em_oferta": True, "desconto": "25% OFF"},
        {"id": 402, "nome_principio": "Ômega 3 Epa DHA", "apresentacao": "1000mg (120 Cápsulas)", "categoria": "Suplemento Alimentar", "classe": "Saúde Cardiovascular", "retencao": False, "orientacao": "Ingerir antes das principais refeições.", "em_oferta": True, "desconto": "30% OFF"},
        {"id": 403, "nome_principio": "Creatina Monohidratada", "apresentacao": "300g em Pó (100% Pura)", "categoria": "Suplemento Alimentar", "classe": "Nutrição Esportiva", "retencao": False, "orientacao": "Consumir diariamente junto a uma fonte de carboidrato.", "em_oferta": False, "desconto": None}
    ])
    
    ofertas = pd.DataFrame([
        {"med_id": 201, "laboratorio": "Medley", "farmacia": "Drogaria São Paulo", "preco": 14.50, "distancia_km": 0.8},
        {"med_id": 201, "laboratorio": "EMS Genéricos", "farmacia": "Droga Raia", "preco": 11.90, "distancia_km": 1.5},
        {"med_id": 202, "laboratorio": "Eurofarma", "farmacia": "Pague Menos", "preco": 32.00, "distancia_km": 1.2},
        {"med_id": 202, "laboratorio": "Aché", "farmacia": "Drogaria São Paulo", "preco": 38.90, "distancia_km": 0.8},
        {"med_id": 203, "laboratorio": "Eurofarma", "farmacia": "Droga Raia", "preco": 28.90, "distancia_km": 1.5},
        {"med_id": 203, "laboratorio": "Medley", "farmacia": "Pague Menos", "preco": 24.50, "distancia_km": 2.1},
        {"med_id": 301, "laboratorio": "Neo Química", "farmacia": "Farmácia Bairro", "preco": 6.50, "distancia_km": 0.5},
        {"med_id": 301, "laboratorio": "EMS Genéricos", "farmacia": "Droga Raia", "preco": 8.90, "distancia_km": 1.5},
        {"med_id": 302, "laboratorio": "Teuto", "farmacia": "Farmácia Bairro", "preco": 7.20, "distancia_km": 0.5},
        {"med_id": 303, "laboratorio": "Medley", "farmacia": "Drogaria São Paulo", "preco": 15.90, "distancia_km": 0.8},
        {"med_id": 401, "laboratorio": "Redoxon (Bayer)", "farmacia": "Droga Raia", "preco": 18.90, "distancia_km": 1.5},
        {"med_id": 401, "laboratorio": "Cimed", "farmacia": "Pague Menos", "preco": 12.90, "distancia_km": 2.1},
        {"med_id": 402, "laboratorio": "Max Titanium", "farmacia": "Drogaria São Paulo", "preco": 59.90, "distancia_km": 0.8},
        {"med_id": 402, "laboratorio": "Catarinense Pharma", "farmacia": "Farmácia Bairro", "preco": 49.90, "distancia_km": 0.5},
        {"med_id": 403, "laboratorio": "Integralmédica", "farmacia": "Droga Raia", "preco": 89.90, "distancia_km": 1.5}
    ])
    
    return cat_meds, ofertas

df_meds, df_ofertas = carregar_banco_dados()

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# ==========================================
# 3. CABEÇALHO E NAVEGAÇÃO
# ==========================================
st.markdown("""
<div class="health-header">
    <small>🩺 Atenção Farmacêutica & Segurança</small>
    <h3 style="margin:0; font-weight:600;">PharmaCare Digital</h3>
</div>
""", unsafe_allow_html=True)

# Navegação segura com tratamento de erro
opcoes_menu = ["Buscar", "Ofertas / Suplementos", "Carrinho"]

if HAS_OPTION_MENU:
    selected = option_menu(
        menu_title=None,
        options=opcoes_menu,
        icons=["search", "lightning-charge", "cart"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff"},
            "icon": {"color": "#1988a6", "font-size": "16px"},
            "nav-link": {"font-size": "13px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#1988a6", "color": "white"}
        }
    )
else:
    # Se a biblioteca não estiver instalada, usa os seletores nativos do Streamlit
    selected = st.radio("Navegação:", opcoes_menu, horizontal=True, label_visibility="collapsed")

# ==========================================
# 4. ABA 1: BUSCA ANINHADA E MENOR PREÇO
# ==========================================
if selected == "Buscar":
    st.caption("Digite abaixo para buscar por nome ou princípio ativo:")
    
    termo_busca = st.selectbox(
        "Selecione ou digite o item desejado:",
        options=[""] + list(df_meds["nome_principio"].unique()),
        format_func=lambda x: "🔍 Digite para pesquisar..." if x == "" else x
    )
    
    if termo_busca != "":
        med_info = df_meds[df_meds["nome_principio"] == termo_busca].iloc[0]
        
        cat_tag = f"<span class='badge-portaria'>{med_info['categoria']}</span>" if med_info['retencao'] else (
            f"<span class='badge-suplemento'>{med_info['categoria']}</span>" if "Suplemento" in med_info['categoria'] else f"<span class='badge-mip'>{med_info['categoria']}</span>"
        )
        
        st.markdown(f"### {med_info['nome_principio']} {cat_tag}", unsafe_allow_html=True)
        st.write(f"**Apresentação / Dosagem:** {med_info['apresentacao']}")
        st.info(f"**Classe:** {med_info['classe']}\n\n**Orientação do Farmacêutico:** {med_info['orientacao']}")
        
        if med_info['retencao']:
            st.error("⚠️ Item de Controle Especial (Portaria 344/98): Exige retenção de receita médica no ato da entrega/retirada.")
            
        st.subheader("🏷️ Comparativo de Laboratórios & Menor Preço")
        
        ofertas_med = df_ofertas[df_ofertas["med_id"] == med_info["id"]].sort_values(by="preco")
        
        if not ofertas_med.empty:
            menor_preco = ofertas_med.iloc[0]["preco"]
            st.success(f"💡 **Menor preço encontrado:** R$ {menor_preco:.2f} ({ofertas_med.iloc[0]['laboratorio']})")
            
            for _, row in ofertas_med.iterrows():
                com_destaque = "border: 2px solid #28a745;" if row["preco"] == menor_preco else ""
                st.markdown(f"""
                <div class="pharmacy-card" style="{com_destaque}">
                    <b>Laboratório: {row['laboratorio']}</b><br>
                    <small>Unidade: {row['farmacia']} (a {row['distancia_km']} km)</small><br>
                    <span style="color:#0d5c75; font-size:18px; font-weight:bold;">R$ {row['preco']:.2f}</span>
                    {" <span style='color:#28a745; font-weight:bold;'>(Menor Valor)</span>" if row['preco'] == menor_preco else ""}
                </div>
                """, unsafe_allow_html=True)
                
                chave_btn = f"add_{row['med_id']}_{row['laboratorio']}_{row['farmacia']}"
                if st.button(f"Adicionar ({row['laboratorio']}) - R$ {row['preco']:.2f}", key=chave_btn):
                    item = {
                        "produto": f"{med_info['nome_principio']} - {med_info['apresentacao']}",
                        "laboratorio": row['laboratorio'],
                        "farmacia": row['farmacia'],
                        "preco": row['preco'],
                        "retencao": med_info['retencao']
                    }
                    st.session_state.carrinho.append(item)
                    st.success("Item adicionado ao carrinho com sucesso!")
                    st.rerun()

# ==========================================
# 5. ABA 2: SUPLEMENTOS EM OFERTA EXPOSTOS
# ==========================================
elif selected == "Ofertas / Suplementos":
    st.subheader("⚡ Suplementos & Vitaminas em Destaque")
    st.caption("Aproveite os descontos especiais para prevenção e qualidade de vida:")
    
    suplementos_oferta = df_meds[(df_meds["categoria"] == "Suplemento Alimentar") & (df_meds["em_oferta"] == True)]
    
    for _, sup in suplementos_oferta.iterrows():
        st.markdown(f"""
        <div class="promo-card">
            <span style="float:right; background:white; color:#218838; font-weight:bold; padding:2px 8px; border-radius:6px;">{sup['desconto']}</span>
            <h4 style="margin:0;">{sup['nome_principio']}</h4>
            <small>{sup['apresentacao']}</small><br>
            <small><b>Indicação:</b> {sup['classe']}</small>
        </div>
        """, unsafe_allow_html=True)
        
        ofertas_sup = df_ofertas[df_ofertas["med_id"] == sup["id"]].sort_values(by="preco")
        if not ofertas_sup.empty:
            melhor = ofertas_sup.iloc[0]
            st.write(f"Vendido por **{melhor['farmacia']}** ({melhor['laboratorio']}) por apenas **R$ {melhor['preco']:.2f}**")
            
            if st.button(f"Garantir Oferta de {sup['nome_principio']}", key=f"sup_{sup['id']}"):
                item = {
                    "produto": f"{sup['nome_principio']} - {sup['apresentacao']}",
                    "laboratorio": melhor['laboratorio'],
                    "farmacia": melhor['farmacia'],
                    "preco": melhor['preco'],
                    "retencao": False
                }
                st.session_state.carrinho.append(item)
                st.success("Oferta adicionada ao carrinho!")
                st.rerun()
        st.divider()

# ==========================================
# 6. ABA 3: CARRINHO E VALIDAÇÃO FARMACÊUTICA
# ==========================================
elif selected == "Carrinho":
    st.subheader("🛒 Seu Carrinho de Saúde")
    
    if not st.session_state.carrinho:
        st.info("O seu carrinho está vazio no momento.")
    else:
        df_cart = pd.DataFrame(st.session_state.carrinho)
        
        for idx, item in df_cart.iterrows():
            st.write(f"**{item['produto']}**")
            st.caption(f"Marca/Lab: {item['laboratorio']} | Retirada: {item['farmacia']} — **R$ {item['preco']:.2f}**")
            if item['retencao']:
                st.warning("⚠️ Exige Envio de Receita Médica (Portaria 344/98)")
            st.divider()
            
        total = df_cart["preco"].sum()
        st.markdown(f"### Total do Pedido: **R$ {total:.2f}**")
        
        if any(df_cart["retencao"]):
            st.file_uploader("📷 Anexar Foto/PDF da Receita Médica (Obrigatório)", type=["jpg", "png", "pdf"])
            
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Finalizar Pedido", type="primary", use_container_width=True):
                st.success("Pedido enviado! O farmacêutico responsável validará as retenções de receita antes do envio.")
                st.balloons()
                st.session_state.carrinho = []
        with col2:
            if st.button("Esvaziar Carrinho", use_container_width=True):
                st.session_state.carrinho = []
                st.rerun()
