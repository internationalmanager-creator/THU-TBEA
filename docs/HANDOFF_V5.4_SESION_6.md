# HANDOFF v5.4 — SESIÓN 6

**Proyecto:** Tesis THU-TBEA — Erick Duque
**ORCID:** 0009-0004-1245-5464
**Versión activa:** v5.4 (reconstrucción auditada capítulo por capítulo)
**Fecha generación:** 2026-09-23
**Estado:** Caps. 1–18 completos. 107 secciones cerradas. Bibliografía v4 certificada (71 entradas, 11 DOIs verificados). Fase de figuras v5.4: 195/195 artefactos regenerados con tema editorial print. Sub-bloque 1e (inserción de figuras en .tex) pendiente.

---

## 1. MODELO DE 3 ROLES

Idéntico a Sesión 5. Sin cambios:

1. **VOS (asistente técnico):** redactás borradores ES/EN/DE, aplicás ajustes del auditor, empaquetás scripts PowerShell únicos, corrés tests, mantenés estado del repo. Si falta un archivo, lo pedís.
2. **AUDITOR EXTERNO (Erick con otro asistente):** revisa borradores, devuelve veredicto + ajustes textuales exactos, aprueba explícitamente antes de empaquetar. Vos NO inventás auditorías.
3. **ERICK (autor y director):** pega borradores al auditor, trae veredicto, ejecuta scripts PowerShell, pega outputs, decide alcance.

**Regla de oro:** no empaquetar scripts sin aprobación del auditor. No preguntar lo que el handoff responde. No tratar esto como proyecto nuevo.

**Repo local:** `C:\Users\kg4tr\Documents\Investigacion_lab_secreto`
**Repo red:** `\\Atila\f\THU-TBEA_Lab`

---

## 2. ESTADO DEL REPOSITORIO (post Sesión 6)

### Hashes verificados al cierre de Sesión 6

