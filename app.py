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
    page_title="PharmaStream Pro - E-Commerce & Gestão",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Personalizada com Cores Vívidas e Transições Suaves
st.markdown("""
<style>
    /* Cores Globais e Tipografia */
    :root {
        --cor-primaria: #00A859;
        --cor-secundaria: #005CA9;
        --cor-oferta: #FF3D00;
        --fundo-card: #FFFFFF;
    }

    /* Transições e Efeitos nos Botões */
    .stButton > button {
        transition: all 0.3s ease-in-out !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15) !important;
    }

    /* Badges de Tarjas Sanitárias */
    .tarja-preta {
        background-color: #1A1A1A;
        color: #FFFFFF;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 8px;
    }
    .tarja-vermelha {
        background-color: #D32F2F;
        color: #FFFFFF;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 8px;
    }
    .tarja-isento {
        background-color: #2E7D32;
        color: #FFFFFF;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 8px;
    }

    /* Cards de Oferta e Destaque */
    .card-produto {
        background: var(--fundo-card);
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 16px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card-produto:hover {
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }
    .tag-laboratorio {
        background-color: #E3F2FD;
        color: #0D47A1;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
    }
    .preco-antigo {
        color: #888888;
        text-decoration: line-through;
        font-size: 0.85rem;
    }
    .preco-destaque {
        color: #00A859;
        font-size: 1.4rem;
        font-weight: bold;
    }
    .badge-cpf {
        background-color: #FFF3E0;
        color: #E65100;
        border: 1px dashed #FB8C00;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    /* Rodapé ANVISA */
    .footer-anvisa {
        text-align: center;
        font-size: 0.78em;
        color: #555555;
        margin-top: 40px;
        padding: 15px;
        border-top: 1px solid #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BANCO DE DADOS E ESTRUTURA EXPANDIDA (COM AUTO-RESET DE ERRO)
# ==========================================
def iniciar_banco_dados():
    db_file = "farmacia_app.db"
    
    # Se o banco estiver travado/corrompido, tenta resetar o arquivo
    try:
        return _montar_estrutura_banco(db_file)
    except sqlite3.OperationalError:
        # Fecha e remove o arquivo corrompido do servidor
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
            except Exception:
                pass
        return _montar_estrutura_banco(db_file)

def _montar_estrutura_banco(db_file):
    conexao = sqlite3.connect(db_file, check_same_thread=False)
    cursor = conexao.cursor()
    
    # 1. Criação da Tabela Completa
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            principio_ativo TEXT DEFAULT '',
            laboratorio TEXT DEFAULT '',
            concentracao TEXT DEFAULT '',
            apresentacao TEXT DEFAULT '',
            quantidade_embalagem TEXT DEFAULT '',
            tarja TEXT DEFAULT 'MIP',
            codigo_atc TEXT NOT NULL,
            preco_de REAL NOT NULL,
            preco_por REAL NOT NULL,
            quantidade_estoque INTEGER NOT NULL,
            requer_receita INTEGER NOT NULL,
            grupo_terapeutico TEXT NOT NULL,
            em_oferta INTEGER DEFAULT 0,
            distancia_km REAL DEFAULT 0.0,
            loja_parceira TEXT DEFAULT 'Farmácia Central',
            imagem_url TEXT DEFAULT ''
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
            cpf_pbm TEXT,
            receita_retida_json TEXT
        )
    """)
    conexao.commit()
    
    # 2. Popula os dados se estiver vazio
    cursor.execute("SELECT COUNT(*) FROM estoque")
    if cursor.fetchone()[0] == 0:
        medicamentos_carga = [
            ("Ibuprofeno", "Ibuprofeno", "EMS", "600mg", "Comprimidos Revestidos", "Caixa com 20 comprimidos", "MIP", "M01AE", 24.90, 16.90, 45, 0, "Anti-inflamatório", 1, 0.8, "Drogaria São Paulo - Centro", "https://img.freepik.com/vetores-gratis/ilustracao-de-design-plano-de-caixa-de-remedio_23-2149363062.jpg"),
            ("Dipirona Monoidratada", "Dipirona Monoidratada", "Medley", "1g", "Comprimidos Desintegráveis", "Caixa com 10 comprimidos", "MIP", "N02BB", 14.50, 8.90, 120, 0, "Analgésico e Antitérmico", 1, 1.2, "Droga Raia - Pinheiros", "https://img.freepik.com/vetores-gratis/pacote-de-pílulas-e-frasco_24908-59265.jpg"),
            ("Diazepam", "Diazepam", "Eurofarma", "10mg", "Comprimidos", "Caixa com 30 comprimidos", "Preta", "N05B", 32.00, 26.50, 12, 1, "Ansiolítico", 0, 2.5, "Farmácia Pague Menos - Jardins", "https://img.freepik.com/vetores-gratis/frasco-de-remedio-com-pilulas_24877-52026.jpg"),
            ("Clonazepam", "Clonazepam", "Aché", "2mg", "Comprimidos Sublinguais", "Caixa com 30 comprimidos", "Preta", "N05B", 28.00, 19.90, 18, 1, "Ansiolítico", 1, 0.8, "Drogaria São Paulo - Centro", "https://img.freepik.com/vetores-gratis/ilustracao-de-design-plano-de-caixa-de-remedio_23-2149363062.jpg"),
            ("Cloridrato de Loratadina", "Loratadina", "Neo Química", "10mg", "Comprimidos", "Caixa com 12 comprimidos", "MIP", "R06", 18.00, 11.50, 50, 0, "Anti-histamínico", 1, 1.8, "Droga Raia - Pinheiros", "https://img.freepik.com/vetores-gratis/pacote-de-pílulas-e-frasco_24908-59265.jpg"),
            ("Sulfato de Salbutamol", "Salbutamol", "GlaxoSmithKline", "100mcg/dose", "Spray Aerossol", "Frasco com 200 doses", "Vermelha", "R03", 45.00, 34.90, 22, 0, "Broncodilatador", 0, 3.1, "Drogaria Pacheco - Paulista", "https://img.freepik.com/vetores-gratis/frasco-de-remedio-com-pilulas_24877-52026.jpg")
        ]
        cursor.executemany("""
            INSERT INTO estoque (nome, principio_ativo, laboratorio, concentracao, apresentacao, quantidade_embalagem, tarja, codigo_atc, preco_de, preco_por, quantidade_estoque, requer_receita, grupo_terapeutico, em_oferta, distancia_km, loja_parceira, imagem_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, medicamentos_carga)
        conexao.commit()
        
    return conexao

conn = iniciar_banco_dados()

# ==========================================
# 3. ESTADO DA SESSÃO
# ==========================================
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []
if "cpf_pbm" not in st.session_state:
    st.session_state.cpf_pbm = ""
if "desconto_pbm_ativo" not in st.session_state:
    st.session_state.desconto_pbm_ativo = False

# ==========================================
# 4. FUNÇÕES AUXILIARES
# ==========================================
def renderizar_badge_tarja(tarja):
    if tarja.lower() == "preta":
        return "<span class='tarja-preta'>⬛ TARJA PRETA - RETENÇÃO DE RECEITA</span>"
    elif tarja.lower() == "vermelha":
        return "<span class='tarja-vermelha'>🟥 TARJA VERMELHA - PRESCAIÇÃO MÉDICA</span>"
    else:
        return "<span class='tarja-isento'>🟩 ISENTO DE PRESCRIÇÃO (MIP)</span>"

def adicionar_ao_carrinho(prod_id, nome, preco, requer_receita):
    for item in st.session_state.carrinho:
        if item["id"] == prod_id:
            item["quantidade"] += 1
            st.toast(f"Unidade de {nome} adicionada!", icon="➕")
            return
    st.session_state.carrinho.append({"id": prod_id, "nome": nome, "preco": preco, "quantidade": 1, "requer_receita": requer_receita})
    st.toast(f"{nome} adicionado ao carrinho!", icon="🛒")

# ==========================================
# 5. INTERFACE DO USUÁRIO (FRONTEND)
# ==========================================
st.title("💊 PharmaStream Pro - E-Commerce")

# Painel Superior: PBM e Validador de CPF para Descontos
with st.expander("💳 Ativar Descontos do Seu Convênio / PBM por CPF", expanded=False):
    col_pbm_1, col_pbm_2 = st.columns([3, 1])
    with col_pbm_1:
        cpf_input = st.text_input("Digite seu CPF para consultar descontos de laboratório:", value=st.session_state.cpf_pbm, placeholder="000.000.000-00")
    with col_pbm_2:
        st.write(" ")
        st.write(" ")
        if st.button("Consultar PBM", type="primary", use_container_width=True):
            if len(cpf_input) >= 11:
                st.session_state.cpf_pbm = cpf_input
                st.session_state.desconto_pbm_ativo = True
                st.success("CPF Validado! Descontos de laboratório aplicados nos produtos elegíveis.")
            else:
                st.error("Insira um CPF válido.")

# Abas Principais da Aplicação
tab_ofertas, tab_catalogo, tab_carrinho = st.tabs([
    "🔥 Maiores Ofertas & Proximidade",
    "💊 Catálogo Completo com Apresentações",
    f"🛒 Meu Carrinho ({sum(i['quantidade'] for i in st.session_state.carrinho)})"
])

# --- ABA 1: MAIORES OFERTAS ---
with tab_ofertas:
    st.subheader("📍 Ofertas com Maiores Descontos perto de Você")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, principio_ativo, laboratorio, concentracao, apresentacao, quantidade_embalagem, tarja, preco_de, preco_por, em_oferta, distancia_km, loja_parceira, requer_receita, imagem_url
        FROM estoque
        WHERE em_oferta = 1
        ORDER BY distancia_km ASC, (preco_de - preco_por) DESC
    """)
    ofertas = cursor.fetchall()
    
    cols = st.columns(3)
    for idx, item in enumerate(ofertas):
        (p_id, p_nome, p_ativo, p_lab, p_conc, p_apres, p_qtd_emb, p_tarja, p_de, p_por, p_oferta, p_dist, p_loja, p_req_rec, p_img) = item
        
        # Cálculo de PBM extra se ativo
        preco_final = p_por * 0.90 if st.session_state.desconto_pbm_ativo else p_por
        
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(renderizar_badge_tarja(p_tarja), unsafe_allow_html=True)
                
                col_img, col_info = st.columns([1, 2])
                with col_img:
                    st.image(p_img, use_container_width=True)
                with col_info:
                    st.markdown(f"<span class='tag-laboratorio'>{p_lab}</span>", unsafe_allow_html=True)
                    st.markdown(f"### {p_nome}")
                    st.caption(f"**Princípio Ativo:** {p_ativo}")
                
                st.markdown(f"📏 **Concentração:** {p_conc}")
                st.markdown(f"📦 **Apresentação:** {p_apres} ({p_qtd_emb})")
                st.markdown(f"🏪 **Loja:** {p_loja} (`{p_dist:.1f} km`)")
                
                st.markdown(f"<span class='preco-antigo'>De: R$ {p_de:.2f}</span>", unsafe_allow_html=True)
                st.markdown(f"<span class='preco-destaque'>Por: R$ {preco_final:.2f}</span>", unsafe_allow_html=True)
                
                if st.session_state.desconto_pbm_ativo:
                    st.markdown("<span class='badge-cpf'>10% OFF PBM Aplicado</span>", unsafe_allow_html=True)
                    
                st.write("")
                if st.button("Adicionar ao Carrinho 🛒", key=f"of_{p_id}", use_container_width=True):
                    adicionar_ao_carrinho(p_id, f"{p_nome} {p_conc}", preco_final, p_req_rec)

