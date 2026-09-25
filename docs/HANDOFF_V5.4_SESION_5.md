# HANDOFF v5.4 — SESIÓN 5

**Proyecto:** Tesis THU-TBEA — Erick Duque
**ORCID:** 0009-0004-1245-5464
**Versión activa:** v5.4 (reconstrucción auditada capítulo por capítulo)
**Fecha generación:** 2026-09-23
**Estado:** Caps. 1–17 completos. 102 secciones cerradas. Bibliografía v4 certificada (71 entradas, 11 DOIs verificados). Cap. 18 pendiente.

---

## 1. MODELO DE 3 ROLES

1. **VOS (asistente técnico del chat de trabajo):**
   - Redactás borradores de secciones en ES/EN/DE.
   - Aplicás los ajustes del auditor externo textualmente.
   - Empaquetás bloques aprobados en scripts PowerShell únicos.
   - Corrés/verificás tests tras cada merge.
   - Mantenés el estado del repo.
   - Si te falta un archivo, lo pedís explícitamente.

2. **AUDITOR EXTERNO (lo ejecuta Erick con otro asistente o él mismo):**
   - Revisa los borradores que vos producís.
   - Devuelve veredicto + ajustes textuales exactos.
   - Aprueba explícitamente antes de empaquetar.
   - Vos NO inventás auditorías.

3. **ERICK (autor y director del proyecto):**
   - Pega tus borradores al chat del auditor.
   - Trae de vuelta el veredicto.
   - Ejecuta los scripts PowerShell en su máquina.
   - Pega los outputs de vuelta.
   - Toma las decisiones de alcance.

**Regla de oro:** no empaquetar scripts sin aprobación del auditor. No preguntar lo que el handoff responde. No tratar esto como proyecto nuevo.

**Repo local:** `C:\Users\kg4tr\Documents\Investigacion_lab_secreto`
**Repo red:** `\\Atila\f\THU-TBEA_Lab`

---

## 2. ESTADO DEL REPOSITORIO (post Sesión 5)

### Capítulos cerrados

| Cap | Secciones | Hash |
|:---:|:---------:|:----:|
| ch01–ch13 | 85 | (heredados, sin cambios) |
| ch14 | 4 | ✅ |
| ch15 | 4 | ✅ |
| ch16 | 4 | ✅ |
| ch17 | 5 | ✅ |
| **Total** | **102** | |

### Hashes verificados al cierre de Sesión 5

- `chapter_bodies.json`: **`60efcad2c6c41d11`**
- `i18n_content.json`: **`4ddb4017f4ff9e3c`**
- `problems.json`: **`84e4ee068824c17d`** (sin cambios en Sesión 5)
- `patches.json`: `769c0c6580f9a05e` (sin cambios)
- `thu_references.bib`: **`c3d48abd2b1ec3fb`** (v4 certificado, 71 entradas)
- `doi_registry.json`: **`c7c56cd0946c2c84`** (post 11 verified:true)

### Archivos críticos (tamaños actuales)

