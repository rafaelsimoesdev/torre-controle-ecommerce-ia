"""Interface de chat do assistente da Torre de Controle.

Para abrir: streamlit run app.py
"""

import streamlit as st

from src.assistente.assistente import perguntar

st.set_page_config(page_title="Torre de Controle · Assistente", page_icon="🗼", layout="centered")

EXEMPLOS = [
    "Qual foi a receita total de setembro de 2026?",
    "Quais as 5 categorias com maior receita em 2026, até 22/10?",
    "Quantos clientes fizeram mais de um pedido?",
    "Qual foi a proporção de entregas atrasadas em setembro de 2026?",
]

st.markdown("##### TORRE DE CONTROLE · ASSISTENTE")
st.title("Pergunte sobre a operação")
st.caption("Pergunta em português → SQL escrito pelo Gemini → travas de segurança → BigQuery → resposta. "
           "Base pública e sintética The Look E-commerce.")

with st.sidebar:
    st.subheader("Experimente")
    for exemplo in EXEMPLOS:
        if st.button(exemplo, width="stretch"):
            st.session_state["pergunta_exemplo"] = exemplo
    st.divider()
    st.caption("Só consultas de leitura, só tabelas liberadas, até 1 GB por pergunta. "
               "Na avaliação com 25 perguntas, o assistente acertou 25.")

if "historico" not in st.session_state:
    st.session_state["historico"] = []


def mostrar(item: dict) -> None:
    with st.chat_message("user"):
        st.write(item["pergunta"])
    with st.chat_message("assistant"):
        # "$" vira fórmula matemática no Streamlit; a barra faz ele aparecer como texto normal
        st.markdown(item["resposta"].replace("$", "\\$"))
        # TODO: mostre o SQL usado dentro de uma caixa que abre e fecha, só se houver SQL.
        # dica: if item["sql"]:
        #           with st.expander("Ver o SQL usado"):
        #               st.code(item["sql"], language="sql")
        if item["sql"]:
            with st.expander("Ver o SQL usado"):
                st.code(item["sql"], language="sql")
        if item["resultado"] is not None and len(item["resultado"]):
            with st.expander("Ver a tabela do resultado"):
                st.dataframe(item["resultado"], hide_index=True)


for item in st.session_state["historico"]:
    mostrar(item)

pergunta = st.chat_input("Ex.: qual foi o ticket médio de setembro de 2026?")
pergunta = pergunta or st.session_state.pop("pergunta_exemplo", None)

if pergunta:
    with st.spinner("Escrevendo o SQL, conferindo a segurança e consultando o BigQuery..."):
        try:
            saida = perguntar(pergunta)
        except Exception as erro:  # Gemini fora do ar, sem internet etc.
            saida = {"resposta": f"Não consegui responder agora: {erro}", "sql": "", "resultado": None}
    item = {"pergunta": pergunta, **saida}
    st.session_state["historico"].append(item)
    mostrar(item)
