# Errata y correcciones — THU-TBEA v5.5

**Autor:** Erick Duque (ORCID 0009-0004-1245-5464)
**Fecha:** 2026-10-29
**Reemplaza a:** v5.4 (DOI de versión 10.5281/zenodo.22949313)
**DOI de concepto (estable, citar este):** 10.5281/zenodo.22949312

Este documento registra los errores detectados en la v5.4 durante la auditoría
de octubre de 2026, qué se corrigió en esta versión y qué queda explícitamente
reclasificado. Se publica junto con la tesis porque el programa declara
explícitamente sus fronteras y su rigor autocorrectivo: ocultar estos puntos
sería inconsistente con el contrato epistémico del propio programa.

Convención de etiquetas: **[D]** derivado · **[P]** postulado · **[F]** frontera
abierta · **[A]** analogía.

---

## Resumen

| ID | Dónde | Afirmación v5.4 | Resultado de la auditoría | Estado en v5.5 |
|----|-------|-----------------|---------------------------|----------------|
| E-01 | Cap. 6 (§6.2–6.4) | $\beta_{\rm eff}=\kappa(1+g-g^2)$ "derivada de tadpole, vértice lineal y dos vértices" **[D]** | Las tres fórmulas del propio capítulo suman $2\kappa(1-g^2)/\epsilon$; el tadpole es idénticamente nulo; un desarrollo de loops no genera términos $g^0$ ni $g^1$ | **[P]** (estructura); [D] sólo el álgebra de las raíces |
| E-02 | Cap. 10 (§10.2–10.5) | $\beta_0=0.3803^\circ$ derivado de un acoplamiento a nivel de árbol **[P]** con $A=1.819$ | No existe vértice $a\gamma\gamma$ a árbol (es la anomalía ABJ); falta el término hadrónico $-1.92$; el $+0.152$ es un ajuste de 4 parámetros a 1 número | **[P]**, con amplitud condicional y advertencia de retrodicción |
| E-03 | Cap. 5 (§5.3–5.4) | "un grado de libertad" **[D]** | Correcto sólo en el sector proyectado $M_6$; en 4D el conteo da 3 = 2 tensoriales + 1 escalar (la torsión aporta 0) | **[D]** ampliado a 4D; se declara la interpretación de $\tau$ como reloj |
| E-04 | Cap. 3 / D.3.2 | "término cinético positivo con signatura $(-,+,+,+)$" | Con esa signatura, $+\tfrac12(\nabla\tau)^2$ da $\rho_\tau=V-\tfrac12\dot\tau^2<0$ (fantasma) | Se fija la convención: $L=-\tfrac12(\nabla\tau)^2-V$ |
| E-05 | Dashboard / publicación | DOI 22949313 como referencia única | Existen dos líneas con concept DOI distintos (22949312 y 22950277) | Se continúa la línea citada (22949312) |
| E-06 | Varios (menores) | $A=1.819\pm0.19$ dentro de un bloque **[D]**; $J^\mu_{\rm hel}=i\Phi^\dagger\partial^\mu\Phi$ | $A$ es [P]; esa corriente no es hermítica ni conservada | Corregido / declarado |

---

## E-01 — Función beta del Cap. 6: los coeficientes $(1,+1,-1)$ no salen de los loops

**Lo que decía la v5.4.** Que $\Sigma^{(1)}$ (tadpole), $\Gamma^{(1)}$ (vértice
lineal) y $\Gamma^{(2)}$ (dos vértices) producían
$\beta_{\rm eff}=\kappa(1+g-g^2)$, con punto fijo $g_\star=\varphi$ **[D]**.

**Lo que se encontró.** Recalculando con las propias fórmulas de §6.2:

$$\Sigma^{(1)}=\frac{2\kappa}{\epsilon},\qquad
\Gamma^{(1)}=0\ \text{(la tesis lo declara por simetría)},\qquad
\Gamma^{(2)}=-\frac{2\kappa g^2}{\epsilon}$$

$$\Sigma^{(1)}+\Gamma^{(1)}+\Gamma^{(2)}=\frac{2\kappa}{\epsilon}\left(1-g^2\right)$$

cuyos puntos fijos son $g_\star=\pm 1$, **no** $\varphi$. Además:

- el término $+g$ se atribuye a $\Gamma^{(1)}$, que el propio texto anula;
- el tadpole con vértice derivativo es $\int d^dl\,l_\mu/(l^2-m^2)=0$
  (integrando impar): no hay término constante;
- con un factor $g$ por vértice, $Z_g$ es serie en $g^2$ y $\beta$ en $g^3$:
  un término $g^0$ o $g^1$ es imposible en el desarrollo de loops;
- la polarización del vacío (con el seagull $KK\Phi^\dagger\Phi$, que el
  cálculo original omitía) es transversal y $\propto g^2(k^2\eta_{\mu\nu}-k_\mu k_\nu)$,
  es decir $Z_g\sim g^2/\epsilon$ y $\beta\sim g^3$: punto fijo $g_\star=0$.