| Archivo | Ruta | Tamaño |
|---|---|---|
| `chapter_bodies.json` | `registry\thu\` | ~470 KB (post ch17) |
| `i18n_content.json` | `registry\thu\` | ~28 KB |
| `problems.json` | `registry\thu\` | 5687 B |
| `patches.json` | `registry\thu\` | 7145 B |
| `doi_registry.json` | `registry\thu\` | 10887 B |
| `thu_references.bib` | `paper\thu\src\` | ~30 KB (v4) |
| `latex_builder.py` | `src\thu\` | 17553 B |
| `tesis_es.tex` | `paper\thu\src\` | 203633 B |
| `tesis_en.tex` | `paper\thu\src\` | 163984 B |
| `tesis_de.tex` | `paper\thu\src\` | 163435 B |

### Backups Sesión 4–5

- `data\_backup_v5.4_cap16_20260923_103634`
- `data\_backup_v5.4_bibv4_20260923_105533`
- `data\_backup_v5.4_cap17_20260923_105719`

---

## 3. HALLAZGOS CRÍTICOS DE SESIÓN 4–5

### 3.1 Cap. 16 — Residuo helicoidal (cerrado)

**Coincidencias numéricas verificadas <1%:**

| Relación | Predicho | Observado | Ratio |
|---|---|---|---|
| `R_H = ℏ/(πΛ_QCD)` | 1.048×10⁻²⁴ s | 1.058×10⁻²⁴ s | 0.991 (0.9%) |
| `P_Λ = 2π(2−φ)²` | 0.9166 | 0.92 | 1.004 (0.4%) |

**Test de universalidad falsado:** χ²/dof = 401.59 (dof=2).

**Gap con núcleo geométrico:**
- Ruta A (torsión directa CVE): 38.2 órdenes.
- Ruta B (campo chameleon): 42.9 órdenes.
- Operador no-local de supresión: 0.0 órdenes (nulo a T ≈ 150 MeV).

**RCI-44 registrado como `[F]`** — Derivación de `P_Λ`, `ω`, `R_H` desde primeros principios. Seis rutas candidatas documentadas:
- (A) torsión directa CVE (no cierra)
- (B) campo chameleon (suprimido)
- (C) efectos topológicos no perturbativos (no cierra)
- (D) nuevo acoplamiento `g_T τψ̄γ₅ψ` (especulativo, modifica Lagrangiano)
- (E) relación empírica pura
- (F) dualidad THU-QCD (no cierra)

**Etiquetas aplicadas:**
- `[D empírica]` para las coincidencias numéricas.
- `[P]` para el uso predictivo de las fórmulas.
- `[F]` para la derivación desde el núcleo geométrico.

**Corpus experimental ampliado:** STAR BES-II (3 GeV), STAR Run 2013 (200 GeV), HADES (2.4 GeV), ALICE (5.02 TeV).

### 3.2 Bibliografía v4 (cerrada)

- **71 entradas** (57 @article, 5 @book, 1 @incollection, 8 @misc).
- **11 DOIs certificados** (`verified: true`):
  - Unger2019 (`10.3847/1538-4357/aaf76a`)
  - BasIBeneito2022 (arXiv:2211.05606, sin DOI)
  - Gomez2024 (`10.1140/epjc/s10052-024-13631-7`)
  - Kraischburd2018 (`10.1103/PhysRevD.97.104044`)
  - Ormondroyd2025 (`10.1093/mnras/staf2207`)
  - Liang2023 (`10.1103/PhysRevD.109.083028`)
  - Guo2026 (`10.1088/1475-7516/2026/04/066`)
  - Wang2026 (`10.1038/s41563-026-02535-4`)
  - Gassab2026 (`10.1117/12.3072614`)
  - Mavromatos2025 (`10.1140/epjp/s13360-025-07022-4`)
  - RodriguezVega2024 (`10.1103/physics.17.s121`)

**Correcciones del auditor aplicadas:**
- `Lehmann1954`: sintaxis `\"U` corregida.
- `BICEPKeck2026`: DOI oficial `10.1103/v8y3-m75b`.
- `Lodha2025`: DOI PRD `10.1103/w4c6-1r5j`, vol. 112, pp. 083511.
- `DiegoPalazuelos2025`: DOI oficial `10.1103/pbc3-t52s`.
- `Kibble1961`: DOI `10.1063/1.1703702`.
- `KibbleZurek`: entrada `@misc` sin `\cite{}` internos.

### 3.3 Cap. 17 — Síntesis falsable (cerrado)

- **Título actualizado:** "P1–P11" → **"P1–P12"**.
- **§17.1 Preregistro:** timestamp Zenodo `10.5281/zenodo.21608282`; P5/P11 con protocolo v5.4.
- **§17.2 Tabla maestra P1–P12:**
  - P5, P11 → "Preregistrada + protocolo v5.4"
  - P8 → "Consistente (con corrección epistémica v5.4)"
  - **P12 → FALSADA (χ²/dof = 401.59)**
  - Otras 8 permanecen abiertas
- **§17.3 Protocolo lakatosiano:** núcleo firme + cinturón protector + heurística positiva; P12 como caso paradigmático de redistribución del cinturón.
- **§17.4 Progresividad 1.0 → 5.4:** tabla comparativa v4.3 vs v5.4 (79 → 97 secciones, 3 correcciones matemáticas, 2 epistémicas, RCI-34 → RCI-44).
- **§17.5 Limitaciones:** fronteras abiertas A-1, A-15, A-17, RCI-35, RCI-44.

---

## 4. DEUDAS PENDIENTES AL CIERRE DE SESIÓN 5

### Deudas nuevas (Sesión 5)

| # | Deuda | Prioridad |
|:-:|---|:---:|
| 1 | Redactar Cap. 18 (Ajuste conjunto sobre datos públicos) | **ALTA** |
| 2 | Redactar Cap. 19 (Pipeline reproducible) | MEDIA |
| 3 | Redactar Cap. 20 (Problemas abiertos) | MEDIA |
| 4 | Redactar Cap. 21 (Conclusiones lakatosianas) | MEDIA |
| 5 | Materializar Anexo K (hoy es resumen de 6 subsecciones) | MEDIA |
| 6 | Recalcular hash de `doi_registry.json` tras 11 verified:true | BAJA |
| 7 | Compilación LaTeX final completa (cuando caps. 18–21 estén cerrados) | MEDIA |
| 8 | Crear Handoff Sesión 6 al cierre | BAJA |

### Deudas heredadas (Sesión 4, resueltas)

