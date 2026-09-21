"""P7 - verificacion de la estructura interna de los .mat de CWRU.

La ficha marca como riesgo principal que la nomenclatura de CWRU se interprete
mal. Este script no procesa nada: abre los archivos, enumera las variables que
contienen y comprueba que la convencion de nombres es la esperada, para poder
escribir `02_preprocess.py` sobre terreno firme.

Convencion documentada de CWRU:
    X<NNN>_DE_time   aceleracion en el extremo de transmision (drive end)
    X<NNN>_FE_time   aceleracion en el extremo del ventilador (fan end)
    X<NNN>_BA_time   aceleracion en la base (no siempre presente)
    X<NNN>RPM        velocidad de giro medida

El canal que usa el articulo es DE, muestreado a 12 kHz.

    python src/00_verificar_estructura.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat

RAIZ = Path(__file__).resolve().parent.parent
CRUDO = RAIZ / "data" / "raw"
FS = 12_000.0


def main() -> int:
    catalogo = pd.read_csv(CRUDO / "catalogo.csv")
    # `avisos` son anomalias conocidas y ya resueltas; `errores` bloquean.
    filas, avisos, errores = [], [], []

    for _, fila in catalogo.iterrows():
        ruta = CRUDO / fila["archivo"]
        contenido = loadmat(ruta)
        claves = [k for k in contenido if not k.startswith("__")]

        numero_archivo = int(Path(fila["archivo"]).stem)
        canal_de = [k for k in claves if k.endswith("_DE_time")]
        canal_fe = [k for k in claves if k.endswith("_FE_time")]
        clave_rpm = [k for k in claves if k.endswith("RPM")]

        if not canal_de:
            errores.append(f"{fila['archivo']}: sin canal DE. Claves: {claves}")
            continue

        # SELECCION ANCLADA AL NUMERO DE ARCHIVO, no al orden de las claves.
        #
        # 99.mat viene empaquetado con DOS registros: X098_* (copia identica de
        # 98.mat) y X099_* (el que corresponde). Tomar "la primera clave que
        # acabe en _DE_time" devuelve X098 por orden alfabetico, y la senal de
        # 1 HP acabaria etiquetada como 2 HP. Como la carga es el eje del
        # articulo, ese error contaminaria la matriz entera sin dar ninguna
        # senal de alarma.
        esperada = f"X{numero_archivo:03d}_DE_time"
        if esperada in claves:
            clave_de = esperada
        else:
            clave_de = canal_de[0]
            incrustado = re.search(r"X(\d+)_DE_time", clave_de)
            errores.append(
                f"{fila['archivo']}: no existe {esperada}; se usa {clave_de} "
                f"(X{incrustado.group(1) if incrustado else '?'})"
            )

        if len(canal_de) > 1:
            avisos.append(
                f"{fila['archivo']}: contiene {len(canal_de)} canales DE "
                f"({', '.join(canal_de)}). Resuelto: se usa {clave_de}, "
                f"anclado al numero de archivo."
            )

        senal = np.ravel(contenido[clave_de])
        rpm = float(np.ravel(contenido[clave_rpm[0]])[0]) if clave_rpm else np.nan

        filas.append({
            "archivo": fila["archivo"],
            "clase": fila["clase"],
            "diametro_pulg": fila["diametro_pulg"],
            "carga_hp": fila["carga_hp"],
            "muestras": senal.size,
            "duracion_s": round(senal.size / FS, 2),
            "rpm_medido": rpm,
            "rpm_catalogo": fila["rpm_aprox"],
            "tiene_FE": bool(canal_fe),
            "rms": round(float(np.sqrt(np.mean(senal**2))), 4),
        })

    resumen = pd.DataFrame(filas)
    resumen.to_csv(RAIZ / "results" / "tables" / "estructura_cwru.csv", index=False)

    print(f"Archivos verificados: {len(resumen)} de {len(catalogo)}\n")
    print("Duracion de registro por clase (segundos):")
    print(resumen.groupby("clase")["duracion_s"].describe()[["min", "max", "mean"]].round(2))

    print("\nRMS medio por clase y carga - debe crecer con la carga y ser mayor")
    print("en las clases con falla que en Normal:")
    print(resumen.pivot_table(index="clase", columns="carga_hp", values="rms").round(4))

    # Ventanas de 2048 con 50 % de solape que produce cada registro.
    resumen["ventanas"] = 1 + (resumen["muestras"] - 2048) // 1024
    print(f"\nVentanas de 2048 (solape 50 %) disponibles: {int(resumen['ventanas'].sum())}")
    print("Por clase:")
    print(resumen.groupby("clase")["ventanas"].sum())

    if avisos:
        print("\nANOMALIAS CONOCIDAS (resueltas, documentar en el manuscrito):")
        for a in avisos:
            print("  -", a)

    if errores:
        print("\nERRORES - no continuar hasta resolverlos:")
        for e in errores:
            print("  -", e)
        return 1

    print("\nEstructura conforme a la convencion documentada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