**Estado en v5.5.** La forma cuadrática $\beta_{\rm eff}=\kappa(1+g-g^2)$ se
reclasifica **[P]**: es un ansatz con la raíz áurea incorporada. Lo único
derivable **[D]** es el álgebra de las raíces y la estabilidad
($\beta'(\varphi)=-\kappa\sqrt5<0$), condicionada a la forma del flujo.

**Qué haría falta para recuperar [D].** (i) regla de Feynman explícita del
vértice $K$–$\Phi$–$\Phi$; (ii) inclusión del seagull; (iii) un mecanismo de
tadpole no nulo, que exige $\langle A_\mu\rangle\neq0$ con dimensión de masa y
hace $\beta=\beta(g,\langle A\rangle/m)$; (iv) cálculo a 2 loops del término $g^2$.

Reproducible: `scripts/beta_eff_loops.py`.

---

## E-02 — $\beta_0$ del Cap. 10: no es una derivación de árbol, y $A$ está ajustada

**Lo que decía la v5.4.** $\beta_0=0.20906\times1.819=0.3803^\circ$, con
$A=5/3+0.152$ y el $+0.152$ de correcciones de umbral de tres estados
vector-like, presentado como [P] condicional.

**Lo que se encontró.**

1. **No hay acoplamiento a árbol.** Un pseudoescalar con acoplamiento derivado
   no tiene vértice $a\gamma\gamma$ a nivel de árbol: el operador
   $\tfrac14 g\,aF\tilde F$ es la anomalía de Adler–Bell–Jackiw (1 loop, exacta,
   no renormalizada). Lo derivable es el factor de grupo y la cinemática.
2. **La cinemática sí cierra.** De $\tfrac14 g aF\tilde F$ con fondo $a(t)$,
   las helicidades circulares obedecen $\omega_\pm=k\mp\tfrac12 g\dot a$, de
   donde $\Delta\phi=g\,\Delta a$ y $\beta=\tfrac12 g\,\Delta a$. Con
   $\Delta a=2\pi f_a N_{\rm DW}$ y $g=\alpha A/(2\pi f_a)$, $f_a$ cancela y
   queda $\beta_0=(\alpha_{\rm em}/2)AN_{\rm DW}$. Verificado simbólicamente.
3. **Falta el término hadrónico.** Cualquier campo acoplado a gluones adquiere
   $-1.92$ por mezcla con $\pi^0,\eta$ por debajo de $\Lambda_{\rm QCD}$. Los
   fermiones declarados son coloreados ($N_c=3$), así que corresponde
   $A=5/3-1.92=-0.253$ y $\beta_0=-0.053^\circ$: **cambio de signo**. Si la
   intención es un ALP sin acoplamiento a gluones, hay que justificar por qué
   aparece la traza de color.
4. **$A_0=5/3$ omite leptones por construcción.** Con el electrón en el mismo
   sector, $A_0=8/3$ y $\beta_0=0.558^\circ$.
5. **El $+0.152$ está ajustado.** Con $y=2$ y las masas declaradas
   ($1.94$, $2.30$, $1.40\times10^{16}$ GeV) se reproduce $0.1518$, pero son
   **cuatro parámetros para un número**. Sensibilidad: $14.9\%$ en $\beta_0$ por
   cada $e$-fold en las masas; con $y=1$ (perturbativo) harían falta masas
   $\sim9.5\times10^{16}$ GeV.
6. **La escalera áurea no rescata la predicción.** Con $m_n=M_P\varphi^{-n}$ y
   los tres estados en $n=10$: $\delta A=0.185$, $\beta_0=0.3870^\circ$
   (1.8 %). Pero 31 de 125 combinaciones discretas caen dentro de $\pm2\%$, el
   paso entre niveles es de $\sim7\%$ en $\beta_0$, y un factor 2 en
   $T_{\rm ex}$ mueve $\beta_0$ entre $0.309$ y $0.426$. El valor observado
   corresponde a $n\approx10.25$, entre dos peldaños.

**Estado en v5.5.** $\beta_0$ queda **[P]**, con tres advertencias explícitas:
(i) requiere decidir el término hadrónico; (ii) $A_0$ depende del espectro
declarado; (iii) la amplitud es un ajuste, no una predicción. La forma
$\beta(z)/\beta_0$ sigue siendo [D].

Reproducible: `scripts/beta0_acoplamiento.py`, `scripts/prueba_escalera_aurea.py`.

---

## E-03 — Dirac–Bergmann: el grado de libertad era proyectado

**Lo que decía la v5.4.** Un grado de libertad físico **[D]** (Cap. 5), con la
limitación D.9.6 reconociendo que el conteo era en el sector proyectado.

**Lo que se encontró (extensión a 4D).** Análisis completo sobre $U_4$ con
métrica ADM, $\Phi$ y torsión axial:

- $\pi_\Phi$ invertible para $\dot\Phi$ (sin restricción primaria);
- $H=N H_\perp+N^iH_i$ exacto, sin velocidad residual (la cadena se detiene en
  el nivel secundario);
- torsión axial: $\pi_A^\mu=0$ (4 primarias) y $\det H=-16M_P^8\alpha^4\neq0$,
  es decir 4 pares de segunda clase: **no aporta ningún grado de libertad**;
- conteo: $\dim\Gamma=30$, 8 de primera clase, 8 de segunda clase
  $\Rightarrow \mathrm{GDL}=(30-16-8)/2=3=2$ tensoriales $+1$ escalar.

El límite proyectado se reproduce exactamente: $\det\mathcal M=(\kappa_2^2+\kappa_3^2)^2$,
rango 8, $\mathrm{GDL}=1$, y $3-2=1$. Limitación declarada: $\tau$ se cuenta
como reloj (identificación estructural, no derivada del conteo); si se contara
como campo que propaga, el total sería 4.

Reproducible: `scripts/dirac_bergmann_4d.py`.

---

## E-04 — Signo del término cinético

Con signatura $(-,+,+,+)$, escribir $+\tfrac12(\nabla\tau)^2$ implica
$\rho_\tau=V-\tfrac12\dot\tau^2<0$: energía negativa (fantasma). La densidad
usada en el Cap. 3, $\rho_\tau=\tfrac12\dot\tau^2+V$, requiere
$L=-\tfrac12(\nabla\tau)^2-V$. Ambas dan $w_K=+1$, pero sólo la segunda tiene
energía positiva. En v5.5 se fija $L=-\tfrac12(\nabla\tau)^2-V$ de forma
explícita y coherente en el Cap. 3 y en D.3.2.

---

## E-05 — Duplicación de la línea de publicación

Al preparar esta versión se encontraron **dos líneas con concept DOI distintos**:

| línea | registro | concept DOI | versión | fecha | contenido |
|-------|----------|-------------|---------|-------|-----------|
| A (citada) | 22949313 | 22949312 | 5.4 | 2026-09-24 | 3 PDFs + README + CITATION |
| B | 23129566 | 22950277 | 5.4.2 | 2026-10-04 | zip del repositorio |

La tesis, `CITATION.cff` y el dashboard citaban A; B no estaba citada. La v5.5
continúa la **línea A** y todas las citas pasan a usar el **DOI de concepto
22949312**, que resuelve siempre a la última versión. La línea B se conserva
como snapshot de código, pero no debe citarse como la tesis.

---

## E-06 — Correcciones menores

1. `A = 1.819 ± 0.19` aparecía dentro de un bloque etiquetado **[D]** en las
   constantes; es **[P]**.
2. La corriente helicoidal escrita como $J^\mu_{\rm hel}=i\Phi^\dagger\partial^\mu\Phi$
   no es hermítica ni conservada; la forma correcta es
   $J^\mu=\tfrac{i}{2}(\Phi^\dagger\partial^\mu\Phi-\partial^\mu\Phi^\dagger\Phi)$.
   Sin ella no vale la identidad de Ward usada en el matching.
3. $0.20906$ es un redondeo de $(\alpha_{\rm em}/2)(180/\pi)=0.209054$;
   el efecto en $\beta_0$ es $\sim3\times10^{-5}$ grados (despreciable, pero se
   documenta).
4. Dashboard: 29 usos de `use_container_width` (parámetro eliminado después del
   2025-12-31), P5 retirada mostrada como valor pre-registrado y $\beta_{\rm eff}$
   sin etiqueta. Corregido en el commit `77ae1a6`.

---

## Lo que **no** cambia

El núcleo geométrico no se toca: torsión axial como solución exacta de Palatini
(Cap. 3), normalización canónica $\tau_c=\sqrt3\,\tau$ (derivada en 4D vía la
eliminación de la torsión, E-03), cancelación del vacío escalar con $N\approx1.2202$
(Cap. 7) y la forma $\beta(z)$ (Cap. 11). Los errores E-01 a E-04 afectan la
*amplitud* y la *etiqueta epistémica*, no la estructura del sector.

## Reproducibilidad

Todos los resultados de esta errata se recalculan con los scripts del repositorio:

```
python scripts/dirac_bergmann_4d.py          # E-03
python scripts/beta_eff_loops.py             # E-01
python scripts/beta0_acoplamiento.py         # E-02
python scripts/prueba_escalera_aurea.py      # E-02 (escalera)
python scripts/chequeo_ajuste_bao.py         # convención rd*h
python scripts/ajuste_cosmologico_alternativas.py   # alternativas (BAO+SNe)
python scripts/smoke_dashboard.py            # 15 secciones del dashboard
```