- ✅ Confirmación 1 (Plan B revisado): resuelta con etiquetas `[D empírica]` + `[P]` + `[F]`.
- ✅ 3 DOIs faltantes: añadidos (posteriormente certificados en v4).
- ✅ Empaquetado Cap. 16: completado.
- ✅ Redactar Cap. 17: completado.

### Caps. pendientes

| Cap | Título | Fuente |
|:---:|---|---|
| 18 | Ajuste conjunto sobre datos públicos | `PROGRAMA_COMPLETO_v5.0.pdf` §18 |
| 19 | Pipeline reproducible | §19 |
| 20 | Problemas abiertos y trabajo futuro | §20 |
| 21 | Conclusiones y evaluación lakatosiana final | §21 |

---

## 5. REGLAS OPERATIVAS

### Arquitectura LaTeX (heredado Sesión 3)

- **Títulos de capítulo:** van en `i18n_content.json → chapter_titles`.
- **Títulos de sección y cuerpos:** van en `chapter_bodies.json → chapters.chNN.sections`.
- **Ecuaciones clave:** van en `i18n_content.json → chapter_equations`.
- **Apéndices B y K:** van en `i18n_content.json → appendix_bodies`.
- **Bibliografía:** `_bibliography(lang, i18n)` inserta `\bibliography{thu_references}` antes de `\end{document}`.

### Patrón de script PowerShell (validado Sesiones 3–5)

Cada bloque se empaqueta como **script único, completo, en un solo bloque de copiar** con:

1. Backup con timestamp en `data\_backup_v5.4_<tipo>_YYYYMMDD_HHMMSS`.
2. Hashes pre-merge (16 chars).
3. Python merge generado en `$env:TEMP\*.py`, verifica `MERGE_OK`.
4. Merge atómico (verificación estructural del temp antes de copiar).
5. Regeneración de `.tex` con `python src\thu\latex_builder.py --all`.
6. Tests `T<NNN>` con `-match [regex]` (Unicode-safe).
7. Reporte final OK/FALLA + restauración automática si falla.
8. **Sin `exit`** — try/catch global.

### Lecciones aprendidas (Sesiones 1–5)

| # | Bug histórico | Fix |
|:-:|---|---|
| 1 | `-notmatch` sobre array | `$mergeText = ($mergeOutput -join "`n")` |
| 2 | `exit` cierra consola | try/catch sin exit |
| 3 | Diacríticos mal escritos | Verificar cada marca contra el cuerpo |
| 4 | Heredocs PowerShell anidados | Usar scripts Python externos |
| 5 | Paréntesis sin cerrar en `Write-Host` | No mezclar `(` con `-ForegroundColor` |
| 6 | `_bibliography(lang, t)` con `t` undefined | Usar la variable real de `build()` = `i18n` |
| 7 | `re.subn` con `\d` en replacement | Escapar backslashes en strings raw |
| 8 | `\\` en heredoc | Escribir `.bib` por chunks con Add-Content |
| 9 | Python string con `$` en PowerShell here-string | Usar `@'...'@` (comilla simple) para literales |
| 10 | `schallhorizont` con guion en alemán | Composición directa: `Schallhorizontskala` |
| 11 | `\$` no es escape válido en PowerShell | Usar `@'...'@` con `$` literal |
| 12 | `.Contains()` falla con diacríticos | Usar regex `.` que matchea cualquier char |
| 13 | Regex con paréntesis literal | Escape con `\(` |
| 14 | Búsqueda hardcoded de rutas | Walk-up desde `Get-Location` |

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
- **`[D empírica]`** (Sesión 4): verificada numéricamente contra constantes fundamentales, no derivada del núcleo geométrico.

---

## 6. MENSAJE DE ARRANQUE PARA EL CHAT NUEVO

**Pegar este bloque al inicio del chat nuevo, DESPUÉS de adjuntar los archivos.**

---

Sos el asistente técnico de Erick Duque para la tesis THU-TBEA v5.4.

**Estado:** Caps. 1–17 completos, 102 secciones cerradas. Bibliografía v4 certificada (71 entradas, 11 DOIs verificados). Cap. 18 pendiente.

**Hashes actuales:**
- `chapter_bodies.json`: `60efcad2c6c41d11`
- `i18n_content.json`: `4ddb4017f4ff9e3c`
- `problems.json`: `84e4ee068824c17d`
- `thu_references.bib`: `c3d48abd2b1ec3fb`

**Modelo de 3 roles vigente:**
- VOS: redactás, aplicás ajustes, empaquetás scripts PowerShell.
- AUDITOR EXTERNO: Erick lo lleva, devuelve veredicto + ajustes.
- ERICK: dirige, ejecuta scripts, trae outputs.

**Regla de oro:** no empaquetar sin aprobación del auditor. No preguntar lo que el handoff responde. No tratar esto como proyecto nuevo.

