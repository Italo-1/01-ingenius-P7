"""P7 - las cuatro figuras del manuscrito.

Consume `data/processed/` y `results/tables/`, escritos por `02_preprocess.py`
y `04_stats.py`. No calcula estadistica nueva; solo dibuja lo que ya esta en
`results/`, con `fieutils.figures`, que es la unica fuente de estilo (paleta
Okabe-Ito, 9 pt, 300 dpi, sin titulos dentro de la figura).

    Fig. 1  Senales crudas: normal, pista interna, pista externa, elemento rodante
    Fig. 2  La misma senal en las 4 representaciones, panel 2x2
    Fig. 3  Mapa de calor 4x4 de F1 por par de carga, un panel por representacion.
            Es la que sostiene el articulo.
    Fig. 4  Diagrama de diferencia critica de Nemenyi

Todas a carga 0 HP para Fig. 1 y 2, la misma condicion en las dos, asi que son
comparables entre si. Fig. 1 y 2 usan la clase IR para el panel de
representaciones porque es la que el analisis de envolvente confirmo 12/12,
sin ambiguedad de firma debil.

    python src/05_figures.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from fieutils import figures as ffig
from fieutils.config import configurar_log

RAIZ = Path(__file__).resolve().parent.parent
PROCESADO = RAIZ / "data" / "processed"
TABLAS = RAIZ / "results" / "tables"
DESTINO = RAIZ / "results" / "figures"

FS = 12_000.0
CLASES = ["Normal", "IR", "B", "OR"]
ETIQUETAS_ESTADISTICOS = {
    "mean": "Mean",
    "rms": "RMS",
    "std": "Std. dev.",
    "skewness": "Skewness",
    "kurtosis": "Kurtosis",
    "peak": "Peak",
    "peak_to_peak": "Peak-to-peak",
    "crest_factor": "Crest factor",
    "shape_factor": "Shape factor",
    "impulse_factor": "Impulse factor",
    "clearance_factor": "Clearance factor",
    "mean_amplitude_root": "Mean sq. root amp.",
}

NOMBRES_CLASE = {
    "Normal": "Normal",
    "IR": "Inner race",
    "B": "Ball",
    "OR": "Outer race",
}
REPRESENTACIONES_NUCLEO = ["Statistical", "FFT", "Wavelet db4", "STFT spectrogram"]


def cargar_todo():
    meta = pd.read_csv(PROCESADO / "metadatos.csv")
    ventanas = np.load(PROCESADO / "ventanas.npy")
    manifiesto = json.loads((PROCESADO / "manifiesto.json").read_text(encoding="utf-8"))
    return meta, ventanas, manifiesto


def ventana_representativa(meta: pd.DataFrame, clase: str, carga: int) -> int:
    """Id de una ventana no purgada, del centro de un registro, a la carga dada.

    El centro evita los transitorios de arranque del registro y las ventanas
    de borde purgadas.
    """
    sub = meta[(meta["clase"] == clase) & (meta["carga_hp"] == carga) & (~meta["purgada"])]
    if sub.empty:
        raise ValueError(f"Sin ventanas utilizables para {clase} a {carga} HP.")
    archivo = sub["archivo"].iloc[0]
    del_archivo = sub[sub["archivo"] == archivo].sort_values("indice_ventana")
    return int(del_archivo.iloc[len(del_archivo) // 2]["id_ventana"])


# ------------------------------------------------------------------------ Fig 1

def figura_1(meta: pd.DataFrame, ventanas: np.ndarray, log) -> None:
    """Senales crudas de las 4 clases a 0 HP, en un panel 2x2."""
    ffig.aplicar_estilo()
    fig, ejes = ffig.plt.subplots(2, 2, figsize=(ffig.ANCHO_DOBLE, ffig.ANCHO_DOBLE * 0.62),
                                   constrained_layout=True)

    t = np.arange(2048) / FS * 1000  # ms
    for i, clase in enumerate(CLASES):
        id_ventana = ventana_representativa(meta, clase, carga=0)
        eje = ejes.flat[i]
        estilo = ffig.estilo_serie(i)
        eje.plot(t, ventanas[id_ventana], color=estilo["color"], linewidth=0.8)
        eje.set_title(ffig.etiqueta_panel(i), pad=4, fontsize=ffig.mpl.rcParams["axes.titlesize"])
        eje.set_xlim(t[0], t[-1])
        if i >= 2:
            eje.set_xlabel("Time [ms]")
        if i % 2 == 0:
            eje.set_ylabel("Acceleration [g]")

    fig.suptitle("")  # la guia prohibe titulo dentro de la figura
    pie = ffig.pie_de_figura(
        "Raw drive-end acceleration signals at 0 HP, one 2048-sample window per class",
        paneles=[NOMBRES_CLASE[c] for c in CLASES],
        nota="Note the different y-axis scale of each panel: RMS ranges from 0.066 g for the healthy record to 0.425 g for the outer race record, so a shared scale would flatten three of the four panels",
    )
    log.info(f"Fig 1 pie: {pie}")
    ffig.guardar(fig, DESTINO, "fig1_senales_crudas")


# ------------------------------------------------------------------------ Fig 2

def figura_2(meta: pd.DataFrame, ventanas: np.ndarray, manifiesto: dict, log) -> None:
    """La misma ventana (IR, 0 HP) en las 4 representaciones, panel 2x2.

    IR se elige porque el analisis de envolvente la confirmo 12/12 sin
    ambiguedad de firma debil (ver README, verificacion fisica de etiquetas).
    """
    from fieutils.signal_repr import estadisticos_temporales, magnitud_fft, wavelet_db4, espectrograma_stft, NOMBRES_ESTADISTICOS

    id_ventana = ventana_representativa(meta, "IR", carga=0)
    x = ventanas[id_ventana]

    ffig.aplicar_estilo()
    fig, ejes = ffig.plt.subplots(2, 2, figsize=(ffig.ANCHO_DOBLE, ffig.ANCHO_DOBLE * 0.75),
                                   constrained_layout=True)

    # (a) estadisticos temporales, como barras HORIZONTALES.
    #
    # Con barras verticales las doce etiquetas hay que girarlas 90 grados y a
    # ancho de columna quedan por debajo de 5 pt en el PDF, ilegibles impresas.
    # En horizontal se leen de corrido al tamano normal del eje.
    est = estadisticos_temporales(x)[0]
    eje = ejes[0, 0]
    estilo = ffig.estilo_serie(0)
    posiciones = range(len(est))
    eje.barh(posiciones, est, color=estilo["color"], height=0.7)
    eje.set_yticks(posiciones)
    # Los nombres internos de `fieutils` indexan datos y no se traducen; para el
    # eje se usa un mapeo de visualizacion aparte, como exige REDACCION.md.
    eje.set_yticklabels([ETIQUETAS_ESTADISTICOS[n] for n in NOMBRES_ESTADISTICOS],
                        fontsize=7)
    eje.invert_yaxis()
    eje.set_xlabel("Value")
    eje.set_title(ffig.etiqueta_panel(0), pad=4, fontsize=ffig.mpl.rcParams["axes.titlesize"])

    # (b) magnitud FFT
    espectro = magnitud_fft(x)[0]
    frecuencias = np.fft.rfftfreq(2048, d=1 / FS)
    eje = ejes[0, 1]
    estilo = ffig.estilo_serie(1)
    eje.plot(frecuencias, espectro, color=estilo["color"], linewidth=0.7)
    eje.set_xlabel("Frequency [Hz]")
    eje.set_ylabel("Magnitude")
    eje.set_title(ffig.etiqueta_panel(1), pad=4, fontsize=ffig.mpl.rcParams["axes.titlesize"])

    # (c) wavelet db4, energia relativa por banda
    #
    # pywt.wavedec devuelve [cA_n, cD_n, cD_n-1, ..., cD_1]: la aproximacion
    # mas gruesa PRIMERO, seguida de los detalles de mas grueso a mas fino.
    # Confirmado con longitudes de coeficiente (70,70,134,262,517,1027), que
    # solo casan con ese orden. Etiquetar al reves invierte que banda domina:
    # con el orden correcto es D1 (3000-6000 Hz), no A5, la que mas energia
    # concentra, y D1 es justo donde cae la resonancia estructural de 2 a
    # 5.5 kHz que excita el impacto de la falla.
    energias = wavelet_db4(x, niveles=5, solo_energia=True)[0]
    etiquetas_banda = ["A5"] + [f"D{i}" for i in range(5, 0, -1)]
    eje = ejes[1, 0]
    estilo = ffig.estilo_serie(2)
    eje.bar(range(len(energias)), energias, color=estilo["color"], width=0.6)
    eje.set_xticks(range(len(energias)))
    eje.set_xticklabels(etiquetas_banda)
    eje.set_ylabel("Relative energy")
    eje.set_title(ffig.etiqueta_panel(2), pad=4, fontsize=ffig.mpl.rcParams["axes.titlesize"])

    # (d) espectrograma STFT, imagen cuadrada (la de la CNN, mas legible que 16x64)
    #
    # La imagen es un remuestreo de las filas y columnas NATIVAS de la STFT
    # (33 frecuencias hasta Nyquist, 63 tramas), no filas de 187.5 Hz reales:
    # redimensionar no crea resolucion. El eje debe ir de 0 a FS/2, nunca a
    # `tamano * delta_f_hz`, que superaria Nyquist.
    info = manifiesto["espectrograma"]
    img = espectrograma_stft(x, fs=FS, tamano=64, nperseg=info["nperseg"])[0]
    eje = ejes[1, 1]
    duracion_ms = 2048 / FS * 1000
    im = eje.imshow(
        img, cmap=ffig.SECUENCIAL, aspect="auto", origin="lower",
        extent=[0, duracion_ms, 0, FS / 2],
    )
    eje.set_xlabel("Time [ms]")
    eje.set_ylabel("Frequency [Hz]")
    eje.set_title(ffig.etiqueta_panel(3), pad=4, fontsize=ffig.mpl.rcParams["axes.titlesize"])
    fig.colorbar(im, ax=eje, fraction=0.046, pad=0.04, label="Normalized magnitude [dB]")

    pie = ffig.pie_de_figura(
        "Same inner-race fault window at 0 HP under the four representations",
        paneles=["Time-domain statistics", "FFT magnitude", "db4 wavelet relative energy per band",
                 "STFT spectrogram (64x64, entry to the CNN)"],
        nota="The twelve descriptors of panel (a) do not share units, so their bar heights are not comparable with one another; wavelet bands run from coarsest approximation (A5) to finest detail (D1); the spectrogram is shown on the CNN grid, not on the 16x64 vector grid used in the statistical comparison",
    )
    log.info(f"Fig 2 pie: {pie}")
    ffig.guardar(fig, DESTINO, "fig2_representaciones")


# ------------------------------------------------------------------------ Fig 3

def figura_3(log) -> None:
    """Mapa de calor 4x4 de F1 por par de carga, un panel por representacion.

    Es la figura que sostiene el articulo. Se genera desde
    `resultados_por_fold.csv`, incluyendo la diagonal (celda de referencia,
    recuadrada por la propia funcion) aunque quede fuera de la inferencia.
    """
    r = pd.read_csv(TABLAS / "resultados_por_fold.csv")
    cargas = [0, 1, 2, 3]

    matrices = {}
    for nombre_legible, nombre_col in zip(
        REPRESENTACIONES_NUCLEO, ["estadisticos", "fft", "wavelet", "espectrograma"]
    ):
        sub = r[(r["representacion"] == nombre_col) & (r["en_comparacion"] == True)]  # noqa: E712
        matriz = sub.groupby(["carga_train", "carga_test"])["f1_macro"].mean().unstack()
        matriz = matriz.reindex(index=cargas, columns=cargas)
        matrices[nombre_legible] = matriz.values

    ffig.aplicar_estilo()
    fig, ejes = ffig.mapa_calor_transferencia(
        matrices, etiquetas=[f"{c} HP" for c in cargas], titulo_color="F1-macro",
        etiqueta_filas="Training load", etiqueta_columnas="Test load",
    )

    pie = ffig.pie_de_figura(
        "F1-macro for every (training load, test load) pair, averaged over the three "
        "vector classifiers (SVM-RBF, Random Forest, MLP) and 5 folds",
        paneles=REPRESENTACIONES_NUCLEO,
        nota=(
            "The diagonal is a reference cell, boxed for orientation, not part of "
            "Friedman or the ANOVA: with a single Normal recording per load it does not "
            "admit a record-level split"
        ),
    )
    log.info(f"Fig 3 pie: {pie}")
    ffig.guardar(fig, DESTINO, "fig3_mapa_calor_transferencia")


# ------------------------------------------------------------------------ Fig 4

def figura_4(log) -> None:
    """Diagrama de diferencia critica de Nemenyi, prueba de Friedman principal."""
    resumen = json.loads((TABLAS / "resumen_estadistico.json").read_text(encoding="utf-8"))
    principal = resumen["friedman_principal"]
    rangos = pd.Series(principal["rangos_medios"]).sort_values()

    ffig.aplicar_estilo()
    # El defecto de fieutils dibuja este diagrama a ANCHO_DOBLE * 0.8 = 5.73",
    # pero en la plantilla de Ingenius entra en UNA columna, 8.17 cm = 3.22":
    # LaTeX lo reducia al 56 % y los rotulos de 8 pt quedaban en 4,5 pt, ilegibles
    # impresos. Se genera al ancho de columna para que la escala sea 1:1.
    # Detectado revisando el PDF a 110 dpi en la ronda 2 (02/09).
    fig, eje = ffig.diagrama_diferencia_critica(
        rangos, principal["distancia_critica"],
        figsize=(ffig.ANCHO_SIMPLE, 2.05),
    )

    pie = ffig.pie_de_figura(
        "Nemenyi critical-difference diagram for the principal Friedman test "
        f"(N={principal['n_bloques']} off-diagonal pairs, k={principal['k_representaciones']} representations, "
        f"chi2={principal['chi2']:.2f}, p={principal['p_valor']:.3f})",
        nota=(
            "Representations joined by a horizontal bar are not distinguishable at "
            "alpha=0.05; the omnibus test did not reach significance, consistent with "
            "the per-classifier Friedman tests disagreeing on ranking"
        ),
    )
    log.info(f"Fig 4 pie: {pie}")
    log.info(
        f"Friedman principal: chi2={principal['chi2']:.3f}, p={principal['p_valor']:.4f} "
        f"(no significativo a alfa=0.05)" if principal["p_valor"] >= 0.05 else
        f"Friedman principal: chi2={principal['chi2']:.3f}, p={principal['p_valor']:.4f} (significativo)"
    )
    ffig.guardar(fig, DESTINO, "fig4_diferencia_critica_nemenyi")


# ----------------------------------------------------------------------- main

def main() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    log = configurar_log("05_figures", RAIZ)

    meta, ventanas, manifiesto = cargar_todo()

    figura_1(meta, ventanas, log)
    log.info("Fig 1 escrita.")

    figura_2(meta, ventanas, manifiesto, log)
    log.info("Fig 2 escrita.")

    figura_3(log)
    log.info("Fig 3 escrita.")

    figura_4(log)
    log.info("Fig 4 escrita.")

    log.info(f"Las cuatro figuras en {DESTINO} (PDF vectorial + PNG 300 dpi).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
