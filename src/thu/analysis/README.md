# THU-TBEA Analysis Modules

Modulos de analisis empirico del programa THU-TBEA.

## Pipelines principales

- `run_fase_f2d_w_phi.py` — Ajuste w0-wa CPL sobre DESI DR2 + Pantheon+
- `run_fase_f3_auditoria.py` — Auditoria de 8 mediciones de beta
- `run_fase_f4_cierre.py` — Cierre final + weighted average
- `run_fase_f1_cbl_alpha.py` — Test de CBL alpha en Planck PR4
- `run_fase_p1_oscilaciones.py` — Test de oscilaciones en H(z)
- `run_retiro_p5.py` — Retiro formal de prediccion P5

## Uso

    python src/thu/analysis/run_fase_f2d_w_phi.py

Cada script lee datos de `data/raw/` y escribe resultados a
`data/inventory/fase_*.json`.

## Outputs verificables

Los resultados estan en `data/inventory/`:
- `fase_f1_cbl_alpha.json`
- `fase_f2b_w_phi_desi.json`
- `fase_f2d_w_phi_refinado.json`
- `fase_f3_auditoria_beta.json`
- `fase_f4_cierre_final.json`
- `fase_p1_oscilaciones_hz.json`
- `fase_p5_retiro.json`
