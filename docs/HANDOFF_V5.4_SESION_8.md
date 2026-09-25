# HANDOFF v5.4 — SESIÓN 8

**Proyecto:** Tesis THU-TBEA — Erick Duque
**ORCID:** 0009-0004-1245-5464
**Versión activa:** v5.4 (reconstrucción auditada capítulo por capítulo)
**Fecha generación:** 2026-09-23
**Estado:** Caps. 1-21 completos. 126 secciones cerradas. Bibliografía v4 certificada. Fase de figuras v5.4 completa (195/195 artefactos, 65/65 insertadas (tras resolucion de D-26 en Sesion 8 via Ruta D)). **Primera compilación LaTeX exitosa de los 3 PDFs** (104/95/96 páginas). 5 huérfanas del Grupo B diferidas. Deudas: 31 cerradas / 1 abiertas / 2 manuales.

---

## 1. MODELO DE 3 ROLES

Sin cambios respecto a Sesiones 5-7:

1. **VOS (asistente técnico):** redactás borradores ES/EN/DE, aplicás ajustes del auditor, empaquetás scripts PowerShell únicos, corrés tests, mantenés estado del repo. Si falta un archivo, lo pedís.
2. **AUDITOR EXTERNO (Erick con otro asistente):** revisa borradores, devuelve veredicto + ajustes textuales exactos, aprueba explícitamente antes de empaquetar. Vos NO inventás auditorías.
3. **ERICK (autor y director):** pega borradores al auditor, trae veredicto, ejecuta scripts PowerShell, pega outputs, decide alcance.

**Regla de oro:** no empaquetar scripts sin aprobación del auditor. No preguntar lo que el handoff responde. No tratar esto como proyecto nuevo.

**Repo local:** `C:\Users\kg4tr\Documents\Investigacion_lab_secreto`
**Repo red:** `\\Atila\f\THU-TBEA_Lab`

---

## 2. ESTADO DEL REPOSITORIO (post Sesión 7)

### Hashes verificados al cierre de Sesión 7

| Archivo | Ruta | Hash (16 chars) |
|---|---|---|
| `chapter_bodies.json` | `registry\thu\` | (recomputar; cambió en S7) |
| `i18n_content.json` | `registry\thu\` | `1ed56e959a8d5d66` |
| `problems.json` | `registry\thu\` | `84e4ee068824c17d` |
| `patches.json` | `registry\thu\` | `769c0c6580f9a05e` |
| `doi_registry.json` | `registry\thu\` | (recomputar; DOIs corregidos) |
| `thu_references.bib` | `paper\thu\src\` | (recomputar; fix braces) |
| `figures.py` | `src\thu\` | `192b08482f463b89` |
| `figures_metadata.json` | `registry\thu\` | `623a94226c221cd5` |
| `figures_manifest.json` | `paper\thu\figures\` | `f077cc21efc573d0` |
| `loader.py` | `src\thu\` | `9e9797aa92db1080` |
| `app_thu.py` | repo raíz | (recomputar; render_history eliminada) |
| `latex_builder.py` | `src\thu\` | (recomputar; newunicodechar + _esc_caption + v2 mapeos + raw docstring) |
| `check_debts.py` | `scripts\` | (nuevo) |
| `debts_history.json` | `docs\` | (nuevo) |

### Capítulos cerrados

| Cap | Secciones | Estado |
|:---:|:---------:|:------:|
| ch01-ch21 | 126 | ✅ |
| **Total** | **126** | |

### Fase de figuras v5.4 — completada

- 65 figuras × 3 formatos = **195 artefactos**.
- **65/65 figuras insertadas** en los 3 `.tex` (53 vía `_chapters()`, 7 vía `_appendix_bodies()` extendida).
- Tema print: fondo blanco, STIX General, spines editoriales, ticks inward.

### Compilación LaTeX — primera exitosa

| Lang | PDF | Páginas | Overfull |
|:-:|:-:|:-:|:-:|
| ES | 2.62 MB | 104 | ~80 |
| EN | 2.55 MB | 95 | ~71 |
| DE | 2.57 MB | 96 | ~105 |

Entorno: MiKTeX 25.12, pdfTeX 4.23, BibTeX 4.2. `biber` no requerido (bibliografía en modo bibtex clásico).

### Deudas: 31 cerradas / 1 abiertas / 2 manuales

**Cerradas en Sesión 7:** D-23, D-24, D-25, D-28, D-29, D-30, D-31, D-33, D-34.

**Abiertas (5):** D-22 (DOIs restantes — auditor decide protocolo), D-26 (Grupo B huérfanas), D-27 (Anexo K materialización), D-32 (descargas CMB), más lo que el auditor identifique.

**Manuales (3):** D-26, D-27, D-32 (requieren input humano).

---

## 3. QUÉ SE CERRÓ EN SESIÓN 7

### 3.1 Fase 0-2: Desbloqueo de la cadena de compilación

- Instalación de MiKTeX + PATH persistente.
- Fix de `thu_references.bib`: 9 entradas truncadas (@misc ISO/FAO/etc. + @book Peskin/Kleinert) con llaves cerradas.
- Fix de `latex_builder.py`: `newunicodechar` con 99 mapeos (griegos + superíndices + tipográficos + matemáticos) + `_esc_caption()` para escapar `_ ^ & # %` fuera de math mode.
- **Primera compilación exitosa** de los 3 PDFs.

