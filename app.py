import streamlit as st
import google.generativeai as genai
import json

# --- CONFIGURAÇÃO DA PÁGINA (Deve ser o primeiro comando) ---
st.set_page_config(
    page_title="Gift.IA",
    page_icon="🎁",
    layout="wide"  # Layout wide usa a tela toda, fica mais profissional
)

# --- ESTILIZAÇÃO (CSS SIMPLES) ---
st.markdown("""
<style>
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
    }
    div[data-testid="stExpander"] {
        border: none;
        box-shadow: 0px 0px 5px #ddd;
    }
</style>
""", unsafe_allow_html=True)

# --- SUA CHAVE AQUI ---
MINHA_API_KEY = "COLE_SUA_CHAVE_AQUI" 

# --- CABEÇALHO ---
c1, c2 = st.columns([1, 4])
with c1:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213650.png", width=80) # Um ícone de presente
with c2:
    st.title("Gift.IA")
    st.write("Encontre o presente perfeito em segundos com Inteligência Artificial.")

st.markdown("---")

# --- BARRA LATERAL (INPUTS) ---
with st.sidebar:
    st.header("📝 Perfil do Presenteado")
    quem = st.text_input("Quem é a pessoa?", placeholder="Ex: Namorada, Pai...")
    idade = st.number_input("Idade:", min_value=0, max_value=120, value=25)
    ocasiao = st.selectbox("Ocasião:", ["Aniversário", "Natal", "Dia dos Namorados", "Amigo Secreto", "Outro"])
    orcamento = st.slider("Orçamento (R$):", 50, 2000, 200)
    st.markdown("---")
    botao_gerar = st.button("🚀 Encontrar Presentes")

# --- ÁREA PRINCIPAL ---
interesses = st.text_area("Do que ela gosta?", 
                          height=100,
                          placeholder="Digite aqui os hobbies, estilo, filmes favoritos, rotina... Quanto mais detalhes, melhor!")

# --- LÓGICA ---
if botao_gerar:
    if not interesses or not quem:
        st.warning("⚠️ Por favor, preencha quem é a pessoa e os interesses na barra lateral e acima.")
    else:
        try:
            with st.spinner('🤖 A IA está pesquisando as melhores opções...'):
                genai.configure(api_key=MINHA_API_KEY)
                model = genai.GenerativeModel('gemini-2.5-flash')

                prompt = f"""
                Atue como um personal shopper de luxo.
                Sugira 3 presentes criativos para: {quem}, {idade} anos.
                Ocasião: {ocasiao}. Orçamento: R$ {orcamento}.
                Interesses: {interesses}
                
                OUTPUT JSON OBRIGATÓRIO:
                [
                    {{
                        "nome": "Nome Curto do Produto",
                        "descricao": "Explicação persuasiva de 2 linhas.",
                        "preco_estimado": "Valor R$",
                        "emoji": "Um emoji que represente o item",
                        "termo_busca": "Termo de busca"
                    }}
                ]
                """
                response = model.generate_content(prompt)
                texto_limpo = response.text.replace("```json", "").replace("```", "")
                sugestoes = json.loads(texto_limpo)

                st.success("✨ Aqui estão 3 sugestões exclusivas:")
                st.markdown("<br>", unsafe_allow_html=True) # Espaço em branco

                # EXIBIÇÃO EM COLUNAS (O SEGREDO DO VISUAL)
                col1, col2, col3 = st.columns(3)

                # Função para criar o cartão visual
                def criar_card(coluna, item):
                    with coluna:
                        with st.container(border=True):
                            st.subheader(f"{item['emoji']} {item['nome']}")
                            st.write(f"_{item['descricao']}_")
                            st.metric(label="Preço Estimado", value=item['preco_estimado'])
                            
                            termo = item['termo_busca'].replace(" ", "+")
                            st.link_button("🔍 Ver no Google", f"https://www.google.com/search?q={termo}&tbm=shop", use_container_width=True)

                # Criando os 3 cards
                criar_card(col1, sugestoes[0])
                criar_card(col2, sugestoes[1])
                criar_card(col3, sugestoes[2])

        except Exception as e:
            st.error(f"Erro: {e}")