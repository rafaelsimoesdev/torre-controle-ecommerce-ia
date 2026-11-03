"""O que o Gemini sabe sobre o banco: as tabelas permitidas e o que cada coluna significa.

A qualidade das respostas depende muito destas descrições. Coluna mal
descrita vira SQL errado, por melhor que seja o modelo.
"""

PROJETO_PUBLICO = "bigquery-public-data.thelook_ecommerce"

TABELAS = {
    "torre_controle.indicadores_diarios": {
        "descricao": "Uma linha por dia com os principais indicadores da operação. "
                     "Use esta tabela para perguntas sobre totais por dia, semana ou mês.",
        "colunas": {
            "dia": "data (DATE) a que os números se referem",
            # TODO: escreva, em português, o que cada coluna abaixo significa.
            # Você criou esta tabela na Fase 1: veja sql/10_indicadores_diarios.sql.
            # Seja específico: diga a unidade (pedidos, US$, proporção de 0 a 1)
            # e o que entra ou não na conta.
            "pedidos": "...",
            "cancelados": "...",
            "receita": "...",
            "pedidos_validos": "...",
            "ticket_medio": "...",
            "itens_vendidos": "...",
            "taxa_devolucao": "...",
            "entregues": "...",
            "taxa_atraso": "...",
        },
    },
    "torre_controle.rfm_clientes": {
        "descricao": "Uma linha por cliente com Recência, Frequência e Valor (RFM), "
                     "calculados até 22/10/2026. Use para perguntas sobre clientes.",
        "colunas": {
            "user_id": "identificador do cliente",
            "recencia": "dias entre a última compra do cliente e 22/10/2026",
            "frequencia": "quantidade de pedidos válidos do cliente (de 1 a 4)",
            "valor": "total gasto pelo cliente em pedidos válidos, em US$",
        },
    },
    f"{PROJETO_PUBLICO}.order_items": {
        "descricao": "Uma linha por item vendido. Use para perguntas sobre produtos, "
                     "categorias e marcas (junte com products por product_id).",
        "colunas": {
            "order_id": "pedido ao qual o item pertence",
            "user_id": "cliente que comprou",
            "product_id": "produto vendido (liga com products.id)",
            "status": "situação do item: Complete, Shipped, Processing, Cancelled ou Returned",
            "created_at": "data e hora da compra (TIMESTAMP)",
            "sale_price": "preço de venda do item, em US$",
        },
    },
    f"{PROJETO_PUBLICO}.products": {
        "descricao": "Catálogo de produtos.",
        "colunas": {
            "id": "identificador do produto",
            "name": "nome do produto",
            "category": "categoria (ex.: Jeans, Tops & Tees, Accessories)",
            "brand": "marca",
            "department": "departamento: Men ou Women",
            "retail_price": "preço de tabela, em US$",
        },
    },
}

REGRAS = """Regras sobre os dados:
- Os dados vão até 29/10/2026, mas de 23/10 a 29/10 existe um salto artificial
  criado pelo gerador da base. Para totais e médias, use dados até 22/10/2026,
  a menos que a pergunta peça explicitamente esses dias.
- Pedidos com status Cancelled ou Returned não contam como venda.
- Valores em dinheiro estão em dólar (US$).
"""


def montar_contexto() -> str:
    """Transforma as tabelas e regras num texto que vai junto da pergunta para o Gemini."""
    partes = ["Tabelas disponíveis no BigQuery (use exatamente estes nomes):\n"]
    for nome, tabela in TABELAS.items():
        partes.append(f"Tabela `{nome}`: {tabela['descricao']}")
        for coluna, descricao in tabela["colunas"].items():
            partes.append(f"  - {coluna}: {descricao}")
        partes.append("")
    partes.append(REGRAS)
    return "\n".join(partes)


if __name__ == "__main__":
    print(montar_contexto())
