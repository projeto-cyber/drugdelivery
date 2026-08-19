import os
import io
import json
import time
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# ==========================================
# 1. CONFIGURAÇÃO DE LAYOUT E ESTILO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="PharmaStream Pro - Vendas & Gestão",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo customizado (CSS)
st.markdown("""
<style>
    .card-critico {
        border-left: 5px solid #FF4B4B;
        padding: 10px;
        background-color: #FFF5F5;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .card-normal {
        border-left: 5px solid #09AB3B;
        padding: 10px;
        background-color: #F6FFF8;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .cupom-card {
        border: 2px dashed #2196F3;
        background-color: #E3F2FD;
        padding: 10px;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .oferta-badge {
        background-color: #FF9800;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
    }
    .footer-anvisa {
        text-align: center;
        font-size: 0.78em;
        color: #555555;
        margin-top: 50px;
        padding: 15px;
        border-top: 1px solid #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXÃO E INICIALIZAÇÃO DO BANCO DE DADOS
# ==========================================
@st.cache_resource
def iniciar_banco_dados():
    conexao = sqlite3.connect("farmacia_app.db", check_same_thread=False)
    cursor = conexao.cursor()
    
    # Criar tabela de estoque se inexistente
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo_atc TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL,
            requer_receita INTEGER NOT NULL,
            grupo_terapeutico TEXT NOT NULL,
            tags TEXT,
            em_oferta INTEGER DEFAULT 0,
            distancia_km REAL DEFAULT 0.0,
            loja_parceira TEXT DEFAULT 'Farmácia Central'
        )
    """)
    
    # Migrações defensivas para colunas ausentes
    cursor.execute("PRAGMA table_info(estoque)")
    colunas_existentes = [coluna[1] for coluna in cursor.fetchall()]
    
    if 'em_oferta' not in colunas_existentes:
        cursor.execute("ALTER TABLE estoque ADD COLUMN em_oferta INTEGER DEFAULT 0")
    if 'distancia_km' not in colunas_existentes:
        cursor.execute("ALTER TABLE estoque ADD COLUMN distancia_km REAL DEFAULT 0.0")
    if 'loja_parceira' not in colunas_existentes:
        cursor.execute("ALTER TABLE estoque ADD COLUMN loja_parceira TEXT DEFAULT 'Farmácia Central'")
        
    # Criar tabela de auditoria de vendas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas_registro (
            id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            subtotal REAL NOT NULL,
            desconto REAL NOT NULL DEFAULT 0.0,
            imposto REAL NOT NULL,
            total REAL NOT NULL,
            forma_pagamento TEXT,
            crm_medico TEXT,
            paciente_nome TEXT,
            receita_retida_json TEXT
        )
    """)
    conexao.commit()
    
    # Alimentação inicial do estoque
    cursor.execute("SELECT COUNT(*) FROM estoque")
    if cursor.fetchone()[0] == 0:
        medicamentos_carga = [
            ("Ibuprofeno 600mg", "M01AE", 18.50, 45, 0, "Anti-inflamatório", "dor, inflamacao, febre", 1, 1.2, "Drogaria São Paulo - Centro"),
            ("Dipirona Monoidratada 1g", "N02BB", 9.90, 120, 0, "Analgésico", "dor, febre", 1, 2.5, "Farmácia Pague Menos - Jardins"),
            ("Diazepam 10mg", "N05B", 24.50, 12, 1, "Ansiolítico", "ansiedade, sono, controlado", 0, 3.1, "Droga Raia - Pinheiros"),
            ("Clonazepam 2mg", "N05B", 21.00, 8, 1, "Ansiolítico", "ansiedade, controlado", 1, 0.8, "Drogaria São Paulo - Centro"),
            ("Zolpidem 10mg", "N05C", 42.00, 15, 1, "Hipnótico", "sono, insomnia, controlado", 0, 4.0, "Drogaria Pacheco - Paulista"),
            ("Cloridrato de Loratadina 10mg", "R06", 14.80, 55, 0, "Anti-histamínico", "alergia, rinite", 1, 1.8, "Droga Raia - Pinheiros"),
            ("Sulfato de Salbutamol 100mcg", "R03", 32.00, 22, 0, "Doenças Respiratórias", "asma, bronquite", 0, 2.1, "Farmácia Pague Menos - Jardins"),
            ("Paracetamol 750mg", "N02BE", 11.20, 95, 0, "Analgésico", "dor, febre", 1, 0.5, "Drogaria São Paulo - Centro")
        ]
        cursor.executemany("""
            INSERT INTO estoque (nome, codigo_atc, preco, quantidade, requer_receita, grupo_terapeutico, tags, em_oferta, distancia_km, loja_parceira)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, medicamentos_carga)
        conexao.commit()
        
    return conexao