### 3.2 Fase 1: Refinamiento del checker de deudas

- `scripts/check_debts.py` persistente (8 tipos de check).
- Protocolo D-22 L1+L2+L3 para DOIs.
- Fix de 4 DOIs: Unger2019 (aaf76a→aaf169), BasIBeneito2022 (título corregido), Ormondroyd2025 (staf2207→staf1144), RodriguezVega2024→Matsuura2024.

### 3.3 Fase 2: 1e-part-2

- Extensión de `_appendix_bodies()` en `latex_builder.py` para insertar las 7 figuras del Apéndice B.
- Verificación: 7/7 presentes en los 3 `.tex`.

### 3.4 Fase 3: Capítulos 19-21 (redacción + auditoría + merge)

- **Cap. 19** (Pipeline reproducible, 6 secciones): 17/17 tests PASS. D-28 CERRADA.
- **Cap. 20** (Problemas abiertos, 7 secciones con §20.7 transiciones): 17/17 tests PASS. D-29 CERRADA.
- **Cap. 21** (Conclusiones lakatosianas, 6 secciones): 15/15 tests PASS. D-30 CERRADA.

### 3.5 Fase 4: Cierre técnico

- D-31: `render_history` huérfana eliminada de `app_thu.py`.
- D-33: `docs/HANDOFF_V5.4_SESION_8.md` generado.
- Fix de `SyntaxWarning` en `latex_builder.py:110` (docstring → raw string).

---

## 4. DEUDAS PENDIENTES AL CIERRE DE SESIÓN 8

### Deudas críticas

| # | Deuda | Prioridad |
|:-:|---|:---:|
| 1 | **D-22**: decidir protocolo L3 para DOIs restantes (auditor) | **ALTA** |
| 2 | **D-26**: decisión sobre las 5 huérfanas del Grupo B | **ALTA** |

### Deudas importantes

| # | Deuda | Prioridad |
|:-:|---|:---:|
| 3 | **D-27**: materializar Anexo K con contenido completo | MEDIA |
| 4 | **D-32**: descargas CMB grandes | BAJA |
| 5 | Integrar `render_history` como sección real en `app_thu.py` | BAJA |
| 6 | Añadir `microtype` para reducir ~250 overfull warnings | BAJA |
| 7 | Handoff Sesión 9 al cierre | BAJA |

---

## 5. REGLAS OPERATIVAS

### Arquitectura LaTeX (actualizada S7)

- Títulos de capítulo: `i18n_content.json → chapter_titles`.
- Títulos de sección y cuerpos: `chapter_bodies.json → chapters.chNN.sections`.
- Ecuaciones clave: `i18n_content.json → chapter_equations`.
- Apéndices B y K: `i18n_content.json → appendix_bodies` (con figuras desde S7).
- Bibliografía: `_bibliography(lang, i18n)` con `\bibliography{thu_references}` (bibtex clásico, no biber).
- Figuras: `latex_builder.py` lee `figures_manifest.json` + `figures_metadata.json`, inserta en `_chapters()` y `_appendix_bodies()` por `sec` normalizado. Requiere `\graphicspath{{figures/}}` (inyectado siempre).
- Unicode: 99 mapeos vía `newunicodechar` para griegos + superíndices + tipográficos + matemáticos.
- Captions: `_esc_caption()` escapa `_ ^ & # %` fuera de math mode.

### Patrón de script PowerShell (validado Sesiones 3-7)

1. Backup con timestamp en `data\_backup_v5.4_<tipo>_YYYYMMDD_HHMMSS`.
2. Hashes pre-merge (16 chars).
3. Python merge en `$env:TEMP\*.py`.
4. Merge atómico (verificación estructural del temp antes de copiar).
5. Regeneración de `.tex` con `python src\thu\latex_builder.py --all`.
6. Tests con `-match [regex]` (Unicode-safe).
7. Reporte final OK/FALLA + restauración automática si falla.
8. **Sin `exit`** — try/catch global.

### Lecciones aprendidas nuevas (S7)

| # | Bug | Fix |
|:-:|---|---|
| 25 | `Missing $ inserted` por caracteres griegos Unicode | `newunicodechar` con 36 mapeos griegos |
| 26 | Superíndices Unicode rompen math mode | Mapeos `\textsuperscript{4}`, etc. |
| 27 | `_` en captions sin escapar | `_esc_caption()` (preserva `$...$`) |
| 28 | `biber` cuelga con `AutoInstall=0` | Tesis usa bibtex clásico; biber no requerido |
| 29 | `pdflatex` no ve `.bib` sin `\bibliographystyle` | Ya presente en builder |
| 30 | `bash`-style `$variable` en PS heredocs | Usar `@'...'@` con `$` literal |
| 31 | 71 cite keys vs 63 (con/sin `@misc`) | Auditor fija 63 (solo @article/@book/@incollection) |
| 32 | `_esc_caption` docstring no-raw en Py3.12+ | `r"""..."""` |
| 33 | Test regex debe tolerar `\_` escapado | `verificacion.?\\?_?simbolica` |

