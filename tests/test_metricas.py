from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from src.demanda.metricas import mae, rmse

REAL = [100, 120, 90, 110]
PREVISTO = [110, 115, 70, 110]


def test_mae_igual_ao_sklearn():
    assert abs(mae(REAL, PREVISTO) - mean_absolute_error(REAL, PREVISTO)) < 1e-9


def test_rmse_igual_ao_sklearn():
    assert abs(rmse(REAL, PREVISTO) - root_mean_squared_error(REAL, PREVISTO)) < 1e-9


def test_rmse_pune_mais_erro_grande():
    # mesmo erro total (20), mas concentrado num dia só
    espalhado = rmse([100, 100], [110, 110])
    concentrado = rmse([100, 100], [100, 120])
    assert concentrado > espalhado
