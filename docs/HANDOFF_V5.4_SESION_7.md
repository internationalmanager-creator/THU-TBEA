# HANDOFF v5.4 — SESIÓN 7

**Proyecto:** Tesis THU-TBEA — Erick Duque
**ORCID:** 0009-0004-1245-5464
**Versión activa:** v5.4 (reconstrucción auditada capítulo por capítulo)
**Fecha generación:** 2026-09-23
**Estado:** Caps. 1-18 completos. 107 secciones cerradas. Bibliografía v4 certificada (71 entradas, 11 DOIs verificados). Fase de figuras v5.4: **1e completado, 53/65 figuras insertadas en los 3 .tex**. Compilación LaTeX pendiente (entorno sin pdflatex). 12 figuras huérfanas clasificadas.

---

## 1. MODELO DE 3 ROLES

Sin cambios respecto a Sesión 5-6:

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
| `problems.json` | `registry\thu\` | `84e4ee068824c17d` |
| `patches.json` | `registry\thu\` | `769c0c6580f9a05e` |
| `doi_registry.json` | `registry\thu\` | `c7c56cd0946c2c84` |
| `thu_references.bib` | `paper\thu\src\` | **`c3d48abd2b1ec3fb`** |
| `figures.py` | `src\thu\` | **`192b08482f463b89`** |
| `figures_metadata.json` | `registry\thu\` | **`623a94226c221cd5`** |
| `figures_manifest.json` | `paper\thu\figures\` | **`f077cc21efc573d0`** |
| `loader.py` | `src\thu\` | **`9e9797aa92db1080`** |
| `app_thu.py` | repo raíz | **`0b45a244f19c1a08`** |
| **`latex_builder.py`** | `src\thu\` | **`e5afb9e7c49d4cd8`** (post-Script-B) |
| `tesis_es.tex` | `paper\thu\src\` | **`3e3b522616fbfac4`** |
| `tesis_en.tex` | `paper\thu\src\` | **`f229fdf819fda59f`** |
| `tesis_de.tex` | `paper\thu\src\` | **`9bb14b0bd49508b8`** |

### Capítulos cerrados

| Cap | Secciones | Estado |
|:---:|:---------:|:------:|
| ch01-ch18 | 107 | ✅ |
| **Total** | **107** | |

### Fase de figuras v5.4

| Artefacto | Cantidad |
|---|:-:|
| Figuras en metadata | **65** |
| Generadores en `figures.py` | **65** |
| **PDFs vectoriales** | **65** |
| **PNG 300 DPI** | **65** |
| **PNG 150 DPI** | **65** |
| **TOTAL artefactos** | **195** |

**Sub-bloque 1e — COMPLETADO:**

- 53/65 figuras insertadas en `tesis_es.tex`, `tesis_en.tex`, `tesis_de.tex`.
- 10/10 tests estáticos PASS (balance figure env, paths, labels, captions, braces, cite keys).
- Backup: `data\_backup_v5.4_scriptB_20260923_132320`

**12 figuras huérfanas (clasificadas):**

**Grupo A — Apéndice B (7 figs), cubrible con 1e-part-2:**
- `fig_B-01a_beta_function` (sec=B.1)
- `fig_B-01b_variacion_palatini` (sec=B.01)
- `fig_B-02_integral_I2` (sec=B.5)
- `fig_B-03_lambert_w` (sec=B.3)
- `fig_B-04_jerarquia_aurea` (sec=B.5)
- `fig_B-05_coeficiente_A` (sec=B.5)
- `fig_B-06_residuo_propagador` (sec=B.2)

Causa: `_appendix_bodies()` en `latex_builder.py` no procesa figuras (solo `_chapters()` lo hace).
Fix: extender `_appendix_bodies()` con la misma lógica de matching por `sec` normalizado.

**Grupo B — apéndices/capítulos inexistentes (5 figs), decisión editorial:**
- `fig_20-01_problemas_status` (sec=20.1) — Cap. 20 no está en chapter_bodies
- `fig_E-01_metrica_FLRW` (sec=E.1) — Apéndice E no existe en appendix_bodies
- `fig_J-01_vertices_feynman` (sec=J.4) — Apéndice J no existe
- `fig_L-01_escalera_transescalar` (sec=L.1) — Apéndice L no existe
- `fig_M-01_PRISMA` (sec=M.1) — Apéndice M no existe

### Streamlit — infra actualizada

- `loader.py` con `figure_metadata(lang)` y `figure_meta(nombre, lang)`.
- `app_thu.py` con `render_figures` i18n-aware.

### Backups Sesión 5-6-7

- `data\_backup_v5.4_cap18_*`
- `data\_backup_v5.4_figures_*` (varios)
- `data\_backup_v5.4_figpy_*` (varios)
- `data\_backup_v5.4_figures_regen_20260923_123121`
- **`data\_backup_v5.4_scriptB_20260923_132320`** (nuevo, contiene latex_builder.py + 3 .tex pre-1e)

---

## 3. QUÉ SE CERRÓ EN SESIÓN 6

### 3.1 Fase de figuras v5.4 (heredada Sesión 5-6)

Cerrada en sesiones previas:
- Sub-bloque 1a: metadata faltante (7 nuevas entradas + cap/sec)
- Sub-bloque 1b: i18n 65/65
- Sub-bloque 1c: limpieza (5 duplicados + 8 renombrados + 6 alias muertos)
- Sub-bloque 1d-A: refactor editorial `figures.py` (THEME_PRINT, 195 artefactos)
- Sub-bloque 1d-B: regeneración 195/195
- Fix i18n en `loader.py` + `app_thu.py`

### 3.2 Sesión 6 — Script A + Script B (1e)

**Script A (manifest fix + graphicspath):**

- M01-M05 PASS → `figures_manifest.json` limpio (65 únicos, 0 duplicados, hash `f077cc21efc573d0`)
- M06 FALLÓ → ninguno de los 3 .tex tenía `\graphicspath`

**Script B (extensión latex_builder.py para 1e):**

Decisiones del auditor aplicadas:
- D1: inyectar `\graphicspath` siempre (preámbulo regenerado)
- D2: `FIG_WIDTH = 0.85\textwidth`
- D3: `\label{fig:<name>}` siempre
- D4: `[htbp]` (sin `float`)
- D5: sin flag CLI, graceful degradation si no hay manifest
- Fix path duplicado: `\includegraphics{name.pdf}` sin prefijo (V1 lo detectó)
- Fix normalización `sec`: `"03.01"` → `"3.1"`, `"B.01"` → `"B.1"` (Problema A detectado por asistente)

Funciones nuevas en `latex_builder.py`:
- `_norm_sec(s)` — normaliza números de sección
- `_load_figures_by_section()` — indexa manifest+metadata por `sec` normalizado
- `\graphicspath{{figures/}}` inyectado tras `\usepackage{graphicx}`
- Bloque de inserción de figuras dentro de `_chapters()`

Tests: 12/12 PASS en generación + 10/10 PASS en validación estática.

**Hallazgo de entorno:**

- `pdflatex` NO está instalado ni en PATH.
- Compilación LaTeX **bloqueada por entorno, no por código**.

---

## 4. DEUDAS PENDIENTES AL CIERRE DE SESIÓN 7

### Deudas críticas (bloquean sesión 7)

| # | Deuda | Prioridad |
|:-:|---|:---:|
| 1 | **Instalar MiKTeX o TeX Live** antes de compilar | **ALTA** |
| 2 | **Compilación LaTeX final 3 idiomas** con figuras | **ALTA** |
| 3 | **1e-part-2**: extender `_appendix_bodies()` para 7 figs del Apéndice B | **ALTA** |

### Deudas importantes

| # | Deuda | Prioridad |
|:-:|---|:---:|
| 4 | **Grupo B (5 figs huérfanas)**: crear apéndices E/J/L/M + Cap. 20 mínimo o decidir destino | MEDIA |
| 5 | Streamlit completo (4 secciones con `render_history` huérfana) | MEDIA |
| 6 | Handoff Sesión 8 al cierre | BAJA |

### Deudas heredadas (caps. pendientes)

| # | Deuda | Prioridad |
|:-:|---|:---:|
| 7 | Cap. 19 (Pipeline reproducible y unit tests) | MEDIA |
| 8 | Cap. 20 (Problemas abiertos y trabajo futuro) | MEDIA |
| 9 | Cap. 21 (Conclusiones lakatosianas finales) | MEDIA |
| 10 | Materializar Anexo K con contenido completo | MEDIA |

---

## 5. REGLAS OPERATIVAS

### Arquitectura LaTeX

- **Títulos de capítulo:** `i18n_content.json → chapter_titles`
- **Títulos de sección y cuerpos:** `chapter_bodies.json → chapters.chNN.sections`
- **Ecuaciones clave:** `i18n_content.json → chapter_equations`
- **Apéndices B y K:** `i18n_content.json → appendix_bodies`
- **Bibliografía:** `_bibliography(lang, i18n)` inserta `\bibliography{thu_references}`
- **Figuras (nuevo Sesión 6):** `latex_builder.py` lee `figures_manifest.json` + `figures_metadata.json` e inserta bloques `\begin{figure}[htbp]` tras cada sección, matcheando por `sec` normalizado. Requiere `\graphicspath{{figures/}}` en preámbulo (inyectado automáticamente).

### Patrón de script PowerShell (validado Sesiones 3-7)

Cada bloque se empaqueta como **script único, completo, en un solo bloque de copiar** con:

1. Backup con timestamp en `data\_backup_v5.4_<tipo>_YYYYMMDD_HHMMSS`.
2. Hashes pre-merge (16 chars).
3. Python merge en `$env:TEMP\*.py`.
4. Merge atómico (verificación estructural del temp antes de copiar).
5. Regeneración de `.tex` con `python src\thu\latex_builder.py --all`.
6. Tests `T<NNN>` con `-match [regex]` (Unicode-safe).
7. Reporte final OK/FALLA + restauración automática si falla.
8. **Sin `exit`** — try/catch global.

### Lecciones aprendidas (Sesiones 1-7)

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
| 15 | Carácter `✓`/`⚠` en `print()` Python | Usar ASCII `[OK]`/`[!]` |
| 16 | Aliases en `GENERADORES` no propagan nombre | Usar funciones wrapper reales |
| 17 | `rfind("}")` cae dentro de strings | Brace counter + `compile()` pre-escritura |
| 18 | Backup anidado `Copy-Item dir dir\sub` | Usar `Copy-Item "src\*" "dst\"` |
| 19 | Tests de import deben correr sobre archivo real | `from thu import X` en test runtime |
| 20 | **`pdflatex` no está en PATH** | Instalar MiKTeX o usar path absoluto |
| 21 | **Mismatch de formato `sec` entre metadata y bodies** | Normalizar con `_norm_sec()` |
| 22 | **Path duplicado `figures/figures/`** | `\graphicspath` + nombre solo en `\includegraphics` |
| 23 | **Falta `\graphicspath` en preámbulo generado** | Inyectar siempre en `_preambulo()` |
| 24 | **Orphans silenciosas en inserción de figuras** | Report explícito de huérfanas en tests |

