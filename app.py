import streamlit as st
import google.generativeai as genai
import json
import time
import random
import ast

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Giftly",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO CSS (VISUAL FULL APP) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(to right, #f8f9fa, #e9ecef); color: #333333; }
    header[data-testid="stHeader"] { background-color: transparent; z-index: 1; }
    div[data-testid="stDecoration"] { visibility: hidden; height: 0px; }
    .block-container { padding-top: 2rem; padding-bottom: 1rem; }
    .stButton>button { background: linear-gradient(45deg, #FF4B4B, #FF914D); color: white; border-radius: 20px; height: 45px; font-weight: bold; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 6px 12px rgba(255, 75, 75, 0.3); color: white; }
    div[data-testid="stVerticalBlockBorderWrapper"] .botao-sair-container button { background-color: #ffffff !important; color: #555 !important; border: 1px solid #ddd !important; height: 32px !important; font-size: 13px !important; border-radius: 8px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] .botao-sair-container button:hover { background-color: #fff0f0 !important; color: #FF4B4B !important; border-color: #FF4B4B !important; }
    div[data-testid="stExpander"] { background-color: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: none; }
    .preco-destaque { color: #198754; font-weight: 800; font-size: 1.2rem; background-color: #e8f5e9; padding: 5px 10px; border-radius: 8px; display: inline-block; margin-top: 5px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- ESTADO ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'usuario_nome' not in st.session_state: st.session_state.usuario_nome = ""
if 'historico' not in st.session_state: st.session_state.historico = []
if 'txt_interesses' not in st.session_state: st.session_state.txt_interesses = ""
# Inicializamos a chave 'quem' para não dar erro na primeira leitura
if 'quem' not in st.session_state: st.session_state.quem = ""

# --- SEGURANÇA ---
try:
    MINHA_API_KEY = st.secrets["MINHA_API_KEY"]
except FileNotFoundError:
    st.error("⚠️ Chave de API não encontrada.")
    st.stop()

# --- INTEELIGÊNCIA DO BOTÃO DADO (LÓGICA HÍBRIDA) ---
def gerar_interesses_aleatorios():
    # 1. Tenta pegar quem é a pessoa do input (se existir)
    quem_input = st.session_state.get("quem", "").lower()
    
    # 2. Banco de Dados de Perfis
    interesses_base = {
        "namorada": ["skincare e maquiagem", "decoração aesthetic", "romance e livros", "moda e acessórios"],
        "namorado": ["futebol e churrasco", "tecnologia e gadgets", "games competitivos", "cervejas artesanais"],
        "mãe": ["plantas e jardinagem", "itens de casa e conforto", "livros de receitas", "bem-estar e spa"],
        "pai": ["ferramentas e DIY", "vinhos e queijos", "história e biografias", "churrasco e lazer"],
        "amigo": ["jogos de tabuleiro", "itens geeks", "bebidas diferentes", "experiências divertidas"],
        "chefe": ["produtividade", "itens de escritório premium", "livros de negócios", "café gourmet"],
        "vo": ["artesanato e tricô", "fotos da família", "chás e biscoitos", "conforto"],
        "avo": ["artesanato e tricô", "fotos da família", "chás e biscoitos", "conforto"]
    }
    
    # 3. Listas Combinatórias (Dão o tom da frase)
    estilos = [
        "curte coisas criativas e únicas",
        "prefere itens personalizados",
        "gosta de produtos premium e duráveis",
        "adora novidades tecnológicas",
        "valoriza experiências acima de bens materiais"
    ]
    
    personalidade = [
        "é uma pessoa mais caseira e tranquila",
        "adora sair e estar com amigos",
        "tem uma rotina agitada e produtiva",
        "é muito curiosa e gosta de aprender",
        "tem um estilo de vida saudável"
    ]

    # 4. O Matchmaker (Cruza os dados)
    # Verifica se alguma chave (ex: 'pai') está no texto digitado (ex: 'meu pai querido')
    lista_hobbies = []
    found = False
    
    for chave, lista in interesses_base.items():
        if chave in quem_input:
            lista_hobbies = lista
            found = True
            break
    
    # Se não achou match, usa uma mistura geral
    if not found:
        lista_hobbies = [
            "viagens e turismo", "fotografia", "cinema e séries", "gastronomia", 
            "música e shows", "tecnologia", "esportes ao ar livre", "leitura"
        ]

    # 5. Montagem da Frase Final
    hobby_escolhido = random.choice(lista_hobbies)
    estilo_escolhido = random.choice(estilos)
    personalidade_escolhida = random.choice(personalidade)

    # Cria uma frase natural
    frase_final = f"Gosta muito de {hobby_escolhido}, {estilo_escolhido} e {personalidade_escolhida}."
    
    st.session_state.txt_interesses = frase_final

# --- LOGIN ---
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

# --- APP PRINCIPAL ---
def app_principal():
    # HEADER
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
        with c_ola: st.markdown(f"<div style='text-align: right; padding-top: 8px; color: #555; font-weight: 500;'>Olá, <b>{st.session_state.usuario_nome}</b>!</div>", unsafe_allow_html=True)
        with c_sair:
            with st.container():
                st.markdown('<div class="botao-sair-container">', unsafe_allow_html=True)
                if st.button("Sair ➝", key="btn_sair", use_container_width=True):
                    st.session_state.logado = False
                    st.session_state.historico = []
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # SIDEBAR
    with st.sidebar:
        st.header("⚙️ Configuração")
        # ADICIONEI key="quem" AQUI PARA O BOTÃO LER O VALOR!
        quem = st.text_input("👤 Quem vai ganhar?", placeholder="Ex: Namorada...", key="quem")
        idade = st.number_input("🎂 Idade:", 0, 120, 25)
        ocasiao = st.selectbox("📅 Ocasião:", ["Aniversário", "Natal", "Dia dos Namorados", "Amigo Secreto", "Outro"])
        orcamento = st.number_input("💰 Máximo (R$):", min_value=0.0, step=50.0, value=200.0)
        
        st.markdown("---")
        if len(st.session_state.historico) > 0:
            st.markdown("### 🕒 Histórico")
            for item in reversed(st.session_state.historico):
                with st.expander(f"{item['quem']} ({item['data']})"):
                    for sug in item['sugestoes']: st.write(f"• {sug['nome']}")

    # INPUTS
    st.subheader("Do que essa pessoa gosta?")
    c_input, c_btn = st.columns([5, 1])
    with c_btn:
        st.write("")
        st.write("")
        # Chama a nova função inteligente
        st.button("🎲 Ideia?", on_click=gerar_interesses_aleatorios, use_container_width=True)
    with c_input:
        interesses = st.text_area("", height=80, key="txt_interesses", placeholder="Ex: Gosta de rock, cozinhar e tecnologia...")

    # AÇÃO
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
                    Aja como um personal shopper experiente e atencioso.
                    Sugira 3 presentes para: {quem}, {idade} anos.
                    Ocasião: {ocasiao}. Orçamento Máximo: R$ {orcamento}.
                    Interesses informados: {interesses}.
                    REGRAS DE OURO PARA A DESCRIÇÃO:
                    1. A descrição DEVE explicar a conexão entre o produto e os interesses informados.
                    2. Use frases como: "Escolhi esta opção porque...", "Como você disse que o {quem} gosta de...", "Ideal para o perfil de quem curte...".
                    OUTPUT JSON OBRIGATÓRIO:
                    [ {{ "nome": "Produto", "descricao": "Explicação personalizada", "preco_estimado": "Valor Numérico", "emoji": "🎁", "termo_busca": "Termo" }} ]
                    """
                    response = model.generate_content(prompt)
                    texto = response.text
                    inicio, fim = texto.find('['), texto.rfind(']') + 1
                    if inicio != -1 and fim != -1:
                        limpo = texto[inicio:fim]
                        try: sugestoes = json.loads(limpo)
                        except: sugestoes = ast.literal_eval(limpo)
            except Exception as e: st.error(f"Erro: {e}")

            if sugestoes:
                st.session_state.historico.append({"quem": quem, "sugestoes": sugestoes, "data": time.strftime("%H:%M")})
                st.success(f"Opções selecionadas para {quem}:")
                cols = st.columns(3)
                for i, item in enumerate(sugestoes):
                    if i < 3:
                        with cols[i]:
                            with st.container(border=True):
                                st.markdown(f"#### {item['emoji']} {item['nome']}")
                                st.write(f"_{item['descricao']}_")
                                preco_texto = str(item['preco_estimado'])
                                if "R$" not in preco_texto and "r$" not in preco_texto: preco_final = f"R$ {preco_texto}"
                                else: preco_final = preco_texto
                                st.markdown(f"<div class='preco-destaque'>{preco_final}</div>", unsafe_allow_html=True)
                                termo = item['termo_busca'].replace(" ", "+")
                                c_amz, c_shp = st.columns(2)
                                c_amz.link_button("📦 Amazon", f"https://www.amazon.com.br/s?k={termo}", use_container_width=True)
                                c_shp.link_button("🛍️ Shopee", f"https://shopee.com.br/search?keyword={termo}", use_container_width=True)

# ROTEADOR
if st.session_state.logado: app_principal()
else: tela_login()