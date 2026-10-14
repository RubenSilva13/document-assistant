from config import obter_vectorstore

perguntas = [
    "qual o conceito do artigo?",
    "o abstract do artigo sobre LiDAR tem que objetivo?",
    "que iPhone foi usado nos testes?",
    "onde fez o Ruben Erasmus?",
    "qual foi a rentabilidade da estratégia de cripto?",
]

retriever = obter_vectorstore().as_retriever(search_kwargs={"k": 3})

for p in perguntas:
    pedacos = retriever.invoke(p)
    paginas = [f"{d.metadata['fonte'][:20]}… p.{d.metadata['pagina']}" for d in pedacos]
    print(f"\n❓ {p}")
    for pg in paginas:
        print("   ", pg)