import streamlit as st
import pandas as pd

try:
    from streamlit_option_menu import option_menu
    HAS_OPTION_MENU = True
except ImportError:
    HAS_OPTION_MENU = False

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA (WEB & MOBILE)
# ==========================================
st.set_page_config(
    page_title="PharmaMarket - Entrega de Farmácias",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização CSS otimizada para Navegador Web + Celular
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
    
    /* Badges Anvisa */
    .badge-portaria { background-color: #dc3545; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-antimicrobiano { background-color: #fd7e14; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-hormonio { background-color: #6f42c1; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-mip { background-color: #17a2b8; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-suplemento { background-color: #28a745; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-beleza { background-color: #e83e8c; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }

    .footer-anvisa {
        margin-top: 40px;
        padding: 15px;
        background-color: #ffffff;
        border-top: 1px solid #e9ecef;
        text-align: center;
        font-size: 11px;
        color: #6c757d;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BANCO DE DADOS DETALHADO (PANDAS)
# ==========================================
@st.cache_data
def carregar_banco_dados():
    cat_meds = pd.DataFrame([
        # --- PORTARIA 344/98 ---
        {"id": 201, "nome_principio": "Clonazepam", "dosagem": "0,5mg", "qtd_embalagem": "30 Comprimidos", "categoria": "Portaria 344/98 (Lista B1)", "classe": "Ansiolítico", "retencao": True, "tipo_receita": "Notificação B (Azul)", "orientacao": "Uso sob orientação médica."},
        {"id": 202, "nome_principio": "Clonazepam", "dosagem": "2,0mg", "qtd_embalagem": "30 Comprimidos", "categoria": "Portaria 344/98 (Lista B1)", "classe": "Ansiolítico", "retencao": True, "tipo_receita": "Notificação B (Azul)", "orientacao": "Uso sob orientação médica."},
        {"id": 203, "nome_principio": "Clonazepam", "dosagem": "2,5mg/mL", "qtd_embalagem": "Frasco Gotas 20mL", "categoria": "Portaria 344/98 (Lista B1)", "classe": "Ansiolítico", "retencao": True, "tipo_receita": "Notificação B (Azul)", "orientacao": "Uso sob orientação médica."},
        {"id": 204, "nome_principio": "Zolpidem (Hemitartarato)", "dosagem": "10mg", "qtd_embalagem": "30 Comprimidos Revestidos", "categoria": "Portaria 344/98 (Lista B1)", "classe": "Indutor do Sono", "retencao": True, "tipo_receita": "Notificação B (Azul)", "orientacao": "Tomar imediatamente antes de deitar."},

        # --- ANTIMICROBIANOS ---
        {"id": 250, "nome_principio": "Amoxicilina + Clavulanato", "dosagem": "500mg + 125mg", "qtd_embalagem": "18 Comprimidos Revestidos", "categoria": "Antimicrobiano", "classe": "Antibiótico", "retencao": True, "tipo_receita": "Receita de Controle Especial (2 vias)", "orientacao": "Seguir rigorosamente os horários prescritos."},
        {"id": 251, "nome_principio": "Amoxicilina + Clavulanato", "dosagem": "875mg + 125mg", "qtd_embalagem": "14 Comprimidos Revestidos", "categoria": "Antimicrobiano", "classe": "Antibiótico", "retencao": True, "tipo_receita": "Receita de Controle Especial (2 vias)", "orientacao": "Seguir rigorosamente os horários prescritos."},
        {"id": 252, "nome_principio": "Azitromicina Monoidratada", "dosagem": "500mg", "qtd_embalagem": "3 Comprimidos Revestidos", "categoria": "Antimicrobiano", "classe": "Antibiótico", "retencao": True, "tipo_receita": "Receita de Controle Especial (2 vias)", "orientacao": "Tomar 1 hora antes ou 2 horas após refeições."},
        {"id": 253, "nome_principio": "Azitromicina Monoidratada", "dosagem": "500mg", "qtd_embalagem": "5 Comprimidos Revestidos", "categoria": "Antimicrobiano", "classe": "Antibiótico", "retencao": True, "tipo_receita": "Receita de Controle Especial (2 vias)", "orientacao": "Tomar 1 hora antes ou 2 horas após refeições."},

        # --- HORMÔNIOS ---
        {"id": 280, "nome_principio": "Levotiroxina Sódica", "dosagem": "25mcg", "qtd_embalagem": "30 Comprimidos", "categoria": "Hormônio / Endocrinologia", "classe": "Hormônio Tireoidiano", "retencao": False, "tipo_receita": None, "orientacao": "Ingerir em jejum absoluto com água."},
        {"id": 281, "nome_principio": "Levotiroxina Sódica", "dosagem": "50mcg", "qtd_embalagem": "30 Comprimidos", "categoria": "Hormônio / Endocrinologia", "classe": "Hormônio Tireoidiano", "retencao": False, "tipo_receita": None, "orientacao": "Ingerir em jejum absoluto com água."},

        # --- MIPS ---
        {"id": 301, "nome_principio": "Dipirona Monoidratada", "dosagem": "500mg", "qtd_embalagem": "20 Comprimidos", "categoria": "MIP (Isento de Prescrição)", "classe": "Analgésico e Antitérmico", "retencao": False, "tipo_receita": None, "orientacao": "Respeitar o intervalo mínimo de 6 horas."},
        {"id": 302, "nome_principio": "Dipirona Monoidratada", "dosagem": "1g (1000mg)", "qtd_embalagem": "10 Comprimidos Efervescentes", "categoria": "MIP (Isento de Prescrição)", "classe": "Analgésico e Antitérmico", "retencao": False, "tipo_receita": None, "orientacao": "Dissolver 1 comprimido em água."},

        # --- SUPLEMENTOS & BELEZA ---
        {"id": 401, "nome_principio": "Vitamina C + Zinco", "dosagem": "1000mg + 10mg", "qtd_embalagem": "10 Comprimidos Efervescentes", "categoria": "Suplemento Alimentar", "classe": "Imunidade", "retencao": False, "tipo_receita": None, "orientacao": "Uso diário.", "em_oferta": True, "desconto": "25% OFF"},
        {"id": 501, "nome_principio": "Protetor Solar Facial FPS 60", "dosagem": "Toque Seco", "qtd_embalagem": "Bisnaga de 50g", "categoria": "Produtos de Beleza", "classe": "Fotoproteção", "retencao": False, "tipo_receita": None, "orientacao": "Reaplicar a cada 3 horas.", "em_oferta": True, "desconto": "20% OFF"}
    ])
    
    # AUTOTESTES RESIDENCIAIS (Para uso pelo próprio consumidor em casa)
    autotestes_casa = pd.DataFrame([
        {"id": 601, "nome": "Autoteste COVID-19 Ag Nasal", "categoria": "Autoteste Residencial", "qtd": "Caixa com 1 Teste Completo", "preco": 24.90, "descricao": "Coleta por swab nasal simples com resultado em 15 minutos na sua casa."},
        {"id": 602, "nome": "Teste de Gravidez Rápido (Caneta/Tira)", "categoria": "Autoteste Residencial", "qtd": "Caixa com 1 Unidade", "preco": 11.90, "descricao": "Detecção de HCG por urina com resultado em 3 minutos."},
        {"id": 603, "nome": "Teste de Ovulação Rápido (Triagem de Fertilidade)", "categoria": "Autoteste Residencial", "qtd": "Caixa com 5 Tiras", "preco": 34.90, "descricao": "Acompanhamento do período fértil no conforto do lar."},
        {"id": 604, "nome": "Autoteste de HIV (Fluido Oral / Sangue Capilar)", "categoria": "Autoteste Residencial", "qtd": "Caixa com 1 Kit Dispositivo", "preco": 69.90, "descricao": "Triagem privada e individualizada aprovada pela Anvisa."}
    ])
    
    ofertas = pd.DataFrame([
        {"med_id": 201, "laboratorio": "Medley", "farmacia": "Drogaria São Paulo", "preco": 11.50, "distancia_km": 0.8},
        {"med_id": 201, "laboratorio": "EMS", "farmacia": "Droga Raia", "preco": 9.90, "distancia_km": 1.5},
        {"med_id": 202, "laboratorio": "Eurofarma", "farmacia": "Pague Menos", "preco": 18.20, "distancia_km": 1.2},
        {"med_id": 203, "laboratorio": "Aché", "farmacia": "Drogaria São Paulo", "preco": 14.90, "distancia_km": 0.8},
        {"med_id": 250, "laboratorio": "Eurofarma", "farmacia": "Pague Menos", "preco": 42.00, "distancia_km": 1.2},
        {"med_id": 250, "laboratorio": "Neo Química", "farmacia": "Drogaria São Paulo", "preco": 38.50, "distancia_km": 0.8},
        {"med_id": 280, "laboratorio": "Merck", "farmacia": "Droga Raia", "preco": 16.90, "distancia_km": 1.5},
        {"med_id": 301, "laboratorio": "Neo Química", "farmacia": "Farmácia Bairro", "preco": 5.50, "distancia_km": 0.5},
        {"med_id": 401, "laboratorio": "Redoxon", "farmacia": "Droga Raia", "preco": 18.90, "distancia_km": 1.5},
        {"med_id": 501, "laboratorio": "L'Oréal", "farmacia": "Pague Menos", "preco": 54.90, "distancia_km": 2.1}
    ])
    
    return cat_meds, autotestes_casa, ofertas

df_meds, df_testes, df_ofertas = carregar_banco_dados()

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# ==========================================
# 3. CABEÇALHO E NAVEGAÇÃO
# ==========================================
st.markdown("""
<div class="health-header">
    <small>🛵 Entrega de Farmácias Parceiras da Cidade</small>
    <h3 style="margin:0; font-weight:600;">PharmaMarket Express</h3>
</div>
""", unsafe_allow_html=True)

opcoes_menu = ["Buscar Remédios", "Ofertas / Beleza", "Autotestes (Em Casa)", "Carrinho"]

if HAS_OPTION_MENU:
    selected = option_menu(
        menu_title=None,
        options=opcoes_menu,
        icons=["search", "sparkles", "house-heart", "cart"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff"},
            "icon": {"color": "#1988a6", "font-size": "15px"},
            "nav-link": {"font-size": "11px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#1988a6", "color": "white"}
        }
    )
else:
    selected = st.radio("Navegação:", opcoes_menu, horizontal=True, label_visibility="collapsed")

# ==========================================
# 4. ABA 1: BUSCA DE MEDICAMENTOS COM APRESENTAÇÕES
# ==========================================
if selected == "Buscar Remédios":
    st.caption("Pesquise por nome do princípio ativo para selecionar a dosagem exata:")
    
    termo_busca = st.selectbox(
        "Selecione ou digite o medicamento:",
        options=[""] + list(df_meds["nome_principio"].unique()),
        format_func=lambda x: "🔍 Digite o nome do remédio..." if x == "" else x
    )
    
    if termo_busca != "":
        # Filtra todas as apresentações disponíveis desse princípio ativo
        opcoes_apresentacao = df_meds[df_meds["nome_principio"] == termo_busca]
        
        st.subheader(f"💊 {termo_busca}")
        st.write("Escolha a **dosagem e quantidade** desejada:")
        
        # Dropdown aninhado com Dosagem + Quantidade
        apresentacao_sel = st.selectbox(
            "Apresentações e Dosagens disponíveis:",
            options=opcoes_apresentacao["id"].tolist(),
            format_func=lambda x: f"{opcoes_apresentacao[opcoes_apresentacao['id'] == x]['dosagem'].values[0]} — {opcoes_apresentacao[opcoes_apresentacao['id'] == x]['qtd_embalagem'].values[0]}"
        )
        
        med_info = opcoes_apresentacao[opcoes_apresentacao["id"] == apresentacao_sel].iloc[0]
        
        if "Portaria 344" in med_info['categoria']:
            cat_tag = f"<span class='badge-portaria'>{med_info['categoria']}</span>"
        elif "Antimicrobiano" in med_info['categoria']:
            cat_tag = f"<span class='badge-antimicrobiano'>{med_info['categoria']}</span>"
        else:
            cat_tag = f"<span class='badge-mip'>{med_info['categoria']}</span>"
            
        st.markdown(f"**Categoria:** {cat_tag}", unsafe_allow_html=True)
        st.info(f"**Classe:** {med_info['classe']}\n\n**Orientação:** {med_info['orientacao']}")
        
        if med_info['retencao']:
            st.error(f"⚠️ Exige retenção de receita ({med_info['tipo_receita']}). O motoboy/farmácia recolherá/validará a receita.")
            
        st.subheader("🏷️ Selecione a Farmácia / Laboratório pelo Menor Preço")
        
        ofertas_med = df_ofertas[df_ofertas["med_id"] == med_info["id"]].sort_values(by="preco")
        
        if not ofertas_med.empty:
            menor_preco = ofertas_med.iloc[0]["preco"]
            st.success(f"💡 **Menor valor na cidade:** R$ {menor_preco:.2f} ({ofertas_med.iloc[0]['laboratorio']})")
            
            for _, row in ofertas_med.iterrows():
                com_destaque = "border: 2px solid #28a745;" if row["preco"] == menor_preco else ""
                st.markdown(f"""
                <div class="pharmacy-card" style="{com_destaque}">
                    <b>Marca/Lab: {row['laboratorio']}</b><br>
                    <small>Vendido por: <b>{row['farmacia']}</b> ({row['distancia_km']} km de você)</small><br>
                    <span style="color:#0d5c75; font-size:18px; font-weight:bold;">R$ {row['preco']:.2f}</span>
                    {" <span style='color:#28a745; font-weight:bold;'>(Menor Preço)</span>" if row['preco'] == menor_preco else ""}
                </div>
                """, unsafe_allow_html=True)
                
                chave_btn = f"add_{row['med_id']}_{row['laboratorio']}_{row['farmacia']}"
                if st.button(f"Comprar ({row['laboratorio']}) - R$ {row['preco']:.2f}", key=chave_btn):
                    item = {
                        "produto": f"{med_info['nome_principio']} {med_info['dosagem']} ({med_info['qtd_embalagem']})",
                        "laboratorio": row['laboratorio'],
                        "farmacia": row['farmacia'],
                        "preco": row['preco'],
                        "retencao": med_info['retencao']
                    }
                    st.session_state.carrinho.append(item)
                    st.success("Adicionado ao carrinho!")
                    st.rerun()

# ==========================================
# 5. ABA 2: OFERTAS & BELEZA
# ==========================================
elif selected == "Ofertas / Beleza":
    st.subheader("✨ Ofertas das Farmácias Parceiras")
    st.caption("Produtos de cuidados pessoais e suplementos com entrega direta:")
    
    itens_oferta = df_meds[df_meds["em_oferta"] == True]
    
    for _, item in itens_oferta.iterrows():
        st.markdown(f"""
        <div class="promo-card">
            <span style="float:right; background:white; color:#218838; font-weight:bold; padding:2px 8px; border-radius:6px;">{item['desconto']}</span>
            <h4 style="margin:0;">{item['nome_principio']}</h4>
            <small>Dosagem/Apres: {item['dosagem']} — {item['qtd_embalagem']}</small>
        </div>
        """, unsafe_allow_html=True)
        
        ofertas_item = df_ofertas[df_ofertas["med_id"] == item["id"]].sort_values(by="preco")
        if not ofertas_item.empty:
            melhor = ofertas_item.iloc[0]
            st.write(f"Parceira: **{melhor['farmacia']}** por apenas **R$ {melhor['preco']:.2f}**")
            
            if st.button(f"Garantir Oferta de {item['nome_principio']}", key=f"oferta_{item['id']}"):
                cart_item = {
                    "produto": f"{item['nome_principio']} {item['dosagem']} ({item['qtd_embalagem']})",
                    "laboratorio": melhor['laboratorio'],
                    "farmacia": melhor['farmacia'],
                    "preco": melhor['preco'],
                    "retencao": False
                }
                st.session_state.carrinho.append(cart_item)
                st.success("Oferta adicionada ao carrinho!")
                st.rerun()
        st.divider()

# ==========================================
# 6. ABA 3: AUTOTESTES RESIDENCIAIS (USO EM CASA)
# ==========================================
elif selected == "Autotestes (Em Casa)":
    st.subheader("🏠 Autotestes para Uso Doméstico")
    st.caption("Kits de autoteste comercializados pelas farmácias para você realizar com privacidade na sua casa:")
    
    for _, teste in df_testes.iterrows():
        st.markdown(f"""
        <div class="pharmacy-card" style="border-left: 4px solid #17a2b8;">
            <b>{teste['nome']}</b><br>
            <small><b>Apresentação:</b> {teste['qtd']}</small><br>
            <small>{teste['descricao']}</small><br>
            <span style="color:#0d5c75; font-size:16px; font-weight:bold;">R$ {teste['preco']:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Comprar Autoteste - R$ {teste['preco']:.2f}", key=f"teste_{teste['id']}"):
            item = {
                "produto": f"{teste['nome']} ({teste['qtd']})",
                "laboratorio": "Kit Autoteste Residencial",
                "farmacia": "Farmácia Parceira Mais Próxima",
                "preco": teste['preco'],
                "retencao": False
            }
            st.session_state.carrinho.append(item)
            st.success("Autoteste adicionado ao carrinho!")
            st.rerun()

# ==========================================
# 7. ABA 4: CARRINHO E PAGAMENTO
# ==========================================
elif selected == "Carrinho":
    st.subheader("🛒 Seu Pedido")
    
    if not st.session_state.carrinho:
        st.info("O seu carrinho está vazio no momento.")
    else:
        df_cart = pd.DataFrame(st.session_state.carrinho)
        
        for idx, item in df_cart.iterrows():
            st.write(f"**{item['produto']}**")
            st.caption(f"Marca: {item['laboratorio']} | Farmácia de Origem: {item['farmacia']} — **R$ {item['preco']:.2f}**")
            if item['retencao']:
                st.warning("⚠️ Exige Envio/Entrega de Receita Médica")
            st.divider()
            
        total = df_cart["preco"].sum()
        st.markdown(f"### Total: **R$ {total:.2f}**")
        
        if any(df_cart["retencao"]):
            st.file_uploader("📷 Anexar Foto da Receita Médica (Obrigatório para Controlados/Antibióticos)", type=["jpg", "png", "pdf"])
            
        st.subheader("💳 Forma de Pagamento")
        forma_pagamento = st.radio("Selecione:", ["Pix (Aprovação Imediata)", "Cartão de Crédito"], horizontal=True)
        
        if forma_pagamento == "Cartão de Crédito":
            st.caption("💳 Aceita: **Visa, Mastercard, Elo, Hipercard, Amex**")
            if total >= 100.0:
                opcoes_parcela = [f"1x de R$ {total:.2f} (À vista)", f"2x de R$ {(total/2):.2f} (Sem juros)"]
                st.selectbox("Parcelamento:", opcoes_parcela)
            else:
                st.info("💡 Parcelamento em até 2x disponível para compras acima de R$ 100,00.")
                
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirmar Pedido", type="primary", use_container_width=True):
                st.success("Pedido enviado à farmácia parceira! Você receberá o código de rastreio da entrega.")
                st.balloons()
                st.session_state.carrinho = []
        with col2:
            if st.button("Esvaziar Carrinho", use_container_width=True):
                st.session_state.carrinho = []
                st.rerun()

# ==========================================
# 8. RODAPÉ INSTITUCIONAL ANVISA
# ==========================================
st.markdown("""
<div class="footer-anvisa">
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 6px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 2ZM12 11.99H19C18.47 16.11 15.72 19.78 12 20.93V12H5V6.3L12 3.97V11.99Z" fill="#0d5c75"/>
        </svg>
        <span style="font-weight: bold; color: #0d5c75; font-size: 12px;">Plataforma em Conformidade com a ANVISA</span>
    </div>
    Plataforma intermediadora de vendas para farmácias licenciadas (RDC 44/2009, RDC 20/2011, Portaria 344/1998 e RDC 786/2023).<br>
    A validação e retenção de receitas médicas é realizada pelos farmacêuticos responsáveis das farmácias parceiras no momento da separação/entrega.
</div>
""", unsafe_allow_html=True)
