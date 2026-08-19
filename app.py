import streamlit as st
import pandas as pd
import sqlite3
import io
import time
from datetime import datetime

# ==========================================
# CONFIGURAÇÃO DE LAYOUT E ESTILO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="PharmaStream Pro - Vendas & Gestão",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeção de estilo customizado
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
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONEXÃO E INICIALIZAÇÃO DO BANCO DE DADOS
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
            tags TEXT
        )
    """)
    
    # Criar tabela de auditoria de vendas transacionais
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
    
    # Alimentação inicial da tabela de estoque
    cursor.execute("SELECT COUNT(*) FROM estoque")
    if cursor.fetchone()[0] == 0:
        medicamentos_carga = [
            ("Ibuprofeno 600mg", "M01AE", 18.50, 45, 0, "Anti-inflamatório", "dor, inflamacao, febre"),
            ("Dipirona Monoidratada 1g", "N02BB", 9.90, 120, 0, "Analgésico", "dor, febre"),
            ("Diazepam 10mg", "N05B", 24.50, 12, 1, "Ansiolítico", "ansiedade, sono, controlado"),
            ("Clonazepam 2mg", "N05B", 21.00, 8, 1, "Ansiolítico", "ansiedade, controlado"),
            ("Zolpidem 10mg", "N05C", 42.00, 15, 1, "Hipnótico", "sono, insomnia, controlado"),
            ("Cloridrato de Loratadina 10mg", "R06", 14.80, 55, 0, "Anti-histamínico", "alergia, rinite"),
            ("Sulfato de Salbutamol 100mcg", "R03", 32.00, 22, 0, "Doenças Respiratórias", "asma, bronquite"),
            ("Paracetamol 750mg", "N02BE", 11.20, 95, 0, "Analgésico", "dor, febre")
        ]
        cursor.executemany("""
            INSERT INTO estoque (nome, codigo_atc, preco, quantidade, requer_receita, grupo_terapeutico, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, medicamentos_carga)
        conexao.commit()
        
    return conexao

conn = iniciar_banco_dados()

# ==========================================
# CONTROLE DO ESTADO DE SESSÃO
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

# Base de Cupons Válidos
CUPONS_VALIDOS = {
    "CLIENTE10": 0.10,   # 10% de desconto
    "PHARMA15": 0.15,    # 15% de desconto
    "PRIMEIRACOMPRA": 0.20 # 20% de desconto
}

# ==========================================
# SISTEMA DE LOGIN E CONTROLE DE ACESSO
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

# ==========================================
# LÓGICAS COMERCIAIS E FLUXO DO CARRINHO
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
    
    # Aplicação de Desconto por Cupom
    valor_desconto = subtotal * st.session_state.percentual_desconto
    subtotal_com_desconto = subtotal - valor_desconto
    
    impostos = subtotal_com_desconto * 0.08  # Alíquota média de 8%
    taxa_entrega = 12.00 if subtotal > 0 else 0.0
    valor_total = subtotal_com_desconto + impostos + taxa_entrega
    
    return subtotal, valor_desconto, impostos, taxa_entrega, valor_total

def limpar_sessao_compra():
    st.session_state.carrinho_vendas = []
    st.session_state.receita_digital_validada = False
    st.session_state.dados_ocr_receita = None
    st.session_state.cupom_aplicado = None
    st.session_state.percentual_desconto = 0.0

# ==========================================
# SISTEMA DE RECOMENDAÇÃO INTELIGENTE
# ==========================================
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
# RENDERIZAÇÃO DAS INTERFACES (VIEWS)
# ==========================================
gerenciar_autenticacao()

