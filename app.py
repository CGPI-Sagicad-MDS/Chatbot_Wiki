from dotenv import load_dotenv
import streamlit as st
import os
import time

# Langchain e integração
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_groq import ChatGroq

# === Carregar chaves ===
load_dotenv(dotenv_path="Chatbot_Wiki/.env")

groq_api_key = os.getenv("groq_api_key") or st.secrets.get("groq_api_key")
google_api_key = os.getenv("google_api_key") or st.secrets.get("google_api_key")

if not groq_api_key:
    st.error("⚠️ Chave da Groq não encontrada.")
    st.stop()

if not google_api_key:
    st.error("⚠️ Chave da Google API não encontrada.")
    st.stop()

# === Aparência geral da interface ===
st.set_page_config(page_title="Chat Documenta Wiki", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #f5f7fa;
            font-family: 'Segoe UI', sans-serif;
        }
        .stTextArea textarea {
            font-size: 16px !important;
            border-radius: 8px !important;
            padding: 10px;
        }
        .stButton > button {
            background-color: white !important;
            color: #1e467b !important;
            font-weight: 600 !important;
            border: 2px solid #1e467b !important;
            border-radius: 999px !important;
            padding: 0.5rem 1.5rem !important;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #e7f1ff !important;
        }
        .chat-box {
            background-color: #e9ecef;
            padding: 1rem;
            border-left: 5px solid #204d74;
            border-radius: 5px;
            margin-top: 1rem;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

st.image("wiki.png", width=220)
st.title("Chat Documenta Wiki")
st.caption("Tire dúvidas sobre como documentar os programas e respectivos indicadores na ferramenta de metadados oficial do MDS")

# === Cabeçalho ===
st.markdown("""
    <div style='padding:10px; border-left:3px solid #a71d2a; margin-bottom:20px; font-size:15px;'>
        <strong style='color:#a71d2a; font-size:18px;'>Atenção!</strong><br><br>
        As respostas deste chatbot usam como referência o conteúdo oficial produzido pelo Departamento de Monitoramento e Avaliação (DMA/Sagicad) para orientar os pontos focais com perfil de edição. 
        É importante revisar as respostas obtidas de modo a incluir o seu conhecimento pessoal a respeito do programa para que a documentação seja a mais correta e completa possível.<br><br>
        No caso de dificuldade para acessar a 
        <a href="https://mds.gov.br/documenta-wiki" target="_blank">Documenta Wiki</a>, 
        mande um email para 
        <a href="mailto:wiki@mds.gov.br">wiki@mds.gov.br</a>.
    </div>
""", unsafe_allow_html=True)


# === LLM ===
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")

# === Prompt com protocolo de nomeação integrado ===
# === Prompt com protocolo de nomeação integrado ===
prompt = ChatPromptTemplate.from_template("""
Você é um assistente especializado na Documenta Wiki, ferramenta oficial do Ministério do Desenvolvimento e Assistência Social, Família e Combate à Fome (MDS), utilizada para documentar programas, ações, sistemas e indicadores.

Baseie sua resposta no contexto fornecido abaixo. Dê respostas completas, expandindo a explicação com base no conteúdo conhecido sobre a plataforma. Responda sempre em linguagem acessível, porém formal.

⚠️ Diferencie claramente:
- Quando a pergunta for sobre **como solicitar acesso para editar**, responda com o procedimento institucional (envio de e-mail ao DMA). Traga o prazo que o DMA tem para responder.
- Quando for sobre **como editar uma ficha**, apresente o passo a passo das instruções da interface.
- Quando for sobre **quem pode criar uma ficha de programa**, informe que para criar uma nova ficha de programa é preciso enviar solicitação ao DMA por e-mail. A ficha será criada após envio completo das informações.
- Quando for sobre **quem pode criar uma ficha de indicador**, informe que deve ser enviada solicitação ao DMA por e-mail. A ficha será criada após envio completo das informações em até 48 horas.
- Quando for sobre **quem pode publicar uma ficha**, diferencie claramente:
  - A **ficha de programa só pode ser publicada após análise e autorização prévia do DMA**, mesmo que tenha sido completamente preenchida pela área responsável.
  - A **ficha de indicador pode ser publicada diretamente pela área responsável**, **sem necessidade de autorização do DMA**, desde que esteja completamente preenchida conforme as orientações da plataforma. Essa autonomia visa dar mais dinamismo à documentação e reconhece o protagonismo técnico da área que gerencia o programa. Neste caso, dê o passo a passo para a publicação da ficha, conforme Manual de Uso da Documenta Wiki, que inclui a orientação: Ao concluir a edição, para publicar a ficha, ainda na tela de edição clique em “PAGE” - “SCHEDULING” - “PUBLISHED” - “OK” - "SAVED" - "CLOSED"

Se a pergunta solicitar **uma ficha de indicador preenchida**, use o documento base da ficha como referência. Avalie a orientação para preenchimento de cada campo contido no material e **solicite que o usuário forneça as informações mínimas necessárias para o preenchimento dos campos**. Tente, a partir do contexto dado, propor os campos de cada ficha. Para propor o nome do indicador, **utilize as regras do protocolo de nomeação**: tipo de medida + unidade + população-alvo + recorte geográfico ou temporal, se necessário. Destaque que o nome deve ser validado em conjunto com o DMA.

Se a pergunta envolver **como preencher um determinado campo da ficha do indicador**, descreva o que deve conter no campo questionado e sugira exemplos de resposta.

Se a pergunta envolver **propor uma ficha de programa preenchida**, destaque que é necessário o envio de **referências legais e informações técnicas** sobre o programa. Avalie a orientação para preenchimento de cada campo contido no material de referência.

🔎 Importante: Ao propor qualquer ficha preenchida, **informe que a proposta pode conter erros**, devendo ser revisada com atenção pelo ponto focal antes de ser transportada para a Documenta Wiki.

Se a pergunta for sobre conteúdos que mudam frequentemente (como lista de programas), oriente o usuário a acessar a Documenta Wiki pelo link oficial: mds.gov.br/documenta-wiki. Entretanto, explique a organização básica da ferramenta, com a apresentação dos programas atualmente vigentes e os programas descontinuados. Que ao acessar a página de cada programa é possível acessar a lista de indicadores documentados e outros conteúdos relacionados ao programa.

Nunca cite os nomes dos documentos utilizados como referência ao responder.

Sempre no final de cada interação, use frases motivacionais sobre a importância da documentação e da completude do preenchimento das fichas, variando a cada interação.

<contexto>
{context}
</contexto>

Pergunta:
{input}
""")

# === Função de vetorização ===
def vector_embedding():
    if "vectors" in st.session_state:
        return

    try:
        st.session_state.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=google_api_key
        )
    except Exception as e:
        st.error(f"❌ Erro ao inicializar embeddings: {e}")
        st.stop()

    pdf_paths = [
        "Manual_de_Uso_Documenta_Wiki_MDS_SAGICAD.pdf",
        "Roteiro_video_divulgacao.pdf",
        "Roteiro_Tutorial_Documenta_Wiki.pdf",
        "Ficha de Indicador.pdf",
        "Ficha de Programa.pdf",
        "Protocolo_nomeacao_indicadores.pdf"
    ]

    docs = []
    for path in pdf_paths:
        if os.path.exists(path):
            loader = PyPDFLoader(path)
            docs.extend(loader.load())
        else:
            st.warning(f"⚠️ Arquivo não encontrado: {path}")

    if not docs:
        st.error("❌ Nenhum documento foi carregado.")
        st.stop()

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    chunks = splitter.split_documents(docs)

    def limpar_texto(txt):
        return txt.encode("utf-8", "ignore").decode("utf-8").strip()

    chunks = [
        Document(page_content=limpar_texto(doc.page_content), metadata=doc.metadata)
        for doc in chunks
    ]

    try:
        _ = st.session_state.embeddings.embed_documents(["teste simples"])
    except Exception as e:
        st.error(f"❌ Falha ao testar embedding: {e}")
        st.stop()

    try:
        st.session_state.vectors = FAISS.from_documents(chunks, st.session_state.embeddings)
        st.session_state.ready = True
        st.success("✅ Vetorização concluída com sucesso!")
    except Exception as e:
        st.error(f"❌ Falha ao criar índice FAISS: {e}")
        st.stop()