---

## 6. MENSAJE DE ARRANQUE PARA EL CHAT NUEVO

**Pegar este bloque al inicio del chat nuevo, DESPUÉS de adjuntar los archivos.**

---

Sos el asistente técnico de Erick Duque para la tesis THU-TBEA v5.4.

**Estado:** Caps. 1-21 completos, 126 secciones cerradas. Bibliografía v4 certificada. Fase de figuras v5.4 completa (65/65 insertadas (tras resolucion de D-26 en Sesion 8 via Ruta D)). **Primera compilación LaTeX exitosa** (3 PDFs: 104/95/96 páginas). Deudas: 31 cerradas / 1 abiertas / 2 manuales.

**Modelo de 3 roles vigente:**
- VOS: redactás, aplicás ajustes, empaquetás scripts PowerShell.
- AUDITOR EXTERNO: Erick lo lleva, devuelve veredicto + ajustes.
- ERICK: dirige, ejecuta scripts, trae outputs.

**Regla de oro:** no empaquetar sin aprobación del auditor. No preguntar lo que el handoff responde. No tratar esto como proyecto nuevo.

**Tarea inmediata — pendientes por prioridad:**

1. **D-22**: verificación externa de ~7 DOIs restantes con protocolo L1+L2+L3 (auditor decide).
2. **D-26**: decisión sobre las 5 huérfanas del Grupo B (A/B/C).
3. **D-27**: materializar Anexo K con contenido completo.
4. **D-32**: descargas CMB grandes (deuda baja, informativa).

**Herramientas nuevas del repo:**
- `scripts/check_debts.py` — checker persistente con protocolo L1+L2+L3.
- `docs/debts_history.json` — registro canónico de deudas.
- `docs/SESSION_BUNDLE.md` — bundle único para handoff (regenerar con `python docs\_bundle.py`).

**Antes de escribir:** verificá que los archivos obligatorios estén adjuntos. Si falta alguno, pedilo.

**Leé el handoff completo antes de escribir.**

---

## 7. ARCHIVOS A ADJUNTAR AL CHAT NUEVO

### Obligatorios (14, vía SESSION_BUNDLE.md)

Mismo bundle de 14 archivos que Sesión 7, más:
- `scripts/check_debts.py`
- `docs/debts_history.json`

### NO adjuntar

- Backups `_backup_*`
- `data\raw\*`
- `paper\thu\figures\_old\`
- Los 195 artefactos (regenerables)

---

## 8. CHECKLIST DE CONTINUIDAD

Antes de cada bloque nuevo:

- [ ] ¿El auditor aprobó el borrador textual (si aplica)?
- [ ] ¿Los hashes de ch01-ch21 están intactos?
- [ ] ¿El script tiene backup + restauración automática?
- [ ] ¿El script es un solo bloque de copiar completo?
- [ ] ¿Las marcas de test usan regex Unicode-safe?
- [ ] ¿El reporte final es OK/FALLA?
- [ ] ¿Se usan caracteres ASCII en `print()` Python?

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
- Etapa III-VI: Cierres formales v4.0 → v5.0.
- Etapas VII-X: Revisiones externas (parches 1-17).
- Etapa XI-XII: Auditoría epistémica + bloques v5.4 (parches 18-24).
- Etapa XIII (2026): Reconstrucción capítulo por capítulo.
  - Sesiones 1-2: Caps. 1-13, fix bibliográfico.
  - Sesión 3-5: Caps. 14-18.
  - Sesión 6: Fase de figuras v5.4 (1a-1d).
  - **Sesión 7:** Cierre de cadena de compilación (MiKTeX + fix bib + fix unicode) + Fase 1 (D-22 L1+L2+L3 + fix 4 DOIs) + Fase 2 (1e-part-2, 7 figs Apéndice B) + Fase 3 (Caps. 19-21 redactados con auditoría externa) + Fase 4 (limpieza técnica). Handoff Sesión 8.

---

## 10. MENSAJE DE CIERRE

**Estado al generar Handoff Sesión 8:** Caps. 1-21 completos, 126 secciones cerradas. 3 PDFs generados (104/95/96 páginas). Deudas: 31 cerradas / 1 abiertas / 2 manuales.

**Fecha generación:** 2026-09-23

**Siguiente sesión debe empezar por:** resolver D-22 (DOIs) y D-26 (Grupo B huérfanas) con veredicto del auditor. Después: materializar Anexo K (D-27) y opcionalmente integrar `render_history` como sección real en el dashboard Streamlit.

**Fin del handoff.**