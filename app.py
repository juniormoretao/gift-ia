import streamlit as st
import google.generativeai as genai
import json
import time
import random
import ast


st.set_page_config(
    page_title="Giftly",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    /* 1. CONFIGURAÇÕES GERAIS */
    .stApp {
        background: linear-gradient(to right, #f8f9fa, #e9ecef);
        color: #333333; /* Força cor da fonte escura */
    }
    
    /* 2. CABEÇALHO LIMPO */
    header[data-testid="stHeader"] { background-color: transparent; z-index: 1; }
    div[data-testid="stDecoration"] { visibility: hidden; height: 0px; }
    .block-container { padding-top: 2rem; padding-bottom: 1rem; }

    /* 3. BOTÕES PRINCIPAIS (Laranja/Vermelho) */
    .stButton>button { 
        background: linear-gradient(45deg, #FF4B4B, #FF914D); 
        color: white; 
        border-radius: 20px; 
        height: 45px; 
        font-weight: bold; 
        border: none; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
    }
    .stButton>button:hover { 
        transform: scale(1.02); 
        box-shadow: 0 6px 12px rgba(255, 75, 75, 0.3); 
        color: white;
    }
    
    /* 4. BOTÃO SAIR (CORRIGIDO PARA NÃO SUMIR) */
    div[data-testid="stVerticalBlockBorderWrapper"] .botao-sair-container button {
        background-color: #ffffff !important; /* Fundo BRANCO para destacar do cinza */
        color: #555 !important; 
        border: 1px solid #ddd !important;
        height: 32px !important; 
        font-size: 13px !important; 
        border-radius: 8px !important; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important; /* Sombra leve */
    }
    div[data-testid="stVerticalBlockBorderWrapper"] .botao-sair-container button:hover {
        background-color: #fff0f0 !important; /* Fundo rosado leve ao passar o mouse */
        color: #FF4B4B !important;
        border-color: #FF4B4B !important;
    }

    /* 5. CARDS E PREÇO */
    div[data-testid="stExpander"] { background-color: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: none; }
    .preco-destaque {
        color: #198754; font-weight: 800; font-size: 1.2rem;
        background-color: #e8f5e9; padding: 5px 10px; border-radius: 8px;
        display: inline-block; margin-top: 5px; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuario_nome' not in st.session_state: st.session_state.usuario_nome = ""
if 'historico' not in st.session_state: st.session_state.historico = []
if 'txt_interesses' not in st.session_state: st.session_state.txt_interesses = ""

# --- SEGURANÇA ---
try:
    MINHA_API_KEY = st.secrets["MINHA_API_KEY"]
except FileNotFoundError:
    st.error("⚠️ Chave de API não encontrada.")
    st.stop()


def gerar_interesses_aleatorios():
    perfis = [
        "Gosta de café gourmet, ler livros de suspense e gatos.",
        "Ama tecnologia, setups de computador, luzes RGB e jogos online.",
        "É fitness, faz crossfit, come saudável e gosta de trilhas.",
        "Gosta de vinhos, queijos, jazz e viagens para a Europa.",
        "Fã de Harry Potter, coleciona funkos e gosta de jogos de tabuleiro."
    ]
    st.session_state.txt_interesses = random.choice(perfis)


def tela_login():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center;">
                <img src="https://cdn-icons-png.flaticon.com/512/4213/4213650.png" width="80" style="margin-bottom: 10px;">
                <h1 style="color: #333; margin: 0;">Bem-vindo ao Giftly</h1>
                <p style="color: #666;">Seu assistente pessoal de presentes</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        nome = st.text_input("Como você gostaria de ser chamado?", placeholder="Seu nome...")
        if st.button("🚀 Entrar", use_container_width=True):
            if nome:
                st.session_state.logado = True
                st.session_state.usuario_nome = nome
                st.rerun()


def app_principal():
    # --- HEADER ---
    col_header_esq, col_header_dir = st.columns([1, 1])
    
    with col_header_esq:
        st.markdown("""
            <div style="display: flex; align-items: center;">
                <img src="https://cdn-icons-png.flaticon.com/512/4213/4213650.png" width="50" style="margin-right: 15px;">
                <h1 style="color: #FF4B4B; margin: 0; padding: 0; font-family: Helvetica, sans-serif; font-size: 2.5rem; line-height: 1;">Giftly</h1>
            </div>
        """, unsafe_allow_html=True)
        
    with col_header_dir:
        c_vazio, c_ola, c_sair = st.columns([4, 3, 2])
        with c_ola:
            st.markdown(f"<div style='text-align: right; padding-top: 8px; color: #555; font-weight: 500;'>Olá, <b>{st.session_state.usuario_nome}</b>!</div>", unsafe_allow_html=True)
        with c_sair:
            with st.container():
                st.markdown('<div class="botao-sair-container">', unsafe_allow_html=True)
                if st.button("Sair ➝", key="btn_sair", use_container_width=True):
                    st.session_state.logado = False
                    st.session_state.historico = []
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Configuração")
        quem = st.text_input("👤 Quem vai ganhar?", placeholder="Ex: Namorada...")
        idade = st.number_input("🎂 Idade:", 0, 120, 25)
        ocasiao = st.selectbox("📅 Ocasião:", ["Aniversário", "Natal", "Dia dos Namorados", "Amigo Secreto", "Outro"])
        orcamento = st.number_input("💰 Máximo (R$):", min_value=0.0, step=50.0, value=200.0)
        
        st.markdown("---")
        if len(st.session_state.historico) > 0:
            st.markdown("### 🕒 Histórico")
            for item in reversed(st.session_state.historico):
                with st.expander(f"{item['quem']} ({item['data']})"):
                    for sug in item['sugestoes']:
                        st.write(f"• {sug['nome']}")

    # --- INPUTS ---
    st.subheader("Do que essa pessoa gosta?")
    c_input, c_btn = st.columns([5, 1])
    with c_btn:
        st.write("")
        st.write("")
        st.button("🎲 Ideia?", on_click=gerar_interesses_aleatorios, use_container_width=True)
    with c_input:
        interesses = st.text_area("", height=80, key="txt_interesses", placeholder="Ex: Gosta de rock, cozinhar e tecnologia...")

    
    if st.button("✨ BUSCAR PRESENTES", use_container_width=True):
        if not interesses or not quem:
            st.warning("⚠️ Preencha os interesses e quem é a pessoa.")
        else:
            sugestoes = None
            try:
                with st.spinner("🤖 A IA está pesquisando..."):
                    genai.configure(api_key=MINHA_API_KEY)
                    model = genai.GenerativeModel('gemini-2.5-flash')

                    prompt = f"""
                    Aja como personal shopper. Sugira 3 presentes para: {quem}, {idade} anos.
                    Ocasião: {ocasiao}. Orçamento Máximo: R$ {orcamento}.
                    Interesses: {interesses}.
                    OUTPUT JSON OBRIGATÓRIO:
                    [ {{ "nome": "Produto", "descricao": "Explicação curta", "preco_estimado": "Valor Numérico", "emoji": "🎁", "termo_busca": "Termo" }} ]
                    """
                    response = model.generate_content(prompt)
                    
                    texto = response.text
                    inicio, fim = texto.find('['), texto.rfind(']') + 1
                    if inicio != -1 and fim != -1:
                        limpo = texto[inicio:fim]
                        try: sugestoes = json.loads(limpo)
                        except: sugestoes = ast.literal_eval(limpo)
            
            except Exception as e:
                st.error(f"Erro: {e}")

            if sugestoes:
                st.session_state.historico.append({"quem": quem, "sugestoes": sugestoes, "data": time.strftime("%H:%M")})
                st.success(f"Opções para {quem}:")
                cols = st.columns(3)
                
                for i, item in enumerate(sugestoes):
                    if i < 3:
                        with cols[i]:
                            with st.container(border=True):
                                st.markdown(f"#### {item['emoji']} {item['nome']}")
                                st.caption(item['descricao'])
                                
                                preco_texto = str(item['preco_estimado'])
                                if "R$" not in preco_texto and "r$" not in preco_texto:
                                    preco_final = f"R$ {preco_texto}"
                                else:
                                    preco_final = preco_texto

                                st.markdown(f"<div class='preco-destaque'>{preco_final}</div>", unsafe_allow_html=True)
                                
                                termo = item['termo_busca'].replace(" ", "+")
                                c_amz, c_shp = st.columns(2)
                                c_amz.link_button("📦 Amazon", f"https://www.amazon.com.br/s?k={termo}", use_container_width=True)
                                c_shp.link_button("🛍️ Shopee", f"https://shopee.com.br/search?keyword={termo}", use_container_width=True)

# --- ROTEADOR ---
if st.session_state.logado:
    app_principal()
else:
    tela_login()