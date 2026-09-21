# Decisiones de Diseno — PIR

> Documento vivo. Formato: D-NNN, fecha, decision, razon, consecuencia.

---

## D-001 — Privacidad del repositorio

**Fecha:** 2026-09-19
**Decision:** Privado hasta decision explicita del PI.
**Razon:** Preservar prioridad, evitar exposicion prematura.
**Consecuencia:** Push a repo privado. Publicacion requiere entrada en `epistemic_log.md`.

---

## D-002 — Formato de provenance obligatorio

**Fecha:** 2026-09-19
**Decision:** Toda entrada requiere cita ISO 690, DOI, metodo, condiciones, extracto, hash SHA-256.
**Razon:** Auditabilidad. Sin provenance la entrada no es verificable.
**Consecuencia:** Entradas sin provenance marcadas `[F]` hasta completarlas.

---

## D-003 — Log epistemico append-only

**Fecha:** 2026-09-19
**Decision:** El log no se edita hacia atras.
**Razon:** Trazabilidad historica del razonamiento.
**Consecuencia:** Cambios de opinion visibles, no ocultos.

---

## D-004 — Nomenclatura de identificadores

**Fecha:** 2026-09-19
**Decision:** IDs con formato `{CATEGORIA}-{NNN}`.
**Razon:** Consistencia y busqueda rapida.
**Consecuencia:** Toda nueva entrada usa este formato.

---

## D-005 — Unidades y formato de fecha

**Fecha:** 2026-09-19
**Decision:** ISO-8601 UTC para fechas. Unidades SI siempre.
**Razon:** Evitar errores de conversion y ambiguedades.
**Consecuencia:** Scripts validan formato en carga.

---

## D-006 — Protocolos pre-registrados

**Fecha:** 2026-09-19
**Decision:** Toda hipotesis lleva criterio de falsacion escrito ANTES de medir.
**Razon:** Prevenir HARKing, p-hacking, cherry-picking.
**Consecuencia:** Sin pre-registro, hipotesis no testeable.

---

## D-007 — Estructura Lakatosiana obligatoria

**Fecha:** 2026-09-19
**Decision:** Cada programa define: nucleo duro, cinturon protector, heuristica positiva y negativa.
**Razon:** Marco MSRP para evaluar progresividad.
**Consecuencia:** Desplazamientos evaluados como progresivos o degenerativos.

---

## D-008 — Reporte PRISMA cuando aplique

**Fecha:** 2026-09-19
**Decision:** Revisiones sistematicas siguen PRISMA 2020 (27 items).
**Razon:** Transparencia y completitud.
**Consecuencia:** Diagrama de flujo PRISMA en `registry/prisma/`.

---

## D-009 — FAIR Principles

**Fecha:** 2026-09-19
**Decision:** Datos publicados siguen FAIR.
**Razon:** Reproducibilidad y reutilizacion.
**Consecuencia:** Metadata rica + licencia CC-BY-4.0.

---

## D-010 — Auditabilidad criptografica

**Fecha:** 2026-09-19
**Decision:** Cada dato lleva SHA-256 del documento fuente. Cada version lleva manifest SHA-256.
**Razon:** Auditability-First Science.
**Consecuencia:** Sin hash, entrada no verificable.

---

## D-011 — Etica de publicacion COPE

**Fecha:** 2026-09-19
**Decision:** Se siguen COPE Core Practices.
**Razon:** Originalidad, no plagio, no publicacion redundante.
**Consecuencia:** Toda publicacion incluye declaracion etica.

---

## D-012 — Trazabilidad completa

**Fecha:** 2026-09-19
**Decision:** Cada dato es rastreable desde su ingreso (JSON) hasta su analisis final.
**Razon:** Escrutinio cientifico con rigor de calificacion.
**Consecuencia:** Pipeline: JSON -> DB -> CSV -> analisis -> resultado, con hashes.

---

## D-013 — Barra de progreso obligatoria en scripts

**Fecha:** 2026-09-19
**Decision:** Todo script con bucles sobre entidades usa `tqdm`.
**Razon:** Verificar progreso + senal de heartbeat a SQLite.
**Consecuencia:** Todos los scripts de procesamiento incluyen `tqdm`.

---

## D-014 — DB canonica, CSV derivado

**Fecha:** 2026-09-19
**Decision:** La base SQLite es la fuente de verdad. El CSV es regenerable y NO se versiona.
**Razon:** Evitar divergencia silenciosa entre DB y CSV.
**Consecuencia:** Todo analisis lee desde DB.

---

## D-015 — Cadena de hashes en el manifest

