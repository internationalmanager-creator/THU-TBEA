# -*- coding: utf-8 -*-
"""Retiro formal de P5 (residuo helicoidal de espin) - PDF v5.0."""
import sys, json, time, hashlib
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
REG = LAB / "registry" / "thu"
OUT = LAB / "data" / "inventory"
REG.mkdir(parents=True, exist_ok=True)

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# ============================================================
# 1: Documento de retiro
# ============================================================
hdr("1. Generando documento de retiro P5")

retiro_p5 = {
    "id": "P5",
    "titulo_original": "Residuo helicoidal de espin (STAR/HADES)",
    "version_declarada": "v5.0 (PDF PROGRAMA_COMPLETO_v5.0.pdf)",
    "fecha_retiro": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "estado": "RETIRADA DE PREDICCIONES FALSABLES",

    "razon_retiro": (
        "La prediccion P5 tal como aparece en el PDF v5.0 no cumple los "
        "estandares minimos de falsabilidad y trazabilidad exigidos por el "
        "propio contrato epistemico del programa. Se retira del registro de "
        "predicciones falsables hasta que cumpla esos estandares."
    ),

    "problemas_identificados": [
        {
            "id": "P5-1",
            "severidad": "ALTA",
            "problema": "Valor STAR citado no verificado",
            "detalle": (
                "El PDF v5.0 §16.4 cita 'STAR (1.05 ± 0.15) %'. El paper "
                "referenciado en el PDF (J. Adam et al., PRC 108, 014910, 2023) "
                "NO reporta ese valor en su abstract. Reporta cotas superiores "
                "(<0.24%, <0.35%) y limites de campo magnetico, no un valor "
                "central de polarizacion global."
            ),
            "evidencia": "Consulta al abstract del paper citado (verificado en linea)",
            "impacto": "El valor contra el que se compara no es verificable desde la fuente citada"
        },
        {
            "id": "P5-2",
            "severidad": "ALTA",
            "problema": "Prediccion THU sin derivacion",
            "detalle": (
                "El PDF v5.0 §16.4 afirma '(0.92 ± 0.10) %' como prediccion THU. "
                "No aparece en el texto ninguna derivacion, formula o calculo que "
                "produzca ese valor ni su incertidumbre. Tampoco hay referencia a "
                "un apendice o seccion previa del PDF que lo derive."
            ),
            "evidencia": "Busqueda exhaustiva en el PDF v5.0",
            "impacto": "Sin derivacion, no es una prediccion [D]; tampoco cumple [P] que exigiria postulado explicito"
        },
        {
            "id": "P5-3",
            "severidad": "MEDIA",
            "problema": "Inconsistencia con el estatus epistemico declarado",
            "detalle": (
                "El PDF v5.0 clasifica las morfologias de espin como [A] analogias "
                "(§16.3) y declara que 'ninguna analogia cuenta como corroboracion' "
                "(§17.5). Sin embargo, la Tabla 17.1 lista P5 como prediccion "
                "pre-registrada ('Prereg.'), lo cual la eleva de facto al nivel de "
                "prediccion falsable sin la derivacion correspondiente."
            ),
            "evidencia": "§16.3 + §17.5 + Tabla 17.1 del PDF v5.0",
            "impacto": "Contradiccion interna entre el estatus declarado y el uso en tabla"
        },
        {
            "id": "P5-4",
            "severidad": "MEDIA",
            "problema": "Comparacion '1 sigma' no significativa",
            "detalle": (
                "El PDF afirma 'dentro de 1 sigma'. Aun aceptando los valores "
                "citados sin verificacion, THU predice 0.92 ± 0.10% mientras STAR "
                "mide 1.05 ± 0.15%. La tension es 0.13% / sqrt(0.10^2 + 0.15^2) = "
                "0.13 / 0.18 = 0.72 sigma. Tecnicamente 'dentro de 1 sigma' es "
                "correcto, pero el acuerdo NO es evidencia de nada: dos modelos sin "
                "relacion con el mismo valor central tambien estarian 'dentro de 1 sigma'."
            ),
            "evidencia": "Calculo aritmetico simple",
            "impacto": "El 'exito' reportado no es discriminante entre THU y una prediccion nula"
        }
    ],

    "verificaciones_fallidas": [
        {
            "verificacion": "Origen del valor 1.05% STAR",
            "resultado": "NO ENCONTRADO en abstract del paper citado",
            "accion_sugerida": "Identificar la fuente exacta o eliminar la comparacion"
        },
        {
            "verificacion": "Origen del valor 0.92% THU",
            "resultado": "NO ENCONTRADO en PDF v5.0",
            "accion_sugerida": "Documentar derivacion o eliminar el valor"
        },
        {
            "verificacion": "Derivacion de incertidumbre +/- 0.10% THU",
            "resultado": "NO ENCONTRADO",
            "accion_sugerida": "Justificar o eliminar"
        }
    ],

    "acciones_tomadas": [
        "Marcar P5 en el registro de predicciones como RETIRADA",
        "Documentar las razones en este archivo (trazabilidad completa)",
        "Sugerir al autor (Erick Duque) revisar si existe version intermedia con la derivacion",
        "No incluir P5 en futuras publicaciones hasta resolver los 4 problemas"
    ],

    "acciones_NO_tomadas": [
        "NO se modifica el PDF v5.0 original (queda como registro historico)",
        "NO se borra P5 del historial del programa (queda documentada su retirada)",
        "NO se reescribe la seccion §16.4 del PDF v5.0",
        "NO se retira el Apendice G (las morfologias como analogias siguen siendo validas)"
    ],

    "recomendacion_para_reversion": {
        "condiciones": [
            "Localizar la fuente exacta del valor STAR citado (puede ser un paper distinto o una agregacion)",
            "Documentar la derivacion de 0.92% +/- 0.10% desde el nucleo teorico",
            "Justificar por que esta prediccion es [D] o [P] y no [A] analogia",
            "Realizar un test discriminante (no solo 'dentro de 1 sigma')"
        ],
        "si_se_cumplen": "P5 puede reintegrarse como prediccion falsable",
        "si_no_se_cumplen": "P5 permanece retirada indefinidamente"
    },

    "contrato_epistemico": (
        "Este retiro es consistente con el contrato epistemico declarado en el "
        "PDF v5.0 (Capitulo 1, Apendice F.2). El propio programa exige: "
        "(1) transparencia radical, (2) reproducibilidad, (3) falsabilidad, "
        "(4) no sobreventa del alcance. Retirar P5 es un acto de cumplimiento "
        "de esos cuatro compromisos, no una debilidad del programa."
    )
}

