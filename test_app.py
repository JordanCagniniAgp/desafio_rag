"""Testes sem rede: a IA e os embeddings são substituídos por versões falsas."""
import app

TRECHOS = [{"arquivo": "veiculos.pdf", "secao": "6. Multas", "pagina": 2, "texto": "Multas são do próprio condutor."},
           {"arquivo": "ferias.pdf", "secao": "2. Antecedência", "pagina": 1, "texto": "Peça férias com 30 dias de antecedência."}]


def embed(textos):  # "multa" e "férias" viram eixos; o resto fica longe de tudo
    return [[1.0 if "ulta" in t else 0.0, 1.0 if "érias" in t else 0.0, 0.1] for t in textos]


def ia(resposta):
    chamadas = []
    def gerar(sistema, usuario):
        chamadas.append((sistema, usuario))
        return resposta
    return gerar, chamadas


def responder(pergunta, resposta):
    gerar, chamadas = ia(resposta)
    return (*app.responder(pergunta, TRECHOS, embed(t["texto"] for t in TRECHOS), embed, gerar), chamadas)


def test_le_os_tres_pdfs_com_pagina():
    trechos = app.ler_documentos()
    assert {t["arquivo"] for t in trechos} == {p.name for p in (app.PASTA / "documentos").glob("*.pdf")}
    assert all(t["pagina"] >= 1 and t["secao"] for t in trechos)


def test_resposta_com_fonte():
    texto, fontes, chamadas = responder("Quem paga a multa?", "O próprio condutor [1].")
    assert texto == "O próprio condutor [1]." and fontes[0][1]["arquivo"] == "veiculos.pdf"
    assert "Multas são do próprio condutor." in chamadas[0][1]


def test_resposta_sem_citacao_vira_recusa():
    assert responder("Quem paga a multa?", "A empresa paga tudo.")[:2] == (app.RECUSA, [])


def test_sem_evidencia_vira_recusa():
    assert responder("Quem paga a multa?", app.SEM)[:2] == (app.RECUSA, [])


def test_cumprimento_tem_resposta_natural_sem_documentos():
    texto, fontes, chamadas = responder("olá", "Olá! Posso ajudar com reembolso, veículos e férias.")
    assert texto.startswith("Olá!") and fontes == [] and chamadas[0][0] == app.PROMPT_CONVERSA


def test_fora_do_assunto_com_numero_vira_recusa():
    assert responder("Qual a capital da França?", "Paris, com 2 milhões de habitantes.")[0] == app.RECUSA
