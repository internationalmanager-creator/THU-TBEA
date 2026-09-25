# -*- coding: utf-8 -*-
"""E.4a — Cierre FASE E: registrar resultado, actualizar handoff, dejar joint abierto."""
import sys, json, hashlib, time
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
REPO = LAB / "data" / "raw" / "cosmic-birefringence-planck-act"
REG = LAB / "registry" / "thu"
REG.mkdir(parents=True, exist_ok=True)

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

def sha256_file(path, chunk=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

# --- 1: Registrar resultado principal ---
hdr("1. Registrar resultado principal E.3-C8f")

resultado = {
    "fase": "FASE E",
    "fecha_cierre": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "estado": "COMPLETADA",
    "modo": "act_dr6",
    "medicion_beta": {
        "valor_deg": 0.207,
        "sigma_plus_deg": 0.073,
        "sigma_minus_deg": 0.073,
        "metodo": "pipeline Eskilt 2026 (arXiv:2608.06480)",
        "config": {
            "MASK": "act_dr6",
            "SAMPLING_MODE": "all",
            "MCMC_N_STEPS": 3000,
            "MCMC_N_BURN": 500,
            "lmax": 8500,
            "offdiag_cov": False,
            "n_walkers": 12,
            "n_parallel_workers": 2,
        },
        "chi2": 1026.19,
        "dof": 989,
        "chi2_dof": 1.0373,
        "PTE": 0.200,
    },
    "alphas_calibracion": {
        "pa4_f220": {"valor": 0.024, "sigma": 0.090},
        "pa5_f090": {"valor": -0.009, "sigma": 0.073},
        "pa5_f150": {"valor": 0.027, "sigma": 0.072},
        "pa6_f090": {"valor": -0.042, "sigma": 0.078},
        "pa6_f150": {"valor": -0.030, "sigma": 0.075},
    },
    "datasets": {
        "principal": {
            "nombre": "ACT DR6.02 SACC oficial",
            "archivo": "dr6_data.fits",
            "size_mb": 855.31,
            "sha256": "eca996ddb1fc57750299bf5757a40f5d178c1a8b3446d3341a99ca5ba7378e8b",
            "url_origen": "https://lambda.gsfc.nasa.gov/data/act/pspipe/sacc_files/dr6_data.tar.gz",
            "paper_datos": "ACT Collaboration (2025), arXiv:2503.14452",
        },
        "comparacion": {
            "nombre": "Planck PR4 beta_planck_pr4",
            "valor_deg": 0.30,
            "sigma_deg": 0.11,
            "paper": "Diego-Palazuelos et al. (2022), PRL 128, 091302, arXiv:2201.07682",
            "doi": "10.1103/PhysRevLett.128.091302",
        },
    },
    "comparacion_con_THU": {
        "beta_THU_deg": 0.3803,
        "sigma_THU_deg": 0.040,
        "delta_deg": 0.1733,
        "sigma_combinada_deg": 0.0832,
        "tension_sigma": 2.082,
        "umbral_falsacion_sigma": 3.0,
        "veredicto": "TENSION MARGINAL — NO FALSADA (umbral 3 sigma no alcanzado)",
    },
    "reproduccion_del_paper": {
        "beta_paper_deg": 0.215,
        "sigma_paper_deg": 0.074,
        "paper": "Diego-Palazuelos & Komatsu (2025), arXiv:2509.13654",
        "delta_vs_paper_deg": 0.008,
        "delta_vs_paper_sigma": 0.108,
        "comentario": "Pipeline reproducido con exito; diferencia 0.008 deg << sigma",
    },
    "pipeline_modificaciones": [
        "E.3-C7: anadido HDF5Backend para checkpoint/reanudacion",
        "E.3-C7c: pspy import hecho opcional (no disponible sin compilador Fortran)",
        "E.3-C8d: fix bug shapes en mk_chi2 (v_batch[..., None])",
        "E.3-C8d: flush HDF5 cada 100 pasos",
        "E.3-C8e: SQLite tracker (mcmc_runs.sqlite) con snapshots por paso",
    ],
    "artefactos": {
        "chain_hdf5": "data/computed/mcmc_chain.h5",
        "sqlite_tracker": "data/computed/mcmc_runs.sqlite",
        "corner_plot": "plots/act_dr6/act_dr6_*_corner.png",
        "trace_plot": "plots/act_dr6/act_dr6_*_trace.png",
    },
    "trabajo_futuro": {
        "modo_joint_ACT_Planck": {
            "estado": "PENDIENTE",
            "razon": "Requiere mapas NPIPE (~20 GB) + compilador Fortran (pspy). Migracion a maquina con capacidad.",
            "prediccion_paper": {
                "beta_deg": 0.277,
                "sigma_deg": 0.057,
                "tension_estimada_con_THU_sigma": 1.48,
            },
            "documentacion": "data/raw/cosmic-birefringence-planck-act/README.md",
            "requisitos": [
                "Mapas NPIPE A/B splits (PLA o NERSC)",
                "Beams NPIPE (Bl_TEB)",
                "Mascaras Planck + combinada ACT x Planck",
                "Compilador Fortran (gfortran o ifort)",
                "pspy >= 1.8.0",
                "~50 GB disco libre",
            ],
            "instrucciones": [
                "Clonar repo (ya clonado en data/raw/cosmic-birefringence-planck-act)",
                "Descargar mapas NPIPE a paths configurados en tools/data_loading.py",
                "Cambiar config.py: MASK='joint', PP_MASK segun eleccion",
                "Correr spectrum_pipeline/run_pipeline.py",
                "Correr spectrum_pipeline/run_coupling.py",
                "Correr likelihood/run_likelihood.py (genera .npz)",
                "Correr beta_mcmc/run_beta_mcmc.py (HDF5 checkpoint activo)",
            ],
        },
        "escalado_a_70000_pasos": {
            "estado": "OPCIONAL",
            "razon": "3000 pasos ya convergen; sigma actual (0.073) ~ sigma paper (0.074). Escalado mejora autocorrelacion pero no sigma materialmente.",
        },
        "analisis_anisotropo": {
            "estado": "PENDIENTE",
            "razon": "Requiere pipeline alpha_lm + productos de Zagatti et al. (2024).",
            "recursos": "data/raw/pred_alpha_lm/ (extraido)",
        },
    },
    "limitaciones_declaradas": [
        "Covarianza EB-TB block-diagonal (no conjunta); modo joint la mejoraria",
        "Sin marginalizacion de foregrounds Planck NPIPE",
        "Sin correcciones de beam Planck",
        "Analisis isotropo unicamente (no tomografia beta(z))",
        "Tension con THU 2.08 sigma esta por debajo del umbral de falsacion (3 sigma)",
    ],
}

out = REG / "fase_e_cierre.json"
out.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  Guardado: {out}")
print(f"  Tamano: {out.stat().st_size} B")

# --- 2: Actualizar README de FASE E ---
hdr("2. Crear README de FASE E en registry/")

readme = """# FASE E — Validación empírica de birefringencia cósmica

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
"""

readme_path = REG / "fase_e_README.md"
readme_path.write_text(readme, encoding="utf-8")
print(f"  Guardado: {readme_path}")

# --- 3: Certificación consolidada ---
hdr("3. Certificación consolidada de todos los archivos")

cert = {
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "archivos_certificados": [],
}

def add_cert(path, descripcion, url=None):
    if path.exists():
        cert["archivos_certificados"].append({
            "path": str(path.relative_to(LAB)),
            "descripcion": descripcion,
            "sha256": sha256_file(path),
            "size_mb": round(path.stat().st_size / 1024/1024, 3),
            "url_origen": url,
        })

# Datos primarios
add_cert(REPO / "data" / "act_dr6" / "v1.0" / "dr6_data.fits",
         "ACT DR6 SACC oficial",
         "https://lambda.gsfc.nasa.gov/data/act/pspipe/sacc_files/dr6_data.tar.gz")
add_cert(LAB / "data" / "raw" / "act_dr6" / "act_dr6.02_spectra_and_cov_xtra.tar.gz",
         "ACT DR6 spectra_and_cov xtra",
         "https://lambda.gsfc.nasa.gov/data/act/pspipe/spectra_and_cov/")
add_cert(LAB / "data" / "raw" / "act_dr6" / "act_dr6.02_spectra_and_cov_binning_50.tar.gz",
         "ACT DR6 spectra_and_cov binning_50",
         "https://lambda.gsfc.nasa.gov/data/act/pspipe/spectra_and_cov/")
add_cert(LAB / "data" / "raw" / "planck_pr4" / "beta_planck_pr4.csv",
         "Planck PR4 beta isotropico",
         "Diego-Palazuelos 2022, PRL 128, 091302")

# Resultados intermedios
add_cert(LAB / "data" / "intermediate" / "cl_lcdm_planck18.npz",
         "C_l LCDM CAMB (Planck 2018 VI)")
add_cert(LAB / "data" / "inventory" / "resultado_beta_act_dr6_marginalizado.json",
         "Resultado E.3-C2 (analisis marginalizado)")
add_cert(LAB / "data" / "inventory" / "certificacion_act_dr6_sacc.json",
         "Certificacion SACC")

# Resultado final
add_cert(REG / "fase_e_cierre.json", "Cierre FASE E")

cert_path = REG / "fase_e_certificacion.json"
cert_path.write_text(json.dumps(cert, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  Guardado: {cert_path}")
print(f"  Archivos certificados: {len(cert['archivos_certificados'])}")

for item in cert["archivos_certificados"]:
    print(f"    {item['path']:60s}  {item['sha256'][:16]}...  ({item['size_mb']} MB)")

# --- 4: Resumen final ---
hdr("4. Resumen FASE E")

print("  ESTADO: COMPLETADA")
print()
print("  RESULTADO PRINCIPAL:")
print(f"    beta = 0.207 +/- 0.073 deg (ACT DR6, pipeline Eskilt 2026)")
print(f"    Reproduccion del paper: 0.008 deg de diferencia (< sigma)")
print()
print("  COMPARACION vs THU-TBEA 5.0:")
print(f"    beta_THU = 0.3803 +/- 0.040 deg")
print(f"    Tension  = 2.082 sigma")
print(f"    Umbral   = 3.0 sigma")
print(f"    Veredicto: NO FALSADA (tension marginal)")
print()
print("  TRABAJO FUTURO:")
print(f"    - Modo joint (ACT+Planck): migrar a maquina con Fortran")
print(f"    - Prediccion paper: beta = 0.277 +/- 0.057 deg")
print(f"    - Tension estimada: 1.48 sigma")
print()
print(f"  Documentacion:")
print(f"    {REG / 'fase_e_README.md'}")
print(f"    {REG / 'fase_e_cierre.json'}")
print(f"    {REG / 'fase_e_certificacion.json'}")