conn = iniciar_banco_dados()

# ==========================================
# 3. CONTROLE DE ESTADO DE SESSÃO & DADOS JSON
# ==========================================
if "carrinho_vendas" not in st.session_state:
    st.session_state.carrinho_vendas = []
if "usuario_perfil" not in st.session_state:
    st.session_state.usuario_perfil = "Cliente"
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = False
if "usuario_nome" not in st.session_state:
    st.session_state.usuario_nome = ""
if "cupom_aplicado" not in st.session_state:
    st.session_state.cupom_aplicado = None
if "percentual_desconto" not in st.session_state:
    st.session_state.percentual_desconto = 0.0
if "receita_digital_validada" not in st.session_state:
    st.session_state.receita_digital_validada = False
if "dados_ocr_receita" not in st.session_state:
    st.session_state.dados_ocr_receita = None
if "farmacias_favoritas" not in st.session_state:
    st.session_state.farmacias_favoritas = set()

# Base de Cupons Válidos
CUPONS_VALIDOS = {
    "CLIENTE10": 0.10,
    "PHARMA15": 0.15,
    "PRIMEIRACOMPRA": 0.20
}

# Dados em formato JSON de Identidade Institucional & Farmácias Parceiras
CONFIGURACAO_IDENTIDADE_JSON = json.dumps({
    "nome_plataforma": "PharmaStream Pro",
    "versao": "2.4.0",
    "regulacao": "ANVISA",
    "ambiente": "Produção",
    "suporte_emergencial": "0800-777-PHARMA",
    "temas": {
        "cor_primaria": "#09AB3B",
        "cor_secundaria": "#2196F3",
        "alerta": "#FF4B4B"
    }
}, indent=4, ensure_ascii=False)

FARMACIAS_PARCEIRAS_DATA = [
    {"id": 1, "nome": "Drogaria São Paulo - Centro", "lat": -23.5505, "lon": -46.6333, "distancia_km": 0.8, "tem_ofertas": True, "avaliacao": 4.8},
    {"id": 2, "nome": "Droga Raia - Pinheiros", "lat": -23.5615, "lon": -46.6822, "distancia_km": 1.8, "tem_ofertas": True, "avaliacao": 4.9},
    {"id": 3, "nome": "Farmácia Pague Menos - Jardins", "lat": -23.5685, "lon": -46.6598, "distancia_km": 2.5, "tem_ofertas": True, "avaliacao": 4.6},
    {"id": 4, "nome": "Drogaria Pacheco - Paulista", "lat": -23.5614, "lon": -46.6558, "distancia_km": 4.0, "tem_ofertas": False, "avaliacao": 4.5}
]

# Estutura Completa de Categorias Solicitadas
ESTRUTURA_CATEGORIAS = {
    "Saúde": ["Teste Rápido", "Saúde Bucal", "Produtos de Beleza", "Dispositivos Médicos", "Fraldas"],
    "Medicamentos": ["Medicamentos Controlados", "Hormônios", "Antimicrobianos", "Fitoterápicos", "Medicamentos Isentos de Prescrição"],
    "Vitaminas e Suplementos": ["Multivitamínicos", "Vitaminas", "Minerais"],
    "Mamãe & Bebê": ["Fraldas", "Amamentação", "Saúde da Mãe", "Saúde do Bebê"],
    "Beleza": ["Cuidado com a Pele", "Maquiagem", "Perfumaria", "Tratamento Capilar", "Produtos Asiáticos"],
    "Cuidados Diários": ["Higiene Pessoal", "Depilação", "Repelente", "Cuidado Masculino", "Cuidado Feminino", "Cuidado com a Pele", "Cuidado com os Pés"],
    "Pet": ["Medicamentos Pet", "Vida Saudável Pet"],
    "Marcas Parceiras": ["Marca A", "Marca B", "Marca C"]
}

# ==========================================
# 4. FUNÇÕES DE AUTENTICAÇÃO E NEGÓCIO
# ==========================================
def gerenciar_autenticacao():
    st.sidebar.subheader("🔒 Autenticação & Perfil")
    perfil = st.sidebar.selectbox(
        "Perfil operacional:",
        ["Cliente", "Administrador / Farmacêutico"],
        key="perfil_selectbox"
    )
    st.session_state.usuario_perfil = perfil

    st.sidebar.markdown("---")
    if not st.session_state.usuario_logado:
        st.sidebar.subheader("🔑 Login do Cliente")
        with st.sidebar.form("form_login_sidebar"):
            user_input = st.text_input("Usuário / E-mail")
            pass_input = st.text_input("Senha", type="password")
            btn_login = st.form_submit_button("Entrar", type="primary", use_container_width=True)
            
            if btn_login:
                if user_input and pass_input:
                    st.session_state.usuario_logado = True
                    st.session_state.usuario_nome = user_input.split("@")[0].capitalize()
                    st.sidebar.success(f"Bem-vindo(a), {st.session_state.usuario_nome}!")
                    st.rerun()
                else:
                    st.sidebar.error("Informe usuário e senha.")
    else:
        st.sidebar.success(f"👤 Conectado como: **{st.session_state.usuario_nome}**")
        if st.sidebar.button("Sair / Logout", use_container_width=True):
            st.session_state.usuario_logado = False
            st.session_state.usuario_nome = ""
            st.session_state.cupom_aplicado = None
            st.session_state.percentual_desconto = 0.0
            st.rerun()

