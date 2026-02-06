import streamlit as st
import google.generativeai as genai
import json
import time # Importei para fazer efeito de carregamento

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gift.IA - O Presenteador",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO CSS AVANÇADA (A Mágica Visual) ---
st.markdown("""
<style>
    /* Fundo geral mais suave */
    .stApp {
        background: linear-gradient(to right, #f8f9fa, #e9ecef);
    }
    
    /* Estilo do Título Principal */
    h1 {
        color: #FF4B4B;
        text-align: center;
        font-family: 'Helvetica', sans-serif;
        font-weight: 800;
    }
    
    /* Subtítulo centralizado */
    .subtitle {
        text-align: center;
        color: #555;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    /* Cards dos presentes */
    div[data-testid="stExpander"] {
        background-color: white;
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); /* Sombra suave */
        transition: transform 0.3s ease;
    }
    
    /* Botões personalizados */
    .stButton>button {
        background: linear-gradient(45deg, #FF4B4B, #FF914D);
        color: white;
        border: none;
        border-radius: 25px;
        height: 50px;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(255, 75, 75, 0.3);
        width: 100%;
    }
    
    /* Efeito hover no botão */
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 15px rgba(255, 75, 75, 0.4);
    }
    
    /* Métricas de preço */
    div[data-testid="stMetricValue"] {
        color: #28a745;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- SEGURANÇA DA CHAVE ---
try:
    MINHA_API_KEY = st.secrets["MINHA_API_KEY"]
except FileNotFoundError:
    st.error("⚠️ Chave de API não encontrada. Configure o secrets.toml")
    st.stop()

# --- CABEÇALHO ---
st.title("🎁 Gift.IA")
st.markdown('<p class="subtitle">Seu assistente pessoal de presentes com Inteligência Artificial</p>', unsafe_allow_html=True)
st.markdown("---")

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213650.png", width=100)
    st.header("⚙️ Configuração")
    st.write("Preencha os dados para a mágica acontecer.")
    
    quem = st.text_input("👤 Quem vai ganhar?", placeholder="Ex: Namorada, Pai, Chefe...")
    idade = st.number_input("🎂 Idade:", 0, 120, 25)
    ocasiao = st.selectbox("📅 Ocasião:", ["Aniversário", "Natal", "Dia dos Namorados", "Amigo Secreto", "Casamento", "Outro"])
    orcamento = st.number_input("💰 Orçamento Máx. (R$):", min_value=0.0, step=50.0, value=200.0)
    
    st.markdown("---")
    botao_gerar = st.button("✨ Encontrar Presentes")
    
    st.markdown("---")
    st.caption("Desenvolvido com ❤️ e IA")

# --- ÁREA PRINCIPAL ---
st.subheader("O que essa pessoa curte?")
interesses = st.text_area("", height=120, placeholder="Ex: Gosta de café especial, séries de ficção, cozinhar, tecnologia, acampar... Quanto mais detalhes, melhor!")

# --- LÓGICA ---
if botao_gerar:
    if not interesses or not quem:
        st.warning("⚠️ Ops! Preciso saber quem é a pessoa e do que ela gosta.")
    else:
        try:
            # Efeito visual de carregamento
            with st.status("🤖 A IA está pensando...", expanded=True) as status:
                st.write("Conectando aos neurônios digitais...")
                time.sleep(1) # Pequena pausa dramática
                st.write("Analisando perfil e tendências...")
                
                genai.configure(api_key=MINHA_API_KEY)
                model = genai.GenerativeModel('gemini-2.5-flash')

                prompt = f"""
                Atue como personal shopper de luxo. Sugira 3 presentes para: {quem}, {idade} anos.
                Ocasião: {ocasiao}. Orçamento: R$ {orcamento}. Interesses: {interesses}.
                OUTPUT JSON OBRIGATÓRIO:
                [
                    {{
                        "nome": "Nome Produto",
                        "descricao": "Explicação curta e persuasiva",
                        "preco_estimado": "R$ Valor",
                        "emoji": "🎁",
                        "termo_busca": "Termo exato busca"
                    }}
                ]
                """
                response = model.generate_content(prompt)
                
                # Tratamento do JSON
                texto_bruto = response.text
                inicio = texto_bruto.find('[')
                fim = texto_bruto.rfind(']') + 1
                
                if inicio != -1 and fim != -1:
                    texto_limpo = texto_bruto[inicio:fim]
                    sugestoes = json.loads(texto_limpo)
                    status.update(label="Presentes Encontrados!", state="complete", expanded=False)

                    st.success(f"Aqui estão 3 ideias incríveis para {quem}!")
                    st.markdown("<br>", unsafe_allow_html=True)

                    # Colunas para os Cards
                    col1, col2, col3 = st.columns(3)

                    def criar_card(coluna, item):
                        with coluna:
                            # Container estilizado pelo CSS
                            with st.container(border=True):
                                st.markdown(f"### {item['emoji']} {item['nome']}")
                                st.write(f"_{item['descricao']}_")
                                st.markdown("---")
                                st.metric("Preço Médio", item['preco_estimado'])
                                
                                termo = item['termo_busca'].replace(" ", "+")
                                link_amazon = f"https://www.amazon.com.br/s?k={termo}"
                                link_shopee = f"https://shopee.com.br/search?keyword={termo}"
                                
                                c_a, c_b = st.columns(2)
                                with c_a:
                                    st.link_button("📦 Amazon", link_amazon, use_container_width=True)
                                with c_b:
                                    st.link_button("🛍️ Shopee", link_shopee, use_container_width=True)

                    if len(sugestoes) >= 3:
                        criar_card(col1, sugestoes[0])
                        criar_card(col2, sugestoes[1])
                        criar_card(col3, sugestoes[2])
                else:
                    status.update(label="Erro na IA", state="error")
                    st.error("A IA ficou confusa. Tente simplificar os interesses.")

        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")