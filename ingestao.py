import os
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
    """Precessa todos os pdfs da pasta"""
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



def ler_pdf(caminho):
    """LE um pdf e devolve um documento por pagina, com o nome do ficheiro e a pagina."""
    nome= os.path.basename(caminho)
    reader = PdfReader(caminho)
    return [
        Document(
            page_content=pagina.extract_text() or "",
            metadata={"fonte": nome, "pagina": i+1},
        )
        for i, pagina in enumerate(reader.pages)
    ]

def ja_processado(vectorstore, nome):
    """Verifica se o ficheiro ja esta na base de dados."""
    existentes = vectorstore = vectorstore.get(where={"fonte": nome}, limit=1)
    return len(existentes["ids"]) > 0


if __name__ == "__main__":
    introduzir()