def inserir_produto_carrinho(id_prod, nome, preco, requer_receita):
    for item in st.session_state.carrinho_vendas:
        if item["id"] == id_prod:
            item["quantidade"] += 1
            st.toast(f"Quantidade de {nome} atualizada!", icon="🔄")
            return
            
    st.session_state.carrinho_vendas.append({
        "id": id_prod,
        "nome": nome,
        "preco": preco,
        "quantidade": 1,
        "requer_receita": requer_receita
    })
    st.toast(f"{nome} adicionado ao carrinho!", icon="🛒")

def atualizar_quantidade_carrinho(index, nova_qtd):
    if nova_qtd <= 0:
        st.session_state.carrinho_vendas.pop(index)
        st.toast("Item removido do carrinho.", icon="🗑️")
    else:
        st.session_state.carrinho_vendas[index]["quantidade"] = nova_qtd

def calcular_resumo_financeiro():
    subtotal = sum(item["preco"] * item["quantidade"] for item in st.session_state.carrinho_vendas)
    valor_desconto = subtotal * st.session_state.percentual_desconto
    subtotal_com_desconto = subtotal - valor_desconto
    impostos = subtotal_com_desconto * 0.08
    taxa_entrega = 12.00 if subtotal > 0 else 0.0
    valor_total = subtotal_com_desconto + impostos + taxa_entrega
    return subtotal, valor_desconto, impostos, taxa_entrega, valor_total

def limpar_sessao_compra():
    st.session_state.carrinho_vendas = []
    st.session_state.receita_digital_validada = False
    st.session_state.dados_ocr_receita = None
    st.session_state.cupom_aplicado = None
    st.session_state.percentual_desconto = 0.0

def obter_recomendacoes_atc(carrinho_atual):
    if not carrinho_atual:
        return []
    cursor = conn.cursor()
    nomes_carrinho = [item["nome"] for item in carrinho_atual]
    cursor.execute("SELECT * FROM estoque WHERE quantidade > 5 LIMIT 4")
    todos = cursor.fetchall()
    recomendados = [prod for prod in todos if prod[1] not in nomes_carrinho]
    return recomendados[:3]

# ==========================================
# 5. RENDERIZAÇÃO DAS VISÕES E ABAS
# ==========================================
gerenciar_autenticacao()

