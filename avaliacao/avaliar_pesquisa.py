import json
import os
import sys 

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import obter_vectorstore, K_PEDACOS

with open(os.path.join(os.path.dirname(__file__), "perguntas.json"), encoding="utf-8") as f:
    perguntas = json.load(f)

retriever = obter_vectorstore().as_retriever(search_kwargs={"k": K_PEDACOS})
com_resposta = [p for p in perguntas if p["fonte"]]

acertos = 0
soma_rr = 0

for p in com_resposta:
    pedacos = retriever.invoke(p["pergunta"])

    posicao = None
    for i, d in enumerate(pedacos, start=1):
        if d.metadata["fonte"] == p["fonte"] and d.metadata["pagina"] in p["paginas"]: 
            posicao = 1
            break
    if posicao:
        acertos += 1
        soma_rr += 1 / posicao
        print(f" [{posicao}] {p['pergunta']}")
    else:
        vieram = ", ".join(f"{d.metadata['fonte'][:15]}... p. {d.metadata['pagina']}" for d in pedacos)
        print(f"x     {p['pergunta']}")
        print(f"      esperado: p.{p['paginas']}  | vieram: {vieram}")


        
n = len(com_resposta)
print(f"\n Hir rate @{K_PEDACOS}: {acertos}/{n}  ({acertos / n:.0%})")
print(f"MRR: {soma_rr /n:.2f}")


