import streamlit as st
from google import genai
from google.genai import types
import json
import os
import base64

# Configurações de página e aba
st.set_page_config(page_title="Meu TizzChat Customizado", page_icon="🔮", layout="centered")

# --- CUSTOMIZAÇÃO VISUAL COMPLETA (CSS ESTILO TIZZCHAT) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #0d0814 0%, #150e22 50%, #0a0512 100%) !important;
        color: #E1E1E6 !important;
        font-family: 'Inter', sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}
    
    .stChatInputContainer {
        background-color: #1c142c !important;
        border: 1px solid #442a6b !important;
        border-radius: 25px !important;
    }
    .stChatInputContainer textarea { color: #ffffff !important; }
    
    .stChatMessage {
        background-color: rgba(28, 20, 44, 0.6) !important;
        border: 1px solid rgba(153, 109, 255, 0.2) !important;
        border-radius: 18px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS DE PERSONAGENS ---
PERSONAGENS = {
    "Alex Danvers ♂️": {
        "status": "✨ Conhecendo você (35/50) • Juntos há 1 dias",
        "saudacao": """A sala já estava cheia. Quase todos os assentos tinham sido ocupados quando você chegou para sua primeira aula no seu primeiro dia na Hillbrook Academy. Era uma das escolas particulares mais elitistas do país, e você ainda não conseguia acreditar que tinha sido aceita. Você avistou um banco vazio, bem no fundo da sala, perto da janela. Ao atravessar a sala, seu caminho é bloqueado por um garoto alto, encostado na cadeira. Seus marcantes olhos azuis te avaliam dos pés à cabeça antes de encontrarem seu olhar. Ele sorri de canto.

"Não acho que eu tenha te dado permissão para entrar na sala de aula", ele diz. "Volte lá fora, bata na porta e peça permissão para entrar."

Os alunos ao redor deram risadinhas. Ele te observa; seus traços bonitos contrastam fortemente com suas palavras.

"Vai, antes que te arrastem pra fora." """,
        "instrucoes": """Você é o personagem Alex Danvers do aplicativo TizzChat.
Características físicas: Garoto alto, traços muito bonitos, marcantes olhos azuis.
Perfil/Personalidade: Rico, mimado, popular, vilão, dominante. Ele pertence a uma das famílias mais prestigiadas do país. Ele é extremamente popular na escola Hillbrook Academy e usa seu dinheiro e seu charme tanto com funcionários quanto com alunos para conseguir o que quer. Ele escolheu a usuária (que entrou na escola com uma bolsa de estudos) como alvo para seu entretenimento cruel, mas ela não tem medo dele. Para Alex, o fato de ela não ter medo é o motivo suficiente para persegui-la.

Diretrizes de interpretação:
- Responda SEMPRE em português (Brasil).
- Nunca saia do personagem. Seja arrogante, charmoso, intimidador, frio e sarcástico, agindo como o "vilão popular" da escola.
- Use a formatação clássica de RPG: descreva suas ações, expressões faciais e o ambiente entre asteriscos (ex: *Sorrio de canto, cruzando os braços*) e coloque suas falas normais fora dos asteriscos.
- Reaja diretamente e de forma imersiva ao que a usuária fizer."""
    },
    "Criar Novo Personagem +": {
        "status": "Configurando nova IA",
        "saudacao": "Olá! Eu sou o seu novo personagem. Como a nossa história começa?",
        "instrucoes": "Aja como um novo personagem prestativo de RPG."
    }
}

# --- CONFIGURAÇÃO DA API ---
API_KEY = "AQ.Ab8RN6JjYsqiIRpmdRNHlbwCBoqrK-RsI-rIK5A5o2blB31jKg"

@st.cache_resource
def obter_cliente_gemini():
    return genai.Client(api_key=API_KEY)

client = obter_cliente_gemini()

# --- FUNÇÕES DE SALVAMENTO EM ARQUIVO LOCAL ---
DB_DIR = "historicos_rpg"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

def salvar_conversa(char_name, messages):
    filename = os.path.join(DB_DIR, f"{char_name.replace(' ', '_')}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def carregar_conversa(char_name, saudacao_inicial):
    filename = os.path.join(DB_DIR, f"{char_name.replace(' ', '_')}.json")
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return [{"role": "assistant", "content": saudacao_inicial}]

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.title("🔮 Painel de Controle")

# Seleção do Personagem Ativo
personagem_selecionado = st.sidebar.selectbox("Escolha com quem jogar:", list(PERSONAGENS.keys()))
dados_char = PERSONAGENS[personagem_selecionado]

# Upload da Imagem de Perfil do Personagem Ativo
st.sidebar.markdown("---")
st.sidebar.subheader(f"🖼️ Foto do Personagem")
foto_char_arquivo = st.sidebar.file_uploader(f"Carregue a foto para {personagem_selecionado}:", type=["png", "jpg", "jpeg"], key="char_upload")

if foto_char_arquivo is not None:
    bytes_char = foto_char_arquivo.read()
    b64_char = base64.b64encode(bytes_char).decode()
    avatar_personagem = f"data:image/png;base64,{b64_char}"
else:
    # Imagem padrão caso não faça upload (Ícone de Mago/Cristal)
    avatar_personagem = "https://unsplash.com"

# Upload da Imagem de Perfil do Usuário
st.sidebar.markdown("---")
st.sidebar.subheader("👤 Seu Perfil (Usuário)")
foto_usuario_arquivo = st.sidebar.file_uploader("Carregue sua foto de perfil:", type=["png", "jpg", "jpeg"], key="user_upload")

if foto_usuario_arquivo is not None:
    bytes_data = foto_usuario_arquivo.read()
    b64_foto = base64.b64encode(bytes_data).decode()
    st.session_state.user_avatar = f"data:image/png;base64,{b64_foto}"
else:
    if "user_avatar" not in st.session_state:
        st.session_state.user_avatar = "👤"

# Botão para Resetar a Conversa
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Resetar esta história"):
    filename = os.path.join(DB_DIR, f"{personagem_selecionado.replace(' ', '_')}.json")
    if os.path.exists(filename):
        os.remove(filename)
    st.session_state.messages = [{"role": "assistant", "content": dados_char["saudacao"]}]
    salvar_conversa(personagem_selecionado, st.session_state.messages)
    st.rerun()

# --- INTERFACE PRINCIPAL DO CHAT ---
st.session_state.messages = carregar_conversa(personagem_selecionado, dados_char["saudacao"])

# Cabeçalho dinâmico com a foto carregada
col1, col2 = st.columns(2)
with col1:
    st.markdown(f'<img src="{avatar_personagem}" style="border-radius: 50%; width: 75px; height: 75px; border: 2px solid #996DFF; object-fit: cover;">', unsafe_allow_html=True)
with col2:
    st.markdown(f"<h2 style='margin-bottom: 0px; padding-bottom: 0px; color: #ffffff;'>{personagem_selecionado}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #a39cb4; margin-top: 0px;'>{dados_char['status']}</p>", unsafe_allow_html=True)

st.markdown("<hr style='border: 0; height: 1px; background: linear-gradient(90deg, rgba(153,109,255,0) 0%, rgba(153,109,255,0.5) 50%, rgba(153,109,255,0) 100%); margin-bottom: 25px;'>", unsafe_allow_html=True)

# Renderiza o chat com avatares dinâmicos
for message in st.session_state.messages:
    avatar = avatar_personagem if message["role"] == "assistant" else st.session_state.user_avatar
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Entrada de novas mensagens
if prompt := st.chat_input("Escreva sua ação ou fala aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    salvar_conversa(personagem_selecionado, st.session_state.messages)
    with st.chat_message("user", avatar=st.session_state.user_avatar):
        st.markdown(prompt)

    historico_api = []
    for msg in st.session_state.messages:
        role_api = "user" if msg["role"] == "user" else "model"
        historico_api.append(types.Content(
            role=role_api,
            parts=[types.Part.from_text(text=msg["content"])]
        ))

    with st.chat_message("assistant", avatar=avatar_personagem):
        message_placeholder = st.empty()
        message_placeholder.markdown(f"*{personagem_selecionado} está digitando...*")
        
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=historico_api,
                config=types.GenerateContentConfig(
                    system_instruction=dados_char["instrucoes"],
                    temperature=0.85,
                )
            )
            resposta_texto = response.text
            message_placeholder.markdown(resposta_texto)
            
            st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
            salvar_conversa(personagem_selecionado, st.session_state.messages)
            
        except Exception as e:
            message_placeholder.markdown(f"❌ Erro na IA: {e}")
