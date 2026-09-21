# Anexos V5.0 — Extension del programa THU-TBEA

> Generado: 2026-09-20T02:16:59Z
> Total: 1 anexos

Los anexos V5.0 son hallazgos surgidos durante el desarrollo del
programa. NO modifican los capitulos 1-21; se anexan como extension
bajo la figura V5.0. Cada uno lleva hash SHA-256 y cadena al cronolog.

---

## V5.0-A001 — Verificacion numerica del residuo del propagador

- **Version:** V5.0
- **Timestamp:** 2026-09-20T02:16:58Z
- **Capitulo de origen:** 4
- **Etiqueta:** [D]
- **SHA-256:** `44a3928b85fbb63ece9b56ee8131fdeb1e4e3ffdbdf9d390b398f3afbd1505ee`

**Hallazgo:**

Se verifica numericamente que el residuo del propagador no local permanece estrictamente positivo para a en [0, 2] y m^2 en [0.5, 2.0]. El minimo se alcanza en a->0 y tiende a 1 - am^2 > 0.

**Impacto epistemico:**

Refuerza el parche 1 de la Etapa VII. El residuo reconstruido es consistente con la unitariedad de la rama principal k=0 de Lambert-W.

**Ecuaciones:**

$$ Res[\Delta] = \frac{e^{-am^2}}{1+am^2} $$

**Referencias:** 6

---