**Fecha:** 2026-09-19
**Decision:** Cada entrada incluye `chain_hash = SHA256(prev_chain || file_sha256)`.
**Razon:** Hash por archivo no detecta reordenamiento ni eliminacion selectiva.
**Consecuencia:** Reordenar o anadir archivos cambia el `chain_root`.

---

## D-016 — Anclaje del manifest en el log cronografico

**Fecha:** 2026-09-19
**Decision:** Cada manifest se ancla via `--anchor` en la tabla `eventos`.
**Razon:** El log cronografico es append-only y encadenado.
**Consecuencia:** `python src/hash_manifest.py X.Y.Z --anchor`.

---

## D-017 — Provenance historico append-only

**Fecha:** 2026-09-19
**Decision:** `provenance_history` nunca se sobrescribe. Cada llamada crea una version encadenada.
**Razon:** Corregir un DOI no debe borrar el anterior.
**Consecuencia:** Toda correccion visible en el dashboard, con hash y `prev_hash`.

---

## D-018 — Registro cronografico encadenado

**Fecha:** 2026-09-19
**Decision:** Todo evento relevante se registra en la tabla `eventos` con cadena SHA-256.
**Razon:** Cualquier alteracion del pasado es detectable matematicamente.
**Consecuencia:** `python src/chronolog.py verificar` es requisito antes de publicar.

---

## D-019 — Schema versionado

**Fecha:** 2026-09-19
**Decision:** Todo cambio de schema pasa por `src/migrations.py`.
**Razon:** Reproducibilidad. Un colaborador con DB vieja puede migrar.
**Consecuencia:** `PRAGMA user_version` indica la version.

---

## D-020 — Firma GPG opcional del manifest

**Fecha:** 2026-09-19
**Decision:** El manifest puede firmarse con GPG via `--sign`.
**Razon:** Firma criptografica = prueba de autoria, no solo de integridad.
**Consecuencia:** Produce `SHA256SUMS.txt.asc`.

---

## D-021 — Reporte de auditoria en TXT (linea por linea)

**Fecha:** 2026-09-19
**Decision:** Cada auditoria produce `outputs/audit_report_<ts>.txt` con checks numerados, PASS/FAIL/SKIP, evidencia y hashes.
**Razon:** Cualquier revisor externo puede verificar el estado sin ejecutar codigo.
**Consecuencia:** `python src/audit_report.py` es requisito antes de publicar.

---

## D-022 — Cadena de reportes de auditoria

**Fecha:** 2026-09-19
**Decision:** Cada reporte incluye `prev_report_hash` y `report_hash`. El indice esta en `registry/reports.jsonl`.
**Razon:** Impedir alteracion retroactiva de reportes.
**Consecuencia:** Verificable con `--verify outputs/audit_report_XXX.txt`.

---

## D-023 — run_all como orquestador observable

**Fecha:** 2026-09-19
**Decision:** `src/run_all.py` ejecuta TODAS las fases en orden, con salida en vivo y log completo a `outputs/run_log_<ts>.txt`.
**Razon:** Reproducibilidad observable.
**Consecuencia:** `python src/run_all.py --seed --dashboard` desde clon fresco.

---

## D-024 — Wrappers multiplataforma (.ps1 / .sh)

**Fecha:** 2026-09-19
**Decision:** `run_all.ps1` y `run_all.sh` activan el venv y delegan en `src/run_all.py`.
**Razon:** Consistencia entre entornos. La logica vive en Python.
**Consecuencia:** Comando identico en ambas plataformas.

---

## D-025 — CI/CD obligatorio antes de merge

**Fecha:** 2026-09-19
**Decision:** Ningun PR se mergea sin `audit.yml` y `chain-guard.yml` en verde.
**Razon:** Proteger la integridad sin depender de disciplina manual.
**Consecuencia:** Si un PR rompe la cadena, CI bloquea el merge.

---

## D-026 — Git hooks locales como primera linea

**Fecha:** 2026-09-19
**Decision:** Tres hooks (`pre-commit`, `pre-push`, `commit-msg`) se instalan via `core.hooksPath=.githooks`.
**Razon:** Atrapar errores antes de llegar a CI.
**Consecuencia:** `./.githooks/install.sh` en cada clon.

---

## D-027 — Conversiones de unidades explicitas

**Fecha:** 2026-09-19
**Decision:** Toda conversion de unidades pasa por `src/unidades.py`.
**Razon:** Evitar errores silenciosos de unidades.
**Consecuencia:** Sin conversion explicita, la entidad no entra al analisis.

---

