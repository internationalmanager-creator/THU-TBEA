# FASE E — Validación empírica de birefringencia cósmica

**Estado:** COMPLETADA (2026-09-21)
**Modo:** act_dr6
**Resultado:** β = 0.207° ± 0.073° (tensión 2.08σ vs THU-TBEA 5.0)

## Resumen

La FASE E midió el ángulo de birefringencia cósmica β usando el SACC
oficial de ACT DR6 (855 MB) y el pipeline público de Eskilt 2026
(arXiv:2608.06480). Se reprodujo el resultado del paper a 0.008° de
precisión.

## Datasets certificados

| Dataset | SHA-256 | Fuente |
|---------|---------|--------|
| ACT DR6 SACC dr6_data.fits | eca996dd... | LAMBDA / arXiv:2503.14452 |
| ACT DR6 spectra_and_cov_xtra | ad78ca92... | LAMBDA / arXiv:2503.14452 |
| ACT DR6 spectra_and_cov_binning_50 | c4289c25... | LAMBDA / arXiv:2503.14452 |
| Planck PR4 beta (comparación) | dadb5812... | PRL 128, 091302 |

## Pipeline

- **Eskilt 2026** — https://github.com/LilleJohs/cosmic-birefringence-planck-act
- Modo `act_dr6` con SACC oficial
- Marginalización de 5 alphas de calibración con priors HFI
- Modelo MK (2020) con likelihood de birefringencia

## Resultados

| Parámetro | Valor | Comentario |
|-----------|-------|------------|
| β | 0.207° ± 0.073° | Medición principal |
| χ²/dof | 1.04 | Ajuste excelente |
| PTE | 0.20 | Consistente con LCDM+β |
| β vs paper | 0.008° | Reproducción exitosa |

## Tensión con THU-TBEA 5.0

- β_THU = 0.3803° ± 0.040°
- Tensión = **2.082σ**
- Umbral de falsación (PDF §11.5): 3σ
- Veredicto: **TENSIÓN MARGINAL — NO FALSADA**

## Trabajo futuro

1. **Modo joint (ACT+Planck)** — migrar a máquina con compilador Fortran
2. **Análisis anisótropo** — pipeline alpha_lm disponible en data/raw/pred_alpha_lm/
3. **Escalado a 70000 pasos** — opcional, no cambia σ materialmente
4. **Tomografía β(z)** — pendiente datos de LiteBIRD/SO

## Artefactos reproducibles

- `data/computed/mcmc_chain.h5` — cadena HDF5 (reanudable)
- `data/computed/mcmc_runs.sqlite` — tracker SQLite con snapshots
- `plots/act_dr6/*_corner.png` — triángulo de posteriores
- `plots/act_dr6/*_trace.png` — trazas de convergencia

## Modificaciones al pipeline original

| Patch | Propósito |
|-------|-----------|
| E.3-C7 | HDF5Backend para reanudación |
| E.3-C7c | pspy import opcional |
| E.3-C8d | Fix mk_chi2 + flush HDF5 |
| E.3-C8e | SQLite tracker |
