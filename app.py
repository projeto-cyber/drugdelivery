import streamlit as st

# Configuração da página
st.set_page_config(page_title="DrugDelivery - Protótipo", layout="wide")

# Título do site
st.title("💊 DrugDelivery - Sistema de Gestão Farmacêutica")
st.write("Protótipo interativo para visualização de fluxos e pedidos.")

# Barra lateral para navegação
st.sidebar.header("Navegação")
opcao = st.sidebar.radio("Selecione a tela:", ["Dashboard", "Pedidos", "Estoque/Medicamentos"])

if opcao == "Dashboard":
    st.subheader("Visão Geral de Entregas")
    col1, col2, col3 = st.columns(3)
    col1.metric("Pedidos Hoje", "24", "+12%")
    col2.metric("Entregas Pendentes", "5", "-2")
    col3.metric("Tempo Médio", "18 min", "-3 min")

elif opcao == "Pedidos":
    st.subheader("Novo Pedido de Medicamento")
    nome_paciente = st.text_input("Nome do Paciente/Cliente")
    medicamento = st.selectbox("Medicamento", ["Amoxicilina 500mg", "Dipirona 1g", "Omeprazol 20mg"])
    quantidade = st.number_input("Quantidade", min_value=1, value=1)
    
    if st.button("Simular Envio do Pedido"):
        st.success(f"Pedido de {quantidade}x {medicamento} registrado para {nome_paciente}!")

elif opcao == "Estoque/Medicamentos":
    st.subheader("Consulta de Estoque da Farmácia")
    st.json({
        "Amoxicilina 500mg": {"estoque": 120, "retencao_receita": True},
        "Dipirona 1g": {"estoque": 450, "retencao_receita": False}
    })
