# Glosario PIR

> Fuente unica de verdad de etiquetas epistemicas y vocabulario.
> Referenciado por `data/README.md`, `app.py`, `app_thu.py` y `registry/`.

---

## Etiquetas epistemicas

| Etiqueta | Nombre | Significado | Ejemplo |
|----------|--------|-------------|---------|
| `[D]` | Derivado | Se sigue de matematicas o de los datos | "f = c/lambda se sigue de Maxwell" |
| `[P]` | Postulado | Ingrediente, NO derivado. Se asume. | "c es constante en el vacio" |
| `[F]` | Frontera | Problema abierto | "Naturaleza de la materia oscura" |
| `[A]` | Analogia | Sugiere, NO valida | "El cerebro como red Bayesiana" |

**Regla dura:** una entrada `[P]` no puede presentarse como `[D]`.
Si dudas, es `[P]`.

**Regla de honestidad:** cuando un parche externo degrada una etiqueta
de `[D]` a `[P]`, se documenta en `patches.json` con antes/despues.
No se edita en silencio.

---

## Origen del dato

| Valor | Significado | Advertencia |
|-------|-------------|-------------|
| `observado` | Medido directamente | Debe tener instrumento + condiciones |
| `generado` | Producido por simulacion | NO mezclar con observados en el mismo analisis |
| `inferido` | Derivado de otros datos | Debe declarar la cadena de inferencia |
| `simulado` | Monte Carlo / sintetico | Reservado para tests de calibracion |

---

## Estados de progreso

| Estado | Significado |
|--------|-------------|
| `pendiente` | Entidad registrada, sin verificar |
| `en_progreso` | Verificacion en curso |
| `completado` | Verificada con provenance completa |

---

## Estados de hipotesis (pre-registro)

| Estado | Significado |
|--------|-------------|
| `borrador` | Editable, sin hash fijo |
| `bloqueado` | Hash SHA-256 fijo. **Inmutable desde aqui.** |
| `testeado` | Resultado registrado con veredicto |
| `confirmado` | Test superado con exito |
| `falsado` | Test fallo. Entrada obligatoria en `HALLAZGOS_FALSADOS.md` |

---

## Estados de problemas THU-TBEA

| Estado | Significado |
|--------|-------------|
| `CERRADO [D]` | Resuelto con derivacion |
| `ABIERTO [F]` | Frontera empírica declarada |
| `ABIERTO [A]` | Analogia en cuarentena (no valida nucleo) |

---

## Vocabulario de auditoria

- **Manifest**: JSON con SHA-256 de cada archivo + cadena encadenada.
- **Chain root**: hash raiz del manifest. Firma el estado del repo.
- **Evento**: unidad del registro cronografico. Encadenado por hash.
- **Hash chain**: `H_i` depende de `H_{i-1}`. Alterar el pasado rompe el futuro.
- **Anclaje**: registrar el hash del manifest en la tabla `eventos`.
- **Reporte de auditoria**: verificacion linea por linea con checks PASS/FAIL.
- **Cadena de reportes**: `registry/reports.jsonl` (append-only).
- **Paquete de replicacion**: ZIP autonomo con `VERIFY.py` embebido.
- **Anexo V5.0**: hallazgo nuevo durante el desarrollo, con hash y cronolog.

---

## Reglas inmutables

1. **Sin pre-registro, no hay hipotesis testeable.**
2. **Sin provenance completa, la entrada es `[F]`.**
3. **Sin hash SHA-256, la entrada no es verificable.**
4. **El log cronografico NO se edita.** Correcciones = nuevos eventos.
5. **Resultados negativos se publican** en `HALLAZGOS_FALSADOS.md`.
6. **No hay ad-hoc, no hay fine-tuning.** Todo pre-registrado.
7. **Las conversiones de unidades son explicitas** (`src/unidades.py`).
8. **La DB es canonica; el CSV es derivado.**

---

## Abreviaturas comunes

| Abrev. | Significado |
|--------|-------------|
| PIR | Programa de Investigacion Rigurosa |
| THU-TBEA | Teoria Helicoidal Universal - Teoria de Bucles Espirales Aureos |
| EFT | Effective Field Theory |
| RG | Renormalization Group |
| MSRP | Methodology of Scientific Research Programmes (Lakatos) |
| PRISMA | Preferred Reporting Items for Systematic Reviews |
| FAIR | Findable, Accessible, Interoperable, Reusable |
| COPE | Committee on Publication Ethics |
| GUM | Guide to the Expression of Uncertainty in Measurement |
| ECSK | Einstein-Cartan-Sciama-Kibble |
| GDL | Grados de libertad |
| CMB | Cosmic Microwave Background |
| BAO | Baryon Acoustic Oscillations |
| SNe | Supernovae |
| FLRW | Friedmann-Lemaitre-Robertson-Walker |

---

## Como usar este glosario

1. **Antes de crear una entrada**, verificar la etiqueta correcta aqui.
2. **Antes de publicar**, verificar que ninguna etiqueta `[P]` se presente
   como `[D]`.
3. **Antes de un parche**, documentar en `DECISIONS.md` y en
   `registry/thu/patches.json` si aplica al programa THU-TBEA.

---

**Fuente unica.** Si algo en el codigo contradice este archivo, el codigo
tiene un bug. Reportar como issue.