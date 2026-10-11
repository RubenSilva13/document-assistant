import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_chroma import Chroma

load_dotenv()

PASTA_DOCUMENTOS = "documents"
PASTA_DB = "chroma_db"
MODELO_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MODELO_LLM = "Qwen/Qwen3-32B"

def obter_embeddings():
    return HuggingFaceEmbeddings(model_name=MODELO_EMBEDDINGS)

def obter_vectorstore():
    return Chroma (
        collection_name="documents",
        embedding_function=obter_embeddings(),
        persist_directory=PASTA_DB,
    )

def obter_llm():
    llm = HuggingFaceEndpoint(
        repo_id = MODELO_LLM,
        task="conversational",
        temperature=0.2,
        max_new_tokens=1024,
        huggingfacehub_api_token=os.environ.get("HUFGGINGFACEHUB_API_TOKEN"),
    )
    return ChatHuggingFace(llm=llm)