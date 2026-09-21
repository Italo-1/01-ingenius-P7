"""P7 - analisis anadido en la revision adversarial (ronda 2).

NO es parte del protocolo pre-especificado. Responde a tres objeciones de la
segunda pasada, todas sobre cifras que el manuscrito daba como puntuales o
agregadas sin mostrar la dispersion que las sostiene:

1. Las cuatro caidas medias entre cargas (0.074 a 0.153) se reportaban sin
   incertidumbre, lo que invita a leer un orden que la prueba de Friedman no
   respalda. Se calcula el IC bootstrap de cada caida remuestreando los 12
   pares fuera de la diagonal, que son la unidad de analisis.

2. La interaccion representacion x clasificador es la conclusion central y se
   apoya en un ANOVA de tres factores cuyo residuo trata los 12 pares como
   replicas intercambiables dentro de cada nivel de distancia de carga. Los
   pares no son independientes: cada carga aparece en seis de ellos. Se
   reajusta el modelo con el par como bloque, que absorbe esa varianza. La
   distancia de carga queda confundida con el bloque y sale del modelo.

3. La fila de la CNN se describe con una desviacion de 0.116 in-domain frente
   a 0.01 de los clasificadores de vector, sin decir de donde viene. Se
   desglosa por carga de entrenamiento.

    C:\\lineaB\\.venv\\Scripts\\python.exe src/07_revision2.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols

from fieutils import stats as fstats
from fieutils import tablas

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "results" / "tables"
LOGS = RAIZ / "results" / "logs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.FileHandler(LOGS / "07_revision2.log", encoding="utf-8"),
              logging.StreamHandler()],
)
log = logging.getLogger(__name__)

SEMILLA = 42
NOMBRES = {
    "estadisticos": "Statistical",
    "fft": "FFT",
    "wavelet": "Wavelet db4",
    "espectrograma": "STFT spectrogram",
}


def ic_de_las_caidas(r: pd.DataFrame) -> pd.DataFrame:
    """IC bootstrap de la caida diagonal - fuera de diagonal, por representacion.

    Se remuestrean los 12 pares, no los 60 folds: el fold no es una replica
    independiente, el par si es la unidad que bloquea la prueba de Friedman.
    """
    nucleo = r[r["en_comparacion"]]
    filas = []
    for clave, etiqueta in NOMBRES.items():
        sub = nucleo[nucleo["representacion"] == clave]
        dentro = sub[sub["carga_train"] == sub["carga_test"]]["f1_macro"].mean()
        fuera = (
            sub[sub["carga_train"] != sub["carga_test"]]
            .groupby(["carga_train", "carga_test"])["f1_macro"]
            .mean()
            .to_numpy()
        )
        _, bajo, alto = fstats.ic_bootstrap(fuera, semilla=SEMILLA)
        filas.append({
            "Representation": etiqueta,
            "F1 in-domain": round(dentro, 4),
            "F1 out-of-domain": round(fuera.mean(), 4),
            "Drop": round(dentro - fuera.mean(), 4),
            "95% CI lower": round(dentro - alto, 4),
            "95% CI upper": round(dentro - bajo, 4),
            "n pairs": len(fuera),
        })
    return pd.DataFrame(filas).sort_values("Drop").reset_index(drop=True)


def anova_bloqueada_por_par(celdas: pd.DataFrame) -> pd.DataFrame:
    """ANOVA representacion x clasificador con el par de cargas como bloque."""
    modelo = ols("f1_macro ~ C(representacion)*C(clasificador) + C(par)", data=celdas).fit()
    tabla = sm.stats.anova_lm(modelo, typ=2)
    residuo = tabla.loc["Residual", "sum_sq"]
    tabla["eta_sq_parcial"] = tabla["sum_sq"] / (tabla["sum_sq"] + residuo)
    return tabla


def main() -> None:
    r = pd.read_csv(TABLAS / "resultados_por_fold.csv")

    log.info("=== IC bootstrap de la caida entre cargas (remuestreo de los 12 pares) ===")
    caidas = ic_de_las_caidas(r)
    log.info(f"\n{caidas.to_string(index=False)}")
    caidas.to_csv(TABLAS / "caidas_ic_bootstrap.csv", index=False)
    tablas.exportar(
        caidas, TABLAS, "caidas_ic_bootstrap_tex",
        caption=("Mean macro-F1 drop from the diagonal to the twelve off-diagonal pairs, "
                 "with a percentile bootstrap confidence interval over the pairs."),
        etiqueta="tab:caidas", decimales=4, indice=False,
    )

    nucleo = r[r["en_comparacion"] & (r["carga_train"] != r["carga_test"])].copy()
    celdas = (
        nucleo.groupby(["representacion", "clasificador", "carga_train", "carga_test"])["f1_macro"]
        .mean()
        .reset_index()
    )
    celdas["representacion"] = celdas["representacion"].map(NOMBRES)
    celdas["par"] = celdas["carga_train"].astype(str) + "_" + celdas["carga_test"].astype(str)

    log.info("=== ANOVA representacion x clasificador con el par como bloque (exploratorio) ===")
    bloqueada = anova_bloqueada_por_par(celdas)
    log.info(f"\n{bloqueada.round(4).to_string()}")
    bloqueada.round(4).to_csv(TABLAS / "anova_bloqueada_por_par.csv")

    etiquetas = {
        "C(representacion)": "Representation",
        "C(clasificador)": "Classifier",
        "C(par)": "Load pair (block)",
        "C(representacion):C(clasificador)": "Representation x Classifier",
        "Residual": "Residual",
    }
    ingles = bloqueada[["sum_sq", "df", "F", "PR(>F)", "eta_sq_parcial"]].round(4)
    ingles.index = [etiquetas.get(i, i) for i in ingles.index]
    ingles.index.name = "Source"
    ingles["df"] = ingles["df"].astype(int)
    ingles.columns = ["Sum of squares", "df", "F", "p", "Partial eta^2"]
    tablas.exportar(
        ingles, TABLAS, "anova_bloqueada_por_par_tex",
        caption=("Exploratory ANOVA on macro-F1 with the load pair entered as a blocking "
                 "factor, over the 144 off-diagonal cells with folds averaged."),
        etiqueta="tab:anovabloque", decimales=4, indice=True,
    )

    log.info("=== CNN 2D: desglose por carga de entrenamiento ===")
    cnn = r[r["clasificador"] == "CNN2D"].copy()
    cnn["regimen"] = np.where(cnn["carga_train"] == cnn["carga_test"], "in-domain", "out-of-domain")
    desglose = (
        cnn.groupby(["carga_train", "regimen"])["f1_macro"]
        .agg(["mean", "std", "count"])
        .round(4)
        .reset_index()
    )
    log.info(f"\n{desglose.to_string(index=False)}")
    desglose.to_csv(TABLAS / "cnn_por_carga_entrenamiento.csv", index=False)

    log.info("07_revision2.py completado.")


if __name__ == "__main__":
    main()
