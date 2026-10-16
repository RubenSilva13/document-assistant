import json
import os
import sys
import time

pasta_avaliacao = os.path.dirname(os.path.abspath(__file__))
pasta_projeto = os.path.dirname(pasta_avaliacao)
sys.path.insert(0, pasta_projeto)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import obter_llm
from consulta import responder

caminho_json = os.path.join(pasta_avaliacao, "perguntas.json")
with open(caminho_json, encoding = "utf-8") as ficheiro:
    perguntas = json.load(ficheiro)

prompt_juiz = ChatPromptTemplate.from_messages([
    ("system",
     "És um avaliador rigoroso de um sistema de perguntas e respostas sobre documentos.\n"
     "Recebes uma pergunta, a resposta esperada (escrita por um humano) e a resposta do sistema.\n"
     "Avalia se a resposta do sistema está correta no SIGNIFICADO; não precisa de usar as mesmas palavras.\n\n"
     "Regras:\n"
     "- CORRETA: contém a informação essencial da resposta esperada, sem erros.\n"
     "- PARCIAL: tem parte da informação, ou falta algum valor ou elemento importante.\n"
     "- ERRADA: tem informação errada, ou diz que não sabe quando havia resposta.\n"
     "- Se a resposta esperada for 'SEM RESPOSTA', a resposta do sistema é CORRETA se disser que não sabe "
     "ou que a informação não está nos documentos, e ERRADA se der uma resposta.\n\n"
     "Responde EXATAMENTE neste formato, em duas linhas:\n"
     "VEREDITO: CORRETA, PARCIAL ou ERRADA\n"
     "JUSTIFICAÇÃO: uma frase curta"),
    ("human",
     "Pergunta: {pergunta}\n\n"
     "Resposta esperada: {esperada}\n\n"
     "Resposta do sistema: {resposta}"),
])

juiz = prompt_juiz | obter_llm() | StrOutputParser()

def ler_veredito (texto_do_juiz):
    """Le o texto do juiz e devolve, veredito e justificaçao"""
    veredito = "DESCONHECIDO"
    justificacao = ""

    linhas = texto_do_juiz.splitlines()
    for linha in linhas:
        linha = linha.strip()
        linha_maiusculas = linha.upper()

        if linha_maiusculas.startswith("VEREDITO"):
            valor = linha_maiusculas.split(":", 1)[1]

            if "ERRADA" in valor or "INCORRETA" in valor:
                veredito = "ERRADA"
            elif "PARCIAL" in valor:
                veredito = "PARCIAL"
            elif "CORRETA" in valor:
                veredito = "CORRETA"
        if linha_maiusculas.startswith("JUSTIFICA"):
            justificacao = linha.split(":", 1)[1].strip()

    return veredito, justificacao


contagem = {"CORRETA": 0, "PARCIAL": 0, "ERRADA": 0, "DESCONHECIDO": 0}
total_sem_resposta = 0
alucinacoes = 0


for numero, item in enumerate(perguntas, start=1):
    pergunta = item["pergunta"]

    if item["resposta_esperada"] is None:
        esperada = "SEM RESPOSTA"
        total_sem_resposta = total_sem_resposta + 1
    else:
        esperada = item["resposta_esperada"]

    resposta, fontes, pesquisa = responder(pergunta)

    texto_do_juiz = juiz.invoke({
        "pergunta": pergunta,
        "esperada": esperada,
        "resposta": resposta,
    })

    veredito, justificacao = ler_veredito(texto_do_juiz)

    contagem[veredito] = contagem[veredito] + 1

    if esperada == "SEM RESPOSTA" and veredito == "ERRADA":
        alucinacoes = alucinacoes + 1

    if veredito =="CORRETA":
        simbolo ="✅"
    elif veredito =="PARCIAL":
        simbolo = "🟡"
    else:
        simbolo = "❌"

    print(f"\n{simbolo} {numero}. {pergunta}")
    print(f"  Veredito: {veredito} - {justificacao}")
    if veredito != "CORRETA":
        print(f"  Esperada: {esperada}")
        print(f"  Sistema:  {resposta[:300]}")

    time.sleep(5)


total = len(perguntas)
total_com_respostas = total - total_sem_resposta

print(f"Corretas:   {contagem['CORRETA']}/{total}")
print(f"Parciais:   {contagem['PARCIAL']} /{total} ")
print(f"Erradas:   {contagem['ERRADA']} / {total}")
if contagem["DESCONHECIDO"] > 0:
    print(f"Sem veredito: {contagem['DESCONHECIDO']}")
print(f"Alucinaçoes nas perguntas sem resposta: {alucinacoes}/{total_sem_resposta}")