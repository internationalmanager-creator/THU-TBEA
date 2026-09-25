# Retiro formal de P5 (v5.0)

**Fecha:** 2026-09-21
**Prediccion:** P5 — Residuo helicoidal de espin (STAR/HADES)
**Version declarada:** PDF `PROGRAMA_COMPLETO_v5.0.pdf`
**Estado:** RETIRADA DE PREDICCIONES FALSABLES

## Motivo del retiro

La prediccion P5, tal como aparece en el PDF v5.0 §16.4 y en la Tabla 17.1,
no cumple los estandares minimos de falsabilidad y trazabilidad exigidos por
el propio contrato epistemico del programa.

## Problemas identificados (4)

### P5-1: Valor STAR citado no verificado

El PDF cita `STAR (1.05 ± 0.15) %`. El paper referenciado (Adam et al. 2023,
PRC 108, 014910) no reporta ese valor en su abstract. El abstract contiene
cotas superiores (<0.24%, <0.35%) y limites de campo magnetico, no un valor
central.

### P5-2: Prediccion THU sin derivacion

El valor `0.92 ± 0.10 %` no tiene derivacion en el PDF v5.0. No hay formula,
calculo, ni referencia a un apendice previo que lo justifique.

### P5-3: Inconsistencia epistemica

El PDF clasifica morfologias de espin como `[A] analogia` (§16.3) y declara
que "ninguna analogia cuenta como corroboracion" (§17.5). Pero la Tabla 17.1
lista P5 como prediccion `Prereg.` (pre-registrada), elevandola de facto a
prediccion falsable sin cumplir los requisitos.

### P5-4: Acuerdo "1 sigma" no discriminante

Aun aceptando los valores sin verificar:
- THU: 0.92 ± 0.10 %
- STAR: 1.05 ± 0.15 %
- Tension: 0.72 sigma

Dos modelos sin relacion que coincidan en el mismo valor central tambien
estarian "dentro de 1 sigma". El acuerdo no es evidencia de THU.

## Acciones tomadas

1. ✅ P5 marcada como RETIRADA en el registro interno (`registry/thu/`)
2. ✅ Documentada la razon completa (este archivo)
3. ✅ Sugerida al autor revision de versiones intermedias
4. ✅ Recomendacion: no citar P5 en futuras publicaciones hasta resolver

## Acciones NO tomadas

1. ❌ NO se modifica el PDF v5.0 original (queda como registro historico)
2. ❌ NO se borra P5 del historial (queda documentada su retirada)
3. ❌ NO se reescribe §16.4
4. ❌ NO se retira el Apendice G (las morfologias como analogias siguen validas)

## Reversion

P5 puede reintegrarse si se cumplen 4 condiciones:

1. Localizar la fuente exacta del valor STAR citado
2. Documentar la derivacion de `0.92 % ± 0.10 %` desde el nucleo teorico
3. Justificar por que es `[D]` o `[P]` y no `[A]`
4. Realizar un test discriminante (no solo "dentro de 1 sigma")

Si se cumplen: P5 vuelve como prediccion falsable.
Si no: P5 permanece retirada indefinidamente.

## Consistencia con el contrato epistemico

Este retiro cumple los 4 compromisos declarados en el PDF v5.0 (Capitulo 1):

1. **Transparencia radical** — se documenta el problema completo
2. **Reproducibilidad** — se traza la fuente de cada afirmacion
3. **Falsabilidad** — se retira lo que no es falsable
4. **No sobreventa** — se reconoce que P5 no cumple el estandar

Retirar P5 no debilita el programa. **Fortalece su credibilidad** al demostrar
que aplica sus propios criterios incluso a sus propias predicciones.

---

**Firmado:** Laboratorio Secreto (auditoria automatica + revision manual)
**Referencia:** `data/inventory/fase_p5_retiro.json`
**Trazabilidad:** PDF v5.0 §16.4, §16.3, §17.5, Tabla 17.1, Apendice F.3
