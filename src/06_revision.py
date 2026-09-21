"""P7 - analisis anadido en la revision adversarial (ronda 1).

NO es parte del protocolo pre-registrado. Se anade porque la ronda 1 detecto
que el manuscrito afirmaba una interaccion representacion x clasificador que
ningun test del articulo media: el ANOVA pre-registrado cruza representacion
con distancia de carga y promedia los clasificadores antes de ajustar, de modo
que el clasificador no era un factor del modelo.

Dos analisis, los dos marcados como exploratorios en el manuscrito:

1. ANOVA de tres factores representacion x clasificador x distancia de carga.
   La unidad de analisis es la celda (representacion, clasificador, par de
   cargas) con los 5 folds YA promediados: 4 x 3 x 12 = 144 observaciones. Los
   folds de una misma celda comparten cuatro quintos del conjunto de
   entrenamiento, asi que tratarlos como replicas independientes -como hace el
   ANOVA pre-registrado de dos factores- infla los grados de libertad del
   residuo. Promediarlos es la correccion conservadora.

2. El mismo ANOVA de dos factores del protocolo, reajustado sobre esas mismas
   celdas promediadas por fold, para medir cuanto de la significacion original
   dependia de la pseudo-replicacion.

    C:\\lineaB\\.venv\\Scripts\\python.exe src/06_revision.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from fieutils import stats as fstats
from fieutils import tablas

RAIZ = Path(__file__).resolve().parents[1]
TABLAS = RAIZ / "results" / "tables"
LOGS = RAIZ / "results" / "logs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.FileHandler(LOGS / "06_revision.log", encoding="utf-8"),
              logging.StreamHandler()],
)
log = logging.getLogger(__name__)

NOMBRES = {
    "estadisticos": "Statistical",
    "fft": "FFT",
    "wavelet": "Wavelet db4",
    "espectrograma": "STFT spectrogram",
}


def celdas_promediadas_por_fold(r: pd.DataFrame) -> pd.DataFrame:
    """Una fila por (representacion, clasificador, par de cargas), fuera de la diagonal."""
    nucleo = r[r["en_comparacion"] & (r["carga_train"] != r["carga_test"])].copy()
    agregado = (
        nucleo.groupby(["representacion", "clasificador", "carga_train", "carga_test"])["f1_macro"]
        .mean()
        .reset_index()
    )
    agregado["distancia_carga"] = (agregado["carga_train"] - agregado["carga_test"]).abs()
    agregado["representacion"] = agregado["representacion"].map(NOMBRES)
    return agregado


def main() -> None:
    r = pd.read_csv(TABLAS / "resultados_por_fold.csv")
    celdas = celdas_promediadas_por_fold(r)
    log.info(f"Celdas fuera de diagonal promediadas por fold: {len(celdas)} observaciones.")

    log.info("=== ANOVA de tres factores: representacion x clasificador x distancia (exploratorio) ===")
    tres = fstats.anova_factorial(
        celdas, dependiente="f1_macro",
        factores=["representacion", "clasificador", "distancia_carga"], interaccion=True,
    )
    log.info(f"\n{tres.round(4).to_string()}")
    tres.round(4).to_csv(TABLAS / "anova_tres_factores.csv")

    log.info("=== ANOVA de dos factores reajustado sin pseudo-replicacion de folds ===")
    dos = fstats.anova_factorial(
        celdas.groupby(["representacion", "carga_train", "carga_test", "distancia_carga"], as_index=False)
        ["f1_macro"].mean(),
        dependiente="f1_macro", factores=["representacion", "distancia_carga"], interaccion=True,
    )
    log.info(f"\n{dos.round(4).to_string()}")
    dos.round(4).to_csv(TABLAS / "anova_dos_factores_sin_pseudorreplicacion.csv")

    # Version en ingles del ANOVA de tres factores para el manuscrito.
    etiquetas = {
        "C(representacion)": "Representation",
        "C(clasificador)": "Classifier",
        "C(distancia_carga)": "Load distance",
        "C(representacion):C(clasificador)": "Representation x Classifier",
        "C(representacion):C(distancia_carga)": "Representation x Load distance",
        "C(clasificador):C(distancia_carga)": "Classifier x Load distance",
        "C(representacion):C(clasificador):C(distancia_carga)": "Representation x Classifier x Load distance",
        "Residual": "Residual",
    }
    ingles = tres[["sum_sq", "df", "F", "PR(>F)", "eta_sq_parcial"]].round(4)
    ingles.index = [etiquetas.get(i, i) for i in ingles.index]
    ingles.index.name = "Source"
    ingles["df"] = ingles["df"].astype(int)  # anova_lm devuelve df como float64
    ingles.columns = ["Sum of squares", "df", "F", "p", "Partial eta^2"]
    tablas.exportar(
        ingles, TABLAS, "anova_tres_factores_tex",
        caption=("Exploratory three-way ANOVA on macro-F1: representation, classifier and "
                 "load distance, over the 144 off-diagonal cells with folds averaged."),
        etiqueta="tab:anova3", decimales=4, indice=True,
    )
    log.info("06_revision.py completado.")


if __name__ == "__main__":
    main()
