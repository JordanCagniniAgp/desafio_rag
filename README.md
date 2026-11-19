# Assistente de Políticas Internas (RAG)

Assistente em Python que responde perguntas em linguagem natural sobre os três PDFs de
`documentos/` (Política de Reembolso, Política de Utilização de Veículos e Procedimento de
Solicitação de Férias). Toda resposta cita a fonte; se os documentos não tratam do assunto,
o assistente avisa em vez de inventar. Tudo fica em um único arquivo, `app.py`, com menos de 200 linhas.

## Instalação e execução

Requisitos: Python 3.10+ e uma chave da API do Gemini.

```bash
pip install -r requirements.txt
copy .env.example .env        # depois preencha GEMINI_API_KEY no .env
streamlit run app.py          # tela web em http://localhost:8501 (ou dois cliques em iniciar.bat)
python app.py --validar       # as 6 perguntas de validação + 1 de controle, no terminal
python -m pytest -q           # testes automáticos, sem rede e sem chave
```

## Arquitetura

```
PDFs ──► 1. Processamento ──► 2. Recuperação ──► 3. IA (Gemini) ──► 4. Confiabilidade ──► 5. Tela
         trechos por seção    embeddings +       resposta com       valida citações       Streamlit
         e por FAQ            cosseno, top 6     citações [n]       ou recusa
```

1. **Processamento** (`ler_documentos`): o texto é extraído com `pypdf`; cabeçalhos e rodapés
   (linhas repetidas em todas as páginas) são removidos. Cada seção numerada ("3. Como solicitar")
   e cada pergunta do FAQ viram um trecho, com arquivo, seção e página: 58 trechos no total.
2. **Recuperação** (`responder`): pergunta e trechos viram vetores com `gemini-embedding-001`;
   os 6 trechos com maior similaridade de cosseno seguem para a IA. Não há banco vetorial:
   58 vetores cabem em memória e a comparação é instantânea.
3. **Integração com IA:** pergunta e trechos vão ao `gemini-3.1-flash-lite` pela API compatível
   com OpenAI. Se ele demorar mais de 30 s ou falhar, o `gemini-3.5-flash-lite` assume.
4. **Confiabilidade:**
   - se nenhum trecho passa de 0,65 de similaridade, a IA não recebe documento nenhum: só
     responde cumprimentos ("olá") e recusa o resto (resposta com número ou longa vira recusa);
   - o prompt obriga a usar só os trechos e citar `[n]` em cada frase; se o documento diz que não
     define algo (ex.: limite de combustível), a resposta diz isso e onde consultar;
   - resposta sem nenhuma citação válida, ou com o marcador `SEM_EVIDENCIA`, vira recusa.
5. **Interface:** conversa em Streamlit, com as perguntas de validação em um botão, as fontes de
   cada resposta (arquivo, seção, página e texto) e os PDFs para baixar na barra lateral.

**Tecnologias:** Python, `pypdf` (leitura), `openai` (cliente da API do Gemini), `python-dotenv`
(chave no `.env`), `streamlit` (tela) e `pytest` (testes com IA falsa).

## Perguntas de validação

| Pergunta | Resposta obtida | Fonte |
|---|---|---|
| 01. Prazo para solicitar o reembolso de viagem | Até 5 dias úteis após o fim da viagem | Reembolso, seção 6 |
| 02. Reembolso sem comprovante fiscal | Não, salvo autorização formal da diretoria | Reembolso, seção 5 e FAQ |
| 03. Multas de veículos corporativos | Do próprio condutor | Veículos, seção 6 e FAQ |
| 04. Procedimento de férias | Canal oficial do RH, 30 dias de antecedência | Férias, seções 2 e 3 |
| 05. Veículos em atividades pessoais | Não é permitido | Veículos, seção 2 e FAQ |
| 06. Limite de combustível por viagem | Os documentos não definem; consultar a área de frota | Veículos, FAQ |
| Controle: valor do vale-alimentação | Recusa: não está nos documentos | — |

A redação muda entre execuções, porque o modelo de IA não é determinístico; o conteúdo e as
fontes se mantêm.

## Tratamento de erros

- Sem chave ou chave inválida: a tela mostra o aviso para conferir `GEMINI_API_KEY`.
- IA lenta ou sobrecarregada: tempo-limite de 30 s e troca para o modelo reserva; se os dois
  falharem, a tela mostra que não conseguiu consultar a IA (no `--validar`, a pergunta é
  registrada com o erro e as demais continuam).

## Limitações

- A citação garante que a frase aponta um trecho, não que ela decorre dele; por isso as fontes
  ficam sempre visíveis.
- O limiar de 0,65 foi calibrado nestes três documentos.
- Sem OCR (PDF escaneado não é lido) e sem memória de conversa.
- Pergunta e trechos são enviados à API do Google.
