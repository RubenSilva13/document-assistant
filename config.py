import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from functools import lru_cache


load_dotenv()

PASTA_DOCUMENTOS = "documents"
PASTA_DB = "chroma_db"
MODELO_EMBEDDINGS = "BAAI/bge-m3"
MODELO_LLM = "openai/gpt-oss-120b"
K_PEDACOS = 6

@lru_cache
def obter_embeddings():
    return HuggingFaceEmbeddings(
        model_name=MODELO_EMBEDDINGS,
        encode_kwargs={"normalize_embeddings": True},
        )

@lru_cache
def obter_vectorstore():
    return Chroma (
        collection_name="documents",
        embedding_function=obter_embeddings(),
        persist_directory=PASTA_DB,
    )

#def obter_llm():
    llm = HuggingFaceEndpoint(
        repo_id = MODELO_LLM,
        task="conversational",
        temperature=0.2,
        max_new_tokens=1024,
        huggingfacehub_api_token=os.environ.get("HUFGGINGFACEHUB_API_TOKEN"),
    )


    return ChatHuggingFace(llm=llm)


def obter_llm():
    return ChatGroq(
        model=MODELO_LLM,
        temperature=0.2,
        api_key=os.environ.get("GROQ_API_KEY"),
    )