# --- ABA 2: CATÁLOGO COMPLETO ---
with tab_catalogo:
    st.subheader("💊 Catálogo Estruturado de Medicamentos")
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, principio_ativo, laboratorio, concentracao, apresentacao, quantidade_embalagem, tarja, preco_de, preco_por, requer_receita, imagem_url FROM estoque")
    produtos = cursor.fetchall()
    
    for prod in produtos:
        (p_id, p_nome, p_ativo, p_lab, p_conc, p_apres, p_qtd_emb, p_tarja, p_de, p_por, p_req_rec, p_img) = prod
        
        preco_final = p_por * 0.90 if st.session_state.desconto_pbm_ativo else p_por
        
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1, 3, 2, 2])
            with c1:
                st.image(p_img, width=90)
            with c2:
                st.markdown(renderizar_badge_tarja(p_tarja), unsafe_allow_html=True)
                st.markdown(f"### {p_nome} {p_conc}")
                st.markdown(f"**Laboratório:** {p_lab} | **Ativo:** {p_ativo}")
                st.caption(f"Apresentação: {p_apres} - {p_qtd_emb}")
            with c3:
                st.markdown(f"<span class='preco-antigo'>De: R$ {p_de:.2f}</span>", unsafe_allow_html=True)
                st.markdown(f"<span class='preco-destaque'>R$ {preco_final:.2f}</span>", unsafe_allow_html=True)
                if st.session_state.desconto_pbm_ativo:
                    st.caption(" Desconto PBM Ativo")
            with c4:
                st.write(" ")
                if st.button("Comprar 🛒", key=f"cat_{p_id}", use_container_width=True):
                    adicionar_ao_carrinho(p_id, f"{p_nome} {p_conc}", preco_final, p_req_rec)

