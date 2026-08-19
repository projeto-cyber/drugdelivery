import streamlit as st
import pandas as pd
import random

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA (WEB APP RESPONSIVO WIDE)
# ==========================================
st.set_page_config(
    page_title="PharmaMarket Express - Marketplace de Saúde",
    page_icon="💊",
    layout="wide",  # Expande para utilizar toda a largura da tela no navegador Web
    initial_sidebar_state="collapsed"
)

# Estilização CSS Avançada para Web App Responsivo
st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; }
    
    /* Header Superior com Barra de Navegação Web */
    .top-navbar {
        background: linear-gradient(135deg, #0d5c75, #1988a6);
        color: white;
        padding: 15px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Cartões de Oferta Estilo E-Commerce */
    .product-card {
        background: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        transition: transform 0.2s;
        margin-bottom: 15px;
    }
    .product-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
    }
    
    .badge-desconto {
        background-color: #28a745;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
    }
    
    /* Badges Regulatórios da Anvisa */
    .badge-portaria { background-color: #dc3545; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-antimicrobiano { background-color: #fd7e14; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-mip { background-color: #17a2b8; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-suplemento { background-color: #28a745; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .badge-beleza { background-color: #e83e8c; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }

    .footer-anvisa {
        margin-top: 50px;
        padding: 20px;
        background-color: #ffffff;
        border-top: 1px solid #e9ecef;
        text-align: center;
        font-size: 12px;
        color: #6c757d;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ESTADOS DA SESSÃO (SESSION STATE)
# ==========================================
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = False
    st.session_state.nome_usuario = ""

if 'pedidos_realizados' not in st.session_state:
    st.session_state.pedidos_realizados = []

# ==========================================
# 3. BANCO DE DADOS (PANDAS)
# ==========================================
@st.cache_data
def carregar_banco_dados():
    cat_meds = pd.DataFrame([
        # --- CONTROLADOS PORTARIA 344/98 ---
        {"id": 201, "nome_principio": "Clonazepam", "dosagem": "0,5mg", "qtd_embalagem": "30 Comprimidos", "categoria": "Portaria 344/98 (Lista B1)", "classe": "Ansiolítico", "retencao": True, "tipo_receita": "Notificação B (Azul)", "orientacao": "Uso sob orientação médica.", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=300"},
        {"id": 202, "nome_principio": "Clonazepam", "dosagem": "2,0mg", "qtd_embalagem": "30 Comprimidos", "categoria": "Portaria 344/98 (Lista B1)", "classe": "Ansiolítico", "retencao": True, "tipo_receita": "Notificação B (Azul)", "orientacao": "Uso sob orientação médica.", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=300"},
        {"id": 204, "nome_principio": "Zolpidem (Hemitartarato)", "dosagem": "10mg", "qtd_embalagem": "30 Comprimidos", "categoria": "Portaria 344/98 (Lista B1)", "classe": "Indutor do Sono", "retencao": True, "tipo_receita": "Notificação B (Azul)", "orientacao": "Tomar antes de deitar.", "img": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=300"},

        # --- ANTIMICROBIANOS ---
        {"id": 250, "nome_principio": "Amoxicilina + Clavulanato", "dosagem": "500mg + 125mg", "qtd_embalagem": "18 Comprimidos Revestidos", "categoria": "Antimicrobiano", "classe": "Antibiótico", "retencao": True, "tipo_receita": "Receita de Controle Especial (2 vias)", "orientacao": "Seguir horários rigorosamente.", "img": "https://images.unsplash.com/photo-1576602976047-174e57a47881?w=300"},
        {"id": 252, "nome_principio": "Azitromicina Monoidratada", "dosagem": "500mg", "qtd_embalagem": "3 Comprimidos Revestidos", "categoria": "Antimicrobiano", "classe": "Antibiótico", "retencao": True, "tipo_receita": "Receita de Controle Especial (2 vias)", "orientacao": "Tomar 1 hora antes de refeições.", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=300"},

        # --- MIPS ---
        {"id": 301, "nome_principio": "Dipirona Monoidratada", "dosagem": "500mg", "qtd_embalagem": "20 Comprimidos", "categoria": "MIP (Isento de Prescrição)", "classe": "Analgésico/Antitérmico", "retencao": False, "tipo_receita": None, "orientacao": "Intervalo mínimo de 6 horas.", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=300"},
        {"id": 302, "nome_principio": "Dipirona Monoidratada", "dosagem": "1g (1000mg)", "qtd_embalagem": "10 Comp. Efervescentes", "categoria": "MIP (Isento de Prescrição)", "classe": "Analgésico/Antitérmico", "retencao": False, "tipo_receita": None, "orientacao": "Dissolver em água.", "img": "https://images.unsplash.com/photo-1550572017-edd951baa742?w=300"},

        # --- SUPLEMENTOS EM OFERTA (COM IMAGENS GERADAS/ILUSTRATIVAS) ---
        {"id": 401, "nome_principio": "Vitamina C + Zinco", "dosagem": "1000mg + 10mg", "qtd_embalagem": "10 Comp. Efervescentes", "categoria": "Suplemento Alimentar", "classe": "Imunidade & Vitalidade", "retencao": False, "tipo_receita": None, "orientacao": "Uso diário.", "em_oferta": True, "desconto": "25% OFF", "img": "https://images.unsplash.com/photo-1577401239170-897942555fb3?w=400"},
        {"id": 402, "nome_principio": "Ômega 3 EPA DHA Ultra", "dosagem": "1000mg", "qtd_embalagem": "120 Cápsulas Gelatinosas", "categoria": "Suplemento Alimentar", "classe": "Saúde Cardiovascular", "retencao": False, "tipo_receita": None, "orientacao": "Ingerir junto às refeições.", "em_oferta": True, "desconto": "30% OFF", "img": "https://images.unsplash.com/photo-1526947425960-945c6e72858f?w=400"},

        # --- PRODUTOS DE BELEZA ---
        {"id": 501, "nome_principio": "Protetor Solar Facial FPS 60", "dosagem": "Toque Seco Anti-oleosidade", "qtd_embalagem": "Bisnaga de 50g", "categoria": "Produtos de Beleza", "classe": "Dermocosmético / Fotoproteção", "retencao": False, "tipo_receita": None, "orientacao": "Reaplicar a cada 3 horas.", "em_oferta": True, "desconto": "20% OFF", "img": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400"},
        {"id": 502, "nome_principio": "Sérum Facial Ácido Hialurônico", "dosagem": "Sérum Concentrado", "qtd_embalagem": "Frasco Conta-gotas 30mL", "categoria": "Produtos de Beleza", "classe": "Anti-idade / Hidratação", "retencao": False, "tipo_receita": None, "orientacao": "Aplicar de dia e à noite.", "em_oferta": True, "desconto": "15% OFF", "img": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400"}
    ])
    
    # AUTOTESTES RESIDENCIAIS
    autotestes_casa = pd.DataFrame([
        {"id": 601, "nome": "Autoteste COVID-19 Ag Nasal", "qtd": "1 Kit Completo", "preco": 24.90, "descricao": "Resultado rápido em 15min no conforto do lar.", "img": "https://images.unsplash.com/photo-1615461066841-6116e61058f4?w=400"},
        {"id": 602, "nome": "Teste de Gravidez Rápido HCG", "qtd": "1 Caneta Dispositivo", "preco": 11.90, "descricao": "Detecção de alta sensibilidade na urina.", "img": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400"},
        {"id": 603, "nome": "Autoteste de Ovulação (Fertilidade)", "qtd": "5 Tiras Reativas", "preco": 34.90, "descricao": "Acompanhe seus dias férteis em casa.", "img": "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=400"},
        {"id": 604, "nome": "Autoteste de HIV (Triagem Privada)", "qtd": "1 Dispositivo de Coleta", "preco": 69.90, "descricao": "Triagem individual e 100% privada aprovada pela Anvisa.", "img": "https://images.unsplash.com/photo-1579154204601-01588f351e67?w=400"}
    ])
    
    ofertas = pd.DataFrame([
        {"med_id": 201, "laboratorio": "Medley", "farmacia": "Drogaria São Paulo", "preco": 11.50, "distancia_km": 0.8},
        {"med_id": 201, "laboratorio": "EMS", "farmacia": "Droga Raia", "preco": 9.90, "distancia_km": 1.5},
        {"med_id": 202, "laboratorio": "Eurofarma", "farmacia": "Pague Menos", "preco": 18.20, "distancia_km": 1.2},
        {"med_id": 204, "laboratorio": "Aché", "farmacia": "Drogaria São Paulo", "preco": 14.90, "distancia_km": 0.8},
        {"med_id": 250, "laboratorio": "Eurofarma", "farmacia": "Pague Menos", "preco": 42.00, "distancia_km": 1.2},
        {"med_id": 250, "laboratorio": "Neo Química", "farmacia": "Drogaria São Paulo", "preco": 38.50, "distancia_km": 0.8},
        {"med_id": 301, "laboratorio": "Neo Química", "farmacia": "Farmácia Bairro", "preco": 5.50, "distancia_km": 0.5},
        {"med_id": 401, "laboratorio": "Redoxon", "farmacia": "Droga Raia", "preco": 18.90, "distancia_km": 1.5},
        {"med_id": 402, "laboratorio": "Max Titanium", "farmacia": "Drogaria São Paulo", "preco": 59.90, "distancia_km": 0.8},
        {"med_id": 501, "laboratorio": "L'Oréal", "farmacia": "Pague Menos", "preco": 54.90, "distancia_km": 2.1},
        {"med_id": 502, "laboratorio": "Vichy", "farmacia": "Droga Raia", "preco": 99.90, "distancia_km": 1.5}
    ])
    
    return cat_meds, autotestes_casa, ofertas

df_meds, df_testes, df_ofertas = carregar_banco_dados()

# Cálculo dinâmico do valor total da Cesta de Compras
valor_total_cesta = sum(item["preco"] for item in st.session_state.carrinho)
qtd_itens_cesta = len(st.session_state.carrinho)

# ==========================================
# 4. BARRA DE NAVEGAÇÃO SUPERIOR (WEB NAVBAR)
# ==========================================
col_logo, col_nav, col_cart = st.columns([2.5, 5, 2.5])

with col_logo:
    st.markdown("### 💊 **PharmaMarket** `Express`")

with col_nav:
    # Menu Superior Estilo Web App
    aba_selecionada = st.radio(
        "Navegação Principais",
        ["🔥 Ofertas & Destaques", "🔍 Buscar Remédios", "🏠 Autotestes em Casa", "🚚 Acompanhar Pedido", "👤 Minha Conta"],
        horizontal=True,
        label_visibility="collapsed"
    )

with col_cart:
    # Cesta Exibida em Tempo Real na Barra Superior
    st.markdown(f"""
    <div style="background-color:#1988a6; color:white; padding:8px 15px; border-radius:8px; text-align:center; font-weight:bold;">
        🛒 Cesta: {qtd_itens_cesta} item(ns) | R$ {valor_total_cesta:.2f}
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. CONTEÚDO DAS ABAS DO WEB APP
# ==========================================

# --- ABA 1: OFERTAS & DESTAQUES (GRID DE PRODUTOS) ---
if aba_selecionada == "🔥 Ofertas & Destaques":
    st.subheader("🌟 Suplementos & Dermocosméticos em Oferta")
    st.caption("Aproveite os melhores preços das farmácias parceiras da sua região:")
    
    itens_oferta = df_meds[df_meds["em_oferta"] == True]
    cols = st.columns(3)  # Grid com 3 colunas para aproveitar a tela Web Wide
    
    for idx, (_, item) in enumerate(itens_oferta.iterrows()):
        with cols[idx % 3]:
            st.image(item["img"], use_container_width=True)
            st.markdown(f"**{item['nome_principio']}** <span class='badge-desconto'>{item['desconto']}</span>", unsafe_allow_html=True)
            st.caption(f"{item['dosagem']} | {item['qtd_embalagem']}")
            
            ofertas_item = df_ofertas[df_ofertas["med_id"] == item["id"]].sort_values(by="preco")
            if not ofertas_item.empty:
                melhor = ofertas_item.iloc[0]
                st.markdown(f"Vendido por **{melhor['farmacia']}**")
                st.markdown(f"### <span style='color:#0d5c75;'>R$ {melhor['preco']:.2f}</span>", unsafe_allow_html=True)
                
                if st.button(f"Adicionar à Cesta", key=f"oferta_btn_{item['id']}", type="primary", use_container_width=True):
                    cart_item = {
                        "produto": f"{item['nome_principio']} {item['dosagem']}",
                        "laboratorio": melhor['laboratorio'],
                        "farmacia": melhor['farmacia'],
                        "preco": melhor['preco'],
                        "retencao": False
                    }
                    st.session_state.carrinho.append(cart_item)
                    st.toast("Item adicionado à cesta!", icon="🛒")
                    st.rerun()

# --- ABA 2: BUSCAR MEDICAMENTOS (BUSCA ANINHADA & COMPARADOR) ---
elif aba_selecionada == "🔍 Buscar Remédios":
    st.subheader("🔍 Pesquisa Geral de Medicamentos")
    st.caption("Consulte dosagens, apresentações e comparativo do menor valor entre as farmácias parceiras:")
    
    col_search1, col_search2 = st.columns([1, 2])
    
    with col_search1:
        termo_busca = st.selectbox(
            "Selecione o Princípio Ativo:",
            options=[""] + list(df_meds["nome_principio"].unique()),
            format_func=lambda x: "Digite ou escolha o remédio..." if x == "" else x
        )
    
    if termo_busca != "":
        opcoes_apresentacao = df_meds[df_meds["nome_principio"] == termo_busca]
        
        with col_search2:
            apresentacao_sel = st.selectbox(
                "Selecione a Dosagem / Apresentação:",
                options=opcoes_apresentacao["id"].tolist(),
                format_func=lambda x: f"{opcoes_apresentacao[opcoes_apresentacao['id'] == x]['dosagem'].values[0]} — {opcoes_apresentacao[opcoes_apresentacao['id'] == x]['qtd_embalagem'].values[0]}"
            )
            
        med_info = opcoes_apresentacao[opcoes_apresentacao["id"] == apresentacao_sel].iloc[0]
        
        st.divider()
        col_med_img, col_med_detalhes = st.columns([1, 3])
        
        with col_med_img:
            st.image(med_info["img"], width=200)
            
        with col_med_detalhes:
            if "Portaria 344" in med_info['categoria']:
                cat_tag = f"<span class='badge-portaria'>{med_info['categoria']}</span>"
            elif "Antimicrobiano" in med_info['categoria']:
                cat_tag = f"<span class='badge-antimicrobiano'>{med_info['categoria']}</span>"
            else:
                cat_tag = f"<span class='badge-mip'>{med_info['categoria']}</span>"
                
            st.markdown(f"## {med_info['nome_principio']} {cat_tag}", unsafe_allow_html=True)
            st.write(f"**Apresentação:** {med_info['dosagem']} ({med_info['qtd_embalagem']})")
            st.info(f"**Classe Farmacêutica:** {med_info['classe']}\n\n**Orientação:** {med_info['orientacao']}")
            
            if med_info['retencao']:
                st.error(f"⚠️ Exige validação de receita médica ({med_info['tipo_receita']}) no momento da entrega.")

        st.subheader("🏷️ Opções das Farmácias da Cidade (Ordenadas do Menor para o Maior Valor)")
        ofertas_med = df_ofertas[df_ofertas["med_id"] == med_info["id"]].sort_values(by="preco")
        
        cols_ofertas = st.columns(len(ofertas_med) if len(ofertas_med) > 0 else 1)
        for idx, (_, row) in enumerate(ofertas_med.iterrows()):
            with cols_ofertas[idx]:
                st.markdown(f"""
                <div class="product-card">
                    <h4>R$ {row['preco']:.2f}</h4>
                    <b>Marca/Lab:</b> {row['laboratorio']}<br>
                    <small>Farmácia: {row['farmacia']}</small><br>
                    <small>Distância: {row['distancia_km']} km</small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Comprar ({row['farmacia']})", key=f"btn_med_{row['med_id']}_{idx}"):
                    item = {
                        "produto": f"{med_info['nome_principio']} {med_info['dosagem']}",
                        "laboratorio": row['laboratorio'],
                        "farmacia": row['farmacia'],
                        "preco": row['preco'],
                        "retencao": med_info['retencao']
                    }
                    st.session_state.carrinho.append(item)
                    st.toast("Item adicionado à cesta!", icon="🛒")
                    st.rerun()

# --- ABA 3: AUTOTESTES RESIDENCIAIS (USO EM CASA) ---
elif aba_selecionada == "🏠 Autotestes em Casa":
    st.subheader("🏡 Kits de Autoteste para Uso Doméstico")
    st.caption("Dispositivos e testes rápidos autorizados pela Anvisa para realização no conforto do seu lar:")
    
    cols_testes = st.columns(2)
    for idx, (_, teste) in enumerate(df_testes.iterrows()):
        with cols_testes[idx % 2]:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(teste["img"], use_container_width=True)
            with c2:
                st.markdown(f"### {teste['nome']}")
                st.caption(f"Embalagem: {teste['qtd']}")
                st.write(teste["descricao"])
                st.markdown(f"#### R$ {teste['preco']:.2f}")
                
                if st.button(f"Adicionar Autoteste", key=f"btn_test_{teste['id']}"):
                    item = {
                        "produto": f"{teste['nome']} ({teste['qtd']})",
                        "laboratorio": "Kit Autoteste Residencial",
                        "farmacia": "Farmácia Parceira Mais Próxima",
                        "preco": teste['preco'],
                        "retencao": False
                    }
                    st.session_state.carrinho.append(item)
                    st.toast("Autoteste adicionado à cesta!", icon="🛒")
                    st.rerun()

# --- ABA 4: ACOMPANHAR PEDIDO (RASTREAMENTO) ---
elif aba_selecionada == "🚚 Acompanhar Pedido":
    st.subheader("📦 Rastreamento do Pedido")
    st.caption("Consulte o status de entrega do seu pedido realizado nas farmácias parceiras:")
    
    codigo_busca = st.text_input("Digite seu Código de Rastreio (ex: PM-8932):")
    
    if codigo_busca:
        # Busca no histórico simulado da sessão
        pedido_encontrado = next((p for p in st.session_state.pedidos_realizados if p["codigo"] == codigo_busca), None)
        
        if pedido_encontrado:
            st.success(f"Pedido **{pedido_encontrado['codigo']}** localizado!")
            st.info(f"**Status Atual:** {pedido_encontrado['status']}")
            st.write(f"**Farmácia de Origem:** {pedido_encontrado['farmacia']}")
            st.write(f"**Total:** R$ {pedido_encontrado['total']:.2f}")
            st.progress(75, text="🛵 O motoboy está a caminho do seu endereço")
        else:
            st.warning("Código de pedido não localizado. Verifique se o código digitado está correto.")
            
    elif st.session_state.pedidos_realizados:
        st.write("### Seus Pedidos Recentes:")
        for ped in st.session_state.pedidos_realizados:
            st.markdown(f"""
            <div class="product-card">
                <b>Código: {ped['codigo']}</b> | Data: Hoje | Total: <b>R$ {ped['total']:.2f}</b><br>
                <small>Status: <span style="color:#28a745; font-weight:bold;">{ped['status']}</span></small>
            </div>
            """, unsafe_allow_html=True)

# --- ABA 5: MINHA CONTA / LOGIN / CADASTRO / CESTA ---
elif aba_selecionada == "👤 Minha Conta":
    col_acc1, col_acc2 = st.columns([1, 1])
    
    with col_acc1:
        st.subheader("🔐 Área do Cliente (Login / Cadastro)")
        if not st.session_state.usuario_logado:
            aba_login, aba_cadastro = st.tabs(["Entrar", "Criar Conta"])
            
            with aba_login:
                email_login = st.text_input("E-mail:")
                senha_login = st.text_input("Senha:", type="password")
                if st.button("Acessar Conta", type="primary"):
                    if email_login:
                        st.session_state.usuario_logado = True
                        st.session_state.nome_usuario = email_login.split("@")[0].capitalize()
                        st.success(f"Bem-vindo(a) de volta, {st.session_state.nome_usuario}!")
                        st.rerun()
                        
            with aba_cadastro:
                st.text_input("Nome Completo:")
                st.text_input("CPF (Para emissão de Nota Fiscal):")
                st.text_input("E-mail para Cadastro:")
                st.text_input("Definir Senha:", type="password")
                if st.button("Cadastrar"):
                    st.success("Conta criada com sucesso! Faça login para continuar.")
        else:
            st.success(f"👤 Conectado como **{st.session_state.nome_usuario}**")
            if st.button("Sair da Conta"):
                st.session_state.usuario_logado = False
                st.session_state.nome_usuario = ""
                st.rerun()

    with col_acc2:
        st.subheader("🛒 Finalizar Compras da Cesta")
        
        if not st.session_state.carrinho:
            st.info("Sua cesta está vazia.")
        else:
            for idx, item in enumerate(st.session_state.carrinho):
                st.write(f"**{item['produto']}** - R$ {item['preco']:.2f}")
                st.caption(f"Farmácia: {item['farmacia']}")
                if item['retencao']:
                    st.warning("⚠️ Requer Receita Médica")
                st.divider()
                
            st.markdown(f"### Total: **R$ {valor_total_cesta:.2f}**")
            
            if any(item['retencao'] for item in st.session_state.carrinho):
                st.file_uploader("📷 Anexar Receita Médica (Obrigatório)", type=["jpg", "png", "pdf"])
                
            forma_pagamento = st.radio("Forma de Pagamento:", ["Pix", "Cartão de Crédito"], horizontal=True)
            
            if forma_pagamento == "Cartão de Crédito" and valor_total_cesta >= 100.0:
                st.selectbox("Parcelas:", [f"1x R$ {valor_total_cesta:.2f}", f"2x R$ {(valor_total_cesta/2):.2f} (Sem juros)"])
                
            if st.button("Finalizar e Gerar Código de Pedido", type="primary", use_container_width=True):
                # Gera código único de pedido
                codigo_gerado = f"PM-{random.randint(1000, 9999)}"
                
                novo_pedido = {
                    "codigo": codigo_gerado,
                    "total": valor_total_cesta,
                    "farmacia": st.session_state.carrinho[0]["farmacia"],
                    "status": "Em Separação pela Farmácia Parceira"
                }
                
                st.session_state.pedidos_realizados.append(novo_pedido)
                st.session_state.carrinho = [] # Limpa a cesta
                
                st.balloons()
                st.success(f"🎉 Pedido Concluído! Seu código de rastreio é: **{codigo_gerado}**")
                st.info("Utilize este código na aba **🚚 Acompanhar Pedido** para monitorar a entrega.")

# ==========================================
# 6. RODAPÉ INSTITUCIONAL ANVISA
# ==========================================
st.markdown("""
<div class="footer-anvisa">
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 6px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 2ZM12 11.99H19C18.47 16.11 15.72 19.78 12 20.93V12H5V6.3L12 3.97V11.99Z" fill="#0d5c75"/>
        </svg>
        <span style="font-weight: bold; color: #0d5c75; font-size: 13px;">Plataforma em Conformidade com as Normas Regulatórias da ANVISA</span>
    </div>
    Plataforma intermediadora de e-commerce e delivery para farmácias e drogarias licenciadas (RDC 44/2009, RDC 20/2011, Portaria 344/1998 e RDC 786/2023).<br>
    A validação e retenção das receitas de medicamentos sujeitos a controle especial e antibióticos é realizada pelos farmacêuticos das unidades parceiras no ato do despacho/entrega.
</div>
""", unsafe_allow_html=True)
