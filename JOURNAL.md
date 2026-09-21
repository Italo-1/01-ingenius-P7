# Ficha de revista

Plantilla de la guía metodológica, sección 1.3. **Completada el 24/08/2026**, tras
recuperarse el sitio y leer las cinco citas obligatorias.

- **Nombre completo:** Ingenius, Revista de Ciencia y Tecnología
- **URL oficial:** https://ingenius.ups.edu.ec
- **Editorial:** Universidad Politécnica Salesiana, Ecuador
- **ISSN:** 1390-650X (impreso) / 1390-860X (electrónico)
- **¿Cobra APC?** `[x] No` `[ ] Sí -> MONTO:`
- **Fuente de la respuesta:** la página de acceso abierto lo dice literalmente:
  *«does not have any economic charge for the publication or for access to the
  material»*
  (`https://ingenius.ups.edu.ec/index.php/ingenius/accesoabierto`). Las normas
  editoriales, leídas completas, tampoco mencionan cargo alguno.
  **Evidencia guardada** el 24/08/2026 en `paper/evidencia/`: el HTML original de
  la página de acceso abierto, el de la política de IA y el PDF de las normas.
  Licencia CC BY-NC-SA 4.0.
- **Indexación:** Scopus (desde abril de 2023), DOAJ, REDALYC, ESCI de Clarivate,
  SciELO Ecuador, Latindex, MIAR, REDIB.
> **Corrección del 24/08 (tarde), al obtener la plantilla LaTeX oficial.** La
> plantilla contradice en dos puntos al PDF de normas de 2021, y **manda la
> plantilla** por ser el documento vigente que la propia revista distribuye:
>
> | Punto | PDF de normas (2021) | Plantilla LaTeX | Adoptado |
> |---|---|---|---|
> | Extensión | 4 000-6 500 palabras | **5 000-6 000** | 5 000-6 000 (el manuscrito tiene 5 822) |
> | Palabras clave | 6 | **3 a 6, en orden alfabético** | 6, **alfabéticas** |
>
> La plantilla añade además que el recuento incluye «títulos, autores,
> adscripción institucional, resúmenes, palabras clave, tablas y referencias».
> El enlace de descarga del PDF de normas (`goo.gl/Mwv8IC`) está **muerto**:
> apunta a un `.7z` de 2017 que devuelve 404. La plantilla vigente solo está en
> Overleaf, que exige cuenta para obtenerla.

- **¿Plantilla LaTeX oficial?** `[x] Sí`
  → **https://www.overleaf.com/latex/templates/revista-ingenius-ecuador/zsnnwhmcwzyj**
  (las normas la enlazan como `https://goo.gl/Mwv8IC`)
  Plantilla Word alternativa: `Template_INGENIUS_2023.docx`
  (`https://goo.gl/ZA2XAk`). **El HTTP 500 del 22/08 se resolvió**: el sitio
  respondía con normalidad el 24/08.
- **Límite de páginas / palabras:** **4 000 a 6 500 palabras** para
  investigaciones, **incluyendo título, resúmenes, palabras clave, tablas y
  referencias**. (Informes y propuestas: 5 000-6 500. Revisiones: 6 000-7 000.)
- **Estilo de citas:** **IEEE**, numeradas entre corchetes por orden de
  aparición. Ninguna referencia puede figurar sin estar citada en el texto.
- **¿Requiere abstract estructurado?** No lo llama así, pero **fija el orden del
  contenido**, lo que equivale a uno: 1) justificación del tema; 2) objetivos;
  3) metodología y muestra; 4) principales resultados; 5) principales
  conclusiones. **Máximo 230 palabras.**
- **¿Requiere declaración de uso de IA?** **Sí, y es obligatoria.** Va **en la
  cover letter**, no en el manuscrito, y hay que especificar **qué herramienta se
  usó y para qué**. La revista admite el uso de IA como apoyo en análisis
  estadístico, redacción y traducción, pero **no acepta en ningún caso una
  herramienta de IA como coautora**, y prohíbe alterar resultados o fabricar
  datos, engañar en la revisión, reproducir contenido de terceros sin permiso y
  volcar información restringida en plataformas públicas.
  (`https://ingenius.ups.edu.ec/index.php/ingenius/ia`, leída el 24/08/2026.)
- **¿Requiere declaración de disponibilidad de datos?** No aparece en las normas.
  Se incluirá igualmente, junto al DOI de Zenodo.
- **Sistema de envío:** OJS. Envío en Word (.doc/.docx) o LaTeX (.tex). En LaTeX
  hay que subir **el PDF como archivo original, más un comprimido con el código
  fuente**, más **cada figura en archivo aparte** a 300 dpi o vectorial.
- **Revisión por pares:** doble ciego, dos o más revisores. El archivo debe estar
  **anonimizado en las propiedades del archivo**. Comprobación inicial de hasta
  4 semanas; segunda fase de 4 semanas como mínimo.
