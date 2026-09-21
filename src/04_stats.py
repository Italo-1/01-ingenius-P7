"""P7 - Friedman-Nemenyi, ANOVA de dos factores y ablacion de amplitud.

Consume `results/tables/resultados_por_fold.csv` y `ablacion_por_fold.csv`,
escritos por `03_experiment.py`. No entrena nada; solo agrega y prueba.

Diseno de la inferencia, decidido el 23/08 antes de ver resultados (ver README)
-------------------------------------------------------------------------------
- La diagonal (carga_train == carga_test) es referencia declarada y NUNCA entra
  en ninguna prueba: en CWRU la clase Normal tiene un unico registro por carga,
  asi que esa celda no admite division por registro real.
- La CNN 2D (representacion `espectrograma_cnn`) es fila de referencia en la
  Tabla 1 y queda FUERA de Friedman y del ANOVA: no existe para las otras tres
  representaciones y un diseno desbalanceado rompe las dos pruebas.
- **Principal**: Friedman sobre las 4 representaciones, k=4, con los 12 pares
  fuera de diagonal como bloques (N=12), usando el F1-macro promediado entre
  los tres clasificadores de vector Y entre los 5 folds. Se promedian los
  clasificadores porque comparten particion y senal: no son bloques
  independientes, y usarlos como si N=48 divide la distancia critica de Nemenyi
  a la mitad apoyandose en esa dependencia.
- **Robustez**: un Friedman por clasificador (tres pruebas, N=12 cada una, solo
  promediando folds). Si el orden de las representaciones se mantiene en las
  tres, el resultado es mas fuerte que cualquier prueba conjunta.
- **ANOVA de dos factores**: representacion (4) x distancia de carga (1, 2, 3;
  la distancia 0 es la diagonal y no entra), con interaccion. La unidad de
  analisis es el F1-macro promediado entre clasificadores PERO NO entre folds:
  el fold es la replica real dentro de cada celda (5 folds x 12 pares x 4
  representaciones = 240 observaciones), consistente con como se define el
  bloque en Friedman.
- **Ablacion de amplitud**: comparacion pareada representacion original vs.
  normalizada en RMS, sobre las mismas 60 observaciones (12 pares x 5 folds),
  para SVM-RBF y Random Forest, que es el alcance fijado en 02_preprocess. Se
  reporta la diferencia pareada con IC bootstrap y el tamano de efecto de
  Cliff, no un ANOVA nuevo: son solo dos condiciones por comparar.

    python src/04_stats.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from fieutils import stats as fstats
from fieutils import tablas
from fieutils.config import SEMILLA, configurar_log

RAIZ = Path(__file__).resolve().parent.parent
TABLAS = RAIZ / "results" / "tables"

CLASIFICADORES_NUCLEO = ["SVM-RBF", "RandomForest", "MLP"]
REPRESENTACIONES_NUCLEO = ["estadisticos", "fft", "wavelet", "espectrograma"]
NOMBRES_LEGIBLES = {
    "estadisticos": "Statistical",
    "fft": "FFT",
    "wavelet": "Wavelet db4",
    "espectrograma": "STFT spectrogram",
}


def cargar_resultados() -> pd.DataFrame:
    r = pd.read_csv(TABLAS / "resultados_por_fold.csv")
    faltan = set(REPRESENTACIONES_NUCLEO) - set(r["representacion"].unique())
    if faltan:
        raise ValueError(f"Faltan representaciones del nucleo en los resultados: {faltan}")
    return r


# --------------------------------------------------------- agregacion a bloques

def tabla_friedman_principal(r: pd.DataFrame) -> pd.DataFrame:
    """12 pares fuera de diagonal x 4 representaciones, F1 promediado.

    Promedia sobre los 3 clasificadores del nucleo Y sobre los 5 folds: cada
    celda de la tabla resultante es un bloque de Friedman, tal como exige
    `fieutils.stats.friedman_nemenyi` (una fila por conjunto, una columna por
    metodo).
    """
    nucleo = r[
        (r["en_comparacion"] == True)  # noqa: E712
        & (r["carga_train"] != r["carga_test"])
        & (r["representacion"].isin(REPRESENTACIONES_NUCLEO))
    ]
    agregado = (
        nucleo.groupby(["representacion", "carga_train", "carga_test"])["f1_macro"]
        .mean()
        .reset_index()
    )
    tabla = agregado.pivot(index=["carga_train", "carga_test"], columns="representacion",
                            values="f1_macro")
    tabla = tabla[REPRESENTACIONES_NUCLEO]
    if tabla.shape != (12, 4):
        raise ValueError(f"Tabla de Friedman con forma inesperada: {tabla.shape}, se esperaba (12, 4).")
    if tabla.isnull().any().any():
        raise ValueError("Huecos en la tabla de Friedman: falta alguna celda-representacion.")
    return tabla.rename(columns=NOMBRES_LEGIBLES)


def tabla_friedman_por_clasificador(r: pd.DataFrame, clasificador: str) -> pd.DataFrame:
    """Igual que la principal, pero de un solo clasificador (robustez)."""
    subset = r[
        (r["clasificador"] == clasificador)
        & (r["carga_train"] != r["carga_test"])
        & (r["representacion"].isin(REPRESENTACIONES_NUCLEO))
    ]
    agregado = (
        subset.groupby(["representacion", "carga_train", "carga_test"])["f1_macro"]
        .mean()
        .reset_index()
    )
    tabla = agregado.pivot(index=["carga_train", "carga_test"], columns="representacion",
                            values="f1_macro")
    tabla = tabla[REPRESENTACIONES_NUCLEO]
    if tabla.shape != (12, 4) or tabla.isnull().any().any():
        raise ValueError(f"Tabla de robustez incompleta para {clasificador}: {tabla.shape}.")
    return tabla.rename(columns=NOMBRES_LEGIBLES)


def tabla_anova(r: pd.DataFrame) -> pd.DataFrame:
    """240 obs: 5 folds x 12 pares x 4 representaciones, F1 promediado entre
    clasificadores pero NO entre folds. El fold es la replica del ANOVA."""
    nucleo = r[
        (r["en_comparacion"] == True)  # noqa: E712
        & (r["carga_train"] != r["carga_test"])
        & (r["representacion"].isin(REPRESENTACIONES_NUCLEO))
    ].copy()
    agregado = (
        nucleo.groupby(["representacion", "carga_train", "carga_test", "fold"])["f1_macro"]
        .mean()
        .reset_index()
    )
    agregado["distancia_carga"] = (agregado["carga_train"] - agregado["carga_test"]).abs()
    if len(agregado) != 240:
        raise ValueError(f"ANOVA con {len(agregado)} observaciones, se esperaban 240.")
    return agregado


# ------------------------------------------------------------------ ablacion

def analizar_ablacion(r: pd.DataFrame, log) -> pd.DataFrame:
    """Compara cada representacion original con su version normalizada en RMS.

    Mismas 60 observaciones (12 pares x 5 folds) por lado, para SVM-RBF y
    Random Forest. La diferencia se reporta pareada, no como grupos
    independientes: cada par (celda, fold, clasificador) comparte particion,
    asi que restar cancela esa fuente de varianza compartida.
    """
    ablacion = pd.read_csv(TABLAS / "ablacion_por_fold.csv")
    pares = [("estadisticos", "estadisticos_rmsnorm"), ("fft", "fft_rmsnorm")]
    clave = ["clasificador", "carga_train", "carga_test", "fold"]
    filas = []

    for original, normalizada in pares:
        for clasificador in ["SVM-RBF", "RandomForest"]:
            a = r[
                (r["representacion"] == original) & (r["clasificador"] == clasificador)
                & (r["carga_train"] != r["carga_test"])
            ][clave + ["f1_macro"]].rename(columns={"f1_macro": "f1_original"})
            b = ablacion[
                (ablacion["representacion"] == normalizada) & (ablacion["clasificador"] == clasificador)
            ][clave + ["f1_macro"]].rename(columns={"f1_macro": "f1_rmsnorm"})

            emparejado = a.merge(b, on=clave, how="inner")
            if len(emparejado) != 60:
                raise ValueError(
                    f"Ablacion {original}/{clasificador}: {len(emparejado)} pares emparejados, "
                    "se esperaban 60. Revisar que 03_experiment corrio ambas partes."
                )

            diferencia = emparejado["f1_rmsnorm"].values - emparejado["f1_original"].values
            valor, li, ls = fstats.ic_bootstrap(diferencia, semilla=SEMILLA)
            delta, magnitud = fstats.cliffs_delta(
                emparejado["f1_rmsnorm"].values, emparejado["f1_original"].values
            )

            filas.append({
                "Representation": NOMBRES_LEGIBLES.get(original, original),
                "Classifier": clasificador,
                "F1 original (mean)": emparejado["f1_original"].mean(),
                "F1 RMS-normalized (mean)": emparejado["f1_rmsnorm"].mean(),
                "Mean difference": valor,
                "95% CI lower": li,
                "95% CI upper": ls,
                "Cliff's delta": delta,
                "Magnitude": magnitud,
                "n pairs": len(emparejado),
            })
            log.info(
                f"ablacion {original}/{clasificador}: rmsnorm - original = "
                f"{valor:+.4f} [{li:+.4f}, {ls:+.4f}], delta de Cliff = {delta:+.3f} ({magnitud})"
            )

    return pd.DataFrame(filas)


# --------------------------------------------------------------------- salida

def escribir_tabla_1(r: pd.DataFrame) -> pd.DataFrame:
    """F1 dentro y fuera de dominio por representacion y clasificador, con
    desviacion estandar. La CNN entra aqui como fila de referencia."""
    r = r.copy()
    r["condicion"] = np.where(r["carga_train"] == r["carga_test"], "dentro", "fuera")

    resumen = (
        r.groupby(["representacion", "clasificador", "condicion"])["f1_macro"]
        .agg(["mean", "std"])
        .reset_index()
    )
    ancho = resumen.pivot_table(
        index=["representacion", "clasificador"], columns="condicion", values=["mean", "std"]
    )
    ancho.columns = [f"{c}_{cond}" for c, cond in ancho.columns]
    ancho = ancho.reset_index()

    for cond, etiqueta_col in [("dentro", "F1 in-domain"), ("fuera", "F1 out-of-domain")]:
        ancho[etiqueta_col] = ancho.apply(
            lambda f, c=cond: f"{f[f'mean_{c}']:.3f} $\\pm$ {f[f'std_{c}']:.3f}", axis=1
        )

    ETIQUETA_CNN = "CNN 2D (reference, excluded from the comparison)"
    ancho["representacion"] = ancho["representacion"].map(
        lambda x: NOMBRES_LEGIBLES.get(x, ETIQUETA_CNN if x == "espectrograma_cnn" else x)
    )
    orden = list(NOMBRES_LEGIBLES.values()) + [ETIQUETA_CNN]
    ancho["representacion"] = pd.Categorical(ancho["representacion"], categories=orden, ordered=True)
    ancho = ancho.rename(columns={"representacion": "Representation", "clasificador": "Classifier"})

    tabla = ancho.sort_values(["Representation", "Classifier"]).set_index(
        ["Representation", "Classifier"]
    )[["F1 in-domain", "F1 out-of-domain"]]

    tablas.exportar(
        tabla, TABLAS, "tabla1_f1_dentro_fuera",
        caption=(
            "F1-macro (mean $\\pm$ standard deviation over 5 folds x cells) in-domain and "
            "out-of-domain, by representation and classifier. The 2D CNN is a reference row: "
            "it does not enter Friedman or the ANOVA because it does not exist for the "
            "other three representations."
        ),
        etiqueta="tab:f1-dentro-fuera", decimales=3, indice=True,
        sin_escapar=["F1 in-domain", "F1 out-of-domain"],
    )
    return tabla


def escribir_costo(r: pd.DataFrame) -> pd.DataFrame:
    """Tabla 2: costo computacional, ajuste + prediccion, por representacion."""
    costo = (
        r.groupby("representacion")[["segundos_ajuste", "segundos_prediccion"]]
        .mean()
        .rename(columns={"segundos_ajuste": "Fit [s]", "segundos_prediccion": "Predict [s]"})
    )
    costo["Representation"] = costo.index.map(
        lambda x: NOMBRES_LEGIBLES.get(x, "CNN 2D" if x == "espectrograma_cnn" else x)
    )
    costo = costo.set_index("Representation")
    tablas.exportar(
        costo, TABLAS, "tabla2_costo_computacional",
        caption="Mean fit and prediction time per representation, in seconds, averaged over classifiers, cells and folds.",
        etiqueta="tab:costo", decimales=3, indice=True,
    )
    return costo


def main() -> int:
    TABLAS.mkdir(parents=True, exist_ok=True)
    log = configurar_log("04_stats", RAIZ)

    r = cargar_resultados()
    log.info(f"Cargadas {len(r)} filas de resultados_por_fold.csv.")

    # ---------------------------------------------------------- Tabla 1 y 2
    escribir_tabla_1(r)
    escribir_costo(r)

    # -------------------------------------------------------- Friedman principal
    tabla_principal = tabla_friedman_principal(r)
    resultado_principal = fstats.friedman_nemenyi(tabla_principal)
    log.info("=== Friedman principal (N=12, k=4, F1 promediado entre clasificadores) ===")
    log.info(resultado_principal.resumen())
    log.info(f"Rangos medios (1 = mejor):\n{resultado_principal.rangos_medios.round(3).to_string()}")

    tablas.exportar(
        tabla_principal.round(4).rename_axis(index=["Training load", "Test load"]),
        TABLAS, "friedman_tabla_bloques",
        caption="F1-macro by (training load, test load) pair and representation, averaged over the three core classifiers. Input to the principal Friedman test.",
        etiqueta="tab:friedman-bloques", decimales=3, indice=True,
    )

    nemenyi_export = resultado_principal.nemenyi.copy()
    nemenyi_export.to_csv(TABLAS / "nemenyi_pvalores.csv")

    # ------------------------------------------------------ Friedman por clasificador
    log.info("=== Robustez: Friedman por clasificador (N=12 cada uno) ===")
    robustez = {}
    for clasificador in CLASIFICADORES_NUCLEO:
        tabla_c = tabla_friedman_por_clasificador(r, clasificador)
        resultado_c = fstats.friedman_nemenyi(tabla_c)
        robustez[clasificador] = resultado_c
        log.info(f"{clasificador}: {resultado_c.resumen()}")
        log.info(f"  rangos: {resultado_c.rangos_medios.round(3).to_dict()}")

    orden_principal = list(resultado_principal.rangos_medios.index)
    ordenes_coinciden = all(
        list(res.rangos_medios.index) == orden_principal for res in robustez.values()
    )
    log.info(f"Orden de representaciones identico en las 3 pruebas por clasificador: {ordenes_coinciden}")

    # --------------------------------------------------------------------- ANOVA
    log.info("=== ANOVA de dos factores: representacion x distancia de carga ===")
    datos_anova = tabla_anova(r)
    tabla_anova_resultado = fstats.anova_factorial(
        datos_anova, dependiente="f1_macro", factores=["representacion", "distancia_carga"],
        interaccion=True,
    )
    log.info(f"\n{tabla_anova_resultado.round(4).to_string()}")
    tabla_anova_resultado.round(4).to_csv(TABLAS / "anova_dos_factores.csv")

    FACTOR_INGLES = {
        "C(representacion)": "Representation",
        "C(distancia_carga)": "Load distance",
        "C(representacion):C(distancia_carga)": "Representation x Load distance",
        "Residual": "Residual",
    }
    tabla_anova_ingles = (
        tabla_anova_resultado[["sum_sq", "df", "F", "PR(>F)", "eta_sq_parcial"]].round(4)
        if "F" in tabla_anova_resultado.columns else tabla_anova_resultado.round(4)
    ).rename(index=FACTOR_INGLES)
    # statsmodels devuelve "df" como float64 aunque sus valores sean grados de
    # libertad enteros (3.0, 2.0, 228.0...). `fieutils.tablas.exportar` solo
    # detecta enteros por dtype (is_integer_dtype), no por valor, asi que sin
    # este cast salian como "3.0000". No es un bug de fieutils: es un dtype
    # semanticamente entero que llega como float. Se corrige aqui, en P7, no en
    # la libreria compartida.
    if "df" in tabla_anova_ingles.columns:
        tabla_anova_ingles["df"] = tabla_anova_ingles["df"].astype(int)
    tablas.exportar(
        tabla_anova_ingles, TABLAS, "anova_dos_factores_tex",
        caption="Two-way ANOVA on F1-macro: representation x load distance (1, 2, or 3 HP), with interaction. The diagonal (distance 0) is excluded.",
        etiqueta="tab:anova", decimales=4, indice=True,
    )

    # ------------------------------------------------------------------ ablacion
    log.info("=== Ablacion de amplitud (SVM-RBF y Random Forest, 12 pares fuera de diagonal) ===")
    tabla_ablacion = analizar_ablacion(r, log)
    tablas.exportar(
        tabla_ablacion.round(4), TABLAS, "ablacion_resumen",
        caption="Paired F1-macro difference (RMS-normalized version minus original version), with 95% bootstrap CI and Cliff's delta, for time-domain statistics and FFT with SVM-RBF and Random Forest.",
        etiqueta="tab:ablacion", decimales=4, indice=False,
    )

    # -------------------------------------------------------------- manifiesto
    resumen = {
        "friedman_principal": {
            "chi2": resultado_principal.estadistico,
            "p_valor": resultado_principal.p_valor,
            "n_bloques": resultado_principal.n_conjuntos,
            "k_representaciones": len(resultado_principal.rangos_medios),
            "distancia_critica": resultado_principal.distancia_critica,
            "rangos_medios": resultado_principal.rangos_medios.round(4).to_dict(),
        },
        "friedman_por_clasificador": {
            c: {
                "chi2": res.estadistico, "p_valor": res.p_valor,
                "rangos_medios": res.rangos_medios.round(4).to_dict(),
            }
            for c, res in robustez.items()
        },
        "orden_identico_en_robustez": bool(ordenes_coinciden),
        "semilla": SEMILLA,
    }
    (TABLAS / "resumen_estadistico.json").write_text(
        json.dumps(resumen, indent=2, ensure_ascii=True), encoding="utf-8"
    )

    log.info("04_stats.py completado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
