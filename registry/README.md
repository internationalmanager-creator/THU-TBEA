# registry/ — Registro del programa

> Directorio de metadatos, decisiones y trazabilidad del programa PIR.

---

## Archivos

| Archivo | Rol | Editable |
|---------|-----|----------|
| `project_metadata.json` | Metadata general | Si |
| `DECISIONS.md` | Decisiones D-001..D-036 | Append-only |
| `GLOSARIO.md` | Vocabulario y etiquetas | Si |
| `epistemic_log.md` | Log cronologico | **Append-only** |
| `HALLAZGOS_FALSADOS.md` | Resultados negativos | **Append-only** |
| `reports.jsonl` | Cadena de reportes | **Append-only** |
| `chronolog.md` | Cronolog exportado | **Auto-generado** |

## Subdirectorios

| Directorio | Rol |
|------------|-----|
| `preregistro/` | Hipotesis pre-registradas (H-YYYY-NNN) |
| `prisma/` | Revisiones sistematicas |
| `thu/` | Contenido THU-TBEA 5.3 |

---

## Reglas de edicion

**`DECISIONS.md`** — Nunca se borra una decision. Cambios = nueva decision que la supersede.

**`epistemic_log.md`** — Append-only estricto. Correcciones = entradas nuevas.

**`HALLAZGOS_FALSADOS.md`** — Toda hipotesis falsada tiene entrada obligatoria.

**`reports.jsonl`** — No editar a mano. Se anaden lineas via `audit_report.py`.

**`chronolog.md`** — Auto-generado. No editar.

---

## Comandos utiles

    # Estado de la cadena cronografica
    python src/chronolog.py verificar
    python src/chronolog.py listar --limit 20

    # Exportar cronolog
    python src/chronolog.py exportar

    # Pre-registros
    python src/preregistro.py listar
    python src/preregistro.py verificar H-2026-001

    # Reportes de auditoria
    python src/audit_report.py

---

**Todo este directorio esta versionado.** No contiene datos binarios grandes ni secretos.