- **Fecha de cierre del próximo número:** **15 de noviembre de 2026** para el
  n.º 37 (enero de 2027). Semestral, con números el 1 de enero y el 1 de julio,
  y convocatoria abierta todo el año. **Sin urgencia de calendario.**

## Requisitos de formato que hay que respetar

| Elemento | Norma |
|---|---|
| Título | En **español e inglés**, los dos, sea cual sea el idioma del manuscrito |
| Autores | Máximo 5, con adscripción y **ORCID** |
| Resumen | ≤ 230 palabras, en **español e inglés** |
| Palabras clave | **6 por idioma**; se valora usar el Tesauro de la UNESCO |
| Epígrafes | Numerados en arábigo, máximo 3 niveles (1. / 1.1. / 1.1.1.), sin mayúsculas, negritas ni subrayado, alineados a la izquierda |
| Tablas | Numeradas en arábigo, **subtítulo encima** de la tabla, justificado a la izquierda |
| Figuras | Archivo aparte cada una, ≥ 300 dpi o vectorial (.ps, .eps, .pdf); texto ≥ 2,5 mm tras la reducción; paneles rotulados a, b, c; no mezclar fotografía y dibujo lineal en la misma figura |
| Ecuaciones | Numeradas y citadas en el texto |
| Página final | 21 × 28 cm |
| Cover letter | **Obligatoria**, con formato propio (`https://goo.gl/XAc9a3`) |

## Choques con `REDACCION.md` que hay que resolver

`REDACCION.md` es el extracto de la guía metodológica y describe una estructura
genérica. Donde las dos normas discrepan, **manda la revista**.

| `REDACCION.md` | Ingenius | Resolución |
|---|---|---|
| Sección *Related Work* propia | **IMRDC no la contempla** | El estado del arte se integra en la Introducción, que las normas obligan a incluir «la literatura más significativa y actual» |
| *Discussion* y *Conclusion* separadas | Los cinco artículos leídos usan «Results and discussion» + «Conclusions» | Se adopta la convención de la revista: 4 secciones |
| Abstract 150-250 palabras | **≤ 230**, con orden fijado | Se respeta el tope de 230 y el orden de cinco partes |
| ~7-8 páginas | **4 000-6 500 palabras con referencias y tablas incluidas** | Es el límite real; hay que contar, no estimar por páginas |
| Manuscrito en inglés | Título, resumen y palabras clave **en los dos idiomas** | Se redacta en inglés y se traducen título, resumen y palabras clave |

Las limitaciones tienen sitio explícito: las normas piden que Discusión y
Conclusiones señalen «aportaciones y limitaciones» y «las deducciones y líneas
para futuras investigaciones». Encaja con las 3-4 limitaciones reales que exige
la guía.

## 5 artículos recientes leídos

**Leídos completos el 24/08/2026**, no solo el resumen.

1. Contreras Urgilés, W. R.; Maldonado Ortega, J.; León Japa, R. (2019).
   *Application of feed-forward backpropagation neural network for the diagnosis
   of mechanical failures in engines provoked ignition*. Ingenius, n.21,
   pp. 32-40. DOI: 10.17163/ings.n21.2019.03
2. Llanes-Cedeño, E. A.; Guardia-Puebla, Y.; De la Rosa-Andino, A.;
   Cevallos-Carvajal, S.; Rocha-Hoyos, J. C. (2019). *Detection of faults in
   combustion engines through indicators of temperature and injection pressure*.
   Ingenius, n.22, pp. 38-46. DOI: 10.17163/ings.n22.2019.04
3. Salazar, L.; Quizhpi, F.; Aller, J. M.; Bueno, A.; Reyna, R. (2012).
   *Detección de fallas en el aislamiento en las chapas del estator de máquinas
   eléctricas rotativas*. Ingenius, n.7, pp. 11-20.
   DOI: 10.17163/ings.n7.2012.02
4. Gómez, R.; Cabrera, D.; Robles, P. (2023). *Study for localization of fault in
   the electrical distribution systems*. Ingenius, n.30, pp. 64-78.
   DOI: 10.17163/ings.n30.2023.06
5. Villa, Y.; Vook, T.; Villa, J. L.; Carbajal, P.; Barrera, L.; Florez, M.
   (2022). *Structural and modal analysis of adapter plates for hydraulic
   hammers and skid steers under real work condition*. Ingenius, n.28,
   pp. 92-99. DOI: 10.17163/ings.n28.2022.09

> Corrección de autoría: la 3 y la 5 tienen **cinco y seis autores**, no cuatro
> como figuraba en la lista de candidatos. La 3 incluye a José Manuel Aller; la 5
> a Leonardo Barrera y Max Florez. Hay que corregirlo en el `.bib`.

### Notas de la lectura

