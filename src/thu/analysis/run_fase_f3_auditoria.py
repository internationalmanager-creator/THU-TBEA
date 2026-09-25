# -*- coding: utf-8 -*-
"""F.3 — Auditoria empirica de beta (Tabla 10.2)."""
import sys, json, time
from pathlib import Path
import numpy as np

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
REG = LAB / "registry" / "thu"
OUT = LAB / "data" / "inventory"
REG.mkdir(parents=True, exist_ok=True)

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# ============================================================
# 1: Definir catalogo de mediciones con estatus de verificacion
# ============================================================
hdr("1. Catalogo de mediciones de beta")

# beta_THU referencia
BETA_THU = 0.3803
SIGMA_THU = 0.040

# Mediciones:
#  - "verificado_disco": tenemos el dato en disco
#  - "verificado_paper": verificado contra paper original
#  - "reportado_pdf": solo tenemos el valor del PDF v5.0
mediciones = [
    {
        "id": "minami_komatsu_2020",
        "paper": "Minami & Komatsu 2020, PRL 125, 221301, arXiv:2011.11254",
        "beta": 0.35,
        "sigma": 0.14,
        "dataset": "Planck PR3",
        "estatus": "reportado_pdf",
        "notas": "Primera deteccion significativa (~2.4 sigma)",
    },
    {
        "id": "eskilt_komatsu_2022",
        "paper": "Eskilt & Komatsu 2022, PRD 106, 063503, arXiv:2205.13962",
        "beta": 0.342,
        "sigma": 0.094,
        "dataset": "Planck PR3 (reanalisis)",
        "estatus": "reportado_pdf",
        "notas": "Refinamiento con correccion de calibracion",
    },
    {
        "id": "diego_palazuelos_2022",
        "paper": "Diego-Palazuelos et al. 2022, PRL 128, 091302, arXiv:2201.07682",
        "beta": 0.30,
        "sigma": 0.11,
        "dataset": "Planck PR4 (NPIPE)",
        "estatus": "verificado_disco",
        "notas": "beta_planck_pr4.csv certificado",
    },
    {
        "id": "ballardini_2025",
        "paper": "Ballardini et al. 2025, JCAP 09, 075",
        "beta": 0.30,
        "sigma": 0.05,
        "dataset": "Planck PR4 + otras",
        "estatus": "reportado_pdf",
        "notas": "Sigma muy pequena - verificar paper (posible distinto dataset)",
    },
    {
        "id": "remazeilles_2025",
        "paper": "Remazeilles 2025, JCAP 12, 013",
        "beta": 0.32,
        "sigma": 0.12,
        "dataset": "Planck ILC",
        "estatus": "reportado_pdf",
        "notas": "Analisis con ILC component separation",
    },
    {
        "id": "act_dr6_2025_paper",
        "paper": "Diego-Palazuelos & Komatsu 2025, arXiv:2509.13654",
        "beta": 0.215,
        "sigma": 0.074,
        "dataset": "ACT DR6",
        "estatus": "verificado_paper",
        "notas": "Valor oficial del paper - replicado en E.3-C8f",
    },
    {
        "id": "planck_pr4_maps_2025",
        "paper": "Scott et al. 2025/2026 (map-space)",
        "beta": 0.46,
        "sigma": 0.07,
        "dataset": "Planck PR4 (map-space)",
        "estatus": "reportado_pdf",
        "notas": "Metodologia map-space - sigma solo estadistico",
    },
    {
        "id": "E3_C8f_thu",
        "paper": "Este analisis (FASE E, E.3-C8f)",
        "beta": 0.207,
        "sigma": 0.073,
        "dataset": "ACT DR6 (SACC oficial)",
        "estatus": "verificado_disco",
        "notas": "Pipeline Eskilt 2026 ejecutado localmente, chi2/dof=1.04",
    },
]

print(f"  Mediciones catalogadas: {len(mediciones)}")
print(f"  Referencia THU: beta = {BETA_THU} +/- {SIGMA_THU}")
print()
print(f"  {'ID':30s}  {'beta':>8s}  {'sigma':>8s}  {'estatus':>18s}")
for m in mediciones:
    print(f"  {m['id']:30s}  {m['beta']:8.4f}  {m['sigma']:8.4f}  {m['estatus']:>18s}")

# ============================================================
# 2: Calcular tension individual vs THU
# ============================================================
hdr("2. Tension individual vs beta_THU = 0.3803 +/- 0.040")

for m in mediciones:
    delta = BETA_THU - m["beta"]
    sigma_comb = np.sqrt(SIGMA_THU**2 + m["sigma"]**2)
    m["delta"] = delta
    m["tension_sigma"] = abs(delta) / sigma_comb
    m["tension_signed"] = delta / sigma_comb

print(f"  {'ID':30s}  {'beta':>8s}  {'sigma':>8s}  {'delta':>9s}  {'tension':>9s}")
for m in mediciones:
    print(f"  {m['id']:30s}  {m['beta']:8.4f}  {m['sigma']:8.4f}  "
          f"{m['delta']:+9.4f}  {m['tension_signed']:+9.4f}")

# ============================================================
# 3: Weighted average (sin correlaciones - advertencia)
# ============================================================
hdr("3. Weighted average (naive, sin correlaciones)")

print("  ADVERTENCIA: mediciones NO independientes (Planck y ACT comparten datos)")
print("  Weighted average es una cota inferior de la tension real")
print()

weights = np.array([1.0/m["sigma"]**2 for m in mediciones])
betas = np.array([m["beta"] for m in mediciones])

w_sum = weights.sum()
beta_wmean = (weights * betas).sum() / w_sum
sigma_wmean = 1.0 / np.sqrt(w_sum)