| Archivo | Ruta | Hash |
|---|---|---|
| `chapter_bodies.json` | `registry\thu\` | **`e0476e46d1af1779`** |
| `i18n_content.json` | `registry\thu\` | **`1ed56e959a8d5d66`** |
| `problems.json` | `registry\thu\` | `84e4ee068824c17d` (sin cambios) |
| `patches.json` | `registry\thu\` | `769c0c6580f9a05e` (sin cambios) |
| `doi_registry.json` | `registry\thu\` | `c7c56cd0946c2c84` |
| `thu_references.bib` | `paper\thu\src\` | **`c3d48abd2b1ec3fb`** (v4 certificado) |
| `figures.py` | `src\thu\` | **`192b08482f463b89`** |
| `figures_metadata.json` | `registry\thu\` | **`623a94226c221cd5`** (i18n completo) |
| `figures_manifest.json` | `paper\thu\figures\` | **`f077cc21efc573d0`** |
| `loader.py` | `src\thu\` | **`9e9797aa92db1080`** |
| `app_thu.py` | repo raíz | **`0b45a244f19c1a08`** |
| `latex_builder.py` | `src\thu\` | `e5afb9e7c49d4cd8` (sin cambios aún) |

### Capítulos cerrados

| Cap | Secciones | Estado |
|:---:|:---------:|:------:|
| ch01–ch17 | 102 | ✅ (heredados Sesión 5) |
| ch18 | 5 | ✅ (cerrado Sesión 5) |
| **Total** | **107** | |

### Fase de figuras v5.4 — completada

| Artefacto | Cantidad |
|---|:-:|
| Figuras en metadata | **65** |
| Generadores en `figures.py` | **65** |
| **PDFs vectoriales** | **65** |
| **PNG 300 DPI** | **65** |
| **PNG 150 DPI** | **65** |
| **TOTAL** | **195** |

- Tema: print (fondo blanco, STIX General, spines editoriales, ticks inward).
- Paleta canónica: [D] `#00B894` · [P] `#6C5CE7` · [F] `#E17055` · [A] `#D4A017` · info `#0984E3`.
- i18n: 65/65 figuras con `theory`/`demo` en ES/EN/DE.
- `figures_metadata.json` tiene `cap` y `sec` por figura (para inserción automática en LaTeX).
- PNGs viejos (dark theme) en `paper\thu\figures\_old\`.

### Streamlit — infra actualizada

- `loader.py`: `figure_metadata(lang="es")` y `figure_meta(nombre, lang="es")` resuelven dict/string i18n.
- `app_thu.py`: `render_figures` pasa `lang=st.session_state.get("lang", "es")`.
- Retrocompat total: 0 legacy restantes.

### Backups Sesión 5–6

- `data\_backup_v5.4_cap18_20260923_111946`
- `data\_backup_v5.4_figures_20260923_121406` (manifest + figures.py pre-cleanup)
- `data\_backup_v5.4_i18n_*` (5 backups, uno por bloque)
- `data\_backup_v5.4_figpy_*` (varios)
- `data\_backup_v5.4_figures_regen_20260923_123121` (65 PNG dark viejos)
- `data\_backup_v5.4_figB01a_20260923_125629`

---

## 3. QUÉ SE CERRÓ EN SESIÓN 5–6

### 3.1 Sesión 5 (heredado)

- **Cap. 18 — Ajuste conjunto sobre datos públicos** (5 secciones).
- Advertencia metodológica textual preservada (§18.4): "Los resultados corresponden exclusivamente a un conjunto de datos sintéticos (mocks)…".
- **107 secciones cerradas** (102 + 5).
- Hash post: `chapter_bodies.json` → `e0476e46d1af1779`; `i18n_content.json` → `1ed56e959a8d5d66`.

### 3.2 Sesión 6 — Fase de figuras v5.4

**Sub-bloque 1a — Metadata faltante:**
- 7 entradas nuevas añadidas: `fig_12-01_escala_masas`, `fig_B-01a_beta_function`, `fig_B-02_integral_I2`, `fig_B-03_lambert_w`, `fig_B-04_jerarquia_aurea`, `fig_B-05_coeficiente_A`, `fig_B-06_residuo_propagador`.
- `cap` y `sec` añadidos a las 65 entradas.

**Sub-bloque 1b — i18n 65/65:**
- 5 bloques de traducción ES/EN/DE (15+17+9+12+5 figuras).
- `theory` y `demo` convertidos de string a dict `{es, en, de}`.
- `i18n_estado = "COMPLETO"` declarado en JSON.

**Sub-bloque 1c — Limpieza:**
- 5 duplicados bit-a-bit eliminados.
- 8 colisiones de naming renombradas a `fig_NN-SSa` / `fig_NN-SSb`.
- 6 alias muertos removidos del metadata.
- `figures.py` actualizado con keys renombradas.

**Fix i18n — `loader.py` + `app_thu.py`:**
- `_resolve_i18n()` + `_figure_metadata_raw()` (cacheada) + `figure_metadata(lang)`.
- Retrocompat 100% (string legacy y dict i18n coexisten).

**Sub-bloque 1d-A — Refactor editorial `figures.py`:**
- `THEME_PRINT` (12 claves), rcParams STIX + spines off + ticks inward.
- `_save()` genera PDF + PNG300 + PNG150 simultáneamente.
- 233 reemplazos de color chrome.
- 7 generadores nuevos añadidos (B-02 a B-06 + B-01a) + alias `fig_03-07_cadena_cy3_n88`.
- Brace counter + `compile()` check (barrera contra SyntaxError).
- 26/26 tests PASS.

**Sub-bloque 1d-B — Regeneración 195/195:**
- 65 figuras × 3 formatos = **195 artefactos**.
- 136s de duración.
- Fix posterior de `fig_B-01a_beta_function` (bug de alias sin propagación de nombre).
- 195/195 verificado.

**Lección aprendida nueva (#15):** los aliases en `GENERADORES` no propagan el nombre — `_save()` tiene el nombre hardcoded. Usar funciones wrapper, no aliases.

**Lección aprendida nueva (#16):** para insertar antes del cierre de un dict grande, usar **brace counter** desde `X = {` en lugar de `rfind("}")` (que puede caer dentro de strings). Además, `compile(src, ...)` antes de escribir para detectar SyntaxError.

---

## 4. DEUDAS PENDIENTES AL CIERRE DE SESIÓN 6

### Deudas críticas (bloquean 1e)

| # | Deuda | Prioridad | Estado |
|:-:|---|:---:|---|
| 1 | **Script A**: Manifest fix + `\graphicspath` diagnostic | **ALTA** | Listo, pendiente ejecutar |
| 2 | **1e**: Extensión de `latex_builder.py` (inserción figuras en .tex) | **ALTA** | Pendiente (requiere veredicto auditor) |

### Deudas importantes (post 1e)

| # | Deuda | Prioridad |
|:-:|---|:---:|
| 3 | Streamlit completo (4 secciones con `render_history` huérfana + dependencies) | MEDIA |
| 4 | Compilación LaTeX final 3 idiomas (ES/EN/DE) con figuras | MEDIA |
| 5 | Handoff Sesión 7 al cierre | BAJA |

### Deudas heredadas (Sesiones previas)

| # | Deuda | Prioridad |
|:-:|---|:---:|
| 6 | Cap. 19 (Pipeline reproducible y unit tests) | MEDIA |
| 7 | Cap. 20 (Problemas abiertos y trabajo futuro) | MEDIA |
| 8 | Cap. 21 (Conclusiones lakatosianas finales) | MEDIA |
| 9 | Materializar Anexo K (hoy es resumen de 6 subsecciones) | MEDIA |
| 10 | Recalcular hash de `doi_registry.json` tras 11 verified:true | BAJA |

### Caps. pendientes

| Cap | Título | Fuente |
|:---:|---|---|
| 19 | Pipeline reproducible y pruebas unitarias | `PROGRAMA_COMPLETO_v5.0.pdf` §19 |
| 20 | Problemas abiertos y trabajo futuro | §20 |
| 21 | Conclusiones y evaluación lakatosiana final | §21 |

---

## 5. REGLAS OPERATIVAS

### Arquitectura LaTeX (heredada Sesión 3)

- **Títulos de capítulo:** `i18n_content.json → chapter_titles`.
- **Títulos de sección y cuerpos:** `chapter_bodies.json → chapters.chNN.sections`.
- **Ecuaciones clave:** `i18n_content.json → chapter_equations`.
- **Apéndices B y K:** `i18n_content.json → appendix_bodies`.
- **Bibliografía:** `_bibliography(lang, i18n)` inserta `\bibliography{thu_references}` antes de `\end{document}`.
- **Figuras (nuevo Sesión 6):** `latex_builder.py` debe leer `figures_metadata.json` + `figures_manifest.json` e insertar bloques `\begin{figure}` tras cada sección. Requiere `\graphicspath{{figures/}}` en el preámbulo.

### Patrón de script PowerShell (validado Sesiones 3–6)

Cada bloque se empaqueta como **script único, completo, en un solo bloque de copiar** con:

1. Backup con timestamp en `data\_backup_v5.4_<tipo>_YYYYMMDD_HHMMSS`.
2. Hashes pre-merge (16 chars).
3. Python merge en `$env:TEMP\*.py`, verifica `MERGE_OK` (o tag específico del bloque).
4. Merge atómico (verificación estructural del temp antes de copiar).
5. Regeneración de `.tex` con `python src\thu\latex_builder.py --all` (cuando aplique).
6. Tests `T<NNN>` con `-match [regex]` (Unicode-safe).
7. Reporte final OK/FALLA + restauración automática si falla.
8. **Sin `exit`** — try/catch global.

### Lecciones aprendidas (Sesiones 1–6)

| # | Bug histórico | Fix |
|:-:|---|---|
| 1 | `-notmatch` sobre array | `$mergeText = ($mergeOutput -join "`n")` |
| 2 | `exit` cierra consola | try/catch sin exit |
| 3 | Diacríticos mal escritos | Verificar cada marca contra el cuerpo |
| 4 | Heredocs PowerShell anidados | Usar scripts Python externos |
| 5 | Paréntesis sin cerrar en `Write-Host` | No mezclar `(` con `-ForegroundColor` |
| 6 | `_bibliography(lang, t)` con `t` undefined | Usar variable real de `build()` = `i18n` |
| 7 | `re.subn` con `\d` en replacement | Escapar backslashes en strings raw |
| 8 | `\\` en heredoc | Escribir `.bib` por chunks con Add-Content |
| 9 | Python string con `$` en PowerShell here-string | Usar `@'...'@` (comilla simple) para literales |
| 10 | `schallhorizont` con guion en alemán | Composición directa: `Schallhorizontskala` |
| 11 | `\$` no es escape válido en PowerShell | Usar `@'...'@` con `$` literal |
| 12 | `.Contains()` falla con diacríticos | Usar regex `.` que matchea cualquier char |
| 13 | Regex con paréntesis literal | Escape con `\(` |
| 14 | Búsqueda hardcoded de rutas | Walk-up desde `Get-Location` |
| 15 | **Carácter `✓`/`⚠` en `print()` Python rompe cp1252 en Windows** | **Usar ASCII `[OK]`/`[!]`** |
| 16 | **Aliases en `GENERADORES` no propagan el nombre en `_save()`** | **Usar funciones wrapper reales** |
| 17 | **`rfind("}")` cae dentro de strings con llaves** | **Brace counter + `compile()` pre-escritura** |
| 18 | **Backup anidado `Copy-Item dir dir\sub`** | **Usar `Copy-Item "src\*" "dst\"`** |
| 19 | **Tests de import deben correr sobre archivo real, no solo grep** | **Siempre `from thu import X` en test runtime** |

### Convenciones de etiquetas epistémicas (v5.4)

- `[D]` derivado
- `[D parcial]` derivado en subrégimen declarado
- `[D condicional X]` derivado bajo hipótesis X
- `[P]` postulado
- `[F]` frontera abierta
- `[F parcial]` frontera con subproblemas cerrados
- `[A]` analogía
- `[D con protocolo preregistrado]`
- `[D con derivación delegada a Cap. N]`
- **`[D empírica]`** (Sesión 4): verificada numéricamente, no derivada del núcleo.

---

## 6. MENSAJE DE ARRANQUE PARA EL CHAT NUEVO

**Pegar este bloque al inicio del chat nuevo, DESPUÉS de adjuntar los archivos.**

---

Sos el asistente técnico de Erick Duque para la tesis THU-TBEA v5.4.

**Estado:** Caps. 1–18 completos, 107 secciones cerradas. Bibliografía v4 certificada (71 entradas, 11 DOIs verificados). **Fase de figuras v5.4 completa: 195/195 artefactos regenerados con tema editorial print.** Sub-bloque 1e (inserción de figuras en .tex) pendiente.

**Hashes actuales:**
- `chapter_bodies.json`: `e0476e46d1af1779`
- `i18n_content.json`: `1ed56e959a8d5d66`
- `problems.json`: `84e4ee068824c17d`
- `thu_references.bib`: `c3d48abd2b1ec3fb`
- `figures.py`: `192b08482f463b89`
- `figures_metadata.json`: `623a94226c221cd5`
- `figures_manifest.json`: `f077cc21efc573d0`
- `loader.py`: `9e9797aa92db1080`
- `app_thu.py`: `0b45a244f19c1a08`

**Modelo de 3 roles vigente:**
- VOS: redactás, aplicás ajustes, empaquetás scripts PowerShell.
- AUDITOR EXTERNO: Erick lo lleva, devuelve veredicto + ajustes.
- ERICK: dirige, ejecuta scripts, trae outputs.

**Regla de oro:** no empaquetar sin aprobación del auditor. No preguntar lo que el handoff responde. No tratar esto como proyecto nuevo.

**Tarea inmediata — Paso 1: Script A (manifest fix + graphicspath):**
- Regenerar `figures_manifest.json` sin duplicados (bug `fig_B-01a` resuelto pre-1e).
- Diagnosticar presencia de `\graphicspath{{figures/}}` en los 3 `.tex`.
- 6 tests PASS/FAIL con backup + restauración automática.

**Tarea inmediata — Paso 2: 1e (inserción de figuras en .tex):**
- Extender `latex_builder.py` para leer `figures_metadata.json` + `figures_manifest.json`.
- Insertar bloques `\begin{figure}` tras cada sección según `sec` del metadata.
- `\includegraphics[width=0.85\textwidth]{figures/<name>.pdf}`.
- `\caption{\textbf{Figura:} <source>}`.
- `\label{fig:<name>}` para futuras referencias.
- Inyectar `\graphicspath{{figures/}}` si falta en los `.tex`.
- **5 decisiones de diseño del auditor** pendientes de resolver (ver §11).

**Antes de escribir:** verificá que los 10 archivos obligatorios estén adjuntos. Si falta alguno, pedilo.

**Leé el handoff completo antes de escribir.**

---

## 7. ARCHIVOS A ADJUNTAR AL CHAT NUEVO

### Obligatorios (10)

1. `docs\HANDOFF_V5.4_SESION_6.md` (este archivo)
2. `registry\thu\chapter_bodies.json`
3. `registry\thu\i18n_content.json`
4. `registry\thu\problems.json`
5. `registry\thu\patches.json`
6. `data\inventory\verificacion_simbolica.json`
7. `src\thu\latex_builder.py`
8. `registry\thu\doi_registry.json`
9. `paper\thu\src\thu_references.bib`
10. `paper\thu\src\tesis_es.tex`

### Obligatorios específicos de Sesión 6 (nuevos)

11. `src\thu\figures.py` (post-refactor 1d-A, hash `192b08482f463b89`)
12. `registry\thu\figures_metadata.json` (i18n completo, hash `623a94226c221cd5`)
13. `paper\thu\figures\figures_manifest.json` (post 1d-B)
14. `src\thu\loader.py` (post-fix i18n, hash `9e9797aa92db1080`)
15. `app_thu.py` (post-fix i18n, hash `0b45a244f19c1a08`)

### Opcionales

16. `PROGRAMA_COMPLETO_v5.0.pdf`
17. `tesis_en.tex`, `tesis_de.tex`
18. Muestra de figuras: `paper\thu\figures\fig_03-01_helice_aurea.pdf` (nueva, tema print), `paper\thu\figures\fig_B-01a_beta_function.pdf` (recién generada)

### NO adjuntar

- Backups `_backup_*` (referenciar por path)
- `data\raw\*`
- `pantheon_cov_used.npy`
- `paper\thu\figures\_old\` (65 PNG dark, temporales)
- Los 195 artefactos nuevos (demasiado peso; se regeneran con `figures.py --all`)

---

## 8. CHECKLIST DE CONTINUIDAD

Antes de cada bloque nuevo:

- [ ] ¿El auditor aprobó el borrador textual (si aplica)?
- [ ] ¿Los hashes de ch01–ch18 están intactos?
- [ ] ¿El script tiene backup + restauración automática?
- [ ] ¿El script es **un solo bloque de copiar** completo?
- [ ] ¿Las marcas de test usan regex Unicode-safe (`-match 'emp.rica'`)?
- [ ] ¿El reporte final es OK/FALLA?
- [ ] ¿Los tests de import corren sobre el archivo real (no solo grep)?
- [ ] ¿Se usan caracteres ASCII en `print()` Python (evitar `✓`/`⚠`)?
- [ ] ¿Se usa brace counter para inserción en dicts grandes?

Antes de compilar LaTeX:

- [ ] ¿`biber` y `pdflatex` disponibles en PATH?
- [ ] ¿`thu_references.bib` sin entradas con `% TODO`?
- [ ] ¿`tesis_es.tex` incluye `\bibliography{thu_references}`?
- [ ] ¿`tesis_es.tex` incluye `\graphicspath{{figures/}}`?
- [ ] ¿Todos los caps. 1–21 completos?

---

## 9. CONTEXTO HISTÓRICO

- Etapa I (2024–2025): Formación inicial.
- Etapa II (2025–2026): Núcleo heurístico.
- Etapa III (2026): Cierre formal v4.0.
- Etapa IV (2026): Corrección estructural v4.1.
- Etapa V (2026): Cierre computacional v4.3.
- Etapa VI (2026): Cristalización v5.0.
- Etapas VII–X (2026): Revisiones externas (parches 1–17).
- Etapa XI (2026): Auditoría epistémica v5.4.
- Etapa XII (2026): Auditoría de bloques v5.4 (parches 18–24).
- Etapa XIII (2026): Reconstrucción capítulo por capítulo.
  - Sesión 1–2: Caps. 1–13, fix bibliográfico.
  - Sesión 3: Verificación DOIs + Caps. 14, 15 + borrador Cap. 16.
  - Sesión 4: Decisión Confirmación 1 + Cap. 16 + bibliografía v3/v4.
  - Sesión 5: Cap. 17 (síntesis falsable P1–P12) + Handoff Sesión 5 + Cap. 18.
  - **Sesión 6 (actual):** Fase de figuras v5.4 completa (1a–1d). 195/195 artefactos. Handoff Sesión 6.

---

## 10. MENSAJE DE CIERRE

**Estado al generar Handoff Sesión 6:** Caps. 1–18 completos, 107 secciones cerradas. Bibliografía v4 certificada (71 entradas, 11 DOIs verificados). Fase de figuras v5.4 completa: 195 artefactos (65 PDF + 65 PNG300 + 65 PNG150) con tema editorial print. Sub-bloque 1e pendiente.

**Hashes:**
- `chapter_bodies.json`: `e0476e46d1af1779`
- `i18n_content.json`: `1ed56e959a8d5d66`
- `figures.py`: `192b08482f463b89`
- `figures_metadata.json`: `623a94226c221cd5`
- `figures_manifest.json`: `f077cc21efc573d0`
- `loader.py`: `9e9797aa92db1080`
- `app_thu.py`: `0b45a244f19c1a08`
**Fecha generación:** 2026-09-23

**Siguiente sesión debe empezar por:** Script A (manifest fix + graphicspath) → Script B (extensión `latex_builder.py` para 1e).

**Fin del handoff.**

---

## 11. DECISIONES PENDIENTES DEL AUDITOR (para 1e)

Estas 5 decisiones deben resolverse antes de empaquetar el Script B:

1. **¿Inyectar `\graphicspath{{figures/}}` siempre o solo si falta?**
   - Mi propuesta: **solo si falta** (idempotente).
2. **¿`FIG_WIDTH = "0.85\\textwidth"` está OK?**
   - Confirmado por auditor con margen de seguridad contra Overfull.
3. **¿Uso `label="fig:<name>"` para `\ref{}` futuras?**
   - Mi propuesta: **sí** (gratis, útil).
4. **¿`[htbp]` (here/top/bottom/page) o `[H]` (here forzado, requiere `float`)?**
   - Mi propuesta: **`[htbp]`** (sin dependencia extra).
5. **¿CLI `--with-figures` opcional o siempre incluir figuras?**
   - Mi propuesta: **`--with-figures` opcional** (retrocompat).

---

**Nota final para Erick:** este handoff está pensado para que lo pegues al inicio del chat nuevo junto con los archivos de la sección 7. Si te falta alguno de los críticos (sobre todo `figures.py` con hash `192b08482f463b89` o `figures_metadata.json` con hash `623a94226c221cd5`), pedímelo antes de arrancar la Sesión 7. Si querés que arranquemos la Sesión 6 continuada en este mismo chat, decime y lo hacemos.
