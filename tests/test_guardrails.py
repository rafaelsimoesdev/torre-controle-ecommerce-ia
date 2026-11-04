import pytest

from src.assistente.guardrails import SQLInseguro, tabelas_usadas, validar

BOM = "SELECT SUM(receita) FROM torre_controle.indicadores_diarios WHERE dia <= '2026-10-22'"


def test_sql_bom_passa_e_ganha_limite():
    final = validar(BOM)
    assert "LIMIT 1000" in final
    assert "indicadores_diarios" in final


def test_with_passa():
    sql = """WITH mes AS (SELECT * FROM torre_controle.indicadores_diarios)
             SELECT COUNT(*) FROM mes"""
    validar(sql)


@pytest.mark.parametrize("sql", [
    "DELETE FROM torre_controle.rfm_clientes WHERE TRUE",
    "DROP TABLE torre_controle.rfm_clientes",
    "UPDATE torre_controle.rfm_clientes SET valor = 0 WHERE TRUE",
    "TRUNCATE TABLE torre_controle.rfm_clientes",
    "CREATE TABLE torre_controle.x AS SELECT 1",
])
def test_comandos_perigosos_sao_barrados(sql):
    with pytest.raises(SQLInseguro):
        validar(sql)


def test_dois_comandos_sao_barrados():
    with pytest.raises(SQLInseguro):
        validar(BOM + "; DROP TABLE torre_controle.rfm_clientes")


def test_perigo_escondido_depois_do_select_e_barrado():
    with pytest.raises(SQLInseguro):
        validar("SELECT 1; DELETE FROM torre_controle.rfm_clientes WHERE TRUE")


def test_tabela_nao_liberada_e_barrada():
    with pytest.raises(SQLInseguro):
        validar("SELECT * FROM `bigquery-public-data.thelook_ecommerce.users`")


def test_comentario_nao_engana():
    with pytest.raises(SQLInseguro):
        validar("-- só um SELECT inocente\nDROP TABLE torre_controle.rfm_clientes")


def test_tabelas_usadas_acha_join():
    sql = ("SELECT p.category FROM `bigquery-public-data.thelook_ecommerce.order_items` i "
           "JOIN `bigquery-public-data.thelook_ecommerce.products` p ON p.id = i.product_id")
    assert tabelas_usadas(sql) == {
        "bigquery-public-data.thelook_ecommerce.order_items",
        "bigquery-public-data.thelook_ecommerce.products",
    }