| Aspecto | Observado |
|---|---|
| **Extensión** | 8 a 15 páginas; mediana **9**. Las de método experimental (n21, n22) son de 9 |
| **Número de referencias** | 4 a 30; mediana **19**. Las dos recientes (n28, n30) traen 19 y 30 |
| **Estructura de secciones** | IMRDC en las cuatro posteriores a 2019: `1. Introduction` / `2. Materials and methods` (con 4 a 7 subsecciones numeradas) / `3. Results and discussion` (con subsecciones) / `4. Conclusions` / `References`. La de 2012 es anterior a la norma y no la sigue |
| **Nivel de detalle del método** | **Alto y concreto.** Se nombran marca y modelo de los equipos (NI DAQ-6009, cámara Fluke Ti25, indicador Leutert DPI-2), el software con versión (LabView 2017, STATGRAPHICS Centurion XV, Ansys, Inventor 2020, CYME) y los parámetros de adquisición (10 kHz durante 5 s; 3,3 kHz; 850 rpm; 92-97 °C). Nuestro nivel de detalle encaja sin problema |
| **Tipo de figuras** | Mezcla amplia: fotografías de la instrumentación, diagramas de flujo con cajas de colores, señales en el tiempo, mapas de tensión FEA en color, capturas de pantalla de Minitab, y **barras 3D**. Tablas con reglas horizontales tipo booktabs |
| **Estadística** | Muy desigual. n22 es el más riguroso: **ANOVA multifactorial con tabla completa** (SS, GL, CM, F-ratio, p), media ± desviación y grupos homogéneos. n21 usa ANOVA de un factor y Tukey con IC del 95 %. n7, n28 y n30 **no usan ninguna prueba estadística** |

**Consecuencia para nuestro manuscrito.** El listón estadístico de la revista es
bajo y desigual, así que Friedman-Nemenyi más ANOVA de dos factores con eta
cuadrado parcial nos deja claramente por encima de la media. No hay que rebajar
nada. En figuras ocurre lo contrario: el estilo publicado incluye barras 3D y
capturas de pantalla, que la guía metodológica prohíbe. **Se sigue la guía**, no
el estilo de la revista: figuras más sobrias no son motivo de rechazo. El
precedente útil es la Figura 2 de n22, que usa medias con barras de intervalo.

## Verificación del paso 3: ¿dice cada cita lo que le vamos a hacer decir?

La verificación de DOI (paso 2, hecha el 21/08) probaba que el artículo existe.
Esto es el paso 3, que exige la guía y es el que más se salta.

| # | Veredicto | Qué sostiene de verdad |
|---|---|---|
| 1 | **Sirve** | Red neuronal para diagnóstico de fallas mecánicas a partir de la señal de un sensor, con **descriptores estadísticos temporales** (área, energía, entropía, máximo, media, mínimo, potencia, RMS) seleccionados por ANOVA, matriz de correlación y Random Forest. Es el paralelo directo de nuestra representación de estadísticos temporales. Además reporta un error de clasificación de 1,89e-11 % validado en el mismo motor: sirve, con cuidado y sin ironía, como ejemplo de evaluación dentro de la misma condición de operación |
| 2 | **Sirve** | **ANOVA multifactorial con interacción**, tabla completa y media ± desviación. Es el precedente metodológico de nuestro ANOVA de dos factores, y el contraste entre enfoque por indicadores medidos y enfoque por representación de señal, que es como ya lo planteaba el protocolo |
| 3 | **Sirve, pero solo en sentido estrecho** | Detección de fallas en máquinas eléctricas rotativas comparando dos métodos de medida, termografía y variación de flujo. **No tiene aprendizaje automático, ni representación de señal, ni estadística**, y trae 4 referencias. Sostiene «en esta revista se ha abordado el diagnóstico de fallas en máquinas rotativas» y nada más |
| 4 | **Sirve, y es la mejor** | Usa **wavelet Daubechies db4 de nivel 4** (`wavedec(I,4,'db4')`) para descomponer señales de falla y estimar la distancia al defecto. Misma familia y casi el mismo nivel que nuestra representación wavelet, publicado en 2023 y firmado desde la propia UPS. Es la cita que ancla nuestra elección de db4 en la revista destino |
| 5 | **NO sostiene lo que se le atribuía** | Es un **diseño estructural**: análisis estático, modal y de fatiga de una placa de adaptación en Inventor y Ansys, más registro de garantías de 10 placas. No mide cómo cambia una señal ni un modelo de diagnóstico al variar la condición de operación; analiza una estructura bajo una condición de diseño. Citarla para «las condiciones de operación cambian el comportamiento medido» sería exactamente el fallo que el paso 3 existe para evitar |

**Decisión propuesta:** retirar la 5 y quedarse con **cuatro** citas de la
revista. La lista de comprobación pide de 3 a 5, así que cuatro cumple. Se buscó
sustituto en el propio buscador de la revista y **Ingenius no tiene ningún
artículo sobre rodamientos, vibración ni diagnóstico por aprendizaje
automático**; lo más próximo son engranajes y control de un eslabón flexible, que
no encajan mejor que las que ya hay. Forzar una quinta cita sería rellenar.

## Idioma

La revista acepta español e inglés. **Decisión del proyecto: inglés**, para
unificar con los otros cuatro manuscritos. Título, resumen y palabras clave van
además en español, como exige la norma.
