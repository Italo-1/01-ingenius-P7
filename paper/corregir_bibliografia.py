#!/usr/bin/env python
"""P7 - hace que los DOI verificados lleguen al PDF, y corrige un autor fantasma.

Diagnostico. La revision cruzada del 03/09 reporto que las quince referencias
"carecen de DOI" e invoco la regla no negociable 2 de la guia. Miro el PDF, y
en el PDF no hay DOI. Pero:

  - `referencias.bib` SI los tiene: once de las quince entradas los llevan, y
    las cuatro que no son las mismas cuatro que el propio informe identifica
    como sin DOI (CWRU, dos de JMLR y las actas de NeurIPS).
  - `paper/references.bib` documenta que las quince se verificaron el 24/08
    siguiendo los tres pasos de la guia, con notas por entrada sobre hasta
    donde llega la comprobacion y para que se puede citar cada una.

O sea que la regla 2 —que exige VERIFICAR abriendo el DOI— se cumplia. Lo que
fallaba es que el DOI no se IMPRIME, y son cosas distintas.

La causa: `IEEEtran.bst` version 1.14 no conoce el campo `doi`. Cero
apariciones de la cadena "doi" en las 2.700 lineas del estilo. Se puede
comprobar con:

    grep -c doi $(kpsewhich IEEEtran.bst)

Y las normas editoriales de Ingenius (seccion 3.2, `paper/evidencia/`) sí piden
que aparezca, en este formato exacto:

    [1] J. Riess, J. J. Abbas, "Adaptive control of cyclic movements...".
        IEEE Trans. Neural Syst. Rehabil. Eng vol. 9, pp.326-330, 2001.
        [Online]. Available: https://doi.org/10.1109/7333.948462

`IEEEtran.bst` si conoce el campo `url` y lo emite justamente como
"[Online]. Available: ...". Asi que la solucion es derivar `url` de `doi`.

Ademas se corrige un error de contenido que no vio ninguno de los dos informes
(ver AUTOR_FANTASMA mas abajo).

    python paper/corregir_bibliografia.py
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Los dos .bib del proyecto. `references.bib` es la copia de trabajo, con las
# notas de verificacion; `referencias.bib` es la que compila el manuscrito.
# Estaban desincronizados: la de trabajo ya tenia las URL de JMLR y la de
# compilacion no.
BIBS = [
    RAIZ / "paper" / "references.bib",
    RAIZ / "paper" / "Revista_Ingenius_Ecuador" / "referencias.bib",
]

# Entradas sin DOI. Las cuatro son legitimas: un dataset y tres publicaciones
# que no tienen DOI asignado. Se les da una via de verificacion estable, que es
# lo que la regla 2 persigue.
SIN_DOI = {
    # JMLR no asigna DOI; la URL del volumen es permanente.
    "demsar2006": "https://www.jmlr.org/papers/v7/demsar06a.html",
    "pedregosa2011": "https://www.jmlr.org/papers/v12/pedregosa11a.html",
    # Las actas de NeurIPS 2019 no tienen DOI. Se usa el arXiv, comprobado el
    # 03/09: titulo y autores coinciden con la entrada.
    "paszke2019": "https://arxiv.org/abs/1912.01703",
    # `cwru` ya lleva su URL en `howpublished`, que IEEEtran si imprime.
}

# Autor fantasma en salazar2012, una de las cuatro citas a la revista destino.
#
# El .bib lista cinco autores. Crossref (10.17163/ings.n7.2012.02) y la propia
# ficha del articulo en el OJS de Ingenius listan CUATRO: Salazar, Quizhpi,
# Bueno y Reyna. "Jose Manuel Aller" no es autor de este articulo. Comprobado
# el 03/09 contra las dos fuentes.
#
# Importa mas de lo que parece: es una cita a la revista a la que se envia, y
# el editor la reconoce.
AUTOR_FANTASMA = ("Salazar, Luisa and Quizhpi, Flavio and Aller, Jos{\\'e} Manuel "
                  "and Bueno, Alexander and Reyna, Rodney")
AUTOR_CORRECTO = ("Salazar, Luisa and Quizhpi, Flavio and Bueno, Alexander "
                  "and Reyna, Rodney")


def procesar(texto: str) -> tuple[str, int, int]:
    """Anade `url` a partir de `doi`, y de `SIN_DOI` donde no hay DOI."""
    bloques = re.split(r"\n(?=@)", texto)
    urls = 0

    for i, bloque in enumerate(bloques):
        m = re.match(r"@(\w+)\{([^,]+),", bloque)
        if not m:
            continue
        clave = m.group(2)

        if re.search(r"^\s*url\s*=", bloque, re.M):
            continue  # ya la tiene

        doi = re.search(r"^(\s*)doi\s*=\s*\{([^}]+)\}(,?)", bloque, re.M)
        if doi:
            # La linea `doi` se reescribe entera para garantizarle la coma
            # final: varias entradas la tenian como ultimo campo y sin coma, y
            # anadir `url` detras dejaba el .bib sintacticamente roto.
            sangria, valor, _ = doi.groups()
            inicio, fin = doi.span()
            bloques[i] = (
                bloque[:inicio]
                + f"{sangria}doi     = {{{valor}}},\n"
                + f"{sangria}url     = {{https://doi.org/{valor}}},"
                + bloque[fin:]
            )
            urls += 1
        elif clave in SIN_DOI:
            # La llave de cierre de una entrada esta en la columna 0. Buscarla
            # asi, y no con `rstrip()`, respeta los comentarios de verificacion
            # que van DESPUES de cada entrada en `references.bib` y que son la
            # documentacion de la regla 2.
            cierre = re.search(r"^\}", bloque, re.M)
            if cierre is None:
                continue
            antes = bloque[:cierre.start()].rstrip()
            if not antes.endswith(","):
                antes += ","
            bloques[i] = (antes + f"\n  url     = {{{SIN_DOI[clave]}}}\n"
                          + bloque[cierre.start():])
            urls += 1

    salida = "\n".join(bloques)
    fantasmas = salida.count(AUTOR_FANTASMA)
    salida = salida.replace(AUTOR_FANTASMA, AUTOR_CORRECTO)
    return salida, urls, fantasmas


def main() -> int:
    total_urls = total_fantasmas = 0
    for bib in BIBS:
        if not bib.exists():
            print(f"AVISO: no existe {bib}")
            continue
        copia = bib.with_suffix(".bib.antes_revision_cruzada")
        if not copia.exists():
            shutil.copy2(bib, copia)

        texto = bib.read_text(encoding="utf-8")
        nuevo, urls, fantasmas = procesar(texto)
        bib.write_text(nuevo, encoding="utf-8")
        print(f"{bib.name}: +{urls} url, {fantasmas} autor fantasma corregido")
        total_urls += urls
        total_fantasmas += fantasmas

    print(f"\n{total_urls} URL anadidas, {total_fantasmas} correcciones de autoria.")
    print("Recompilar: pdflatex + bibtex + pdflatex x2 en "
          "paper/Revista_Ingenius_Ecuador/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
