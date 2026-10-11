from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import obter_vectorstore, obter_llm

vectorstore = obter_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

prompt = ChatPromptTemplate.from_messages ([
    ("system",
     "Responde em portugues de Portugal, usando apenas o contexto abaixo.\n"
     "Indica a fonte, ficheiro e pagina, de cada informaçao.\n"
     "Distingue o trabalho do autor do que é citado em outros trabalhos.\n"
     "Se a resposta nao estiver no contexto, diz que nao sabes.\n\n"
     "Contexto:\n{contexto}"),
     ("human", "{pergunta}"),

])


chain = prompt | obter_llm() | StrOutputParser()

def formatar(pedacos):
    """Junta os pedaços num so texto, cada um com o ficheiro e a pagina."""
    return "\n\n".join(
        f"[{p.metadata['fonte']}, p. {p.metadata['pagina']}]\n{p.page_content}"
        for p in pedacos
    )

while True:
    pergunta = input("\nPergunta: ")
    if pergunta.lower() == "sair":
        break
    if not pergunta.strip():
        continue

    pedacos = retriever.invoke(pergunta)
    resposta = chain.invoke({"contexto": formatar(pedacos), "pergunta": pergunta})
    print("\n" + resposta)

    fontes = sorted ({f"{p.metadata['fonte']} (p. {p.metadata['pagina']})" for p in pedacos})
    print("\n Fontes:", ", ". join(fontes))

    