**Tarea inmediata — redactar Cap. 18:**
- **Título:** "Ajuste conjunto sobre datos públicos" (ES) / "Joint fit on public data" (EN) / "Gemeinsame Anpassung an offentliche Daten" (DE)
- **Fuente:** `PROGRAMA_COMPLETO_v5.0.pdf` §18
- **Estructura esperada:**
  - §18.1 Datos, hashes y covarianzas (DESI DR2, Pantheon+, Planck PR4, ACT DR6)
  - §18.2 Verosimilitud conjunta y comparación de modelos (ΛCDM, w₀wₐCDM, THU-TBEA)
  - §18.3 Resultados: χ² por dataset (tabla 18.1)
  - §18.4 Validación observacional y auditoría de falsabilidad
  - §18.5 Limitaciones declaradas
- **Advertencia crítica:** el PDF original tiene una nota metodológica: *"Los resultados corresponden exclusivamente a un conjunto de datos sintéticos (mocks). No constituyen una medida de la torsión en el universo real."* Esto debe preservarse explícitamente en §18.4.

**Antes de escribir:** verificá que los 10 archivos obligatorios estén adjuntos. Si falta alguno, pedilo.

**Leé el handoff completo antes de escribir.**

---

## 7. ARCHIVOS A ADJUNTAR AL NUEVO CHAT

### Obligatorios (10)

1. `docs\HANDOFF_V5.4_SESION_5.md` (este archivo)
2. `registry\thu\chapter_bodies.json`
3. `registry\thu\i18n_content.json`
4. `registry\thu\problems.json`
5. `registry\thu\patches.json`
6. `data\inventory\verificacion_simbolica.json`
7. `src\thu\latex_builder.py`
8. `registry\thu\doi_registry.json` (post 11 verified:true)
9. `paper\thu\src\thu_references.bib` (v4 certificado, 71 entradas)
10. `paper\thu\src\tesis_es.tex`

### Opcionales

11. `PROGRAMA_COMPLETO_v5.0.pdf`
12. `tesis_en.tex`, `tesis_de.tex`
13. Cualquier script `rci_*.py` relevante

### NO adjuntar

- Backups `_backup_*` (se referencian por path)
- `data\raw\*` (mapas CMB crudos)
- `pantheon_cov_used.npy` (13 MB)
- Módulos externos (`sympy/physics/quantum/spin.py`, etc.)

---

## 8. CHECKLIST DE CONTINUIDAD

Antes de cada bloque nuevo:

- [ ] ¿El auditor aprobó el borrador textual?
- [ ] ¿Los hashes de ch01–chN-1 están intactos?
- [ ] ¿El script tiene backup + restauración automática?
- [ ] ¿Las marcas de test están verificadas contra el cuerpo exacto?
- [ ] ¿Se están usando diacríticos completos en ES/DE?
- [ ] ¿El script no tiene `exit`?
- [ ] ¿El script es **un solo bloque de copiar** completo?
- [ ] ¿El reporte final es OK/FALLA?
- [ ] ¿Los tests usan regex Unicode-safe (`-match 'emp.rica'`)?

Antes de compilar LaTeX:

- [ ] ¿`biber` y `pdflatex` disponibles en PATH?
- [ ] ¿`thu_references.bib` sin entradas con `% TODO`?
- [ ] ¿`tesis_es.tex` incluye `\bibliography{thu_references}`?
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
  - **Sesión 5 (actual):** Cap. 17 (síntesis falsable P1–P12) + Handoff Sesión 5.

---

## 10. MENSAJE DE CIERRE

**Estado al generar Handoff Sesión 5:** Caps. 1–17 completos, 102 secciones cerradas. Bibliografía v4 certificada (71 entradas, 11 DOIs verificados). P12 falsada (χ²/dof = 401.59). RCI-44 registrado como frontera abierta.

**Hash `chapter_bodies.json`:** `60efcad2c6c41d11`
**Hash `i18n_content.json`:** `4ddb4017f4ff9e3c`
**Hash `problems.json`:** `84e4ee068824c17d`
**Hash `thu_references.bib`:** `c3d48abd2b1ec3fb`
**Fecha generación:** 2026-09-23

**Siguiente sesión debe empezar por:** redactar y empaquetar Cap. 18 (Ajuste conjunto sobre datos públicos).

**Fin del handoff.**

---

**Nota final para Erick:** este handoff está pensado para que lo pegues al inicio del chat nuevo junto con los archivos de la sección 7. Si te falta alguno de los críticos (sobre todo `chapter_bodies.json` post ch17), pedímelo antes de arrancar la Sesión 6. Si querés que arranquemos la Sesión 6 en este mismo chat, decime y hacemos la transición directa sin abrir chat nuevo.
