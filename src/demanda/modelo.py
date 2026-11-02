"""Treina o LightGBM de demanda, compara com o baseline e registra no MLflow."""

import lightgbm as lgb
import mlflow
import pandas as pd

from src.demanda.dados import separar_treino_teste
from src.demanda.features import FEATURES, criar_features
from src.demanda.metricas import mae, rmse

PARAMETROS = {
    "n_estimators": 400,
    "learning_rate": 0.03,
    "num_leaves": 15,
    "min_child_samples": 10,
    "random_state": 42,
}


def treinar(treino: pd.DataFrame) -> lgb.LGBMRegressor:
    modelo = lgb.LGBMRegressor(**PARAMETROS, verbose=-1)
    modelo.fit(treino[FEATURES], treino["alvo"])
    return modelo


def prever(modelo: lgb.LGBMRegressor, df: pd.DataFrame) -> pd.Series:
    # o modelo devolve a proporção; multiplicando pela média volta a ser pedidos
    return pd.Series(modelo.predict(df[FEATURES]), index=df.index) * df["media_28"]


if __name__ == "__main__":
    serie = pd.read_parquet("dados/serie_pedidos.parquet")
    df = criar_features(serie).dropna()  # os primeiros dias não têm histórico
    treino, teste = separar_treino_teste(df)

    modelo = treinar(treino)
    previsao = prever(modelo, teste)

    resultado = {
        "baseline_mae": mae(teste["pedidos"], teste["lag_7"]),
        "baseline_rmse": rmse(teste["pedidos"], teste["lag_7"]),
        "lightgbm_mae": mae(teste["pedidos"], previsao),
        "lightgbm_rmse": rmse(teste["pedidos"], previsao),
    }

    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("previsao-demanda")
    with mlflow.start_run(run_name="lightgbm"):
        mlflow.log_params(PARAMETROS)
        mlflow.log_param("features", ", ".join(FEATURES))
        mlflow.log_metrics(resultado)

    ganho = 1 - resultado["lightgbm_mae"] / resultado["baseline_mae"]
    print(f"Baseline | MAE: {resultado['baseline_mae']:.1f} | RMSE: {resultado['baseline_rmse']:.1f}")
    print(f"LightGBM | MAE: {resultado['lightgbm_mae']:.1f} | RMSE: {resultado['lightgbm_rmse']:.1f}")
    print(f"O LightGBM erra {ganho:.0%} menos que o baseline")
