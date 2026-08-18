import streamlit as st
import pandas as pd

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

# Estilização CSS com suporte a novos componentes e rodapé Anvisa
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
    
    /* Badges Regulatórios da Anvisa */
    .badge-portaria { background-color: #dc3545; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-antimicrobiano { background-color: #fd7e14; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-hormonio { background-color: #6f42c1; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-mip { background-color: #17a2b8; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-suplemento { background-color: #28a745; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-beleza { background-color: #e83e8c; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }

    /* Estilo do Rodapé Institucional */
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
# 2. BANCO DE DADOS EXPANDIDO (PANDAS)
# ==========================================
@st.cache_data
def carregar_banco_dados():
    cat_meds = pd.DataFrame([
        # --- PORTARIA 344/98 ---
        {"id": 201, "nome_principio": "Clonazepam", "apresentacao": "2,5mg/mL Gotas (20mL)", "categoria": "Portaria 344/98 (Lista B1)", "classe": "Ansiolítico / Anticonvulsivante", "retencao": True, "tipo_receita": "Notificação B (Azul)", "orientacao": "Causa dependência. Uso conforme orientação médica."},
        {"id": 202, "nome_principio": "Zolpidem", "apresentacao": "10mg (30 Comprimidos)", "categoria": "Portaria 344/98 (Lista B1)", "classe": "Indutor do Sono", "retencao": True, "tipo_receita": "Notificação B (Azul)", "orientacao": "Ingerir imediatamente antes de deitar."},

        # --- ANTIMICROBIANOS (RDC 20/2011 e RDC 471/2021) ---
        {"id": 250, "nome_principio": "Amoxicilina + Clavulanato", "apresentacao": "500mg/125mg (18 Comprimidos)", "categoria": "Antimicrobiano", "classe": "Antibiótico (Penicelina)", "retencao": True, "tipo_receita": "Receita de Controle Especial (2 vias)", "orientacao": "Respeitar rigorosamente os horários e completar todo o ciclo prescrito."},
        {"id": 251, "nome_principio": "Azitromicina", "apresentacao": "500mg (3 Comprimidos)", "categoria": "Antimicrobiano", "classe": "Antibiótico (Macrolídeo)", "retencao": True, "tipo_receita": "Receita de Controle Especial (2 vias)", "orientacao": "Tomar 1 hora antes ou 2 horas após as refeições."},

        # --- HORMÔNIOS E ESTEROIDES (RDC 52/2011 & Controle) ---
        {"id": 280, "nome_principio": "Levotiroxina Sódica", "apresentacao": "50mcg (30 Comprimidos)", "categoria": "Hormônio / Endocrinologia", "classe": "Hormônio Tireoidiano", "retencao": False, "tipo_receita": None, "orientacao": "Tomar em jejum absoluto, pelo menos 30 a 60 minutos antes do café da manhã."},
        {"id": 281, "nome_principio": "Estradiol (Valerato)", "apresentacao": "2mg (28 Comprimidos)", "categoria": "Hormônio / Endocrinologia", "classe": "Estrogênio / TSH", "retencao": False, "tipo_receita": None, "orientacao": "Seguir rigorosamente o esquema de administração diária."},

        # --- MIPS ---
        {"id": 301, "nome_principio": "Dipirona Monoidratada", "apresentacao": "1g (10 Comprimidos)", "categoria": "MIP (Isento de Prescrição)", "classe": "Analgésico e Antitérmico", "retencao": False, "tipo_receita": None, "orientacao": "Uso adulto. Respeitar o intervalo mínimo de 6 horas."},

        # --- SUPLEMENTOS ALIMENTARES ---
        {"id": 401, "nome_principio": "Vitamina C + Zinco", "apresentacao": "1000mg (10 Comp. Efervescentes)", "categoria": "Suplemento Alimentar", "classe": "Imunidade", "retencao": False, "tipo_receita": None, "orientacao": "Dissolver 1 comprimido em água ao dia.", "em_oferta": True, "desconto": "25% OFF"},
        {"id": 402, "nome_principio": "Ômega 3 EPA DHA", "apresentacao": "1000mg (120 Cápsulas)", "categoria": "Suplemento Alimentar", "classe": "Saúde Cardiovascular", "retencao": False, "tipo_receita": None, "orientacao": "Ingerir antes das principais refeições.", "em_oferta": True, "desconto": "30% OFF"},

        # --- PRODUTOS DE BELEZA / DERMOCOSMÉTICOS ---
        {"id": 501, "nome_principio": "Protetor Solar Facial FPS 60", "apresentacao": "Toque Seco (50g)", "categoria": "Produtos de Beleza", "classe": "Fotoproteção Cutânea", "retencao": False, "tipo_receita": None, "orientacao": "Reaplicar a cada 2 a 3 horas para eficácia total.", "em_oferta": True, "desconto": "20% OFF"},
        {"id": 502, "nome_principio": "Sérum Facial Ácido Hialurônico", "apresentacao": "Sérum Hidratante (30mL)", "categoria": "Produtos de Beleza", "classe": "Dermocosmético / Anti-idade", "retencao": False, "tipo_receita": None, "orientacao": "Aplicar de 3 a 4 gotas no rosto limpo pela manhã e à noite.", "em_oferta": False, "desconto": None}
    ])
    
    # Testes Rápidos Permitidos em Farmácias (RDC 786/2023)
    testes_rapidos = pd.DataFrame([
        {"id": 601, "nome": "Teste Rápido de Glicemia Capilar", "categoria": "Saúde Pessoal / Perfil Metabólico", "preco": 15.00, "descricao": "Aferição imediata com gota de sangue capilar."},
        {"id": 602, "nome": "Auto-teste COVID-19 / Influenza A+B", "categoria": "Saúde Pessoal / Painel Respiratório", "preco": 39.90, "descricao": "Coleta por swab nasal simples com resultado em 15 minutos."},
        {"id": 603, "nome": "Teste de Gravidez (Beta-HCG Urina)", "categoria": "Saúde Pessoal / Triagem Hormonal", "preco": 12.50, "descricao": "Detecção de alta sensibilidade a partir do 1º dia de atraso."},
        {"id": 604, "nome": "Teste Rápido Perfil Lipídico (Colesterol Total)", "categoria": "Saúde Pessoal / Triagem Cardiovascular", "preco": 29.90, "descricao": "Aferição rápida de colesterol total em ambiente farmacêutico."}
    ])
    
    ofertas = pd.DataFrame([
        {"med_id": 201, "laboratorio": "Medley", "farmacia": "Drogaria São Paulo", "preco": 14.50, "distancia_km": 0.8},
        {"med_id": 201, "laboratorio": "EMS", "farmacia": "Droga Raia", "preco": 11.90, "distancia_km": 1.5},
        {"med_id": 250, "laboratorio": "Eurofarma", "farmacia": "Pague Menos", "preco": 42.00, "distancia_km": 1.2},
        {"med_id": 250, "laboratorio": "Neo Química", "farmacia": "Drogaria São Paulo", "preco": 38.50, "distancia_km": 0.8},
        {"med_id": 280, "laboratorio": "Merck", "farmacia": "Droga Raia", "preco": 18.90, "distancia_km": 1.5},
        {"med_id": 301, "laboratorio": "Neo Química", "farmacia": "Farmácia Bairro", "preco": 6.50, "distancia_km": 0.5},
        {"med_id": 401, "laboratorio": "Redoxon", "farmacia": "Droga Raia", "preco": 18.90, "distancia_km": 1.5},
        {"med_id": 402, "laboratorio": "Max Titanium", "farmacia": "Drogaria São Paulo", "preco": 59.90, "distancia_km": 0.8},
        {"med_id": 501, "laboratorio": "La Roche-Posay", "farmacia": "Droga Raia", "preco": 69.90, "distancia_km": 1.5},
        {"med_id": 501, "laboratorio": "L'Oréal", "farmacia": "Pague Menos", "preco": 54.90, "distancia_km": 2.1},
        {"med_id": 502, "laboratorio": "Vichy", "farmacia": "Drogaria São Paulo", "preco": 129.90, "distancia_km": 0.8}
    ])
    
    return cat_meds, testes_rapidos, ofertas

df_meds, df_testes, df_ofertas = carregar_banco_dados()

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# ==========================================
# 3. CABEÇALHO E NAVEGAÇÃO
# ==========================================
st.markdown("""
<div class="health-header">
    <small>🩺 Atenção Farmacêutica Digital</small>
    <h3 style="margin:0; font-weight:600;">PharmaCare & Beleza</h3>
</div>
""", unsafe_allow_html=True)

opcoes_menu = ["Buscar", "Ofertas / Beleza", "Saúde Pessoal", "Carrinho"]

if HAS_OPTION_MENU:
    selected = option_menu(
        menu_title=None,
        options=opcoes_menu,
        icons=["search", "sparkles", "activity", "cart"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff"},
            "icon": {"color": "#1988a6", "font-size": "15px"},
            "nav-link": {"font-size": "12px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#1988a6", "color": "white"}
        }
    )
else:
    selected = st.radio("Navegação:", opcoes_menu, horizontal=True, label_visibility="collapsed")

# ==========================================
# 4. ABA 1: BUSCA ANINHADA E PREÇOS
# ==========================================
if selected == "Buscar":
    st.caption("Pesquise por Medicamentos (Controlados, Antimicrobianos, Hormônios, MIPs) ou Dermocosméticos:")
    
    termo_busca = st.selectbox(
        "Selecione ou digite o item desejado:",
        options=[""] + list(df_meds["nome_principio"].unique()),
        format_func=lambda x: "🔍 Digite para pesquisar..." if x == "" else x
    )
    
    if termo_busca != "":
        med_info = df_meds[df_meds["nome_principio"] == termo_busca].iloc[0]
        
        # Seleção de Tag dinâmica conforme a norma da Anvisa
        if "Portaria 344" in med_info['categoria']:
            cat_tag = f"<span class='badge-portaria'>{med_info['categoria']}</span>"
        elif "Antimicrobiano" in med_info['categoria']:
            cat_tag = f"<span class='badge-antimicrobiano'>{med_info['categoria']}</span>"
        elif "Hormônio" in med_info['categoria']:
            cat_tag = f"<span class='badge-hormonio'>{med_info['categoria']}</span>"
        elif "Beleza" in med_info['categoria']:
            cat_tag = f"<span class='badge-beleza'>{med_info['categoria']}</span>"
        else:
            cat_tag = f"<span class='badge-mip'>{med_info['categoria']}</span>"
        
        st.markdown(f"### {med_info['nome_principio']} {cat_tag}", unsafe_allow_html=True)
        st.write(f"**Apresentação / Dosagem:** {med_info['apresentacao']}")
        st.info(f"**Classe:** {med_info['classe']}\n\n**Orientação Farmacêutica:** {med_info['orientacao']}")
        
        if med_info['retencao']:
            st.error(f"⚠️ Item sujeito a controle especial ({med_info['tipo_receita']}): Exige retenção de receita médica na entrega/retirada.")
            
        st.subheader("🏷️ Laboratórios Disponíveis (Menor Valor Primeiro)")
        
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
                    st.success("Item adicionado ao carrinho!")
                    st.rerun()

# ==========================================
# 5. ABA 2: OFERTAS & PRODUTOS DE BELEZA
# ==========================================
elif selected == "Ofertas / Beleza":
    st.subheader("✨ Ofertas em Suplementos & Dermocosméticos")
    st.caption("Destaques com descontos especiais expostos diretamente para você:")
    
    # Exibe itens marcados com em_oferta = True (Suplementos e Beleza)
    itens_oferta = df_meds[df_meds["em_oferta"] == True]
    
    for _, item in itens_oferta.iterrows():
        st.markdown(f"""
        <div class="promo-card">
            <span style="float:right; background:white; color:#218838; font-weight:bold; padding:2px 8px; border-radius:6px;">{item['desconto']}</span>
            <h4 style="margin:0;">{item['nome_principio']}</h4>
            <small>{item['apresentacao']}</small><br>
            <small><b>Categoria:</b> {item['categoria']} | <b>Indicação:</b> {item['classe']}</small>
        </div>
        """, unsafe_allow_html=True)
        
        ofertas_item = df_ofertas[df_ofertas["med_id"] == item["id"]].sort_values(by="preco")
        if not ofertas_item.empty:
            melhor = ofertas_item.iloc[0]
            st.write(f"Vendido por **{melhor['farmacia']}** ({melhor['laboratorio']}) por apenas **R$ {melhor['preco']:.2f}**")
            
            if st.button(f"Aproveitar Oferta de {item['nome_principio']}", key=f"oferta_{item['id']}"):
                cart_item = {
                    "produto": f"{item['nome_principio']} - {item['apresentacao']}",
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
# 6. ABA 3: SAÚDE PESSOAL (TESTES RÁPIDOS)
# ==========================================
elif selected == "Saúde Pessoal":
    st.subheader("🩸 Testes Rápidos & Triagem de Saúde")
    st.caption("Serviços de saúde autorizados para comercialização e realização em farmácias (RDC 786/2023):")
    
    for _, teste in df_testes.iterrows():
        st.markdown(f"""
        <div class="pharmacy-card" style="border-left: 4px solid #17a2b8;">
            <b>{teste['nome']}</b><br>
            <small><b>Categoria:</b> {teste['categoria']}</small><br>
            <small>{teste['descricao']}</small><br>
            <span style="color:#0d5c75; font-size:16px; font-weight:bold;">R$ {teste['preco']:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Agendar / Adicionar Teste - R$ {teste['preco']:.2f}", key=f"teste_{teste['id']}"):
            item = {
                "produto": f"{teste['nome']} (Serviço/Teste Rápido)",
                "laboratorio": "Farmácia / Serviço Farmacêutico",
                "farmacia": "Unidade Selecionada",
                "preco": teste['preco'],
                "retencao": False
            }
            st.session_state.carrinho.append(item)
            st.success("Serviço adicionado ao carrinho!")
            st.rerun()

# ==========================================
# 7. ABA 4: CARRINHO E OPÇÕES DE PAGAMENTO
# ==========================================
elif selected == "Carrinho":
    st.subheader("🛒 Seu Carrinho de Saúde")
    
    if not st.session_state.carrinho:
        st.info("O seu carrinho está vazio no momento.")
    else:
        df_cart = pd.DataFrame(st.session_state.carrinho)
        
        for idx, item in df_cart.iterrows():
            st.write(f"**{item['produto']}**")
            st.caption(f"Marca/Lab: {item['laboratorio']} | Unidade: {item['farmacia']} — **R$ {item['preco']:.2f}**")
            if item['retencao']:
                st.warning("⚠️ Exige Envio/Apresentação de Receita Médica")
            st.divider()
            
        total = df_cart["preco"].sum()
        st.markdown(f"### Total do Pedido: **R$ {total:.2f}**")
        
        # Envio de receita médica caso haja retenção
        if any(df_cart["retencao"]):
            st.file_uploader("📷 Anexar Foto ou PDF da Receita Médica (Obrigatório para Controlados/Antimicrobianos)", type=["jpg", "png", "pdf"])
            
        st.subheader("💳 Forma de Pagamento")
        forma_pagamento = st.radio("Selecione como deseja pagar:", ["Pix (Aprovação Imediata)", "Cartão de Crédito"], horizontal=True)
        
        if forma_pagamento == "Cartão de Crédito":
            st.caption("💳 Bandeiras aceitas: **Visa, Mastercard, Elo, Hipercard, American Express**")
            
            # Opção de parcelamento a partir de R$ 100,00
            if total >= 100.0:
                opcoes_parcelamento = [
                    "1x de R$ {:.2f} (À vista sem juros)".format(total),
                    "2x de R$ {:.2f} (Sem juros)".format(total / 2)
                ]
                st.selectbox("Opções de Parcelamento:", opcoes_parcelamento)
            else:
                st.info("💡 Parcelamento em até 2x sem juros disponível para compras a partir de R$ 100,00.")
                
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Finalizar Pedido", type="primary", use_container_width=True):
                st.success("Pedido concluído! O farmacêutico fará a conferência das receitas anexadas antes do envio.")
                st.balloons()
                st.session_state.carrinho = []
        with col2:
            if st.button("Esvaziar Carrinho", use_container_width=True):
                st.session_state.carrinho = []
                st.rerun()

# ==========================================
# 8. RODAPÉ INSTITUCIONAL (NORMATIVA ANVISA)
# ==========================================
st.markdown("""
<div class="footer-anvisa">
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 6px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 2ZM12 11.99H19C18.47 16.11 15.72 19.78 12 20.93V12H5V6.3L12 3.97V11.99Z" fill="#0d5c75"/>
        </svg>
        <span style="font-weight: bold; color: #0d5c75; font-size: 12px;">Conforme Regulamentação ANVISA</span>
    </div>
    Este aplicativo cumpre integralmente as Boas Práticas Farmacêuticas dispostas nas Resoluções da Anvisa (RDC 44/2009, RDC 20/2011, RDC 471/2021, Portaria SVS/MS 344/1998 e RDC 786/2023).<br>
    A dispensação de medicamentos sujeitos a controle especial e antimicrobianos está condicionada à apresentação e validação da receita por farmacêutico habilitado.
</div>
""", unsafe_allow_html=True)
