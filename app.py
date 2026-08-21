import base64
from datetime import datetime
import json
import os
import sqlite3
import time
import pandas as pd
import streamlit as st


# Cria duas colunas de tamanhos iguais
col1, col2 = st.columns(2)

with col1:
    st.header("Coluna 1")
    st.write
    st.markdown((
    """
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
        <img src="https://cdn-icons-png.flaticon.com/512/883/883407.png" width="30" height="30" alt="Blister">
        <h4 style="margin: 0;">Medicamentos e Blisters</h4>
    </div>
    """,
    unsafe_allow_html=True,
))

with col2:
    st.header("Coluna 2")
    st.write
    st.markdown((
    """
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
        <img src="https://cdn-icons-png.flaticon.com/512/1077/1077035.png" width="30" height="30" alt="Fachada">
        <h4 style="margin: 0;">Nossas Lojas e Farmácias </h4>
    </div>
    """,
    unsafe_allow_html=True,
))

# ==========================================
# 1. CONFIGURAÇÃO ÚNICA DE LAYOUT (DEVE SER A PRIMEIRA)
# ==========================================
st.set_page_config(
    page_title="PharmaStream Pro - Vendas & Gestão",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos Customizados CSS
st.markdown(
    """
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
    .oferta-badge {
        background-color: #FF9800;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
    }
    .badge-loja {
        background-color: #007bff;
        color: white;
        padding: 2px 6px;
        border-radius: 8px;
        font-size: 0.75em;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. IDENTIDADE VISUAL E CONFIGURAÇÃO JSON
# ==========================================
CONFIGURACAO_IDENTIDADE_JSON = {
    "aplicacao": {
        "nome": "PharmaStream Pro",
        "versao": "2.4.0",
        "segmento": "E-Commerce & Gestão Farmacêutica",
        "conformidade_regulatoria": (
            "ANVISA - Agência Nacional de Vigilância Sanitária"
        ),
    },
    "identidade_visual": {
        "cor_primaria": "#1E3A8A",
        "cor_secundaria": "#09AB3B",
        "cor_alerta": "#FF4B4B",
        "cor_destaque": "#FF9800",
        "logo_anvisa_url": (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Anvisa_logo.svg/320px-Anvisa_logo.svg.png"
        ),
    },
    "farmacias_parceiras": [
        {
            "id": 1,
            "nome": "PharmaStream Centro",
            "lat": -15.7942,
            "lon": -47.8822,
            "distancia_km": 0.8,
            "oferta_ativa": True,
            "estrelinha": True,
        },
        {
            "id": 2,
            "nome": "PharmaStream Asa Sul",
            "lat": -15.8102,
            "lon": -47.8995,
            "distancia_km": 2.4,
            "oferta_ativa": True,
            "estrelinha": False,
        },
        {
            "id": 3,
            "nome": "PharmaStream Lago Sul",
            "lat": -15.8320,
            "lon": -47.8710,
            "distancia_km": 4.1,
            "oferta_ativa": False,
            "estrelinha": False,
        },
        {
            "id": 4,
            "nome": "PharmaStream Taguatinga",
            "lat": -15.8340,
            "lon": -48.0560,
            "distancia_km": 8.5,
            "oferta_ativa": True,
            "estrelinha": True,
        },
    ],
    "categorias_catalogo": {
        "Saúde": [
            "Teste Rápido",
            "Saúde Bucal",
            "Produtos de Beleza",
            "Dispositivos Médicos",
            "Fraldas",
        ],
        "Medicamentos": [
            "Medicamentos Controlados",
            "Hormônios",
            "Antimicrobianos",
            "Fitoterápicos",
            "Medicamentos Isentos de Prescrição",
        ],
        "Vitaminas e Suplementos": ["Multivitamínicos", "Vitaminas", "Minerais"],
        "Mamãe & Bebê": [
            "Fraldas",
            "Amamentação",
            "Saúde da Mãe",
            "Saúde do Bebê",
        ],
        "Beleza": [
            "Cuidado com a Pele",
            "Maquiagem",
            "Perfumaria",
            "Tratamento Capilar",
            "Produtos Asiáticos",
        ],
        "Cuidados Diários": [
            "Higiene Pessoal",
            "Depilação",
            "Repelente",
            "Cuidado Masculino",
            "Cuidado Feminino",
            "Cuidado com a Pele",
            "Cuidado com os Pés",
        ],
        "Pet": ["Medicamentos Pet", "Vida Saudável Pet"],
        "Marcas Parceiras": ["Marca A", "Marca B", "Marca C"],
    },
}

# ==========================================
# 3. BANCO DE DADOS AUTOMÁTICO (SQLITE)
# ==========================================


@st.cache_resource
def iniciar_banco_dados():
    conexao = sqlite3.connect("farmacia_app.db", check_same_thread=False)
    cursor = conexao.cursor()

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
            loja_parceira TEXT DEFAULT 'PharmaStream Centro',
            distancia_km REAL DEFAULT 0.8,
            em_oferta INTEGER DEFAULT 0
        )
    """)

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

    cursor.execute("SELECT COUNT(*) FROM estoque")
    if cursor.fetchone()[0] == 0:
        medicamentos_carga = [
            (
                "Ibuprofeno 600mg",
                "M01AE",
                18.50,
                45,
                0,
                "Anti-inflamatório",
                "dor, inflamacao, febre",
                "PharmaStream Centro",
                0.8,
                1,
            ),
            (
                "Dipirona Monoidratada 1g",
                "N02BB",
                9.90,
                120,
                0,
                "Analgésico",
                "dor, febre",
                "PharmaStream Asa Sul",
                2.4,
                1,
            ),
            (
                "Diazepam 10mg",
                "N05B",
                24.50,
                12,
                1,
                "Ansiolítico",
                "ansiedade, sono, controlado",
                "PharmaStream Centro",
                0.8,
                0,
            ),
            (
                "Clonazepam 2mg",
                "N05B",
                21.00,
                8,
                1,
                "Ansiolítico",
                "ansiedade, controlado",
                "PharmaStream Taguatinga",
                8.5,
                1,
            ),
            (
                "Zolpidem 10mg",
                "N05C",
                42.00,
                15,
                1,
                "Hipnótico",
                "sono, insomnia, controlado",
                "PharmaStream Asa Sul",
                2.4,
                0,
            ),
            (
                "Cloridrato de Loratadina 10mg",
                "R06",
                14.80,
                55,
                0,
                "Anti-histamínico",
                "alergia, rinite",
                "PharmaStream Lago Sul",
                4.1,
                0,
            ),
            (
                "Sulfato de Salbutamol 100mcg",
                "R03",
                32.00,
                22,
                0,
                "Doenças Respiratórias",
                "asma, bronquite",
                "PharmaStream Centro",
                0.8,
                1,
            ),
            (
                "Paracetamol 750mg",
                "N02BE",
                11.20,
                95,
                0,
                "Analgésico",
                "dor, febre",
                "PharmaStream Taguatinga",
                8.5,
                1,
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO estoque (nome, codigo_atc, preco, quantidade, requer_receita, grupo_terapeutico, tags, loja_parceira, distancia_km, em_oferta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            medicamentos_carga,
        )
        conexao.commit()

    return conexao


conn = iniciar_banco_dados()

# ==========================================
# 4. SESSÃO E AUTENTICAÇÃO
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
if "farmacias_favoritas" not in st.session_state:
    st.session_state.farmacias_favoritas = [1, 4]


def gerenciar_autenticacao():
    st.sidebar.subheader("🔒 Autenticação & Perfil")
    perfil = st.sidebar.selectbox(
        "Perfil operacional:",
        ["Cliente", "Administrador / Farmacêutico"],
        key="perfil_selectbox",
    )
    st.session_state.usuario_perfil = perfil

    st.sidebar.markdown("---")
    if not st.session_state.usuario_logado:
        st.sidebar.subheader("🔑 Login do Cliente")
        with st.sidebar.form("form_login_sidebar"):
            user_input = st.text_input("Usuário / E-mail")
            pass_input = st.text_input("Senha", type="password")
            btn_login = st.form_submit_button(
                "Entrar", type="primary", use_container_width=True
            )

            if btn_login:
                if user_input and pass_input:
                    st.session_state.usuario_logado = True
                    st.session_state.usuario_nome = user_input.split("@")[
                        0
                    ].capitalize()
                    st.sidebar.success(
                        f"Bem-vindo(a), {st.session_state.usuario_nome}!"
                    )
                    st.rerun()
                else:
                    st.sidebar.error("Informe usuário e senha.")
    else:
        st.sidebar.success(
            f"👤 Conectado como: **{st.session_state.usuario_nome}**"
        )
        if st.sidebar.button("Sair / Logout", use_container_width=True):
            st.session_state.usuario_logado = False
            st.session_state.usuario_nome = ""
            st.session_state.cupom_aplicado = None
            st.session_state.percentual_desconto = 0.0
            st.rerun()


# ==========================================
# 5. LÓGICAS COMERCIAIS
# ==========================================
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
        "requer_receita": requer_receita,
    })
    st.toast(f"{nome} adicionado ao carrinho!", icon="🛒")


def calcular_resumo_financeiro():
    subtotal = sum(
        item["preco"] * item["quantidade"]
        for item in st.session_state.carrinho_vendas
    )
    valor_desconto = subtotal * st.session_state.percentual_desconto
    subtotal_com_desconto = subtotal - valor_desconto
    impostos = subtotal_com_desconto * 0.08
    taxa_entrega = 12.00 if subtotal > 0 else 0.0
    valor_total = subtotal_com_desconto + impostos + taxa_entrega
    return subtotal, valor_desconto, impostos, taxa_entrega, valor_total


# ==========================================
# 6. RENDERIZAÇÃO DA INTERFACE PRINCIPAL
# ==========================================
gerenciar_autenticacao()

if st.session_state.usuario_perfil == "Cliente":
    st.title("🛒 PharmaStream - E-Commerce de Saúde")

    # Header e Resumo Rápido
    col_head_1, col_head_2 = st.columns([3, 1])
    with col_head_1:
        st.markdown(
            "Encontre seus medicamentos de uso diário, envie receitas e compre"
            " nas lojas parceiras mais próximas."
        )
    with col_head_2:
        qtd_itens_total = sum(
            item["quantidade"] for item in st.session_state.carrinho_vendas
        )
        sub_temp, desc_temp, imp_temp, frete_temp, total_temp = (
            calcular_resumo_financeiro()
        )

        with st.popover(
            f"🛒 Carrinho ({qtd_itens_total}) - R$ {total_temp:.2f}",
            use_container_width=True,
        ):
            st.markdown("### 🛒 Resumo Rápido do Carrinho")
            if not st.session_state.carrinho_vendas:
                st.info("Seu carrinho está vazio.")
            else:
                for item_p in st.session_state.carrinho_vendas:
                    st.write(
                        f"• **{item_p['nome']}** x{item_p['quantidade']} — R$"
                        f" {item_p['preco']*item_p['quantidade']:.2f}"
                    )
                st.markdown("---")
                if desc_temp > 0:
                    st.write(f"🏷️ **Desconto:** -R$ {desc_temp:.2f}")
                st.write(f"📦 **Frete estimado:** R$ {frete_temp:.2f}")
                st.markdown(f"#### **Total: R$ {total_temp:.2f}**")

    if st.session_state.usuario_logado:
        st.info(
            f"🎉 **Ofertas Exclusivas para {st.session_state.usuario_nome}!** Use"
            " o cupom **CLIENTE10** para 10% OFF!"
        )

    # Ofertas
    st.markdown("### 🔥 Ofertas Especiais por Lojas Parceiras Próximas")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM estoque WHERE em_oferta = 1 ORDER BY distancia_km ASC"
        " LIMIT 4"
    )
    ofertas_destaque = cursor.fetchall()

    if ofertas_destaque:
        cols_ofertas = st.columns(len(ofertas_destaque))
        for idx_of, of_item in enumerate(ofertas_destaque):
            (
                id_of,
                nome_of,
                atc_of,
                preco_of,
                est_of,
                req_of,
                grupo_of,
                tags_of,
                loja_of,
                dist_of,
                em_of,
            ) = of_item
            with cols_ofertas[idx_of]:
                with st.container(border=True):
                    st.markdown(
                        f"<span class='badge-loja'>📍 {loja_of} ({dist_of}"
                        " km)</span>",
                        unsafe_allow_html=True,
                    )
                    st.subheader(nome_of)
                    preco_promo = preco_of * 0.85
                    st.markdown(
                        f"**R$ {preco_promo:.2f}** <span"
                        " class='oferta-badge'>15% OFF</span>",
                        unsafe_allow_html=True,
                    )
                    st.caption(f"De R$ {preco_of:.2f}")
                    if st.button(
                        "Aproveitar 🛒",
                        key=f"btn_of_{id_of}",
                        use_container_width=True,
                    ):
                        inserir_produto_carrinho(
                            id_of, nome_of, preco_promo, req_of
                        )
                        st.rerun()

    st.markdown("---")

    # Abas
    (
        tab_catalogo,
        tab_categorias,
        tab_farmacias,
        tab_carrinho,
        tab_receitas,
        tab_json,
    ) = st.tabs([
        "💊 Catálogo Geral",
        "🏷️ Categorias",
        "📍 Buscar Farmácias",
        f"🛒 Meu Carrinho ({qtd_itens_total})",
        "📄 Validação de Prescrições",
        "⚙️ Identidade & JSON",
    ])

    with tab_catalogo:
        col_filtro_1, col_filtro_2 = st.columns([2, 1])
        with col_filtro_1:
            busca_termo = st.text_input(
                "Procurar por medicamentos, sintomas ou substâncias:",
                placeholder="Ex: Dor de cabeça",
            )
        with col_filtro_2:
            categoria_filtro = st.selectbox(
                "Restrição sanitária:",
                [
                    "Todos",
                    "Venda Livre (OTC)",
                    "Controle Especial (Exige Receita)",
                ],
            )

        query = "SELECT * FROM estoque WHERE quantidade > 0"
        filtros_params = []
        if busca_termo:
            query += (
                " AND (nome LIKE ? OR tags LIKE ? OR grupo_terapeutico LIKE ?)"
            )
            termo = f"%{busca_termo}%"
            filtros_params.extend([termo, termo, termo])

        if categoria_filtro == "Venda Livre (OTC)":
            query += " AND requer_receita = 0"
        elif categoria_filtro == "Controle Especial (Exige Receita)":
            query += " AND requer_receita = 1"

        cursor.execute(query, filtros_params)
        produtos = cursor.fetchall()

        if produtos:
            colunas_grade = st.columns(3)
            for idx, prod in enumerate(produtos):
                (
                    id_p,
                    nome_p,
                    atc_p,
                    preco_p,
                    estoque_p,
                    requer_rec_p,
                    grupo_p,
                    tags_p,
                    loja_p,
                    dist_p,
                    em_of_p,
                ) = prod
                with colunas_grade[idx % 3]:
                    with st.container(border=True):
                        st.caption(
                            f"📍 Disponível em: **{loja_p}** ({dist_p} km)"
                        )
                        if requer_rec_p == 1:
                            st.error("Reter Receita")
                        else:
                            st.success("Venda Livre")
                        st.subheader(nome_p)
                        st.markdown(f"### R$ {preco_p:.2f}")
                        if st.button(
                            "Comprar 🛒",
                            key=f"compra_{id_p}",
                            use_container_width=True,
                        ):
                            inserir_produto_carrinho(
                                id_p, nome_p, preco_p, requer_rec_p
                            )
                            st.rerun()

    with tab_categorias:
        st.subheader("🏷️ Navegação por Categorias de Produtos")
        cats_json = CONFIGURACAO_IDENTIDADE_JSON["categorias_catalogo"]
        cols_cat = st.columns(2)
        idx_c = 0
        for nome_categoria, subcategorias in cats_json.items():
            with cols_cat[idx_c % 2]:
                with st.container(border=True):
                    st.markdown(f"#### 📂 {nome_categoria}")
                    for sub in subcategorias:
                        st.markdown(f"• **{sub}**")
            idx_c += 1

    with tab_farmacias:
        st.subheader("📍 Encontre a Farmácia Parceira Mais Próxima")
        farmacias = CONFIGURACAO_IDENTIDADE_JSON["farmacias_parceiras"]
        df_farmacias = pd.DataFrame(farmacias)
        st.map(df_farmacias, latitude="lat", longitude="lon", zoom=11)

        st.markdown("### 🏬 Lista de Farmácias e Preferências")
        for f in farmacias:
            col_f1, col_f2, col_f3, col_f4 = st.columns([3, 2, 2, 1])
            with col_f1:
                st.write(f"**{f['nome']}**")
            with col_f2:
                st.write(f"📏 Distância: **{f['distancia_km']} km**")
            with col_f3:
                if f["oferta_ativa"]:
                    st.markdown(
                        "🔥 <span class='oferta-badge'>Ofertas"
                        " Ativas!</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.caption("Preços Padrão")
            with col_f4:
                is_fav = f["id"] in st.session_state.farmacias_favoritas
                star_icon = "⭐" if is_fav else "☆"
                if st.button(star_icon, key=f"fav_{f['id']}"):
                    if is_fav:
                        st.session_state.farmacias_favoritas.remove(f["id"])
                    else:
                        st.session_state.farmacias_favoritas.append(f["id"])
                    st.rerun()

    with tab_carrinho:
        st.subheader("Carrinho de Compras")
        if st.session_state.carrinho_vendas:
            subtotal, desconto, impostos, frete, total = (
                calcular_resumo_financeiro()
            )
            df_carrinho = pd.DataFrame(st.session_state.carrinho_vendas)
            st.dataframe(
                df_carrinho[["nome", "preco", "quantidade"]],
                use_container_width=True,
            )
            st.markdown(f"## **Total Final: R$ {total:.2f}**")
        else:
            st.info("O carrinho está vazio.")

    with tab_receitas:
        st.subheader("Análise Documental Inteligente")
        st.file_uploader(
            "Upload da Receita Médica:", type=["png", "jpg", "pdf"]
        )

    with tab_json:
        st.subheader("⚙️ Configurações & Arquitetura JSON do Projeto")
        st.json(CONFIGURACAO_IDENTIDADE_JSON)

# ==========================================
# 7. RODAPÉ INFERIOR REGULATÓRIO (ANVISA)
# ==========================================
st.divider()


def carregar_imagem_base64(caminho_imagem):
    """Lê uma imagem local e a converte para uma string Base64."""
    if os.path.exists(caminho_imagem):
        with open(caminho_imagem, "rb") as file:
            encoded = base64.b64encode(file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return None


def renderizar_rodape_anvisa(caminho_logo):
    logo_base64 = carregar_imagem_base64(caminho_logo)
    src_imagem = (
        logo_base64
        if logo_base64
        else CONFIGURACAO_IDENTIDADE_JSON["identidade_visual"]["logo_anvisa_url"]
    )

    footer_html = f"""
    <style>
        .anvisa-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            padding: 20px 0;
            margin-top: 30px;
            border-top: 1px solid #dcdcdc;
        }}
        .anvisa-logo {{
            width: 85px;
            height: auto;
            object-fit: contain;
            opacity: 0.85;
            transition: opacity 0.3s;
        }}
        .anvisa-logo:hover {{
            opacity: 1;
        }}
        .anvisa-info p {{
            margin: 0;
            font-size: 11px;
            color: #666;
            line-height: 1.4;
        }}
        .anvisa-info .legal {{
            font-size: 10px;
            color: #999;
        }}
    </style>

    <div class="anvisa-container">
        <a href="https://www.gov.br/anvisa/pt-br" target="_blank" rel="noopener noreferrer">
            <img src="{src_imagem}" class="anvisa-logo" alt="Selo ANVISA">
        </a>
        <div class="anvisa-info">
            <p><strong>Conformidade Regulatória:</strong> Adequado à Resolução RDC nº 44/2009 e RDC nº 727/2022 (ANVISA).</p>
            <p class="legal">
                Razão Social: PharmaStream Pro Intermediação de Negócios Ltda | CNPJ: 00.000.000/0001-00<br>
                Farmacêutico Responsável: Dr. Nome Exemplo - CRF-DF nº 00000 | Licença Sanitária nº 1234/2026
            </p>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)


# Renderiza o rodapé com busca de imagem local na pasta 'assets/anvisa.png' ou URL remota como fallback
renderizar_rodape_anvisa("assets/anvisa.png")
