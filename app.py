import os
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from config import PASTA_DOCUMENTOS
from ingestao import introduzir_ficheiro, listar_documentos
from consulta import responder

st.set_page_config(page_title = "OXIGENIUM FITNESS - DOCUMENTOS", page_icon="📄")
st.title("📄 Assistente de documentos - OXIGENIUM FITNESS")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

with st.sidebar:
    st.header("Documentos")

    ficheiros = st.file_uploader("Carregar pdfs", type ="pdf", accept_multiple_files=True)
    if ficheiros and st.button("Processar"):
        os.makedirs(PASTA_DOCUMENTOS, exist_ok=True)
        for f in ficheiros:
            caminho = os.path.join(PASTA_DOCUMENTOS, f.name)
            with open(caminho, "wb") as destino:
                destino.write(f.getbuffer())

            with st.spinner(f"A processar {f.name}..."):
                n = introduzir_ficheiro(caminho)

            if n:
                st.success (f"{f.name}: {n} pedaços")
            else:
                st.info(f"{f.name} ja esta na base de dados")

    st.subheader("Na base")
    documentos = listar_documentos()
    if documentos:
        for d in documentos:
            st.write("-", d)
        else:
            st.caption("Nao ha qualquer documento")

        if st.button("Limpar conversa"):
            st.session_state.mensagens = []
            st.rerun()

for m in st.session_state.mensagens:
    with st.chat_message(m["papel"]):
        if m.get("pesquisa"):
            st.caption(f"Pesquisado: {m['pesquisa']}")
        st.markdown(m["texto"])
        if m.get("fontes"):
            with st.expander("Fontes"):
                for fonte in m["fontes"]:
                    st.write("-", fonte)

pergunta = st.chat_input("Faz uma pergunta sobre os documentos")

if pergunta:
    with st.chat_message("user"):
        st.markdown(pergunta)

    historico = [
        HumanMessage(content=m["texto"]) if m["papel"] == "user" else AIMessage (content=m["texto"])
        for m in st.session_state.mensagens[-10:]
    ]

    with st.chat_message("assistant"):
        with st.spinner("A pensar..."):
            resposta, fontes, pesquisa = responder(pergunta, historico)
        st.caption(f"Pesquisado: {pesquisa}")
        st.markdown(resposta)
        with st.expander("Fontes"):
            for fonte in fontes:
                st.write("-", fonte)

    st.session_state.mensagens.append({"papel": "user", "texto": pergunta})
    st.session_state.mensagens.append({"papel": "assistant", "texto": resposta, "fontes": fontes, "pesquisa": pesquisa})

    