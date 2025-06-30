# Documenta Wiki Chatbot

**Documentação do Documenta-Wiki-Chatbot**

Este repositório contém um assistente conversacional baseado em modelos de linguagem (LLM), desenvolvido para apoiar usuários da plataforma Documenta Wiki do Ministério do Desenvolvimento e Assistência Social, Família e Combate à Fome (MDS). Ele responde perguntas sobre uso da ferramenta, orienta a documentação de programas e indicadores, e gera sugestões automáticas de fichas.

---

## 🚀 Funcionalidades

* 🧠 **Responde dúvidas sobre uso da Documenta Wiki**
* ✏️ **Explica como editar, publicar e solicitar acesso às fichas**
* 📄 **Gera propostas de fichas de programa e indicador com base em PDFs oficiais**
* 🔭 **Usa vetorizacão semântica para aumentar a precisão das respostas**
* ☁️ **Compatível com publicação no Streamlit Cloud**

---

## 🛠️ Tecnologias Utilizadas

* **LangChain**: para orquestração do mecanismo RAG (Retrieval-Augmented Generation)
* **Google Generative AI (embedding-001)**: para vetorizacão semântica
* **FAISS**: para indexação eficiente dos documentos
* **Groq API**: para acesso ao modelo LLaMA 3
* **Streamlit**: interface gráfica para interação com o chatbot

---

## 📆 Como Executar Localmente

```bash
# 1. Clone o repositório
git clone https://github.com/CGPI-Sagicad-MDS/Chatbot_Wiki.git
cd Chatbot_Wiki

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate    # Windows

# 3. Instale as dependências
pip install -r requirements.txt
```

Crie um arquivo `.env` com suas chaves de API:

```env
groq_api_key=sk-xxxxxxx
google_api_key=AIza-xxxxxx
```

Execute o aplicativo:

```bash
streamlit run app.py
```

---

## ☁️ Como Publicar no Streamlit Cloud

1. Suba o repositório para o GitHub
2. Acesse [https://share.streamlit.io](https://share.streamlit.io)
3. Clique em “New app”
4. Escolha o repositório e o arquivo `app.py`
5. Em *Settings > Secrets*, adicione:

```
groq_api_key = "sk-..."
google_api_key = "AIza..."
```

6. Clique em **Deploy** 🎉

---

## 📅 Observações Importantes

* O PDF **Ficha de Indicador.pdf** é usado como base para gerar fichas de indicador.
* Para gerar ficha de programa, o usuário precisa fornecer insumos como referências legais e objetivos.
* O nome sugerido para indicadores segue o **Protocolo de Nomeação** oficial.
* As fichas e respostas geradas são apenas sugestões, devendo passar por revisão técnica.

---

## 📄 Licença

MIT - Desenvolvido por **Mariana N. Resende**, 2025

---

## 🔗 Acesso Rápido

* Repositório: [github.com/CGPI-Sagicad-MDS/Chatbot\_Wiki](https://github.com/CGPI-Sagicad-MDS/Chatbot_Wiki)
* Documenta Wiki: [mds.gov.br/documenta-wiki](https://mds.gov.br/documenta-wiki)
* Suporte: [wiki@mds.gov.br](mailto:wiki@mds.gov.br)

