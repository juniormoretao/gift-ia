import streamlit as st
import google.generativeai as genai
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gift.IA", page_icon="🎁", layout="wide")

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
<style>
    .stButton>button {
        background-color: #FF4B4B; color: white; border-radius: 10px; height: 3em; font-weight: bold;
    }
    div[data-testid="stExpander"] { border: none; box-shadow: 0px 0px 5px #ddd; }
</style>
""", unsafe_allow_html=True)

# --- SEGURANÇA DA CHAVE (O PULO DO GATO) ---
# Tenta pegar a chave do cofre do Streamlit (funciona local e na nuvem)
try:
    MINHA_API_KEY = st.secrets["MINHA_API_KEY"]
except FileNotFoundError:
    st.error("Chave de API não encontrada. Configure o arquivo .streamlit/secrets.toml")
    st.stop()

# --- CABEÇALHO ---
c1, c2 = st.columns([1, 4])
with c1:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213650.png", width=80)
with c2:
    st.title("Gift.IA")
    st.write("Encontre o presente perfeito em segundos com IA.")
st.markdown("---")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📝 Perfil")
    quem = st.text_input("Quem é?", placeholder="Ex: Namorada, Pai...")
    idade = st.number_input("Idade:", 0, 120, 25)
    ocasiao = st.selectbox("Ocasião:", ["Aniversário", "Natal", "Dia dos Namorados", "Amigo Secreto", "Outro"])
    orcamento = st.slider("Orçamento (R$):", 50, 2000, 200)
    st.markdown("---")
    botao_gerar = st.button("🚀 Encontrar Presentes")

# --- ÁREA PRINCIPAL ---
interesses = st.text_area("Do que a pessoa gosta?", height=100, placeholder="Digite hobbies, estilo, filmes...")

# --- LÓGICA ---
if botao_gerar:
    if not interesses or not quem:
        st.warning("⚠️ Preencha quem é a pessoa e os interesses.")
    else:
        try:
            with st.spinner('🤖 A IA está pesquisando...'):
                genai.configure(api_key=MINHA_API_KEY)
                model = genai.GenerativeModel('gemini-2.5-flash')

                prompt = f"""
                Atue como personal shopper. Sugira 3 presentes para: {quem}, {idade} anos.
                Ocasião: {ocasiao}. Orçamento: R$ {orcamento}. Interesses: {interesses}.
                OUTPUT JSON OBRIGATÓRIO:
                [
                    {{
                        "nome": "Nome Produto",
                        "descricao": "Curta explicação",
                        "preco_estimado": "Valor R$",
                        "emoji": "🎁",
                        "termo_busca": "Termo busca"
                    }}
                ]
                """
                response = model.generate_content(prompt)
                texto_limpo = response.text.replace("```json", "").replace("```", "")
                sugestoes = json.loads(texto_limpo)

                st.success("✨ Sugestões encontradas:")
                col1, col2, col3 = st.columns(3)

                def criar_card(coluna, item):
                    with coluna:
                        with st.container(border=True):
                            st.subheader(f"{item['emoji']} {item['nome']}")
                            st.write(f"_{item['descricao']}_")
                            st.metric("Preço", item['preco_estimado'])
                            termo = item['termo_busca'].replace(" ", "+")
                            st.link_button("🔍 Ver no Google", f"https://www.google.com/search?q={termo}&tbm=shop", use_container_width=True)

                if len(sugestoes) >= 3:
                    criar_card(col1, sugestoes[0])
                    criar_card(col2, sugestoes[1])
                    criar_card(col3, sugestoes[2])

        except Exception as e:
            st.error(f"Erro: {e}")