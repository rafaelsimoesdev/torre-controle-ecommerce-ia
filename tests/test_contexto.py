from src.assistente.contexto import TABELAS, montar_contexto


def test_toda_coluna_tem_descricao():
    for nome, tabela in TABELAS.items():
        for coluna, descricao in tabela["colunas"].items():
            assert descricao and descricao != "...", f"{nome}.{coluna} está sem descrição"
            assert len(descricao) >= 15, f"{nome}.{coluna}: descrição curta demais"


def test_contexto_cita_todas_as_tabelas():
    texto = montar_contexto()
    for nome in TABELAS:
        assert nome in texto
