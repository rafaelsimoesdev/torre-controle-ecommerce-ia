"""Pipeline diário da Torre de Controle.

1. confere se os dados chegaram (frescor)
2. atualiza a tabela de indicadores no BigQuery
3. roda o detector de anomalias
4. o Gemini escreve o resumo (se falhar, entra um texto padrão)
5. manda o relatório para o Telegram

Para rodar: python -m src.pipeline.diario
"""

import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from src.assistente import llm
from src.bq import cliente, consultar
from src.demanda.anomalias import carregar_serie_completa, detectar
from src.pipeline import telegram
from src.pipeline.frescor import dias_de_atraso, ultimo_dia_com_dados

load_dotenv()

SQL_INDICADORES = Path("sql/10_indicadores_diarios.sql")


def atualizar_indicadores() -> None:
    # "utf-8-sig" descarta o BOM, uma marca invisível que o PowerShell põe no começo
    # dos arquivos. O BigQuery recusa a consulta se ela começar com essa marca.
    cliente().query(SQL_INDICADORES.read_text(encoding="utf-8-sig")).result()


def numeros_do_dia(dia: date) -> dict:
    tabela = consultar(f"""
        SELECT receita, pedidos, ticket_medio, taxa_atraso
        FROM torre_controle.indicadores_diarios WHERE dia = '{dia}'
    """)
    return tabela.iloc[0].to_dict() if len(tabela) else {}


def status(dados: dict) -> str:
    """Um sinal no topo da mensagem para bater o olho e saber se precisa agir."""
    # TODO: devolva "ALERTA" se os dados estiverem atrasados OU se o dia for anomalia;
    #       senão, devolva "OK".
    # dica: if dados["dias_de_atraso"] > 0 or dados["anomalia"]:
    #           return "ALERTA"
    #       return "OK"
    if dados["dias_de_atraso"] > 0 or dados["anomalia"]:
        return "ALERTA"
    return "OK"


def texto_padrao(dados: dict) -> str:
    """Relatório sem IA: usado quando o Gemini não responde. O relatório nunca deixa de sair."""
    linhas = [
        f"Torre de Controle | {status(dados)}",
        f"Último dia com dados: {dados['dia']:%d/%m/%Y}",
    ]
    if dados["dias_de_atraso"] > 0:
        linhas.append(f"Dados atrasados: faltam {dados['dias_de_atraso']} dia(s) na base.")
    linhas.append(f"Pedidos: {dados['pedidos']:.0f} (esperado ~{dados['esperado']:.0f})")
    if dados.get("receita") is not None:
        linhas.append(f"Receita: US$ {dados['receita']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    if dados["anomalia"]:
        linhas.append(f"Anomalia: o dia fugiu {dados['desvio']:+.0%} do esperado.")
    return "\n".join(linhas)


def _numeros_legiveis(dados: dict) -> str:
    """Entrega os números já no formato de leitura, para o Gemini não escrever "40,0" ou "8,57 por cento"."""
    linhas = [
        f"- último dia com dados: {dados['dia']:%d/%m/%Y}",
        f"- dias de dados faltando: {dados['dias_de_atraso']}",
        f"- pedidos: {dados['pedidos']:.0f} (esperado: cerca de {dados['esperado']:.0f})",
        f"- desvio em relação ao esperado: {dados['desvio']:+.0%}",
        f"- anomalia: {'sim' if dados['anomalia'] else 'não'}",
    ]
    if dados.get("receita") is not None:
        linhas.append(f"- receita: US$ {dados['receita']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    if dados.get("ticket_medio") is not None:
        linhas.append(f"- ticket médio: US$ {dados['ticket_medio']:.2f}".replace(".", ","))
    if dados.get("taxa_atraso") is not None:
        linhas.append(f"- entregas atrasadas: {dados['taxa_atraso']:.0%}")
    return "\n".join(linhas)


def montar_relatorio(dados: dict) -> str:
    prompt = f"""Você escreve o relatório diário de operação de um e-commerce, em português,
para ler no celular. No máximo 6 linhas, frases curtas, sem markdown.
Comece exatamente com: "Torre de Controle | {status(dados)}".
Use SÓ os números abaixo, sem inventar nada. Dinheiro em US$ no formato 1.234,56.
Se houver atraso nos dados ou anomalia, diga isso primeiro e sugira o que conferir.

Números (já arredondados):
{_numeros_legiveis(dados)}"""
    try:
        return llm.gerar(prompt).strip()
    except Exception as erro:
        print(f"Gemini indisponível, usando o texto padrão: {erro}")
        return texto_padrao(dados)


def rodar() -> dict:
    hoje = date.today()
    ultimo_dia = ultimo_dia_com_dados()
    print(f"1/4 frescor: último dia com dados = {ultimo_dia}")

    atualizar_indicadores()
    print("2/4 tabela de indicadores atualizada")

    serie = detectar(carregar_serie_completa())
    dia = serie.iloc[-1]
    print(f"3/4 anomalias: {dia['dia']:%d/%m} nota {dia['nota']:.1f}")

    dados = {
        "dia": dia["dia"].date(),
        "dias_de_atraso": dias_de_atraso(ultimo_dia, hoje),
        "pedidos": float(dia["pedidos"]),
        "esperado": float(dia["esperado"]),
        "desvio": float(dia["desvio"]),
        "anomalia": bool(dia["anomalia"]),
        **numeros_do_dia(dia["dia"].date()),
    }
    texto = montar_relatorio(dados)
    enviado = telegram.enviar(texto)
    print(f"4/4 relatório {'enviado ao Telegram' if enviado else 'mostrado na tela'}")
    return dados


if __name__ == "__main__":
    try:
        rodar()
    except Exception as erro:
        # Falha visível: o GitHub Actions marca a execução como vermelha e manda e-mail.
        telegram.enviar(f"Torre de Controle | FALHA no pipeline diário: {erro}")
        print(f"FALHA: {erro}")
        sys.exit(1)