### Convenciones de etiquetas epistémicas (v5.4)

- `[D]` derivado
- `[D parcial]` derivado en subrégimen declarado
- `[D condicional X]` derivado bajo hipótesis X
- `[P]` postulado
- `[F]` frontera abierta
- `[F parcial]` frontera con subproblemas cerrados
- `[A]` analogía
- `[D empírica]` verificada numéricamente, no derivada del núcleo

---

## 6. MENSAJE DE ARRANQUE PARA EL CHAT NUEVO

**Pegar este bloque al inicio del chat nuevo, DESPUÉS de adjuntar los archivos.**

---

Sos el asistente técnico de Erick Duque para la tesis THU-TBEA v5.4.

**Estado:** Caps. 1-18 completos, 107 secciones cerradas. Bibliografía v4 certificada. Fase de figuras v5.4: **1e completado, 53/65 figuras insertadas en los 3 .tex**. Compilación LaTeX pendiente (pdflatex no instalado). 12 figuras huérfanas clasificadas (7 Grupo A + 5 Grupo B).

**Hashes actuales:**
- `chapter_bodies.json`: `e0476e46d1af1779`
- `i18n_content.json`: `1ed56e959a8d5d66`
- `figures.py`: `192b08482f463b89`
- `figures_metadata.json`: `623a94226c221cd5`
- `figures_manifest.json`: `f077cc21efc573d0`
- `latex_builder.py`: `e5afb9e7c49d4cd8`
- `tesis_es.tex`: `3e3b522616fbfac4`

