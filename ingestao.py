import os
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import PASTA_DOCUMENTOS, obter_vectorstore


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

def ingerir():
    vectorstore = obter_vectorstore()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    pdfs = [f for f in os.listdir(PASTA_DOCUMENTOS) if f.lower().endswith(".pdf")]
    if not pdfs:
        print(f"Nao ha pdfs na pasta '{PASTA_DOCUMENTOS}'")
        return
    for nome in pdfs:
        if ja_processado(vectorstore, nome):
            print(f" {nome} ja esta na base.")
            continue

        paginas = ler_pdf(os.path.join(PASTA_DOCUMENTOS, nome))
        pedacos = splitter.split_documents(paginas)
        ids = [f"{nome}-{i}" for i in range (len(pedacos))]

        vectorstore.add_documents(pedacos, ids=ids)
        print(f" {nome}: {len(paginas)} paginas, {len(pedacos)} padaços")



if __name__ == "__main__":
    ingerir()