# --- ABA 3: CARRINHO ---
with tab_carrinho:
    st.subheader("🛒 Carrinho de Compras")
    if not st.session_state.carrinho:
        st.info("Seu carrinho está vazio.")
    else:
        total = 0.0
        for item in st.session_state.carrinho:
            subtotal = item["preco"] * item["quantidade"]
            total += subtotal
            st.write(f"• **{item['nome']}** — Qtd: {item['quantidade']} — R$ {subtotal:.2f}")
        
        st.markdown("---")
        st.markdown(f"### Total Final: **R$ {total:.2f}**")
        if st.button("Finalizar Pedido", type="primary"):
            st.success("Pedido enviado com sucesso!")
            st.session_state.carrinho = []

# ==========================================
# 6. RODAPÉ INFERIOR REGULATÓRIO (ANVISA)
# ==========================================
st.markdown("---")
col_foot_1, col_foot_2 = st.columns([1, 5])
with col_foot_1:
    st.image("https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/2021/anvisa-reforca-orientacoes-sobre-uso-de-mascaras/logo-anvisa.png/@@images/image", width=110)
with col_foot_2:
    st.markdown("""
    <div class="footer-anvisa">
        o nosso projeto segue as determinações da anvisa (agência nacional de vigilância sanitária) e as normas de boa prática de dispensação farmacêutica vigente.
    </div>
    """, unsafe_allow_html=True)