## D-028 — Investigaciones como unidades de primer nivel

**Fecha:** 2026-09-19
**Decision:** Cada investigacion produce 7 artefactos: preregistro, script, resultado, falsacion, evento, paper, JSON.
**Razon:** Una investigacion sin trazabilidad completa no es auditable.
**Consecuencia:** `docs/INVESTIGACIONES.md` documenta el flujo.

---

## D-029 — THU-TBEA como programa de primer nivel

**Fecha:** 2026-09-19
**Decision:** El contenido de la tesis THU-TBEA se aloja en `registry/thu/` como JSON estructurado.
**Razon:** Auditabilidad. Los problemas deben ser consultables por codigo.
**Consecuencia:** `app_thu.py` renderiza el estado desde los JSON.

---

## D-030 — Etiquetas epistemicas como campo obligatorio

**Fecha:** 2026-09-19
**Decision:** Cada problema, prediccion, parche y afirmacion lleva etiqueta `[D]/[P]/[F]/[A]`.
**Razon:** Contrato epistemico. La transparencia distingue un programa progresivo.
**Consecuencia:** Los tests verifican que problemas abiertos solo lleven `[F]` o `[A]`.

---

## D-031 — Trazabilidad de cada parche

**Fecha:** 2026-09-19
**Decision:** Cada correccion externa se registra en `patches.json` con antes/despues/etiqueta.
**Razon:** La historia de las correcciones es parte del valor epistemico.
**Consecuencia:** El dashboard muestra la timeline de parches por etapa.

---

## D-032 — Predicciones pre-registradas antes de datos

**Fecha:** 2026-09-19
**Decision:** Las predicciones P1-P11 se consideran pre-registradas en `predictions.json`.
**Razon:** Prevenir HARKing. Los valores `[P]` condicionales se distinguen de `[D]` robustos.
**Consecuencia:** La tabla muestra por separado estado "Preregistrada" de "Abierta".

---

## D-033 — Anexos V5.0 con hash y cronolog

**Fecha:** 2026-09-19
**Decision:** Todo hallazgo nuevo se registra como anexo V5.0 con ID permanente, etiqueta y hash.
**Razon:** El PDF original es fijo. La extension debe ser trazable y separable.
**Consecuencia:** `python src/thu/annex.py nuevo --titulo ...`

---

## D-034 — LaTeX generado desde JSON, no escrito a mano

**Fecha:** 2026-09-19
**Decision:** Los `.tex` se generan desde `registry/thu/*.json` + `i18n_content.json`.
**Razon:** Cualquier cambio en los JSON se refleja automaticamente en los PDFs.
**Consecuencia:** `python src/thu/latex_builder.py --all`

---

## D-035 — Compilacion multi-idioma ES / EN / DE

**Fecha:** 2026-09-19
**Decision:** La tesis se compila a PDF en tres idiomas desde la misma fuente JSON.
**Razon:** FAIR (accesibilidad) + ISO 690.
**Consecuencia:** `python src/thu/latex_compile.py --all` produce 3 PDFs con hashes.

---

## D-036 — Descarga desde Streamlit

**Fecha:** 2026-09-19
**Decision:** El dashboard `app_thu.py` sirve los PDFs y `.tex` via `st.download_button`.
**Razon:** Accesibilidad a colaboradores y arbitros.
**Consecuencia:** Seccion "Compilar y descargar" en `app_thu.py`.

---

## Indice rapido

| Rango | Bloque tematico |
|-------|-----------------|
| D-001..D-013 | Fundamentos |
| D-014..D-020 | Infraestructura criptografica |
| D-021..D-024 | Auditoria y orquestacion |
| D-025..D-028 | CI/CD e investigaciones |
| D-029..D-032 | THU-TBEA |
| D-033..D-036 | Anexos V5.0 y LaTeX multi-idioma |

**Total:** 36 decisiones. Proxima: D-037.
---

## D-037 — DOIs solo si estan publicados

**Fecha:** 2026-09-19
**Decision:** Los campos DOI en cualquier JSON del repositorio solo
contienen valores verificables. Si el trabajo no esta publicado,
el valor es `null` y el status es `PENDIENTE`.
**Razon:** Un DOI inventado viola el principio de provenance del
propio protocolo. Cualquier revisor externo que intente resolverlo
va a fallar. Los DOIs de borradores o PDFs no-publicados no se
copian al repositorio.
**Consecuencia:** Los placeholders se marcan explicitamente con
`status: PENDIENTE` o `status: no-publicado`. No se inventan
identificadores bajo ninguna circunstancia.
