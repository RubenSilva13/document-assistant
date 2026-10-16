#  Document Assistant

Assistente de perguntas e respostas sobre documentos PDF, com interface web, pesquisa semântica e citação de fontes. Construído com **RAG** (Retrieval-Augmented Generation): o modelo responde **apenas** com base nos documentos carregados, indica de onde tirou cada informação e diz "Não sei" quando a resposta não está lá.

A qualidade do sistema é **medida** com um conjunto de teste e avaliação automática (LLM como juiz).

## Funcionalidades

- **Upload de PDFs** pela interface, com processamento incremental (os ficheiros já processados não são reprocessados)
- **Base de conhecimento persistente** em ChromaDB
- **Chat com memória** da conversa
- **Reformulação da pergunta** com base no histórico ("e em que ano?" → "Em que ano fez o Ruben Erasmus?")
- **Citações numeradas** `[n]` e lista apenas das fontes realmente usadas (ficheiro e página)
- **Avaliação automática** da pesquisa e das respostas

## Arquitetura

```
                ┌──────────────────── Ingestão ─────────────────────┐
PDFs ──► texto por página ──► remoção das referências ──► pedaços (1000 car.)
                                                              │
                                                     embeddings (bge-m3)
                                                              │
                                                              ▼
                                                         ChromaDB
                                                              │
                ┌──────────────────── Consulta ─────────────────┼───┐
Pergunta + histórico ──► reformulação (LLM) ──► pesquisa (k = 6)  │
                                                              │
                         contexto numerado [1]..[6] ◄─────────┘
                                       │
                                       ▼
                     LLM (gpt-oss-120b via Groq) ──► resposta com [n]
                                       │
                                       ▼
                         fontes citadas (ficheiro + página)
```

## Tecnologias

| Componente | Escolha |
|---|---|
| Interface | Streamlit |
| Orquestração | LangChain |
| Base vetorial | ChromaDB |
| Embeddings | `BAAI/bge-m3` (multilingue, corre localmente) |
| LLM | `openai/gpt-oss-120b` via Groq |
| PDFs | pypdf |

## Avaliação

O conjunto de teste (`avaliacao/perguntas.json`) tem **16 perguntas** escritas à mão sobre três documentos de temas diferentes: factuais, numéricas, sobre tabelas, vagas e **3 perguntas sem resposta** nos documentos, para medir alucinações.

- `avaliar_pesquisa.py` — mede se o retriever encontra a página certa (*hit rate* e MRR), sem usar o LLM.
- `avaliar_respostas.py` — compara cada resposta com a esperada, usando o LLM como juiz (CORRETA / PARCIAL / ERRADA).

### Experiência: número de pedaços recuperados (k)

| k | Pesquisa (hit rate) | MRR | Corretas | Parciais | Erradas | Alucinações |
|---|---|---|---|---|---|---|
| 1 | 11/13 | 0.85 | 7/16 | 6 | 3 | 0/3 |
| 2 | 13/13 | 1.00 | 11/16 | 4 | 1 | 0/3 |
| 3 | 13/13 | 1.00 | 13/16 | 3 | 0 | 0/3 |
| 4 | 13/13 | 1.00 | 14/16 | 2 | 0 | 0/3 |
| **6** | **13/13** | **1.00** | **15–16/16** | 0–1 | 0 | **0/3** |

**Conclusões:**
- Com k = 2 a pesquisa já tem nota máxima, mas as respostas continuam incompletas. Acertar na página não chega: a informação de uma resposta (tabelas, listas, resumos) está muitas vezes espalhada por vários pedaços.
- A configuração escolhida é **k = 6**, a única sem respostas parciais de forma consistente.
- **Zero alucinações** em todas as configurações: com pouco contexto, o sistema diz "Não sei" em vez de inventar.
- Os resultados variam ±1 pergunta entre execuções; diferenças pequenas devem ser lidas com cuidado.

## O que aprendi

- **Medir antes e depois.** Trocar para um modelo de embeddings mais forte, sozinho, não melhorou a pesquisa — só a avaliação o mostrou.
- **A qualidade dos dados conta mais do que o modelo.** As listas de referências dos artigos, cheias de palavras-chave, "ganhavam" a pesquisa a pedaços úteis. Excluí-las na ingestão resolveu o problema.
- **O retriever não vê o histórico.** Perguntas como "e do mesmo?" falhavam até ser adicionada a reformulação da pergunta.
- **O modelo nem sempre segue o formato pedido** (citava com `【2】` em vez de `[2]`); o código tem de ser tolerante a variações.
- **Avaliar a pesquisa e as respostas separadamente** permite saber onde está o problema: se o modelo não recebeu a informação, ou se a recebeu e respondeu mal.

## Instalação

```bash
git clone https://github.com/RubenSilva13/document-assistant.git
cd document-assistant
python -m venv venv
venv\Scripts\activate        
pip install -r requirements.txt
```

Copia `.env.example` para `.env` e coloca a tua chave da API do Groq (console.groq.com).

## Utilização

```bash
streamlit run app.py
```

Carrega PDFs na barra lateral, carrega em **Processar** e faz perguntas no chat.

Também é possível usar pelo terminal:

```bash
python ingestao.py     
python consulta.py     
```

Avaliação:

```bash
python avaliacao/avaliar_pesquisa.py
python avaliacao/avaliar_respostas.py
```

## Estrutura

```
document-assistant/
├── app.py                 # interface Streamlit
├── config.py              # modelos, base de dados e parâmetros (k)
├── ingestao.py            # leitura de PDFs, divisão em pedaços e indexação
├── consulta.py            # reformulação, pesquisa, resposta e citações
├── avaliacao/
│   ├── perguntas.json     # conjunto de teste
│   ├── avaliar_pesquisa.py
│   └── avaliar_respostas.py
└── requirements.txt
```

## Limitações

- O juiz da avaliação é o mesmo modelo que responde, o que pode torná-lo mais tolerante com as próprias respostas.
- O conjunto de teste é pequeno (16 perguntas, 3 documentos); com mais documentos sobre temas semelhantes, a pesquisa seria mais exigente.
- A exclusão das referências usa uma regra simples (o título da secção sozinho numa linha), pensada para artigos científicos.
- Perguntas ambíguas podem dar respostas incompletas (por exemplo, "valores medidos" sem especificar quais).

## Próximos passos

- [ ] Deploy online
- [ ] Ingestão de notas em Markdown (por exemplo, um vault do Obsidian)
- [ ] Versão 100% local com Ollama, para documentos privados