**Modelo de 3 roles vigente:**
- VOS: redactás, aplicás ajustes, empaquetás scripts PowerShell.
- AUDITOR EXTERNO: Erick lo lleva, devuelve veredicto + ajustes.
- ERICK: dirige, ejecuta scripts, trae outputs.

**Regla de oro:** no empaquetar sin aprobación del auditor. No preguntar lo que el handoff responde. No tratar esto como proyecto nuevo.

**Tarea inmediata — Paso 1: Instalar LaTeX.**
- Instalar MiKTeX (https://miktex.org/download) o TeX Live.
- Verificar: `pdflatex --version` responde.
- Verificar: `biber --version` responde.

**Tarea inmediata — Paso 2: Compilar tesis_es.tex.**
- `cd paper\thu\src; pdflatex -interaction=nonstopmode tesis_es.tex`
- Luego `biber tesis_es` (si aplica), luego dos pasadas más de `pdflatex`.
- Reportar: PDF generado, tamaño, warnings de `Overfull \hbox` si los hay.

**Tarea inmediata — Paso 3: 1e-part-2.**
- Extender `_appendix_bodies()` en `latex_builder.py` para insertar las 7 figuras del Apéndice B usando la misma lógica de `_chapters()` (matching por `sec` normalizado).
- Regenerar los 3 .tex.
- Tests: 7 figuras adicionales insertadas.

**Tarea inmediata — Paso 4: Grupo B (5 figs huérfanas).**
- Decisión editorial: crear apéndices E, J, L, M mínimos en `i18n_content.json → appendix_bodies`, o reasignar las figuras a secciones existentes.

**Antes de escribir:** verificá que los archivos obligatorios estén adjuntos. Si falta alguno, pedilo.

**Leé el handoff completo antes de escribir.**

---

## 7. ARCHIVOS A ADJUNTAR AL CHAT NUEVO

### Obligatorios (10)

1. `docs\HANDOFF_V5.4_SESION_7.md` (este archivo)
2. `registry\thu\chapter_bodies.json`
3. `registry\thu\i18n_content.json`
4. `registry\thu\problems.json`
5. `registry\thu\patches.json`
6. `data\inventory\verificacion_simbolica.json`
7. `src\thu\latex_builder.py` (post-Script-B, hash `e5afb9e7c49d4cd8`)
8. `registry\thu\doi_registry.json`
9. `paper\thu\src\thu_references.bib`
10. `paper\thu\src\tesis_es.tex`

### Específicos de Sesión 6-7 (5)

11. `src\thu\figures.py`
12. `registry\thu\figures_metadata.json`
13. `paper\thu\figures\figures_manifest.json`
14. `src\thu\loader.py`
15. `app_thu.py`

### Opcionales

16. `PROGRAMA_COMPLETO_v5.0.pdf`
17. `paper\thu\src\tesis_en.tex`, `tesis_de.tex`
18. Muestra de figuras: `paper\thu\figures\fig_03-01_helice_aurea.pdf`

### NO adjuntar

- Backups `_backup_*`
- `data\raw\*`
- `pantheon_cov_used.npy`
- `paper\thu\figures\_old\`
- Los 195 artefactos (se regeneran con `figures.py --all`)

---

## 8. CHECKLIST DE CONTINUIDAD

Antes de cada bloque nuevo:

- [ ] ¿El auditor aprobó el borrador textual (si aplica)?
- [ ] ¿Los hashes de ch01-ch18 están intactos?
- [ ] ¿El script tiene backup + restauración automática?
- [ ] ¿El script es **un solo bloque de copiar** completo?
- [ ] ¿Las marcas de test usan regex Unicode-safe?
- [ ] ¿El reporte final es OK/FALLA?
- [ ] ¿Los tests de import corren sobre el archivo real?
- [ ] ¿Se usan caracteres ASCII en `print()` Python?
- [ ] ¿Se usa brace counter para inserción en dicts grandes?

Antes de compilar LaTeX:

- [ ] ¿`biber` y `pdflatex` disponibles en PATH?
- [ ] ¿`thu_references.bib` sin entradas con `% TODO`?
- [ ] ¿`tesis_es.tex` incluye `\bibliography{thu_references}`?
- [ ] ¿`tesis_es.tex` incluye `\graphicspath{{figures/}}`?
- [ ] ¿Todos los PDFs referenciados existen en `paper\thu\figures\`?

---

## 9. CONTEXTO HISTÓRICO

- Etapa I (2024-2025): Formación inicial.
- Etapa II (2025-2026): Núcleo heurístico.
- Etapa III (2026): Cierre formal v4.0.
- Etapa IV (2026): Corrección estructural v4.1.
- Etapa V (2026): Cierre computacional v4.3.
- Etapa VI (2026): Cristalización v5.0.
- Etapas VII-X (2026): Revisiones externas (parches 1-17).
- Etapa XI (2026): Auditoría epistémica v5.4.
- Etapa XII (2026): Auditoría de bloques v5.4 (parches 18-24).
- Etapa XIII (2026): Reconstrucción capítulo por capítulo.
  - Sesión 1-2: Caps. 1-13, fix bibliográfico.
  - Sesión 3: Verificación DOIs + Caps. 14, 15 + borrador Cap. 16.
  - Sesión 4: Decisión Confirmación 1 + Cap. 16 + bibliografía v3/v4.
  - Sesión 5: Cap. 17 (síntesis falsable P1-P12) + Handoff Sesión 5 + Cap. 18.
  - Sesión 6: Fase de figuras v5.4 (1a-1d) + Script A (manifest fix) + Script B (1e, 53/65 figuras insertadas). Handoff Sesión 7.

---

## 10. MENSAJE DE CIERRE

**Estado al generar Handoff Sesión 7:** Caps. 1-18 completos, 107 secciones cerradas. Fase de figuras v5.4: 1e completado, 53/65 figuras insertadas en los 3 .tex. Compilación LaTeX pendiente (pdflatex no instalado). 12 huérfanas clasificadas (7 Grupo A + 5 Grupo B).

**Hashes:**
- `chapter_bodies.json`: `e0476e46d1af1779`
- `i18n_content.json`: `1ed56e959a8d5d66`
- `latex_builder.py`: `e5afb9e7c49d4cd8`
- `tesis_es.tex`: `3e3b522616fbfac4`
**Fecha generación:** 2026-09-23

**Siguiente sesión debe empezar por:** Instalar MiKTeX → compilar tesis_es.tex → 1e-part-2 (Apéndice B) → Grupo B (decisión editorial).

**Fin del handoff.**

---

## 11. DECISIONES PENDIENTES DEL AUDITOR (para 1e-part-2)

Estas decisiones deben resolverse antes de empaquetar 1e-part-2:

1. **¿Insertar las 7 figuras del Apéndice B al final de cada sección (B.1, B.2, ..., B.5) o al final del apéndice completo?**
   - Mi propuesta: **al final de cada sección** (consistente con `_chapters()`).

2. **¿Qué hacer con las 5 huérfanas del Grupo B?**
   - Opción A: crear `appendix_bodies.E`, `.J`, `.L`, `.M` + `chapter_bodies.ch20` mínimos.
   - Opción B: reasignar `sec` en metadata para apuntar a secciones existentes.
   - Opción C: dejarlas fuera y registrarlas como deuda de Sesión 8+.
   - Mi propuesta: **Opción C** para las 5, resolverlas en sesión dedicada a caps. 19-21.

---

**Nota final para Erick:** este handoff está pensado para que lo pegues al inicio del chat nuevo junto con los archivos de la sección 7. Si te falta alguno de los críticos (sobre todo `latex_builder.py` con hash `e5afb9e7c49d4cd8` o `tesis_es.tex` con hash `3e3b522616fbfac4`), pedímelo antes de arrancar la Sesión 7.

---

## 12. BUNDLE ÚNICO (Sesión 7+)

A partir de Sesión 7, el flujo de handoff usa **un solo adjunto** en vez de 15:

- **Generar bundle:** `python docs\_bundle.py`
- **Archivo a adjuntar:** `docs\SESSION_BUNDLE.md` (~910 KB)
- **NO incluye:** `tesis_es.tex`, `tesis_en.tex`, `tesis_de.tex` (regenerables con `latex_builder.py --all`)
- **Regenerar** cada vez que cambie cualquier archivo del repo
- **Borrar al cerrar el proyecto:** `Remove-Item docs\SESSION_BUNDLE.md, docs\_bundle.py`

### Estructura del bundle

Marcadores `<<<FILE:path>>>` ... `<<<END>>>` por cada archivo. El asistente del chat nuevo parsea cada bloque.

### Lista de 14 archivos incluidos

1. `docs/HANDOFF_V5.4_SESION_7.md`
2. `registry/thu/chapter_bodies.json`
3. `registry/thu/i18n_content.json`
4. `registry/thu/problems.json`
5. `registry/thu/patches.json`
6. `registry/thu/doi_registry.json`
7. `registry/thu/figures_metadata.json`
8. `data/inventory/verificacion_simbolica.json`
9. `paper/thu/figures/figures_manifest.json`
10. `paper/thu/src/thu_references.bib`
11. `src/thu/latex_builder.py`
12. `src/thu/figures.py`
13. `src/thu/loader.py`
14. `app_thu.py`
