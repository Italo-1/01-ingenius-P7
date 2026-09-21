"""P7 - descarga y organizacion del CWRU Bearing Data Center.

La nomenclatura de CWRU es la fuente de error mas comun en la literatura de
diagnostico de rodamientos: los archivos se identifican solo por un numero y la
correspondencia con (tipo de falla, diametro, carga) vive en tablas HTML del
sitio. Aqui esa correspondencia queda EXPLICITA en `CATALOGO`, verificable de un
vistazo, y se vuelca a `data/raw/catalogo.csv` para citarla en el manuscrito.

Configuracion usada: extremo de transmision (drive end), muestreo a 12 kHz,
cuatro condiciones de carga (0, 1, 2, 3 HP) y cuatro clases de estado.

    python src/01_download.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "data" / "raw"
BASE_URL = "https://engineering.case.edu/sites/default/files/{}.mat"

# ---------------------------------------------------------------------------
# Catalogo: numero de archivo -> (clase, diametro en pulgadas, carga en HP)
#
# Normal            = rodamiento sano
# IR                = falla en pista interna (inner race)
# B                 = falla en elemento rodante (ball)
# OR                = falla en pista externa (outer race), centrada a las 6:00
#
# Las cuatro filas de cada bloque son las cargas 0, 1, 2 y 3 HP en ese orden.
# Fuente: tablas de descarga del Bearing Data Center, Case Western Reserve
# University. Contrastado contra la convencion usada en la literatura del area.
# ---------------------------------------------------------------------------
CATALOGO: list[tuple[int, str, float, int]] = []

_BLOQUES = {
    ("Normal", 0.000): [97, 98, 99, 100],
    ("IR", 0.007): [105, 106, 107, 108],
    ("IR", 0.014): [169, 170, 171, 172],
    ("IR", 0.021): [209, 210, 211, 212],
    ("B", 0.007): [118, 119, 120, 121],
    ("B", 0.014): [185, 186, 187, 188],
    ("B", 0.021): [222, 223, 224, 225],
    ("OR", 0.007): [130, 131, 132, 133],
    ("OR", 0.014): [197, 198, 199, 200],
    ("OR", 0.021): [234, 235, 236, 237],
}

for (_clase, _diam), _numeros in _BLOQUES.items():
    for _carga, _num in enumerate(_numeros):
        CATALOGO.append((_num, _clase, _diam, _carga))


def descargar(numero: int, destino: Path, reintentos: int = 3) -> tuple[bool, str]:
    """Descarga un `.mat` si no existe ya. Devuelve (exito, detalle)."""
    archivo = destino / f"{numero}.mat"
    if archivo.exists() and archivo.stat().st_size > 1024:
        return True, f"ya presente ({archivo.stat().st_size / 1024:.0f} KB)"

    url = BASE_URL.format(numero)
    for intento in range(1, reintentos + 1):
        try:
            r = requests.get(url, timeout=60, stream=True)
            if r.status_code != 200:
                if intento == reintentos:
                    return False, f"HTTP {r.status_code}"
                time.sleep(2 * intento)
                continue

            contenido = r.content
            # Un .mat de MATLAB empieza por la cabecera de texto "MATLAB".
            # Si el servidor devuelve una pagina de error, se detecta aqui.
            if not contenido.startswith(b"MATLAB"):
                return False, "la respuesta no es un archivo .mat"

            archivo.write_bytes(contenido)
            return True, f"descargado ({len(contenido) / 1024:.0f} KB)"

        except requests.RequestException as exc:
            if intento == reintentos:
                return False, f"{type(exc).__name__}: {exc}"
            time.sleep(2 * intento)

    return False, "agotados los reintentos"


def main() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    print(f"CWRU Bearing Data Center -> {DESTINO}")
    print(f"{len(CATALOGO)} archivos: 10 combinaciones clase-diametro x 4 cargas\n")

    filas, fallidos = [], []
    for numero, clase, diametro, carga in CATALOGO:
        ok, detalle = descargar(numero, DESTINO)
        estado = "OK  " if ok else "FALLO"
        print(f"  {estado} {numero:>4}.mat  {clase:<7} {diametro:.3f}\"  {carga} HP  - {detalle}")

        if ok:
            filas.append({
                "archivo": f"{numero}.mat",
                "clase": clase,
                "diametro_pulg": diametro,
                "carga_hp": carga,
                "rpm_aprox": {0: 1797, 1: 1772, 2: 1750, 3: 1730}[carga],
            })
        else:
            fallidos.append(numero)

    if filas:
        catalogo = pd.DataFrame(filas)
        catalogo.to_csv(DESTINO / "catalogo.csv", index=False)
        print(f"\nCatalogo escrito en {DESTINO / 'catalogo.csv'}")
        print("\nCobertura por clase y carga:")
        print(pd.crosstab(catalogo["clase"], catalogo["carga_hp"]))

    if fallidos:
        print(f"\nAVISO: fallaron {len(fallidos)} archivos: {fallidos}")
        print("Revisar si el sitio de CWRU cambio las rutas antes de continuar.")
        return 1

    print("\nDescarga completa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
