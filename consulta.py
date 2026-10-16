import re
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from config import obter_vectorstore, obter_llm, K_PEDACOS



prompt = ChatPromptTemplate.from_messages ([
    ("system",
     "Responde em portugues de Portugal, usando apenas o contexto abaixo.\n"
     "Cada excerto do contexto tem um numero entre parentese retos, por exemplo [2].\n"
     "Depois de cada informalao, cita o numero do excerto de onde a tiraste, por exemplo: "
     "'O dispositivo usado foi o iphone 14 pro [3].'\n"
     "Usa apenas este formato de citaçao; nao escrevas nomes de ficheiros nem paginas.\n"
     "Distingue o trabalho do autor do que é citado de outros trabalhos.\n"
     "Se a resposta nao estiver no contexto, diz que nao sabes e nao cites nada.\n"
     "Contexto:\n{contexto}"),
     MessagesPlaceholder(variable_name="historico"),
     ("human", "{pergunta}"),

])


chain = prompt | obter_llm() | StrOutputParser()

prompt_reformular = ChatPromptTemplate.from_messages([
    ("system",
    "Recebes uma conversa e uma nova pergunta do utilizador.\n"
    "Reescreve a nova pergunta para que seja autonoma e completa, "
    "percetivel sem a conversa, substitui 'isso, 'do mesmo', 'ele', pelo que referem.\n" 
    "Se a pergunta ja for autonoma, devolve-a igual\n"
    "Responde apenas com a pergunta reescrita, sem explicaçoes."),
    MessagesPlaceholder(variable_name="historico"),
    ("human","{pergunta}"),
])


chain_reformular = prompt_reformular | obter_llm() | StrOutputParser()



def reformular(pergunta, historico):
    """Transforma um pergunta dependente do contexto numa pergunta autonoma."""
    if not historico:
        return pergunta
    return chain_reformular.invoke({"historico": historico, "pergunta": pergunta}).strip()


def formatar(pedacos):
    """Junta os pedaços num so texto, numerados: [1], [2], ..."""
    return "\n\n".join(
        f"[{i}]  ({p.metadata['fonte']}, p. {p.metadata['pagina']})\n{p.page_content}"
        for i, p in enumerate(pedacos, start=1)
    )

def responder(pergunta, historico=None):
    """Responde a uma pergunta com base nos documentos. Devolve: resposta, fontes, pergunta_pesquisada"""
    historico = historico or []

    pergunta_pesquisada = reformular(pergunta, historico)

    retriever = obter_vectorstore().as_retriever(search_kwargs={"k": K_PEDACOS})
    pedacos = retriever.invoke(pergunta_pesquisada)

    resposta = chain.invoke ({
        "contexto": formatar(pedacos),
        "historico": historico or [],
        "pergunta": pergunta,
    })

    resposta = resposta.replace("【", "[").replace("】", "]")

    citados = sorted({int(n) for n in re.findall(r"\[(\d+)\]", resposta)})
    usados = [n for n in citados if 1 <= n <= len(pedacos)]

    fontes = [
        f"[{n}] {pedacos[n-1].metadata['fonte']} (p. {pedacos[n - 1].metadata['pagina']})"
        for n in usados
    ]
    return resposta, fontes, pergunta_pesquisada

if __name__ == "__main__":
    historico = []
    while True:
        pergunta = input ("\nPergunta: ")
        if pergunta.lower() == "sair":  
            break
        if not pergunta.strip():
            continue

        resposta, fontes, pesquisa = responder(pergunta, historico)  
        print(f"\n Pesquisado: {pesquisa}")
        print("\n" + resposta)
        print("\n Fontes", ", ". join(fontes))

        historico += [HumanMessage(content=pergunta), AIMessage(content=resposta)]
        historico = historico[-10:]