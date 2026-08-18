import streamlit as st

# ==========================================
# 1. CONFIGURAÇÃO DA TELA (FRONTEND MOBILE)
# ==========================================
st.set_page_config(
    page_title="PharmaExpress - Mobile View",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização CSS para simular o design de apps como Drogasil/Raia
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    
    /* Topo do App */
    .mobile-header {
        background: linear-gradient(135deg, #004b87, #0066b2);
        color: white;
        padding: 20px;
        border-radius: 0 0 24px 24px;
        margin: -60px -20px 20px -20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Cards de Produtos */
    .product-card {
        background: white;
        padding: 16px;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 12px;
        border: 1px solid #edf2f7;
    }
    
    .badge-prescricao {
        background-color: #fff3cd;
        color: #856404;
        font-size: 10px;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. BACKEND / LÓGICA DE DADOS (API SIMULADA)
# ==========================================
class PharmaBackendAPI:
    """Simula o backend que futuramente será feito em FastAPI ou Node.js"""
    
    @staticmethod
    def get_catalog():
        return [
            {"id": 1, "nome": "Amoxicilina 500mg 21 Cáp.", "lab": "Medley", "preco": 28.90, "requer_receita": True},
            {"id": 2, "nome": "Dipirona Sódica 500mg/ml", "lab": "Neo Química", "preco": 8.50, "requer_receita": False},
            {"id": 3, "nome": "Vitamina D3 2000UI 30 Cáp.", "lab": "Cimed", "preco": 42.00, "requer_receita": False},
            {"id": 4, "nome": "Losartana Potássica 50mg", "lab": "EMS", "preco": 14.90, "requer_receita": True}
        ]

    @staticmethod
    def process_order(cart_items, patient_name, has_prescription):
        if not patient_name:
            return False, "Informe o nome do paciente."
        
        # Validação de negócio farmacêutico
        for item in cart_items:
            if item['requer_receita'] and not has_prescription:
                return False, f"O item '{item['nome']}' exige envio obrigatório de receita médica (RDC 344/98)."
                
        return True, "Pedido integrado com sucesso ao sistema da farmácia!"


# Inicializa o estado da sessão do carrinho (Sessão do Usuário)
if 'cart' not in st.session_state:
    st.session_state.cart = []


# ==========================================
# 3. INTERFACE VISUAL DO APLICATIVO (FRONTEND)
# ==========================================

# Cabeçalho Visual
st.markdown("""
<div class="mobile-header">
    <p style="margin:0; font-size:13px; opacity:0.8;">FarmaExpress Digital</p>
    <h2 style="margin:0; font-weight:600;">Olá, Farmacêutico 🩺</h2>
</div>
""", unsafe_allow_html=True)

# Abas de Navegação Inferior/Superior simulando App Mobile
tab_vitrine, tab_carrinho, tab_validacao = st.tabs(["💊 Vitrine", "🛒 Carrinho", "📋 Validação de Receita"])

catalog = PharmaBackendAPI.get_catalog()

with tab_vitrine:
    st.subheader("Medicamentos em Destaque")
    busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Dipirona, Amoxicilina...")
    
    for product in catalog:
        if busca.lower() in product['nome'].lower():
            with st.container():
                st.markdown(f"""
                <div class="product-card">
                    <b style="font-size:16px;">{product['nome']}</b><br>
                    <span style="color: #718096; font-size:12px;">Laboratório: {product['lab']}</span><br>
                    {'<span class="badge-prescricao">📄 Exige Receita</span><br>' if product['requer_receita'] else '<br>'}
                    <span style="color: #e53e3e; font-size:18px; font-weight:bold;">R$ {product['preco']:.2f}</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Adicionar ao Carrinho", key=f"btn_{product['id']}"):
                    st.session_state.cart.append(product)
                    st.success(f"Adicionado: {product['nome']}")

with tab_carrinho:
    st.subheader("Seu Carrinho de Compras")
    if not st.session_state.cart:
        st.info("O carrinho está vazio.")
    else:
        total = 0
        for idx, item in enumerate(st.session_state.cart):
            st.write(f"- {item['nome']} (**R$ {item['preco']:.2f}**)")
            total += item['preco']
        
        st.divider( )
        st.markdown(f"### Total: R$ {total:.2f}")
        
        if st.button("Limpar Carrinho"):
            st.session_state.cart = []
            st.rerun()

with tab_validacao:
    st.subheader("Checkout e Validação Farmacêutica")
    patient_name = st.text_input("Nome Completo do Paciente")
    has_prescription = st.checkbox("Possui Receita Médica Válida?")
    
    # Campo de upload de imagem para simular o envio da receita médica
    uploaded_file = st.file_uploader("Enviar Foto da Receita (PDF ou Imagem)", type=["png", "jpg", "jpeg", "pdf"])
    
    if st.button("Finalizar Pedido", type="primary"):
        # Chamada ao "Backend" validando as regras de negócio
        success, message = PharmaBackendAPI.process_order(
            st.session_state.cart, 
            patient_name, 
            has_prescription or (uploaded_file is not None)
        )
        
        if success:
            st.success(message)
            st.balloons()
            st.session_state.cart = [] # Limpa o carrinho após finalizar
        else:
            st.error(message)