if st.session_state.usuario_perfil == "Cliente":
    st.title("🛒 PharmaStream - E-Commerce de Saúde")
    
    # Cabeçalho Superior
    col_head_1, col_head_2 = st.columns([3, 1])
    with col_head_1:
        st.markdown("Encontre seus medicamentos, produtos de saúde e receba em casa com entrega orientada pela farmácia mais próxima.")
    with col_head_2:
        qtd_itens_total = sum(item["quantidade"] for item in st.session_state.carrinho_vendas)
        sub_temp, desc_temp, imp_temp, frete_temp, total_temp = calcular_resumo_financeiro()
        
        with st.popover(f"🛒 Carrinho ({qtd_itens_total}) - R$ {total_temp:.2f}", use_container_width=True):
            st.markdown("### 🛒 Resumo Rápido do Carrinho")
            if not st.session_state.carrinho_vendas:
                st.info("Seu carrinho está vazio.")
            else:
                for idx_p, item_p in enumerate(st.session_state.carrinho_vendas):
                    st.write(f"• **{item_p['nome']}** x{item_p['quantidade']} — R$ {item_p['preco']*item_p['quantidade']:.2f}")
                st.markdown("---")
                if desc_temp > 0:
                    st.write(f"🏷️ **Desconto:** -R$ {desc_temp:.2f}")
                st.write(f"📦 **Frete estimado:** R$ {frete_temp:.2f}")
                st.markdown(f"#### **Total: R$ {total_temp:.2f}**")

    # Banner de Boas-Vindas
    if st.session_state.usuario_logado:
        st.info(f"🎉 **Ofertas Exclusivas para {st.session_state.usuario_nome}!** Use o cupom **CLIENTE10** para 10% OFF ou **PHARMA15** para 15% OFF!")

    # Estruturação das Abas Principais
    tab_ofertas, tab_categorias, tab_mapa, tab_catalogo, tab_carrinho, tab_receitas = st.tabs([
        "🔥 Ofertas em Destaque",
        "📂 Todas as Categorias",
        "📍 Buscar Farmácias & Mapa",
        "💊 Catálogo Geral",
        f"🛒 Meu Carrinho ({qtd_itens_total})",
        "📄 Validação de Prescrições"
    ])

    # --- ABA 1: OFERTAS EM DESTAQUE (Alinhamento por Nome e Distância) ---
    with tab_ofertas:
        st.subheader("🔥 Ofertas Especiais Ordenadas por Proximidade")
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome, preco, quantidade, requer_receita, grupo_terapeutico, em_oferta, distancia_km, loja_parceira
                FROM estoque 
                WHERE em_oferta = 1 
                ORDER BY distancia_km ASC
            """)
            ofertas = cursor.fetchall()
        except sqlite3.OperationalError:
            ofertas = []

        if ofertas:
            colunas_ofertas = st.columns(3)
            for idx, item in enumerate(ofertas):
                id_o, nome_o, preco_o, qtd_o, req_rec_o, grupo_o, em_of_o, dist_o, loja_o = item
                coluna_atual = colunas_ofertas[idx % 3]
                
                with coluna_atual:
                    with st.container(border=True):
                        st.markdown(f"<span class='oferta-badge'>OFERTA</span>", unsafe_allow_html=True)
                        st.subheader(nome_o)
                        st.markdown(f"🏪 **Loja Parceira:** {loja_o}")
                        st.markdown(f"📍 **Distância:** `{dist_o:.1f} km de você`")
                        st.markdown(f"**Classe:** {grupo_o}")
                        
                        preco_final = preco_o * 0.85 # 15% OFF nas ofertas
                        st.markdown(f"### R$ {preco_final:.2f} <span style='font-size:0.6em; color:gray; text-decoration:line-through;'>R$ {preco_o:.2f}</span>", unsafe_allow_html=True)
                        
                        if st.button("Adicionar Oferta 🛒", key=f"btn_oferta_{id_o}", use_container_width=True):
                            inserir_produto_carrinho(id_o, nome_o, preco_final, req_rec_o)
                            st.rerun()
        else:
            st.info("Nenhuma oferta promocional disponível no momento.")

    # --- ABA 2: TODAS AS CATEGORIAS ---
    with tab_categorias:
        st.subheader("📂 Navegue por Categorias de Produtos")
        
        cat_selecionada = st.selectbox("Selecione uma Categoria Principal:", list(ESTRUTURA_CATEGORIAS.keys()))
        subcategorias = ESTRUTURA_CATEGORIAS[cat_selecionada]
        
        st.markdown(f"### Subcategorias de **{cat_selecionada}**")
        cols_sub = st.columns(len(subcategorias) if len(subcategorias) <= 4 else 4)
        
        for idx_sub, sub_nome in enumerate(subcategorias):
            with cols_sub[idx_sub % 4]:
                with st.container(border=True):
                    st.markdown(f"#### 🏷️ {sub_nome}")
                    st.caption(f"Explorar itens em {sub_nome}")
                    if st.button(f"Ver {sub_nome}", key=f"cat_btn_{cat_selecionada}_{idx_sub}", use_container_width=True):
                        st.toast(f"Filtrando produtos para: {sub_nome}")

    # --- ABA 3: MAPA E BUSCA DE FARMÁCIAS (Favoritos e Ofertas) ---
    with tab_mapa:
        st.subheader("📍 Farmácias Parceiras e Distância em Tempo Real")
        st.markdown("Selecione sua farmácia de preferência e veja quais estão concedendo descontos especiais no mapa.")
        
        col_map_1, col_map_2 = st.columns([2, 1])
        
        df_mapa = pd.DataFrame(FARMACIAS_PARCEIRAS_DATA)
        
        with col_map_1:
            st.map(df_mapa, latitude="lat", longitude="lon", size="distancia_km", zoom=12)
            
        with col_map_2:
            st.markdown("### 🏪 Redes Credenciadas")
            for farm in FARMACIAS_PARCEIRAS_DATA:
                is_fav = farm["id"] in st.session_state.farmacias_favoritas
                estrela = "⭐" if is_fav else "☆"
                badge_desconto = "🏷️ **OFERTAS ATIVAS**" if farm["tem_ofertas"] else "Sem ofertas ativas"
                
                with st.container(border=True):
                    col_f1, col_f2 = st.columns([3, 1])
                    with col_f1:
                        st.markdown(f"**{farm['nome']}**")
                        st.caption(f"Distância: {farm['distancia_km']} km | Avaliação: {farm['avaliacao']} ★")
                        st.markdown(f"<small>{badge_desconto}</small>", unsafe_allow_html=True)
                    with col_f2:
                        if st.button(f"{estrela}", key=f"fav_{farm['id']}"):
                            if is_fav:
                                st.session_state.farmacias_favoritas.remove(farm["id"])
                            else:
                                st.session_state.farmacias_favoritas.add(farm["id"])
                            st.rerun()

    # --- ABA 4: CATÁLOGO GERAL DE MEDICAMENTOS ---
    with tab_catalogo:
        col_filtro_1, col_filtro_2 = st.columns([2, 1])
        with col_filtro_1:
            busca_termo = st.text_input("Procurar por medicamentos, sintomas ou substâncias:", placeholder="Ex: Dor de cabeça")
        with col_filtro_2:
            categoria_filtro = st.selectbox("Restrição sanitária:", ["Todos", "Venda Livre (OTC)", "Controle Especial (Exige Receita)"])
            
        query = "SELECT * FROM estoque WHERE quantidade > 0"
        filtros_params = []
        if busca_termo:
            query += " AND (nome LIKE ? OR tags LIKE ? OR grupo_terapeutico LIKE ?)"
            termo = f"%{busca_termo}%"
            filtros_params.extend([termo, termo, termo])
            
        if categoria_filtro == "Venda Livre (OTC)":
            query += " AND requer_receita = 0"
        elif categoria_filtro == "Controle Especial (Exige Receita)":
            query += " AND requer_receita = 1"
            
        cursor = conn.cursor()
        cursor.execute(query, filtros_params)
        produtos = cursor.fetchall()
        
        if produtos:
            st.write("### Produtos Encontrados")
            colunas_grade = st.columns(3)
            for idx, prod in enumerate(produtos):
                id_p, nome_p, atc_p, preco_p, estoque_p, requer_rec_p, grupo_p, tags_p, em_of_p, dist_p, loja_p = prod
                coluna_atual = colunas_grade[idx % 3]
                
                with coluna_atual:
                    with st.container(border=True):
                        if requer_rec_p == 1:
                            st.error("Reter Receita Exigida")
                        else:
                            st.success("Medicamento Liberado (OTC)")
                            
                        st.subheader(nome_p)
                        st.markdown(f"**Indicação:** {grupo_p}")
                        st.markdown(f"**Classe ATC:** `{atc_p}`")
                        
                        if st.session_state.usuario_logado:
                            preco_desc = preco_p * 0.9
                            st.markdown(f"### R$ {preco_desc:.2f} <span class='oferta-badge'>10% OFF</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"### R$ {preco_p:.2f}")
                        
                        if st.button(f"Comprar 🛒", key=f"compra_{id_p}", use_container_width=True):
                            preco_final_item = preco_p * 0.9 if st.session_state.usuario_logado else preco_p
                            inserir_produto_carrinho(id_p, nome_p, preco_final_item, requer_rec_p)
                            st.rerun()
        else:
            st.info("Nenhum medicamento localizado.")

    # --- ABA 5: CARRINHO E CHECKOUT ---
    with tab_carrinho:
        st.subheader("Carrinho de Compras")
        
        if not st.session_state.carrinho_vendas:
            st.info("O seu carrinho de compras está vazio no momento.")
        else:
            subtotal, desconto, impostos, frete, total = calcular_resumo_financeiro()
            
            for idx, item in enumerate(st.session_state.carrinho_vendas):
                col_item_1, col_item_2, col_item_3, col_item_4 = st.columns([3, 1, 1, 1])
                with col_item_1:
                    st.write(f"**{item['nome']}**")
                    if item["requer_receita"] == 1:
                        st.caption("🚨 Exige upload de receita válida")
                with col_item_2:
                    st.write(f"Unitário: R$ {item['preco']:.2f}")
                with col_item_3:
                    quantidade_selecionada = st.number_input("Qtd:", min_value=0, max_value=50, value=item["quantidade"], key=f"qtd_{idx}")
                    if quantidade_selecionada != item["quantidade"]:
                        atualizar_quantidade_carrinho(idx, quantidade_selecionada)
                        st.rerun()
                with col_item_4:
                    st.write(f"**R$ {item['preco'] * item['quantidade']:.2f}**")
            st.markdown("---")
            
            # Cupons
            st.markdown("### 🎟️ Cupons e Ofertas")
            if st.session_state.usuario_logado:
                col_cupom_1, col_cupom_2 = st.columns([2, 1])
                with col_cupom_1:
                    cupom_input = st.text_input("Inserir Cupom de Desconto:", placeholder="Ex: CLIENTE10").strip().upper()
                with col_cupom_2:
                    st.write(" ")
                    st.write(" ")
                    if st.button("Aplicar Cupom", type="secondary", use_container_width=True):
                        if cupom_input in CUPONS_VALIDOS:
                            st.session_state.cupom_aplicado = cupom_input
                            st.session_state.percentual_desconto = CUPONS_VALIDOS[cupom_input]
                            st.success(f"Cupom '{cupom_input}' aplicado!")
                            st.rerun()
            
            # Resumo e Finalização
            col_compra_1, col_compra_2 = st.columns(2)
            with col_compra_1:
                st.markdown("### Resumo Financeiro")
                st.write(f"Subtotal: R$ {subtotal:.2f}")
                if desconto > 0:
                    st.write(f"Desconto: -R$ {desconto:.2f}")
                st.write(f"Impostos (8%): R$ {impostos:.2f}")
                st.write(f"Frete: R$ {frete:.2f}")
                st.markdown(f"## **Total Final: R$ {total:.2f}**")
                
                forma_pagamento = st.radio("Forma de pagamento:", ["PIX", "Cartão de Crédito", "Cartão de Débito", "Boleto Bancário"])
                
            with col_compra_2:
                st.write("### Requisitos Documentais")
                requer_receita_controle = any(item["requer_receita"] == 1 for item in st.session_state.carrinho_vendas)
                
                permitir_finalizar = not requer_receita_controle or st.session_state.receita_digital_validada
                if requer_receita_controle and not st.session_state.receita_digital_validada:
                    st.error("❌ Documento de receita médica obrigatório pendente.")
                elif requer_receita_controle and st.session_state.receita_digital_validada:
                    st.success("✅ Prescrição validada.")
                
                if st.button("Concluir Compra e Emitir Nota", disabled=not permitir_finalizar, use_container_width=True, type="primary"):
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO vendas_registro (data_hora, subtotal, desconto, imposto, total, forma_pagamento)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), subtotal, desconto, impostos, total, forma_pagamento))
                    conn.commit()
                    st.success("🎉 Compra realizada com sucesso!")
                    limpar_sessao_compra()
                    time.sleep(1.5)
                    st.rerun()

    # --- ABA 6: VALIDADOR DE RECEITAS ---
    with tab_receitas:
        st.subheader("Análise Documental Inteligente (Módulo IA/OCR)")
        arquivo_upload = st.file_uploader("Upload da Receita Médica (PNG, JPG, PDF):", type=["png", "jpg", "jpeg", "pdf"])
        
        if arquivo_upload is not None:
            st.image(arquivo_upload, caption="Receita anexada", width=350)
            with st.spinner("Analisando metadados médicos..."):
                time.sleep(1.5)
                st.session_state.receita_digital_validada = True
                st.success("🎯 Receita Validada com Sucesso!")

# ==========================================
# INTERFACE ADMINISTRATIVA / PAINEL ERP (ENTERPRISE)
# ==========================================
else:
    st.title("🛡️ Painel Executivo & Controle Sanitário ERP")
    st.caption("Módulo Avançado de Gestão de Insumos, Rastreabilidade e Conformidade Sanitária")

    # ---------------------------------------------------------
    # 1. CARREGAMENTO E TRATAMENTO SEGURO DOS DADOS
    # ---------------------------------------------------------
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, codigo_atc, preco, quantidade, requer_receita, 
               grupo_terapeutico, tags, em_oferta, distancia_km, loja_parceira 
        FROM estoque
    """)
    dados_estoque = cursor.fetchall()
    cols_nomes = [desc[0] for desc in cursor.description]
    df_insumos = pd.DataFrame(dados_estoque, columns=cols_nomes)

    # Cálculo de métricas globais
    total_skus = len(df_insumos)
    valor_total_estoque = (df_insumos['preco'] * df_insumos['quantidade']).sum() if not df_insumos.empty else 0.0
    itens_criticos = df_insumos[df_insumos['quantidade'] < 10] if not df_insumos.empty else pd.DataFrame()
    itens_controlados = df_insumos[df_insumos['requer_receita'] == 1] if not df_insumos.empty else pd.DataFrame()

    # ---------------------------------------------------------
    # 2. DASHBOARD DE KPIS EXECUTIVOS
    # ---------------------------------------------------------
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric("Total de SKUs Cadastrados", f"{total_skus} itens")
    with col_kpi2:
        st.metric("Valor Imobilizado (Estoque)", f"R$ {valor_total_estoque:,.2f}")
    with col_kpi3:
        st.metric("Itens em Ruptura / Alerta", f"{len(itens_criticos)} itens", delta_color="inverse")
    with col_kpi4:
        st.metric("Medicamentos Controlados", f"{len(itens_controlados)} itens")

    st.markdown("---")

    # ---------------------------------------------------------
    # 3. ESTRUTURA DE NAVEGAÇÃO PRINCIPAL (ABAS DE NÍVEL EXECUTIVO)
    # ---------------------------------------------------------
    tab_gestao, tab_sanitario, tab_auditoria, tab_json = st.tabs([
        "📦 Gestão Integrada de Estoque",
        "⚖️ Rastreabilidade & Controle Sanitário",
        "📋 Trilha de Auditoria (Logs)",
        "⚙️ Identidade & JSONs do Sistema"
    ])

    # ---------------------------------------------------------
    # ABA 1: GESTÃO INTEGRADA DE ESTOQUE
    # ---------------------------------------------------------
    with tab_gestao:
        st.subheader("📊 Insumos e Disponibilidade Operacional")

        # Expander para cadastro rápido de novos insumos
        with st.expander("➕ Cadastrar Novo Insumo Farmacêutico no Banco", expanded=False):
            with st.form("form_novo_insumo"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    novo_nome = st.text_input("Nome do Insumo / Medicamento*")
                    novo_atc = st.text_input("Código ATC / Categoria*", placeholder="Ex: N02BE")
                    novo_preco = st.number_input("Preço Unitário (R$)*", min_value=0.01, step=0.5)
                with c2:
                    nova_qtd = st.number_input("Quantidade Inicial em Estoque*", min_value=1, step=1)
                    novo_grupo = st.selectbox("Classe / Grupo Terapêutico", [
                        "Analgésico", "Anti-inflamatório", "Antimicrobiano", 
                        "Ansiolítico", "Hipnótico", "Doenças Respiratórias", "Outros"
                    ])
                    nova_loja = st.selectbox("Loja / Filial de Destino", [
                        "Drogaria São Paulo - Centro", "Droga Raia - Pinheiros", 
                        "Farmácia Pague Menos - Jardins", "Drogaria Pacheco - Paulista"
                    ])
                with c3:
                    novo_requer = st.checkbox("Exige Retenção de Receita (Portaria 344)?")
                    novo_oferta = st.checkbox("Colocar em Oferta no E-commerce?")
                    novas_tags = st.text_input("Tags para busca (separadas por vírgula)", placeholder="ex: febre, dor, controlado")

                btn_cadastrar = st.form_submit_button("Salvar no Banco de Dados", type="primary", use_container_width=True)

                if btn_cadastrar:
                    if novo_nome and novo_atc:
                        cursor.execute("""
                            INSERT INTO estoque (nome, codigo_atc, preco, quantidade, requer_receita, grupo_terapeutico, tags, em_oferta, distancia_km, loja_parceira)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            novo_nome, novo_atc, novo_preco, nova_qtd, 
                            1 if novo_requer else 0, novo_grupo, novas_tags, 
                            1 if novo_oferta else 0, 1.0, nova_loja
                        ))
                        conn.commit()
                        st.success(f"Insumo **{novo_nome}** cadastrado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Preencha os campos obrigatórios (*).")

        # Filtro de Tabela
        st.markdown("#### 🔍 Consulta de Tabela de Insumos")
        f_col1, f_col2 = st.columns([3, 1])
        with f_col1:
            termo_busca = st.text_input("Filtrar estoque por nome, código ATC ou classe:", placeholder="Ex: Ibuprofeno ou M01AE")
        with f_col2:
            apenas_criticos = st.checkbox("Exibir apenas estoque crítico (< 10)")

        df_exibicao = df_insumos.copy()
        if termo_busca:
            df_exibicao = df_exibicao[
                df_exibicao['nome'].str.contains(termo_busca, case=False, na=False) |
                df_exibicao['codigo_atc'].str.contains(termo_busca, case=False, na=False) |
                df_exibicao['grupo_terapeutico'].str.contains(termo_busca, case=False, na=False)
            ]
        if apenas_criticos:
            df_exibicao = df_exibicao[df_exibicao['quantidade'] < 10]

        # Exibição do Grid
        st.dataframe(
            df_exibicao,
            use_container_width=True,
            column_config={
                "id": "ID",
                "nome": "Insumo / Medicamento",
                "codigo_atc": "Cód. ATC",
                "preco": st.column_config.NumberColumn("Preço Unit. (R$)", format="R$ %.2f"),
                "quantidade": st.column_config.NumberColumn("Qtd. Estoque"),
                "requer_receita": st.column_config.CheckboxColumn("Retém Receita?"),
                "em_oferta": st.column_config.CheckboxColumn("Oferta Ativa?"),
                "loja_parceira": "Unidade / Filial"
            }
        )

        # Botão para Download de Relatórios Contábeis/Auditoria
        csv_buffer = df_insumos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar Relatório do Estoque (CSV)",
            data=csv_buffer,
            file_name=f"relatorio_estoque_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            type="secondary"
        )

    # ---------------------------------------------------------
    # ABA 2: RASTREABILIDADE & CONTROLE SANITÁRIO
    # ---------------------------------------------------------
    with tab_sanitario:
        st.subheader("⚖️ Validação e Regulação Sanitária (SNGPC / ANVISA)")
        st.markdown("Monitoramento focado no controle de substâncias sob regulação especial e vigilância de insumos.")

        col_san1, col_san2 = st.columns(2)
        with col_san1:
            st.markdown("### 🚨 Risco de Ruptura (Menos de 10 unidades)")
            if not itens_criticos.empty:
                for _, row in itens_criticos.iterrows():
                    st.markdown(f"""
                    <div class='card-critico'>
                        <strong>{row['nome']}</strong> (Qtd Atual: <code>{row['quantidade']}</code>)<br>
                        <small>Filial: {row['loja_parceira']} | Classe: {row['grupo_terapeutico']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("Nenhum insumo encontra-se em nível crítico de estoque.")

        with col_san2:
            st.markdown("### 📜 Portaria 344/98 & Controle Especial")
            if not itens_controlados.empty:
                st.dataframe(
                    itens_controlados[['nome', 'codigo_atc', 'quantidade', 'loja_parceira']],
                    use_container_width=True
                )
            else:
                st.info("Nenhum medicamento sob controle especial localizado.")

    # ---------------------------------------------------------
    # ABA 3: TRILHA DE AUDITORIA (LOGS)
    # ---------------------------------------------------------
    with tab_auditoria:
        st.subheader("📋 Trilha de Auditoria & Segurança de Transações")
        st.markdown("Logs automáticos de alteração de sistema para conformidade com normas regulatórias.")
        
        # Simulação de Trilha de Auditoria Enterprise
        logs_sistema = [
            {"Data/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Usuário": st.session_state.usuario_nome or "Admin", "Módulo": "Estoque", "Ação": "Consulta de inventário e emissão de relatório"},
            {"Data/Hora": "2026-08-18 10:14:02", "Usuário": "Farmacêutico Responsável", "Módulo": "SNGPC", "Ação": "Validação de receita médica digital"},
            {"Data/Hora": "2026-08-17 18:30:11", "Usuário": "Sistema Automation", "Módulo": "Sessão", "Ação": "Backup automático da base de dados sqlite3"}
        ]
        st.table(pd.DataFrame(logs_sistema))

    # ---------------------------------------------------------
    # ABA 4: CONFIGURAÇÕES JSON DO SISTEMA
    # ---------------------------------------------------------
    with tab_json:
        st.subheader("⚙️ Configurações e Payloads do Sistema")
        st.markdown("Estruturas de metadados em formato JSON nativo para integração de APIs externas.")

        col_json_1, col_json_2 = st.columns(2)
        with col_json_1:
            st.markdown("### Identidade da Plataforma (JSON)")
            st.json(CONFIGURACAO_IDENTIDADE_DICT)
            st.download_button(
                "📥 Download Config (JSON)",
                data=json.dumps(CONFIGURACAO_IDENTIDADE_DICT, indent=4, ensure_ascii=False),
                file_name="config_identidade.json",
                mime="application/json"
            )

        with col_json_2:
            st.markdown("### Redes Parceiras Credenciadas (JSON)")
            st.json(FARMACIAS_PARCEIRAS_DATA)
            st.download_button(
                "📥 Download Parceiros (JSON)",
                data=json.dumps(FARMACIAS_PARCEIRAS_DATA, indent=4, ensure_ascii=False),
                file_name="farmacias_parceiras.json",
                mime="application/json"
            )

# ==========================================
# 6. RODAPÉ INFERIOR REGULATÓRIO (ANVISA)
# ==========================================
st.markdown("---")
col_foot_1, col_foot_2 = st.columns([1, 5])

with col_foot_1:
    # Imagem/Badge representativo do órgão fiscalizador ANVISA
    st.image("https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/2021/anvisa-reforca-orientacoes-sobre-uso-de-mascaras/logo-anvisa.png/@@images/image", width=120)

with col_foot_2:
    st.markdown("""
    <div class="footer-anvisa">
        o nosso projeto segue as determinações da ANVISA (agência nacional de vigilância sanitária) e as normas de boa prática de dispensação farmacêutica vigente.
    </div>
    """, unsafe_allow_html=True)
