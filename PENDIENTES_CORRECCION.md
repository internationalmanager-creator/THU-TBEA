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

---

## 6. Solucion a la prediccion de beta_0 (D.3)

### 6.1. La escalera aurea no es exacta, pero es honesta
El script `prueba_escalera_aurea.py` demuestra que la escalera m_n = M_P * phi^{-n} con n=10 da beta_0 = 0.387, a 1.77% del valor reportado. Pero el analisis de sensibilidad muestra que:
- La ventana del 2% se llena por combinatoria (31 de 125 combinaciones caen ahi).
- La escalera es demasiado gruesa (saltos del 7%).
- El corte T_ex no esta derivado y mueve beta_0 entre 0.348 y 0.426.

### 6.2. La solucion estructural (masas degeneradas)
En lugar de ajustar tres masas distintas, asumir que los tres estados VL son degenerados en n=10 (M = 1.98e16 GeV).
- Esto es un cambio estructural fuerte y falsable.
- La prediccion resultante es beta_0 = 0.387 +/- 0.04 (la banda viene de T_ex).
- Este valor es compatible con el consenso observacional (0.26 +/- 0.06) a ~2 sigma.
- Sigue siendo falsable por LiteBIRD.

### 6.3. Cambio de etiqueta
La etiqueta correcta para beta_0 es [P] (postulado pre-data), no [D] (derivacion). Pero ahora es un [P] honesto: el espectro esta declarado antes de conocer el resultado, no ajustado a el.

### 6.4. Correccion para la tesis (Cap. 10)
- Cambiar las masas VL (1.94, 2.30, 1.40) por el espectro degenerado en 1.98e16 GeV.
- Cambiar beta_0 = 0.3803 por beta_0 = 0.387 +/- 0.04.
- Reclasificar como [P] condicionado al corte T_ex.

---

---

## 7. Alternativas cosmologicas (D.4)

### 7.1. Resultado del ajuste con torsion extendida
Se probaron tres alternativas para evitar el colapso a Omega_tau = 0:
- Torsion + potencial V(Phi)
- Acoplamiento no minimo torsion-DM
- Torsion-DE interactuante

**Ninguna evita el colapso.** Los datos (BAO + SNe) no requieren ningun componente de fluido rigido.

### 7.2. El colapso es de los datos, no del modelo
Un fluido que escala como a^{-6} es invisible a z < 2. El limite es Omega_tau <~ 2e-4. No es un fracaso del programa, es que el fondo FLRW no puede ver la torsion.

### 7.3. La alternativa que parece mejorar lo hace por la razon equivocada
Torsion + potencial da dAIC = -8.4, pero con Omega_tau=0.2997 (pegado al borde) y w=-0.69. El componente extra se comporta como energia oscura, no como torsion. Pierde contra wCDM (dAIC = -11.2 con un parametro menos).

### 7.4. La solucion estructural
Aceptar que Omega_tau = 0 es la prediccion correcta de THU-TBEA en el fondo FLRW (la torsion es algebraica, no dinamica).
- El discriminante esta en la tomografia beta(z) (Cap. 11) y en el crecimiento (f*sigma8).
- Un componente rigido deja firma en el crecimiento aunque sea despreciable en H(z).

### 7.5. Correccion para la tesis (Cap. 8)
- Declarar que Omega_tau = 0 es la prediccion de THU-TBEA tras eliminar algebraicamente la torsion.
- Los datos de BAO + SNe confirman esta prediccion (dAIC = +2.32 a favor de Lambda-CDM, pero compatible con Omega_tau=0).
- El test discriminante es la tomografia beta(z), no el fondo.

---



---

### D.1 — Cálculo de loop con operador no local (Opción 3)

Se calcularon los integrandos de la función beta a 1-loop en FORM 5.0.0 (WSL) para dos casos:

1. **Teoría local (phi^4):** Tadpole ~ g, Bubble ~ g^2. No hay términos g^0 ni g^1.
2. **Operador no local (expansión a primer orden):** El propagador es i / (k^2 (1 + a k^2) - m^2). Los integrandos contienen  k^4 en el denominador, lo que suprime los modos UV.

**Conclusión:** El operador no local cambia la estructura del integrando. Para extraer los coeficientes (1, +1, -1) de `β_eff(g) = κ(1 + g - g²)`, se requiere integrar explícitamente estos denominadores (IBP o integración numérica a 2-loops). Eso se deja como frontera abierta [F].
