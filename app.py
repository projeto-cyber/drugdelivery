import os
import sqlite3
import pandas as pd
import streamlit as st
import requests

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Drug Delivery System",
    page_icon="💊",
    layout="wide"
)

# ==========================================
# 2. CONEXÃO E INICIALIZAÇÃO DO BANCO (SQLITE)
# ==========================================
# Conexão com o banco de dados local
conn = sqlite3.connect('drugdelivery.db', check_same_thread=False)
cursor = conn.cursor()

def inicializar_banco():
    """Garante que a tabela e todas as colunas necessárias existam."""
    # Criação base da tabela
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT DEFAULT 'Geral',
        preco REAL NOT NULL,
        qtd INTEGER DEFAULT 0,
        em_oferta INTEGER DEFAULT 0,
        distancia_km REAL DEFAULT 0.0
    )
    """)
    conn.commit()

    # Verificação de colunas existentes (Migração defensiva)
    cursor.execute("PRAGMA table_info(estoque)")
    colunas_existentes = [coluna[1] for coluna in cursor.fetchall()]

    if 'em_oferta' not in colunas_existentes:
        cursor.execute("ALTER TABLE estoque ADD COLUMN em_oferta INTEGER DEFAULT 0")
        conn.commit()

    if 'distancia_km' not in colunas_existentes:
        cursor.execute("ALTER TABLE estoque ADD COLUMN distancia_km REAL DEFAULT 0.0")
        conn.commit()

    if 'categoria' not in colunas_existentes:
        cursor.execute("ALTER TABLE estoque ADD COLUMN categoria TEXT DEFAULT 'Geral'")
        conn.commit()

# Executa a validação do schema do banco de dados
inicializar_banco()

# ==========================================
# 3. CAMADA DE SERVIÇOS E INTEGRAÇÃO DE APIS
# ==========================================
BASE_URL = os.getenv("EXTERNAL_API_URL", "https://api.exemplo.com")

@st.cache_data(ttl=300)
def buscar_dados_externos():
    """Exemplo de integração com API de terceiros ou dados auxiliares."""
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        return {"status": "offline"}
    return {"status": "offline"}

# ==========================================
# 4. INTERFACE DO USUÁRIO & NAVEGAÇÃO
# ==========================================
st.title("💊 Sistema de Gestão & Drug Delivery")

# Barra Lateral (Sidebar)
st.sidebar.header("Navegação e Filtros")
menu = st.sidebar.radio("Selecione a opção:", ["Dashboard / Ofertas", "Cadastrar Item", "Ver Estoque Completo"])

# ==========================================
# 5. LÓGICA DAS TELAS
# ==========================================

# --- ABA 1: DASHBOARD DE OFERTAS (ONDE OCORRIA O ERRO DA LINHA 299) ---
if menu == "Dashboard / Ofertas":
    st.subheader("🔥 Ofertas em Destaque e Proximidade")
    
    # Bloco protegido para consulta SQL (Evita sqlite3.OperationalError)
    try:
        cursor.execute("""
            SELECT id, nome, preco, qtd, em_oferta, distancia_km 
            FROM estoque 
            WHERE em_oferta = 1 
            ORDER BY distancia_km ASC 
            LIMIT 4
        """)
        ofertas = cursor.fetchall()
    except sqlite3.OperationalError as e:
        st.error(f"Erro ao acessar a tabela de estoque: {e}")
        ofertas = []

    if ofertas:
        cols = st.columns(len(ofertas) if len(ofertas) <= 4 else 4)
        for idx, item in enumerate(ofertas):
            item_id, nome, preco, qtd, em_oferta, distancia_km = item
            with cols[idx % 4]:
                st.metric(label=f"🏷️ {nome}", value=f"R$ {preco:.2f}", delta=f"{distancia_km:.1f} km")
                st.caption(f"Em estoque: {qtd} un.")
                if st.button(f"Comprar {nome}", key=f"btn_{item_id}"):
                    st.success(f"{nome} adicionado ao carrinho!")
    else:
        st.info("Nenhuma oferta cadastrada no momento ou banco de dados em inicialização.")

# --- ABA 2: CADASTRO DE PRODUTOS ---
elif menu == "Cadastrar Item":
    st.subheader("➕ Cadastrar Novo Medicamento / Produto")
    
    with st.form("form_cadastro"):
        nome = st.text_input("Nome do Produto")
        preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
        qtd = st.number_input("Quantidade em Estoque", min_value=0, step=1)
        em_oferta = st.checkbox("Colocar em Oferta?")
        distancia = st.number_input("Distância de Entrega (km)", min_value=0.0, format="%.1f")
        
        btn_salvar = st.form_submit_button("Salvar Produto")
        
        if btn_salvar:
            if nome:
                oferta_val = 1 if em_oferta else 0
                cursor.execute("""
                    INSERT INTO estoque (nome, preco, qtd, em_oferta, distancia_km)
                    VALUES (?, ?, ?, ?, ?)
                """, (nome, preco, qtd, oferta_val, distancia))
                conn.commit()
                st.success(f"Produto '{nome}' cadastrado com sucesso!")
            else:
                st.warning("Por favor, informe o nome do produto.")

# --- ABA 3: VISUALIZAÇÃO TOTAL ---
elif menu == "Ver Estoque Completo":
    st.subheader("📦 Estoque Cadastrado")
    
    df = pd.read_sql_query("SELECT * FROM estoque", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.write("Nenhum item localizado no banco de dados.")
