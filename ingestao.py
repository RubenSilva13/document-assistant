import os
import re
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import PASTA_DOCUMENTOS, obter_vectorstore




splitter = RecursiveCharacterTextSplitter(chunk_size= 1000, chunk_overlap=200)

def introduzir_ficheiro(caminho):
    """Processa um pdf. Devolve o numero de pedaços criados, 0 se ja estava na base."""
    vectorstore = obter_vectorstore()
    nome = os.path.basename(caminho)

    if ja_processado(vectorstore, nome):
        return 0

    paginas = ler_pdf(caminho)
    pedacos = splitter.split_documents(paginas)
    ids = [f"{nome}-{i}" for i in range (len(pedacos))]
    vectorstore.add_documents(pedacos, ids=ids)
    return len(pedacos)


def listar_documentos():
    """Devolve os nomes dos ficheiros que estao na base de dados"""
    dados = obter_vectorstore().get(include=["metadatas"])
    return sorted({m["fonte"] for m in dados ["metadatas"]})

def introduzir():
    """Processa todos os pdfs da pasta"""
    pdfs = [f for f in os.listdir(PASTA_DOCUMENTOS) if f.lower().endswith(".pdf")]
    if not pdfs:
        print(f"Nao ha pdfs na pasta '{PASTA_DOCUMENTOS}'.")
        return

    for nome in pdfs:
        n = introduzir_ficheiro(os.path.join(PASTA_DOCUMENTOS, nome))
        if n:
            print(f" Novo: {nome}: {n} pedaços")
        else:
            print(f" {nome} ja esta na base de dados.")




FIM_DO_CONTEUDO = re.compile(
     r"^\s*(References|Referências|Bibliography|Bibliografia|Acknowledge?ments|Agradecimentos)\s*$",
     re.IGNORECASE | re.MULTILINE
)




def ler_pdf(caminho):
    """LE um pdf pagina a pagina, parando nas referencias/agradecimentos"""
    nome= os.path.basename(caminho)
    reader = PdfReader(caminho)
    documentos = []

    for i, pagina in enumerate(reader.pages):
        texto = pagina.extract_text() or ""

        fim = FIM_DO_CONTEUDO.search(texto)
        if fim:
            texto = texto[:fim.start()]

        if texto.strip():
            documentos.append(Document(
                page_content=texto,
                metadata={"fonte": nome, "pagina": i+1},
            ))

        if fim:
            break

    return documentos


def ja_processado(vectorstore, nome):
    """Verifica se o ficheiro ja esta na base de dados."""
    existentes = vectorstore = vectorstore.get(where={"fonte": nome}, limit=1)
    return len(existentes["ids"]) > 0


if __name__ == "__main__":
    introduzir()

