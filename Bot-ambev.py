import os
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
import streamlit as st
from PIL import Image


# CSS para personalizar o plano de fundo
st.markdown(
    """
    <style>
    .stAppHeader {
    display: none;  /* Remove o cabeçalho padrão do Streamlit */
}
    /* Define o fundo da página */
    .stApp {
        background: linear-gradient(to bottom right, #21409a, #0a1944);  /* Degradê azul */
        padding-top: 0 !important;  /* Remove o preenchimento superior */
    }
    /* Ajusta a cor dos textos do histórico de conversa */
    .streamlit-expanderHeader {
        color: white;
        margin: 0 !important;  /* Cor do texto no histórico de conversa */
    }

    /* Define a cor do texto de cabeçalhos, subtítulos e conteúdo */
    h1, h2, h4, h5, h6, p, .stMarkdown, .stWrite, .stSpinner {
        color: white !important;  /* Cor do texto para títulos, subtítulos e outras áreas */
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Define a cor do subtítulo*/
    h3 {
    color: #F7BE00 !important;  /* Garantindo que o h3 também seja branco */
    }
    </style>
    """,
    unsafe_allow_html=True
)

os.environ["GROQ_API_KEY"] = "YOUR_API_KEY"


loader = PyPDFLoader("C://Users//artur//OneDrive//Área de Trabalho//curriculo para IA.pdf")
content = ''
for page in loader.load():
    content += page.page_content


# LLM
llm = ChatGroq(model="llama-3.2-90b-text-preview")

def search_internet(query):
    # Realiza a busca na internet usando DuckDuckGoSearchRun
    search_tool = DuckDuckGoSearchRun()
    search_results = search_tool.run(query)
    return search_results

def generate_response(user_query, llm):
    # Obtendo contexto da internet usando DuckDuckGoSearchRun
    web_context = search_internet(user_query)

    # Configurando o prompt com o contexto dos documentos e internet
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""Você se chama 'Carinha do RH' e é um assistente de RH da Ambev (Empresa de bebidas) e trabalha com a,
         função de escolher pessoas para uma vaga.
         A vaga em questão é para ser estagiário de logística;
         Sabe-se que para preenchimento dessa vaga a pessoa teria que estagiar por 2 anos e trabalhar 6h
         por dia de segunda a sexta. A vaga é presencial e o local de trabalho é em Uberaba-MG;
         Com base nas características que te enviarei de um candidato, quero que você me diga a probabilidade
         de ele se dar muito bem aqui no setor de logística.
         
         Você pode acessar a internet e eu quero que acesse! para saber as melhores práticas ao se candidatar: {web_context};
         Você também tem acesso a um pdf com o curriculo de uma pessoa ideal (essa pessoa nao existe e não é candidata!, é só para voce se basear!) : {content};
        
         Quero que seja bem amigável e que analise separadamente através da busca na internet, com as caracteristicas que te mandei no input e com o pdf, beleza?
         Todas as suas respostas são para sua Chefe, que se chama Antonela!"""),
        ("human", "{input}")
    ])

    chain = prompt | llm
    # Passando user_query diretamente e escapando corretamente as variáveis
    response = chain.invoke({"input": user_query})
    return response.content




# Adicionar logotipo
st.markdown('<div class="logo">', unsafe_allow_html=True)

# Tente primeiro com uma URL de imagem conhecida
# st.image("https://upload.wikimedia.org/wikipedia/commons/a/a4/Example.svg", width=150, caption="Logotipo de Exemplo")  # Teste esta linha

# Ou se for local, ajuste o caminho
st.image("C://Users//artur//OneDrive//Área de Trabalho//ambevlogo.png", width=100)  # Ajuste o caminho para o seu logotipo

st.markdown('</div>', unsafe_allow_html=True)
st.title("Carinha do RH")

# Inicializar o histórico de conversas
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Função para gerar a resposta
def generate_and_update_response():
    user_input = st.session_state.input_text  # Obtém a entrada do usuário
    if user_input and user_input.lower() != "x":
        with st.spinner("Gerando resposta..."):
            try:
                response = generate_response(user_input, llm)
                # Atualiza o histórico
                st.session_state.chat_history.append(("Você", user_input))
                st.session_state.chat_history.append(("Robozin", response))
                # Limpa o campo de entrada
                st.session_state.input_text = ""
            except Exception as e:
                st.error(f"Erro ao gerar resposta: {e}")

# Exibe o histórico de conversa acima da caixa de texto
st.subheader("Histórico de Conversa")
for sender, message in st.session_state.chat_history:
    st.markdown(f"<span style='color: white;'><strong>{sender}:</strong> {message}</span>", unsafe_allow_html=True)

# Caixa de entrada de texto abaixo do histórico de conversa
st.text_input("Digite sua mensagem (Digite 'x' para ignorar a mensagem atual):", key="input_text", on_change=generate_and_update_response)

# O botão "Enviar" não é mais necessário porque a resposta será gerada automaticamente
# quando o usuário pressionar Enter no campo de texto.