print(f"  Suma pesos: {w_sum:.2f}")
print(f"  beta_weighted = {beta_wmean:.4f} +/- {sigma_wmean:.4f}")
print(f"  (esto NO es un meta-analisis correcto - solo referencia)")

# Tension del combinado vs THU
delta_w = BETA_THU - beta_wmean
sigma_comb_w = np.sqrt(SIGMA_THU**2 + sigma_wmean**2)
tension_w = abs(delta_w) / sigma_comb_w
print(f"  Tension weighted vs THU: {tension_w:.4f} sigma")

# ============================================================
# 4: Analisis por subgrupos
# ============================================================
hdr("4. Analisis por subgrupo de datos")

# Solo mediciones verificadas en disco
disk_only = [m for m in mediciones if m["estatus"] == "verificado_disco"]
print(f"  Verificadas en disco: {len(disk_only)}")
if disk_only:
    w = np.array([1.0/m["sigma"]**2 for m in disk_only])
    b = np.array([m["beta"] for m in disk_only])
    bm = (w*b).sum() / w.sum()
    sm = 1.0/np.sqrt(w.sum())
    print(f"    beta = {bm:.4f} +/- {sm:.4f}")
    print(f"    Tension vs THU: {abs(BETA_THU - bm)/np.sqrt(SIGMA_THU**2 + sm**2):.4f} sigma")

# Excluyendo el analisis propio (para evitar doble conteo ACT)
paper_only = [m for m in mediciones if m["id"] != "E3_C8f_thu"]
w = np.array([1.0/m["sigma"]**2 for m in paper_only])
b = np.array([m["beta"] for m in paper_only])
bm = (w*b).sum() / w.sum()
sm = 1.0/np.sqrt(w.sum())
print(f"\n  Solo mediciones publicadas (sin E.3-C8f):")
print(f"    beta = {bm:.4f} +/- {sm:.4f}")
print(f"    Tension vs THU: {abs(BETA_THU - bm)/np.sqrt(SIGMA_THU**2 + sm**2):.4f} sigma")

# ACT solo (medicion mas precisa)
act = [m for m in mediciones if "act_dr6" in m["id"]]
if act:
    m = act[0]
    print(f"\n  Solo ACT DR6 (medicion mas precisa):")
    print(f"    beta = {m['beta']} +/- {m['sigma']}")
    print(f"    Tension vs THU: {m['tension_signed']:+.4f} sigma")

# ============================================================
# 5: Cuadro consolidado (formato Tabla 10.2 actualizada)
# ============================================================
hdr("5. Tabla 10.2 actualizada (auditoria F.3)")

print(f"  {'Dataset':32s}  {'beta':>6s}  {'sigma':>6s}  {'Tension':>9s}  {'Estatus':>18s}")
print(f"  {'-'*32}  {'-'*6}  {'-'*6}  {'-'*9}  {'-'*18}")
for m in mediciones:
    print(f"  {m['id']:32s}  {m['beta']:6.3f}  {m['sigma']:6.3f}  "
          f"{m['tension_signed']:+9.3f}  {m['estatus']:>18s}")

# ============================================================
# 6: Veredicto
# ============================================================
hdr("6. Veredicto")

max_tension = max(m["tension_sigma"] for m in mediciones)
max_m = [m for m in mediciones if m["tension_sigma"] == max_tension][0]

print(f"  Medicion con mayor tension: {max_m['id']}")
print(f"    beta = {max_m['beta']} +/- {max_m['sigma']}")
print(f"    Tension con THU: {max_m['tension_signed']:+.4f} sigma")
print()
print(f"  Umbral de falsacion (PDF 11.5): 3 sigma")
print()

if max_tension > 3:
    veredicto = "FALSACION"
    print(f"  VEREDICTO: FALSACION - {max_m['id']} excede 3 sigma")
elif max_tension > 2.5:
    veredicto = "TENSION_ALTA"
    print(f"  VEREDICTO: TENSION ALTA - {max_m['id']} esta cerca de 3 sigma")
elif max_tension > 2:
    veredicto = "TENSION_MODERADA"
    print(f"  VEREDICTO: TENSION MODERADA - bajo 3 sigma")
else:
    veredicto = "COMPATIBLE"
    print(f"  VEREDICTO: COMPATIBLE - maximo {max_tension:.2f} sigma")

print()
print(f"  Weighted average (naive): {beta_wmean:.4f} +/- {sigma_wmean:.4f}")
print(f"  Tension combined: {tension_w:.4f} sigma")

# ============================================================
# 7: Guardar
# ============================================================
hdr("7. Guardar auditoria")

auditoria = {
    "fase": "F.3",
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "beta_thu": {"valor": BETA_THU, "sigma": SIGMA_THU},
    "mediciones": mediciones,
    "weighted_average": {
        "beta": float(beta_wmean),
        "sigma": float(sigma_wmean),
        "tension_vs_THU": float(tension_w),
        "nota": "sin correlaciones - cota inferior",
    },
    "veredicto": veredicto,
    "max_tension": {
        "medicion": max_m["id"],
        "tension_sigma": float(max_m["tension_signed"]),
    },
    "advertencias": [
        "Las mediciones NO son independientes (Planck y ACT comparten datos)",
        "El weighted average es una cota inferior de la tension real",
        "Ballardini 2025 tiene sigma=0.05 (verificar paper)",
        "Planck PR4 map-space tiene sigma solo estadistico",
    ],
}

out = OUT / "fase_f3_auditoria_beta.json"
out.write_text(json.dumps(auditoria, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  Guardado: {out}")

# Tambien copiar a registry
reg_out = REG / "fase_f3_auditoria_beta.json"
reg_out.write_text(json.dumps(auditoria, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  Guardado: {reg_out}")

print()
print("="*72)
print("  FIN F.3")
print("="*72)