retiro_path = REG / "P5_retirada_v5.0.json"
retiro_path.write_text(json.dumps(retiro_p5, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  Guardado: {retiro_path}")
print(f"  Tamano: {retiro_path.stat().st_size} B")

# ============================================================
# 2: README de retiro (narrativa)
# ============================================================
hdr("2. Generando README de retiro")

readme = """# Retiro formal de P5 (v5.0)

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
"""

readme_path = REG / "P5_retirada_v5.0_README.md"
readme_path.write_text(readme, encoding="utf-8")
print(f"  Guardado: {readme_path}")

# ============================================================
# 3: Actualizar lista de predicciones
# ============================================================
hdr("3. Actualizando lista de predicciones")

predicciones_path = REG / "predicciones_estado.json"

# Estado actual de las 11 predicciones (basado en lo verificado)
predicciones_estado = {
    "fecha_actualizacion": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "version_referencia": "v5.0 (PDF PROGRAMA_COMPLETO_v5.0.pdf)",
    "predicciones": {
        "P1": {
            "titulo": "Oscilaciones helicoidales en H(z)",
            "estado": "AUDITADA",
            "metodo": "DESI DR2 BAO",
            "resultado": "CONSISTENTE_CON_NULO (p=0.45)",
            "referencia": "data/inventory/fase_p1_oscilaciones_hz.json",
            "conclusion": "No detectable con datos actuales. No falsa THU."
        },
        "P2": {"estado": "PENDIENTE", "razon": "Requiere mapas Planck crudos"},
        "P3": {"estado": "PENDIENTE", "razon": "Requiere datos de lentes gravitacionales"},
        "P4": {"estado": "PENDIENTE", "razon": "Sin datos accesibles"},
        "P5": {
            "titulo": "Residuo helicoidal de espin (STAR/HADES)",
            "estado": "RETIRADA",
            "razon": "4 problemas: valor STAR no verificado, THU sin derivacion, inconsistencia epistemica, acuerdo no discriminante",
            "referencia": "registry/thu/P5_retirada_v5.0.json"
        },
        "P6": {"estado": "PENDIENTE", "razon": "Experimental"},
        "P7": {"estado": "PENDIENTE", "razon": "Requiere analisis teorico adicional"},
        "P8": {"estado": "PENDIENTE", "razon": "Auditoria pendiente (Tarea C)"},
        "P9": {"estado": "PENDIENTE", "razon": "Requiere datos experimentales"},
        "P10": {"estado": "PENDIENTE", "razon": "Requiere simulacion numerica"},
        "P11": {"estado": "PENDIENTE", "razon": "Experimental (microtubulos)"}
    }
}

pred_path = REG / "predicciones_estado.json"
pred_path.write_text(json.dumps(predicciones_estado, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  Guardado: {pred_path}")

# ============================================================
# 4: Copia de seguridad en inventory
# ============================================================
hdr("4. Copia en inventory")

inv_path = OUT / "fase_p5_retiro.json"
inv_path.write_text(json.dumps(retiro_p5, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  Guardado: {inv_path}")

# ============================================================
# 5: Resumen
# ============================================================
hdr("5. RESUMEN")

print(f"  P5 RETIRADA del registro de predicciones falsables")
print()
print(f"  Documentos generados:")
print(f"    {REG / 'P5_retirada_v5.0.json'}")
print(f"    {REG / 'P5_retirada_v5.0_README.md'}")
print(f"    {REG / 'predicciones_estado.json'}")
print(f"    {OUT / 'fase_p5_retiro.json'}")
print()
print(f"  Problemas identificados:")
for p in retiro_p5["problemas_identificados"]:
    print(f"    [{p['severidad']:5s}] {p['id']}: {p['problema']}")
print()
print(f"  Proxima accion:")
print(f"    - Comunicar al autor (Erick Duque)")
print(f"    - Revisar si existen versiones intermedias con la derivacion")
print(f"    - NO citar P5 en publicaciones futuras")
print()
print("=" * 72)
print("  RETIRO COMPLETADO")
print("=" * 72)
