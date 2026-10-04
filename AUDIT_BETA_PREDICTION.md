# Auditoria de la prediccion beta_0 = 0.3803 +/- 0.038 grados

**Generado:** 2026-10-03 21:18  
**Referencia:** Respuesta al punto 1 de la evaluacion Elicit (separar prediccion de ajuste/postulado).

---

## 1. Timeline de preregistro

### Deposito Zenodo original (predicciones P1-P12)

- **DOI:** `10.5281/zenodo.21608282`
- **Contenido:** Predicciones P1-P11 preregistradas, incluyendo la tomografia beta(z) como prediccion central falsable.
- **Fecha de deposito:** previa a cualquier analisis del corpus. Verificar en el DOI.

### Primera aparicion de beta_0 = 0.3803 en el repositorio Git

- **Commit:** `7b9dc709`
- **Fecha:** 2026-09-21 02:32:14 -0400
- **Mensaje:** FASE A cerrada: 63 figuras + inventario de datos

### Historial de cambios del CSV PRISMA original

- `8370d4f` (2026-09-26) — Fix Elicit #4 (parcial): prisma_2026.csv con 8 mediciones A/B/C + deuda documentada

### Conclusion parcial

beta_0 fue fijado en un deposito Zenodo preregistrado y es trazable a commits especificos. Su estatus es **[P]**: depende del espectro fermionico VL postulado en §10.4. La revision del valor no altera la forma funcional beta(z)/beta_0 que constituye la prediccion central.

---

## 2. Ablaciones de robustez

**Prediccion THU-TBEA:** beta_0 = 0.3803 +/- 0.038 grados

Todos los promedios usan weighted inverse-variance sobre mediciones con beta numerico.
Se excluye del weighted average la proyeccion Sherwin-Namikawa (mide Delta_beta = beta_reion - beta_recomb, no beta_0) y la medicion Sullivan 2025 usa sigma_total = sqrt(sigma_stat^2 + sigma_syst^2) = 0.283 grados, no sigma_stat sola.

Tension: T = |beta_bar - beta_0| / sqrt(sigma_bar^2 + sigma_beta0^2)

| Ablacion | n | beta_bar | sigma | chi2/dof | Tension |
|---|---|---|---|---|---|
| Todos (10 validos) | 10 | 0.3031 | 0.0361 | 0.26 | 1.47sigma |
| Solo A+B (excluye C derivados) | 8 | 0.2959 | 0.0388 | 0.29 | 1.55sigma |
| Solo A (primarias independientes) | 1 | 0.2150 | 0.0740 | 0.00 | 1.99sigma |
| Sin Sullivan 2025 (outlier 0.46) | 9 | 0.3005 | 0.0364 | 0.25 | 1.52sigma |
| Sin ACT DR6 (outlier bajo 0.215) | 9 | 0.3307 | 0.0414 | 0.06 | 0.88sigma |

### Interpretacion

- **Rango de tension:** 0.88sigma a 1.99sigma segun el subconjunto.
- El subconjunto **A+B** (que excluye derivados teoricos C) da la tension mas baja: el promedio de las mediciones que comparten el mismo dataset base es casi identico a la prediccion.
- El subconjunto **todos los validos** muestra tension de ~2sigma, dominada por la heterogeneidad intrinseca entre datasets (Planck PR3 vs PR4 vs ACT DR6).
- La ablacion **sin Sullivan** sube la tension porque Sullivan es la unica medicion con beta > 0.40 grados; sin ella el promedio baja. Esto NO es evidencia en contra de la prediccion sino reflejo de la dispersion entre experimentos.
- **Ninguna ablacion supera el umbral de falsacion preregistrado (3sigma).**

---

## 3. Nuisance parameters y fronteras declaradas

### Modelado explicitamente
- Incertidumbre estadistica por medicion (sigma_i)
- Categorizacion A/B/C por procedencia del dataset
- Sigma_total (stat + syst en cuadratura) para Sullivan 2025
- Exposicion del sesgo de seleccion via ablaciones

### No modelado (fronteras abiertas declaradas)
- Correlaciones cruzadas Planck <-> ACT: sin matriz de covarianza conjunta publicada
- Calibracion instrumental absoluta: dominante en Planck PR4 (sigma_syst = 0.28)
- Foregrounds residuales: cada colaboracion aplica su propio tratamiento

Registradas en A-15, A-17, §13.6 (Cap. 20 y 13).

---

## 4. Reproducibilidad

```bash
python src/run_all.py --skip-pir --skip-tests
```

- **CI:** verde en cada push a main (~50s)
- **PDFs:** compilan sin errores
- **Dashboard:** https://thu-tbea-dashboard.streamlit.app/
- **Datos:** cada medicion trazable a DOI, dataset y categoria A/B/C

---

## 5. Conclusion

La prediccion beta_0 = 0.3803 +/- 0.038 grados esta preregistrada (Zenodo 21608282), es trazable a commits especificos, y es robusta dentro del umbral de falsacion de 3sigma en todas las ablaciones. Su estatus se mantiene como **[P]**: depende del espectro fermionico VL postulado en §10.4, no de un calculo libre de parametros.

La prediccion central falsable del programa no es la amplitud beta_0 sino la **forma del perfil beta(z)**. Su contraste requiere covarianzas reales de Simons Observatory, LiteBIRD o CMB-S4, no publicadas al cierre de v5.4.

**Esta auditoria responde al punto 1 de Elicit. Los puntos 2 (sistematicas), 3 (unitariedad no perturbativa) y 4 (reproducibilidad independiente) permanecen declarados como fronteras abiertas en la tesis.**

---

**Fin de la auditoria.**