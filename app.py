import streamlit as st

# 1. Configuração da página para simular tela de celular
st.set_page_config(
    page_title="DrogaExpress - App Farmácia",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. CSS Customizado para deixar com cara de App Mobile
st.markdown("""
<style>
    /* Estilização geral estilo aplicativo */
    .stApp {
        background-color: #f5f7fa;
    }
    
    /* Header do App */
    .app-header {
        background-color: #0056b3;
        color: white;
        padding: 18px;
        border-radius: 0px 0px 20px 20px;
        margin-top: -60px;
        margin-bottom: 20px;
    }
    
    /* Card de Produto estilo Droga Raia */
    .product-card {
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
        border: 1px solid #e1e8ed;
    }
    
    .price-tag {
        color: #d93025;
        font-size: 20px;
        font-weight: bold;
    }

    .badge-receita {
        background-color: #fff3cd;
        color: #856404;
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 3. Cabeçalho no estilo App
st.markdown("""
<div class="app-header">
    <small>Olá, Farmacêutico 👋</small>
    <h3 style="margin:0; padding-top:4px;">Como podemos ajudar hoje?</h3>
</div>
""", unsafe_allow_html=True)

# 4. Campo de busca em destaque
busca = st.text_input("🔍 Buscar medicamentos, cosméticos...", placeholder="Ex: Dipirona, Dorflex, Protetor Solar")

# 5. Categorias Rápidas (Atalhos estilo app)
st.subheader("Categorias Rápidas")
cat_col1, cat_col2, cat_col3, cat_col4 = st.columns(4)

with cat_col1:
    st.button("💊\nMedicamentos", use_container_width=True)
with cat_col2:
    st.button("🩺\nReceita", use_container_width=True)
with cat_col3:
    st.button("🧴\nHigiene", use_container_width=True)
with cat_col4:
    st.button("⚡\nOfertas", use_container_width=True)

st.write("---")

# 6. Feed de Produtos em Destaque
st.subheader("Mais Vendidos")

# Lista simulada de banco de dados de medicamentos
produtos = [
    {
        "nome": "Amoxicilina 500mg - 21 Cáp.",
        "lab": "Medley Genérico",
        "preco": "R$ 28,90",
        "retencao": True
    },
    {
        "nome": "Dipirona Monoidratada 1g - 10 Comprimidos",
        "lab": "EMS Genéricos",
        "preco": "R$ 9,50",
        "retencao": False
    },
    {
        "nome": "Protetor Solar Facial FPS 60 50g",
        "lab": "Minesol Neostrata",
        "preco": "R$ 69,90",
        "retencao": False
    }
]

# Renderização dinâmica dos Cards dos Produtos
for prod in produtos:
    with st.container():
        st.markdown(f"""
        <div class="product-card">
            <h4>{prod['nome']}</h4>
            <p style="color: #6c757d; font-size: 13px; margin-bottom: 5px;">{prod['lab']}</p>
            {"<span class='badge-receita'>📄 Exige Retenção de Receita</span><br><br>" if prod['retencao'] else ""}
            <span class="price-tag">{prod['preco']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            st.button("Adicionar ao Carrinho 🛒", key=f"add_{prod['nome']}", use_container_width=True)
        with col_btn2:
            st.button("❤️", key=f"fav_{prod['nome']}", use_container_width=True)

# 7. Rodapé do App (Menu Inferior de Navegação)
st.write("---")
st.caption("📱 **Modo de Exibição Mobile Ativo**")
