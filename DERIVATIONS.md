# Apéndice D — Derivaciones Mínimas del Núcleo THU-TBEA

**Autor:** Erick Duque (ORCID 0009-0004-1245-5464)
**Versión:** v5.4-post-review | **Fecha:** 2026-09-26
**Referencia:** Respuesta a Crítica Mayor #7 del revisor externo

---

## Propósito

Reunir las derivaciones mínimas necesarias para verificar el núcleo del programa sin depender de la tesis completa. Cada resultado se presenta con: acción de partida, convenciones, pasos intermedios, dominio de validez, estatus epistémico [D]/[P]/[F]/[A].

---

## D.1 — Convenciones generales

### D.1.1 Geometría

- Variedad: **U4 = (M, g_munu, Gamma^lambda_munu)** (Riemann-Cartan, métrica y conexión independientes).
- Signatura: **(-,+,+,+)** en 4D; **(-,-,-,+,+,+)** en 6D.
- Riemann: **R^rho_sigma_mu_nu = d_mu Gamma^rho_nu_sigma - d_nu Gamma^rho_mu_sigma + Gamma^rho_mu_lambda Gamma^lambda_nu_sigma - Gamma^rho_nu_lambda Gamma^lambda_mu_sigma**.
- Ricci: **R_mu_nu = R^lambda_mu_lambda_nu**.
- Unidades: **hbar = c = 1**.
- Planck reducida: **M_P = 2.435e18 GeV**.

### D.1.2 Descomposición de la torsión

T^lambda_mu_nu se descompone en tres piezas irreducibles:

```
T^lambda_mu_nu = (1/3)(delta^lambda_nu T_mu - delta^lambda_mu T_nu) + (1/6) epsilon^lambda_mu_nu_rho S^rho + q^lambda_mu_nu
```

donde T_mu = traza vectorial, S^rho = parte axial, q = parte tensorial. **THU-TBEA retiene únicamente S^rho** (T_mu = q = 0) por postulado [P].

---

## D.2 — Variación de Palatini

### D.2.1 Acción base

```
S = (1/2kappa^2) int d^4x sqrt(-g) R(g,Gamma) + int d^4x sqrt(-g)[(1/2)(nabla_mu phi)(nabla^mu phi) - V(phi)]
```

con **kappa^2 = M_P^(-2)**. El campo phi es un **pseudoescalar**.

### D.2.2 Variación respecto a la conexión

Tratando Gamma como variable independiente (Palatini), la variación da:

```
delta_Gamma S = (1/2kappa^2) int d^4x sqrt(-g) g^mu_nu delta R_mu_nu = 0
```

Para torsión axial pura, la solución algebraica es:

```
T^lambda_mu_nu = (1/M_P) epsilon^lambda_mu_nu_rho nabla^rho tau
S^rho = (6/M_P) nabla^rho tau
```

**Resultado clave:** la torsión axial no propaga, se elimina algebraicamente a favor de nabla tau. **Dominio:** torsión axial pura (T_mu = q = 0). **Estatus:** [D].

---

## D.3 — Redefinición canónica

### D.3.1 Motivación

tau tiene término cinético no canónico. Se redefine:

```
tau_c = sqrt(3) tau
```

### D.3.2 Lagrangiano canónico

```
L_escalar = (1/2)(nabla_mu tau_c)(nabla^mu tau_c) - V(tau_c)
```

Término cinético **positivo** con signatura (-,+,+,+). Dimensiones: [tau_c]=M, [nabla tau_c]=M^2, [L]=M^4. **Estatus:** [D].

### D.3.3 Consecuencia cosmológica

En fondo FLRW, tau_c actúa como fluido rígido **w_K = +1** con:

```
H^2 = (1/3 M_P^2)[rho_materia + rho_tau]
rho_tau = (1/2) tau_c_dot^2 + V(tau_c)
```

**Estatus:** [D] bajo FLRW.

---

## D.4 — Operador cinético no local

### D.4.1 Postulado

```
Box_efectivo = Box * exp(-phi_param * Box / M_P^2)
```

**Estatus:** [P] postulado, no derivado de primeros principios.

### D.4.2 Propagador

```
Delta(k^2) = i / [k^2 * exp(phi_param * k^2 / M_P^2) - m^2]
```

### D.4.3 Polos y función W de Lambert

Con x = k^2/M_P^2:

```
x * exp(phi_param * x) = m^2/M_P^2
x = (1/phi_param) W(phi_param * m^2/M_P^2)
```

**Ramas:** W_0 (física, k^2 > 0) y W_-1 (no física, k^2 < 0, eliminada con prescripción fakeon).

### D.4.4 Residuo en el polo físico

```
Res[Delta] = exp(-a m^2)/(1 + a m^2) > 0
```

con a = phi_param/M_P^2. **Numerador > 0** siempre. **Denominador > 1** siempre. Resultado: **Res > 0** para todo a, m > 0. Garantiza norma positiva en el espacio de Hilbert perturbativo.

**Dominio:** perturbativo, condicionado a la prescripción de contorno. **No implica unitariedad no perturbativa.**