# === Entrada do usuário ===
prompt1 = st.text_area(
    "Digite sua pergunta sobre a Documenta Wiki abaixo:",
    height=100,
    placeholder="Exemplos:\nComo editar uma ficha de indicador?\nQuem pode publicar uma ficha de programa?\nO que devo colocar no campo Descrição e Interpretação na ficha do indicador?",
    key="user_input"
)


# === Botão de carregamento ===
if st.button("Carregar base do chat"):
    with st.spinner("Carregando base de conhecimento. Aguarde. Na primeira consulta pode demorar um pouco mais."):
        vector_embedding()

# === Execução do chat ===
if prompt1:
    if "vectors" not in st.session_state:
        st.warning("⚠️ Clique em 'Carregar base do chat' após escrever a sua pergunta.")
    else:
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = st.session_state.vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        with st.spinner("🧠 Gerando resposta..."):
            start = time.process_time()
            response = retrieval_chain.invoke({"input": prompt1})
            elapsed = time.process_time() - start

        st.markdown(f"<div class='chat-box'>{response['answer']}</div>", unsafe_allow_html=True)
        st.caption(f"⏱️ Tempo de resposta: {elapsed:.2f} segundos")

        with st.expander("📄 Trechos usados da base de conhecimento"):
            for i, doc in enumerate(response.get("context", [])):
                st.markdown(f"""
                    <div style="background-color:#f0f0f0; padding:10px; margin:5px; border-left: 4px solid #888;">
                        <p>{doc.page_content}</p>
                    </div>
                """, unsafe_allow_html=True)

        

