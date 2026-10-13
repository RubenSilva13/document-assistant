from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from config import obter_vectorstore, obter_llm
from langchain_core.messages import HumanMessage, AIMessage



prompt = ChatPromptTemplate.from_messages ([
    ("system",
     "Responde em portugues de Portugal, usando apenas o contexto abaixo.\n"
     "Indica a fonte, ficheiro e pagina, de cada informaçao.\n"
     "Distingue o trabalho do autor do que é citado em outros trabalhos.\n"
     "Se a resposta nao estiver no contexto, diz que nao sabes.\n\n"
     "Contexto:\n{contexto}"),
     MessagesPlaceholder(variable_name="historico"),
     ("human", "{pergunta}"),

])


chain = prompt | obter_llm() | StrOutputParser()

def formatar(pedacos):
    """Junta os pedaços num so texto, cada um com o ficheiro e a pagina."""
    return "\n\n".join(
        f"[{p.metadata['fonte']}, p. {p.metadata['pagina']}]\n{p.page_content}"
        for p in pedacos
    )

def responder(pergunta, historico=None):
    """Responde a uma pergunta com base nos documentos. Devolve: resposta, fontes."""
    retriever = obter_vectorstore().as_retriever(search_kwargs={"k": 6})
    pedacos = retriever.invoke(pergunta)

    resposta = chain.invoke ({
        "contexto": formatar(pedacos),
        "historico": historico or [],
        "pergunta": pergunta,
    })

    fontes = sorted({f"{p.metadata['fonte']} (p. {p.metadata['pagina']})" for p in pedacos})
    return resposta, fontes

if __name__ == "__main__":
    historico = []
    while True:
        pergunta = input ("\nPergunta: ")
        if pergunta.lower() == "sair":  
            break
        if not pergunta.strip():
            continue

        resposta, fontes = responder(pergunta, historico)  
        print("\n" + resposta)
        print("\n Fontes", ", ". join(fontes))

        historico += [HumanMessage(content=pergunta), AIMessage(content=resposta)]
        historico = historico[-10:]