**Estatus:** [D].

---

## D.5 — Punto fijo áureo

### D.5.1 Flujo RG

```
beta_eff(g) = kappa_RG (1 + g - g^2)
```

### D.5.2 Punto fijo

```
g^2 - g - 1 = 0  =>  g* = (1 +- sqrt(5))/2
```

Raíz positiva: **g* = phi = 1.618...** (número áureo). Raíz negativa descartada por estabilidad.

### D.5.3 Estabilidad

```
beta_eff'(phi) = kappa_RG (1 - 2phi) = -2.236 kappa_RG < 0
```

**IR estable.** **Dominio:** válido al orden 1 en la truncación. Estabilidad bajo órdenes superiores: [F]. **Estatus:** [D] al orden 1.

---

## D.6 — Cancelación modulada del vacío

### D.6.1 Postulado

```
N = 4 * 22 = 88
```

**Estatus:** [P]. Motivación: conteo de modos CY3 (h^{1,1}=22) y factor 4 del espacio-tiempo.

### D.6.2 Resultado

```
Lambda_THU = M_P * phi^(-88) ~ 989.89 MeV
```

**Nota de honestidad:** mecanismo propuesto, no solución establecida al problema de la constante cosmológica. **Estatus:** [P].

---

## D.7 — Matriz de dependencias P1-P12

| ID | Predicción | Acción base | Hipótesis auxiliares | Truncamiento | Dominio |
|----|-----------|-------------|---------------------|--------------|---------|
| P1 | Oscilaciones H(z) | D.2+D.3 | w_K=+1, FLRW | O(E^2/M_P^2) | z<2 |
| P2 | Modulación CMB | D.2+D.4 | beta_0 [P], fakeon | O(k^2/M_P^2) | l<2000 |
| P3 | Tomografía beta(z) | D.4 | Forma funcional [D] | O(k^2/M_P^2) | z en [0,3] |
| P4 | Chameleon | D.4 | beta_c<2.1e-4 | O(phi/M_P) | sub-mm |
| P5 | Residuo espín | D.2 | RETIRADA v5.4 | — | — |
| P6 | Escala trans-escalar | D.6 | N=88 [P] | O(phi/M_P) | 989.89 MeV |
| P7 | Neutrón-hidrógeno | D.6 | RETIRADA v4.1 | — | — |
| P8 | Espectro de modos | D.4 | fakeon | O(k^2/M_P^2) | k<<M_P |
| P9 | Estabilidad RG | D.5 | Flujo beta_eff orden 1 | O(g^2) | g~phi |
| P10 | Causalidad | D.2 | Sector proyectado | O(E^2/M_P^2) | lineal |
| P11 | Paridad CMB | D.4 | Anisotropía [P] | O(k^2/M_P^2) | l<500 |
| P12 | Falsación sistemática | Protocolo | Umbral 3 sigma | — | P1-P11 |

P5 y P7 retiradas formalmente (ver `registry/HALLAZGOS_FALSADOS.md`).

---

## D.8 — Resumen de estatus epistémico

| Resultado | Estatus | Dominio | Verificación independiente |
|-----------|---------|---------|---------------------------|
| Torsión axial = nabla tau (D.2) | [D] | Torsión axial pura | Pendiente |
| Redefinición canónica (D.3) | [D] | Sector escalar | Verificable |
| w_K = +1 (D.3.3) | [D] | FLRW | Cosmología estándar |
| Operador no local (D.4.1) | [P] | Postulado | No derivado |
| Propagador W (D.4.3) | [D] | Perturbativo | Función estándar |
| Residuo > 0 (D.4.4) | [D] | Fakeon | Verificable |
| Punto fijo phi (D.5) | [D] orden 1 | Truncación O(g^2) | Verificable |
| Lambda_THU (D.6) | [P] | Fenomenología | Sin verificación |

---

## D.9 — Limitaciones declaradas

1. Variación de Palatini exacta **solo para torsión axial pura**.
2. Operador cinético no local es **postulado**, no derivado.
3. Consistencia no perturbativa **abierta**. Residuo positivo es necesario, no suficiente.
4. Punto fijo áureo **estable al orden 1**. Persistencia a orden superior no demostrada.
5. Lambda_THU es **mecanismo propuesto**, no solución establecida.
6. Conteo de 1 g.d.l. es **en sector proyectado**, no 4D general.
7. P5 y P7 fueron **retiradas formalmente** (registro de autocorrección).

---

## D.10 — Invitación a verificación independiente

El programa solicita revisión externa de:

1. Variación de Palatini completa (D.2), verificación simbólica en SymPy.
2. Residuo del propagador (D.4.4), verificación numérica.
3. Estabilidad del punto fijo áureo (D.5) al orden siguiente.
4. Matriz de dependencias P1-P12 (D.7), para detectar hipótesis ocultas.

Scripts en `src/thu/verificacion_simbolica.py`. Resultados con hash SHA-256 en `registry/thu/verificacion_simbolica.json`.

---

**Fin del apéndice.**