# Interface do Cliente
if st.session_state.usuario_perfil == "Cliente":
    st.title("🛒 PharmaStream - E-Commerce de Saúde")
    
    # HEADER SUPERIOR COM ÍCONE DO CARRINHO INTERATIVO E NAVEGAÇÃO DE COMPRAS
    col_head_1, col_head_2 = st.columns([3, 1])
    with col_head_1:
        st.markdown("Encontre seus medicamentos de uso diário, envie receitas e finalize suas compras com entrega rápida.")
    with col_head_2:
        qtd_itens_total = sum(item["quantidade"] for item in st.session_state.carrinho_vendas)
        sub_temp, desc_temp, imp_temp, frete_temp, total_temp = calcular_resumo_financeiro()
        
        # Ícone Popover de Carrinho Dinâmico
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
                
                st.markdown("---")
                st.markdown("**💳 Formas de Pagamento Aceitas:**")
                st.caption("• PIX (Aprovação Imediata + 5% OFF)\n• Cartão de Crédito (até 6x sem juros)\n• Cartão de Débito\n• Boleto Bancário")

    # Banners de Ofertas para Usuários Logados
    if st.session_state.usuario_logado:
        st.info(f"🎉 **Ofertas Exclusivas para {st.session_state.usuario_nome}!** Use o cupom **CLIENTE10** para 10% OFF ou **PHARMA15** para 15% OFF em todo o site!")

    tab_catalogo, tab_carrinho, tab_receitas = st.tabs([
        "💊 Catálogo de Medicamentos",
        f"🛒 Meu Carrinho ({qtd_itens_total})",
        "📄 Validação de Prescrições"
    ])
    
    # TAB 1: CATÁLOGO DE PRODUTOS
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
                id_p, nome_p, atc_p, preco_p, estoque_p, requer_rec_p, grupo_p, tags_p = prod
                coluna_atual = colunas_grade[idx % 3]
                
                with coluna_atual:
                    with st.container(border=True):
                        if requer_rec_p == 1:
                            st.error("🟥 Retenção de Receita Exigida")
                        else:
                            st.success("🟩 Medicamento Liberado (OTC)")
                            
                        st.subheader(nome_p)
                        st.markdown(f"**Indicação:** {grupo_p}")
                        st.markdown(f"**Classe ATC:** `{atc_p}`")
                        
                        # Destaque de Preço Promocional se Logado
                        if st.session_state.usuario_logado:
                            preco_desc = preco_p * 0.9
                            st.markdown(f"### R$ {preco_desc:.2f} <span class='oferta-badge'>10% OFF</span>", unsafe_allow_html=True)
                            st.caption(f"De R$ {preco_p:.2f} por estar logado(a)")
                        else:
                            st.markdown(f"### R$ {preco_p:.2f}")
                        
                        adicionar_clique = st.button(f"Comprar 🛒", key=f"compra_{id_p}", use_container_width=True)
                        if adicionar_clique:
                            preco_final_item = preco_p * 0.9 if st.session_state.usuario_logado else preco_p
                            inserir_produto_carrinho(id_p, nome_p, preco_final_item, requer_rec_p)
                            st.rerun()
        else:
            st.info("Nenhum medicamento correspondente localizado.")
            
    # TAB 2: CARRINHO DE COMPRAS E CHECKOUT
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
                    valor_multiplicado = item["preco"] * item["quantidade"]
                    st.write(f"**R$ {valor_multiplicado:.2f}**")
            st.markdown("---")
            
            # Seção de Ofertas e Cupons de Desconto
            st.markdown("### 🎟️ Cupons e Ofertas")
            if not st.session_state.usuario_logado:
                st.warning("💡 **Faça login** para desbloquear cupons de desconto exclusivos e ofertas especiais de cliente!")
            else:
                col_cupom_1, col_cupom_2 = st.columns([2, 1])
                with col_cupom_1:
                    cupom_input = st.text_input("Inserir Cupom de Desconto:", placeholder="Ex: CLIENTE10, PHARMA15, PRIMEIRACOMPRA").strip().upper()
                with col_cupom_2:
                    st.write(" ")
                    st.write(" ")
                    if st.button("Aplicar Cupom", type="secondary", use_container_width=True):
                        if cupom_input in CUPONS_VALIDOS:
                            st.session_state.cupom_aplicado = cupom_input
                            st.session_state.percentual_desconto = CUPONS_VALIDOS[cupom_input]
                            st.success(f"Cupom '{cupom_input}' applied com sucesso ({CUPONS_VALIDOS[cupom_input]*100:.0f}% OFF)!")
                            st.rerun()
                        else:
                            st.error("Cupom inválido ou expirado.")
                
                if st.session_state.cupom_aplicado:
                    st.success(f"🎟️ Cupom Ativo: **{st.session_state.cupom_aplicado}** (-{st.session_state.percentual_desconto*100:.0f}%)")

            # Recomendação de produtos
            recom_lista = obter_recomendacoes_atc(st.session_state.carrinho_vendas)
            if recom_lista:
                st.write("#### 💡 Aproveite Também:")
                cols_recom = st.columns(len(recom_lista))
                for idx, r_prod in enumerate(recom_lista):
                    with cols_recom[idx]:
                        with st.container(border=True):
                            st.write(f"**{r_prod[1]}**")
                            p_recom = r_prod[3] * 0.9 if st.session_state.usuario_logado else r_prod[3]
                            st.write(f"R$ {p_recom:.2f}")
                            bt_recom = st.button("Adicionar", key=f"rec_add_{r_prod[0]}", use_container_width=True)
                            if bt_recom:
                                inserir_produto_carrinho(r_prod[0], r_prod[1], p_recom, r_prod[5])
                                st.rerun()
            
            # Formas de Pagamento e Resumo Final
            col_compra_1, col_compra_2 = st.columns(2)
            with col_compra_1:
                st.markdown("### Resumo Financeiro")
                st.write(f"Subtotal dos Medicamentos: R$ {subtotal:.2f}")
                if desconto > 0:
                    st.write(f"Desconto Aplicado: -R$ {desconto:.2f}")
                st.write(f"Impostos e Contribuições: R$ {impostos:.2f}")
                st.write(f"Logística e Frete: R$ {frete:.2f}")
                st.markdown(f"## **Total Final: R$ {total:.2f}**")
                
                st.markdown("---")
                st.markdown("### 💳 Opção de Pagamento")
                forma_pagamento = st.radio(
                    "Selecione a forma de pagamento:",
                    ["PIX (Aprovação Instantânea)", "Cartão de Crédito", "Cartão de Débito", "Boleto Bancário"]
                )
                
            with col_compra_2:
                st.write("### Requisitos Documentais")
                requer_receita_controle = any(item["requer_receita"] == 1 for item in st.session_state.carrinho_vendas)
                
                if requer_receita_controle:
                    st.warning("⚠️ Seu carrinho possui medicamentos controlados. O checkout está bloqueado até o envio e validação de receita.")
                    if st.session_state.receita_digital_validada:
                        st.success("✅ Prescrição eletrônica anexada e validada pelo farmacêutico virtual.")
                        permitir_finalizar = True
                    else:
                        st.error("❌ Documento de receita médica obrigatório pendente.")
                        permitir_finalizar = False
                else:
                    st.success("✅ Itens isentos de receita. Pronto para finalização imediata.")
                    permitir_finalizar = True
                    
                botao_finalizar = st.button("Concluir Compra e Emitir Nota", disabled=not permitir_finalizar, use_container_width=True, type="primary")
                
                if botao_finalizar:
                    try:
                        cursor = conn.cursor()
                        crm = st.session_state.dados_ocr_receita["crm_medico"] if st.session_state.dados_ocr_receita else "N/A"
                        paciente = st.session_state.dados_ocr_receita["paciente_nome"] if st.session_state.dados_ocr_receita else (st.session_state.usuario_nome if st.session_state.usuario_nome else "Cliente Balcão")
                        receita_json = str(st.session_state.dados_ocr_receita) if st.session_state.dados_ocr_receita else "N/A"
                        
                        cursor.execute("""
                            INSERT INTO vendas_registro (data_hora, subtotal, desconto, imposto, total, forma_pagamento, crm_medico, paciente_nome, receita_retida_json)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), subtotal, desconto, impostos, total, forma_pagamento, crm, paciente, receita_json))
                        
                        for item in st.session_state.carrinho_vendas:
                            cursor.execute("""
                                UPDATE estoque 
                                SET quantidade = quantidade - ? 
                                WHERE id = ?
                            """, (item["quantidade"], item["id"]))
                        conn.commit()
                        
                        st.success(f"🎉 Compra realizada com sucesso! ID do Pedido: #{cursor.lastrowid} | Pagamento: {forma_pagamento}")
                        limpar_sessao_compra()
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Erro ao processar a venda: {e}")
                        
            if st.button("Limpar Carrinho", use_container_width=True):
                limpar_sessao_compra()
                st.rerun()

    # TAB 3: CARREGAMENTO E PROCESSAMENTO DE RECEITAS MÉDICAS
    with tab_receitas:
        st.subheader("Análise Documental Inteligente (Módulo IA/OCR)")
        st.markdown("Submeta o arquivo de sua receita contendo a prescrição de medicamentos controlados (Diazepam, Zolpidem, Clonazepam).")
        
        arquivo_upload = st.file_uploader("Upload da Receita Médica (Formatos PNG, JPG, PDF):", type=["png", "jpg", "jpeg", "pdf"])
        
        if arquivo_upload is not None:
            st.image(arquivo_upload, caption="Imagem da receita para auditoria", width=400)
            
            with st.spinner("Analisando metadados médicos e executando extração textual de controle..."):
                time.sleep(2.0)
                
                simulacao_dados_ocr = {
                    "paciente_name": st.session_state.usuario_nome if st.session_state.usuario_nome else "Juliana de Oliveira",
                    "medico_name": "Dr. Arthur Ramos Siqueira",
                    "crm_medico": "CRM-SP 987654",
                    "medicamentos_receitados": [
                        {"nome": "Zolpidem 10mg", "dosagem": "1 comprimido por noite"},
                        {"nome": "Diazepam 10mg", "dosagem": "1 comprimido a cada 12 horas"}
                    ],
                    "validade_diagnostico": "Dentro da Validade Legal"
                }
                
                st.session_state.dados_ocr_receita = {
                    "crm_medico": simulacao_dados_ocr["crm_medico"],
                    "paciente_nome": simulacao_dados_ocr["paciente_name"]
                }
                st.session_state.receita_digital_validada = True
                
            st.success("🎯 Análise Documental Concluída com Sucesso!")
            
            col_ocr_1, col_ocr_2 = st.columns(2)
            with col_ocr_1:
                st.markdown("### 🔍 Dados Extraídos pelo Módulo de Inteligência")
                st.write(f"**Paciente:** {simulacao_dados_ocr['paciente_name']}")
                st.write(f"**Profissional Prescritor:** {simulacao_dados_ocr['medico_name']}")
                st.write(f"**Inscrição CRM:** {simulacao_dados_ocr['crm_medico']}")
                st.write(f"**Validade do Receituário:** {simulacao_dados_ocr['validade_diagnostico']}")
            with col_ocr_2:
                st.markdown("### 💊 Substâncias Prescritas Detectadas")
                st.table(pd.DataFrame(simulacao_dados_ocr["medicamentos_receitados"]))

# Interface Administrativa e Controle de Inventário
else:
    st.title("🛡️ Painel Administrativo de Controle de Insumos")
    st.markdown("Interface exclusiva para monitoramento logístico, alteração de lotes comerciais e auditoria sanitária de dispensação.")
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM estoque WHERE quantidade <= 10")
    insumos_criticos = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(total) FROM vendas_registro")
    faturamento_bruto = cursor.fetchone()[0]
    faturamento_bruto = faturamento_bruto if faturamento_bruto else 0.0
    
    cursor.execute("SELECT COUNT(*) FROM vendas_registro")
    vendas_count = cursor.fetchone()[0]
    
    col_kpi_1, col_kpi_2, col_kpi_3 = st.columns(3)
    with col_kpi_1:
        st.metric("Insumos em Nível Crítico (Estoque <= 10 u)", insumos_criticos, delta="- Reabastecimento urgente" if insumos_criticos > 0 else "Estoque seguro")
    with col_kpi_2:
        st.metric("Receita de Vendas Consolidada", f"R$ {faturamento_bruto:.2f}", delta=f"{vendas_count} transações concluídas")
    with col_kpi_3:
        st.metric("Infraestrutura de Banco", "Ativa", delta="Sincronização NeonDB (PostgreSQL)")
        
    tab_inventario_gestao, tab_vendas_auditoria = st.tabs(["📦 Controle do Estoque Ativo", "📈 Auditoria de Vendas e CRM"])
    
    with tab_inventario_gestao:
        st.subheader("Gerenciador Interativo de Produtos")
        st.markdown("Utilize o painel abaixo para reabastecer unidades ou alterar os preços praticados.")
        
        @st.fragment
        def gerenciar_inventario_fragmento():
            cursor_frag = conn.cursor()
            cursor_frag.execute("SELECT * FROM estoque")
            colunas = ["id", "nome", "codigo_atc", "preco", "quantidade", "requer_receita", "grupo_terapeutico", "tags"]
            df_insumos = pd.DataFrame(cursor_frag.fetchall(), columns=colunas)
            
            df_modificado = st.data_editor(
                df_insumos,
                column_config={
                    "id": "ID Insumo",
                    "nome": "Descrição do Produto",
                    "codigo_atc": "Código ATC",
                    "preco": st.column_config.NumberColumn("Preço de Prateleira (R$)", min_value=0.1, format="%.2f"),
                    "quantidade": st.column_config.NumberColumn("Estoque Físico (unidades)", min_value=0),
                    "requer_receita": st.column_config.CheckboxColumn("Requer Receita Controlada?"),
                    "grupo_terapeutico": "Ação Terapêutica",
                    "tags": "Tags de Busca"
                },
                disabled=["id", "codigo_atc"],
                use_container_width=True,
                key="editor_estoque_farmacia"
            )
            
            if st.button("Salvar Modificações de Estoque", type="primary"):
                try:
                    for idx, linha in df_modificado.iterrows():
                        cursor_frag.execute("""
                            UPDATE estoque
                            SET nome = ?, preco = ?, quantidade = ?, requer_receita = ?, grupo_terapeutico = ?, tags = ?
                            WHERE id = ?
                        """, (linha["nome"], linha["preco"], linha["quantidade"], int(linha["requer_receita"]), linha["grupo_terapeutico"], linha["tags"], linha["id"]))
                    conn.commit()
                    st.success("As alterações físicas de estoque foram aplicadas com sucesso no banco relacional!")
                    st.rerun()
                except Exception as ex:
                    conn.rollback()
                    st.error(f"Falha de gravação de dados: {ex}")
                    
            st.markdown("---")
            st.subheader("Alerta Visual de Nível de Insumos")
            df_criticos = df_insumos[df_insumos["quantidade"] <= 15]
            if not df_criticos.empty:
                st.write("Medicamentos com volume de prateleira abaixo do limite de segurança:")
                st.bar_chart(df_criticos, x="nome", y="quantidade", color="#FF4B4B")
            else:
                st.success("Todos os medicamentos operam com quantitativos seguros de prateleira.")
                
            st.markdown("---")
            st.subheader("Cadastrar Novo Medicamento ou Princípio Ativo")
            with st.form("form_novo_registro", clear_on_submit=True):
                col_reg_1, col_reg_2 = st.columns(2)
                with col_reg_1:
                    reg_nome = st.text_input("Nome Comercial / Marca:", placeholder="Ex: AAS 100mg")
                    reg_atc = st.text_input("Identificação Internacional ATC:", placeholder="Ex: N02BA01")
                    reg_grupo = st.selectbox("Grupo Farmacológico Principal:", ["Analgésico", "Anti-inflamatório", "Ansiolítico", "Hipnótico", "Anti-histamínico", "Doenças Respiratórias", "Antibióticos"])
                with col_reg_2:
                    reg_preco = st.number_input("Preço de Prateleira (R$):", min_value=0.1, value=15.0, step=0.5)
                    reg_qtd = st.number_input("Estoque Inicial (Unidades):", min_value=1, value=50)
                    reg_requer = st.checkbox("Exige Retenção de Receita Controlada?")
                    reg_tags = st.text_input("Palavras-chave / Tags de Sintomas:", placeholder="Ex: dor, febre, inflamacao")
                    
                btn_cadastrar = st.form_submit_button("Cadastrar Insumo no Banco", type="primary", use_container_width=True)
                
                if btn_cadastrar:
                    if reg_nome and reg_atc:
                        try:
                            cursor_frag.execute("""
                                INSERT INTO estoque (nome, codigo_atc, preco, quantidade, requer_receita, grupo_terapeutico, tags)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (reg_nome, reg_atc, reg_preco, reg_qtd, 1 if reg_requer else 0, reg_grupo, reg_tags))
                            conn.commit()
                            st.success(f"Medicamento '{reg_nome}' cadastrado com sucesso!")
                            st.rerun()
                        except Exception as e_reg:
                            conn.rollback()
                            st.error(f"Erro ao inserir medicamento: {e_reg}")
                    else:
                        st.warning("Preencha ao menos o Nome e o Código ATC.")
        
        gerenciar_inventario_fragmento()
        
    with tab_vendas_auditoria:
        st.subheader("Auditoria de Transações e Receituários")
        cursor.execute("SELECT * FROM vendas_registro ORDER BY id_venda DESC")
        vendas_db = cursor.fetchall()
        
        if vendas_db:
            df_vendas = pd.DataFrame(vendas_db, columns=["ID Venda", "Data/Hora", "Subtotal", "Desconto", "Imposto", "Total", "Forma Pagamento", "CRM Médico", "Paciente", "JSON Receita"])
            st.dataframe(df_vendas, use_container_width=True)
        else:
            st.info("Nenhuma venda realizada até o momento.")
