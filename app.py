import streamlit as st
import google.generativeai as genai
import json
import time
import random

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Giftly - Presentes com IA",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO CSS (CORRIGIDA) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(to right, #f8f9fa, #e9ecef); }
    
    /* Título Giftly - Correção para não quebrar linha */
    h1 { 
        color: #FF4B4B; 
        text-align: center; 
        font-family: 'Helvetica', sans-serif; 
        font-weight: 800;
        white-space: nowrap; /* O Pulo do Gato: Impede quebra de linha */
    }
    
    .subtitle { text-align: center; color: #555; margin-bottom: 2rem; }
    
    /* Cards e Botões */
    div[data-testid="stExpander"] { background-color: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: none; }
    .stButton>button { background: linear-gradient(45deg, #FF4B4B, #FF914D); color: white; border-radius: 25px; height: 50px; font-weight: bold; border: none; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 6px 15px rgba(255, 75, 75, 0.4); }
    
    /* Botão Sair (Pequeno e discreto) */
    .botao-sair > button {
        background: #6c757d !important;
        height: 35px !important;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- GERENCIAMENTO DE ESTADO ---
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'usuario_nome' not in st.session_state:
    st.session_state.usuario_nome = ""
if 'historico' not in st.session_state:
    st.session_state.historico = []
# Importante: Inicializamos a chave do text_area se ela não existir
if 'txt_interesses' not in st.session_state:
    st.session_state.txt_interesses = ""

# --- SEGURANÇA ---
try:
    MINHA_API_KEY = st.secrets["MINHA_API_KEY"]
except FileNotFoundError:
    st.error("⚠️ Chave de API não encontrada.")
    st.stop()

# --- FUNÇÃO AUXILIAR: GERAR INTERESSES (CORREÇÃO DO BOTÃO) ---
def gerar_interesses_aleatorios():
    perfis = [
        "Gosta de café gourmet, ler livros de suspense e gatos.",
        "Ama tecnologia, setups de computador, luzes RGB e jogos online.",
        "É fitness, faz crossfit, come saudável e gosta de trilhas.",
        "Gosta de vinhos, queijos, jazz e viagens para a Europa.",
        "Fã de Harry Potter, coleciona funkos e gosta de jogos de tabuleiro.",
        "Adora jardinagem, plantas suculentas e decoração DIY.",
        "Músico amador, toca violão e gosta de vinis antigos."
    ]
    # Atualiza DIRETAMENTE a chave do componente de texto
    st.session_state.txt_interesses = random.choice(perfis)

# --- TELA DE LOGIN ---
def tela_login():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/4213/4213650.png", width=120)
        st.title("Bem-vindo ao Giftly")
        st.markdown("<h3 style='text-align: center;'>Seu assistente pessoal de presentes</h3>", unsafe_allow_html=True)
        
        nome = st.text_input("Como você gostaria de ser chamado?", placeholder="Digite seu nome...")
        
        if st.button("🚀 Entrar no Sistema", use_container_width=True):
            if nome:
                st.session_state.logado = True
                st.session_state.usuario_nome = nome
                st.rerun()
            else:
                st.warning("Por favor, digite um nome.")

# --- APP PRINCIPAL ---
def app_principal():
    # BARRA DE NAVEGAÇÃO (User + Sair)
    # Usamos container para separar visualmente do título
    with st.container():
        c_user, c_vazio, c_sair = st.columns([6, 4, 2])
        with c_user:
            st.markdown(f"#### Olá, {st.session_state.usuario_nome}! 👋")
        with c_sair:
            # Coloquei uma div para estilizar especificamente este botão se precisar
            st.markdown('<div class="botao-sair">', unsafe_allow_html=True)
            if st.button("Sair", key="btn_sair", use_container_width=True):
                st.session_state.logado = False
                st.session_state.historico = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # TÍTULO PRINCIPAL (Agora em linha própria para não quebrar)
    st.title("🎁 Giftly")
    st.markdown("---")

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.header("⚙️ Configuração")
        quem = st.text_input("👤 Quem vai ganhar?", placeholder="Ex: Namorada, Pai...")
        idade = st.number_input("🎂 Idade:", 0, 120, 25)
        ocasiao = st.selectbox("📅 Ocasião:", ["Aniversário", "Natal", "Dia dos Namorados", "Amigo Secreto", "Outro"])
        orcamento = st.number_input("💰 Orçamento (R$):", min_value=0.0, step=50.0, value=200.0)
        
        st.markdown("---")
        if len(st.session_state.historico) > 0:
            st.header("🕒 Histórico Recente")
            for item in reversed(st.session_state.historico):
                with st.expander(f"🎁 {item['quem']} ({item['data']})"):
                    for sugestao in item['sugestoes']:
                        st.write(f"- {sugestao['nome']}")

    # --- ÁREA DE INTERESSES ---
    st.subheader("Do que essa pessoa gosta?")
    
    col_text, col_dice = st.columns([4, 1])
    
    with col_dice:
        st.write("") 
        st.write("") 
        # AQUI ESTÁ A CORREÇÃO DO BOTÃO:
        # Usamos on_click para chamar a função ANTES de recarregar a tela
        st.button("🎲 Sem ideia?", on_click=gerar_interesses_aleatorios, use_container_width=True)
    
    with col_text:
        # A key="txt_interesses" conecta esse campo direto ao session_state
        interesses = st.text_area("", height=100, key="txt_interesses", placeholder="Descreva os hobbies aqui ou clique no dado ao lado...")

    st.markdown("<br>", unsafe_allow_html=True)
    botao_gerar = st.button("✨ ENCONTRAR PRESENTES PERFEITOS")

    # --- LÓGICA DE GERAÇÃO ---
    if botao_gerar:
        if not interesses or not quem:
            st.warning("⚠️ Preencha os campos para a mágica acontecer.")
        else:
            try:
                with st.status("🤖 A IA está trabalhando...", expanded=True) as status:
                    st.write("Analisando perfil...")
                    genai.configure(api_key=MINHA_API_KEY)
                    model = genai.GenerativeModel('gemini-2.5-flash')

                    prompt = f"""
                    Atue como personal shopper. Sugira 3 presentes para: {quem}, {idade} anos.
                    Ocasião: {ocasiao}. Orçamento: R$ {orcamento}. Interesses: {interesses}.
                    OUTPUT JSON OBRIGATÓRIO:
                    [
                        {{ "nome": "Produto", "descricao": "Curta explicação", "preco_estimado": "R$ Valor", "emoji": "🎁", "termo_busca": "Termo" }}
                    ]
                    """
                    response = model.generate_content(prompt)
                    
                    texto_bruto = response.text
                    inicio = texto_bruto.find('[')
                    fim = texto_bruto.rfind(']') + 1
                    
                    if inicio != -1 and fim != -1:
                        texto_limpo = texto_bruto[inicio:fim]
                        sugestoes = json.loads(texto_limpo)
                        status.update(label="Concluído!", state="complete", expanded=False)

                        st.session_state.historico.append({
                            "quem": quem,
                            "sugestoes": sugestoes,
                            "data": time.strftime("%H:%M")
                        })

                        st.success(f"Sugestões para {quem}:")
                        c1, c2, c3 = st.columns(3)
                        
                        def criar_card(col, item):
                            with col:
                                with st.container(border=True):
                                    st.subheader(f"{item['emoji']} {item['nome']}")
                                    st.write(f"_{item['descricao']}_")
                                    st.metric("Preço", item['preco_estimado'])
                                    termo = item['termo_busca'].replace(" ", "+")
                                    link_a = f"https://www.amazon.com.br/s?k={termo}"
                                    link_s = f"https://shopee.com.br/search?keyword={termo}"
                                    ca, cb = st.columns(2)
                                    ca.link_button("Amazon", link_a, use_container_width=True)
                                    cb.link_button("Shopee", link_s, use_container_width=True)

                        if len(sugestoes) >= 3:
                            criar_card(c1, sugestoes[0])
                            criar_card(c2, sugestoes[1])
                            criar_card(c3, sugestoes[2])
                    else:
                        st.error("Erro na leitura da IA.")
            except Exception as e:
                st.error(f"Erro: {e}")

# --- CONTROLE DE FLUXO ---
if st.session_state.logado:
    app_principal()
else:
    tela_login()