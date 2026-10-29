# PENDIENTES DE CORRECCION - THU-TBEA

**Fecha:** 2026-10-29
**Autor:** Erick Duque (ORCID 0009-0004-1245-5464)

Este documento acumula las correcciones pendientes para la tesis, basadas en los resultados de las derivaciones y auditorias.

---

## 1. Prediccion de Omega_tau falsada (D.4)

En el Capitulo 8 de la tesis se afirma: `w_K = +1, rho_K ∝ a^{-6}`.
El ajuste con BAO DESI DR2 + SNe Pantheon+ da `Omega_tau = 0.0000`.
Delta AIC = +2.32 (Lambda-CDM preferido).
**Correccion:** Reclasificar Omega_tau como [F] frontera abierta. Documentar la tension entre w_K = +1 y los datos.

## 2. Hallazgos de la derivacion D.5 (Dirac-Bergmann 4D)

### 2.1. Cierre de D.9.6
El script `scripts/dirac_bergmann_4d.py` demuestra que en 4D: dim(Gamma)=30, FC=8, SC=8, GDL=3.
Desglose: 2 tensoriales (graviton) + 1 escalar.
El sector escalar propaga 1 g.d.l. en 4D, coincidiendo con el resultado proyectado de M6.
**Correccion:** Eliminar la limitacion D.9.6 de DERIVATIONS.md.

### 2.2. Derivacion del factor sqrt(3)
El factor sqrt(3) no es un postulado. Sale de la estructura de restricciones + Palatini.
Coeficiente cinetico efectivo = 1/2 - alpha. Con alpha=-1, beta=2, da 3/2.
**Correccion:** En DERIVATIONS.md D.3.1, cambiar el estatus de [P] a [D].

### 2.3. Inconsistencia de signo en el termino cinetico
Con firma (-,+,+,+) y L = +(1/2)(grad tau)^2 - V, rho < 0 (fantasma).
La version con energia positiva requiere L = -(1/2)(grad tau)^2 - V.
**Correccion:** Elegir una convencion de signo global y aplicarla en Cap. 3, DERIVATIONS.md y scripts.

### 2.4. Inconsistencia entre el conteo de 4D y M6
En 4D: (30-16-8)/2=3, restando graviton da 1. En M6: (10-8)/2=1. Son consistentes.
**Correccion:** Agregar el paso intermedio (restar graviton en 4D) en la tesis.

---

## 3. Estado de las 5 derivaciones

| Derivacion | Estado | Herramienta |
|---|---|---|
| D.1-PUNTO-FIJO (loops) | Pendiente | FORM/FeynCalc |
| D.2-VACIO (N=88, CY3) | Verificado | CoCalc (SageMath) |
| D.3-BETA0 (amplitud) | Pendiente | FORM/FeynCalc |
| D.4-AJUSTE (BAO+SNe) | Completado | scipy |
| D.5-DIRAC-4D (U4) | Completado | SymPy |

---

**Fin del documento.**
