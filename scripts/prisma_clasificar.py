"""Clasifica las 47 mediciones PRISMA con mapeo manual y deduplicacion."""
import json
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
JSON_FILE = BASE / "registry" / "prisma" / "raw_exports" / "prisma_extraccion_llm.json"
CSV_FILE = BASE / "registry" / "prisma" / "prisma_2026.csv"
RESUMEN_FILE = BASE / "registry" / "prisma" / "prisma_resumen.json"

# Mapeo manual: DOI -> (categoria, razon, grupo_dedup)
# grupo_dedup: si dos papers son el mismo estudio, tienen el mismo grupo
MAPEO_DOIS = {
    # === CATEGORIA A: Primarias independientes ===
    # ACT DR6
    "10.1103/pbc3-t52s": ("A", "ACT DR6 (Diego-Palazuelos & Komatsu 2025)", "act_dr6"),
    "10.48550/arxiv.2509.13654": ("A", "ACT DR6 (arXiv version)", "act_dr6"),
    
    # Planck PR3
    "10.1103/physrevlett.125.221301": ("A", "Planck PR3 (Minami & Komatsu 2020)", "planck_pr3_minami"),
    "10.1103/physrevd.106.063503": ("A", "Planck PR3 (Eskilt & Komatsu 2022)", "planck_pr3_eskilt"),
    
    # Planck PR4 (journal + arXiv del mismo paper = duplicados)
    "10.1103/physrevlett.128.091302": ("A", "Planck PR4 (Diego-Palazuelos 2022)", "planck_pr4_dp"),
    "10.48550/arxiv.2203.04830": ("A", "Planck PR4 (arXiv version)", "planck_pr4_dp"),
    
    # Planck PR4 map-space
    "10.1088/1475-7516/2025/06/025": ("A", "Planck PR4 map-space (Scott 2025)", "planck_pr4_map"),
    
    # Planck LFI
    "10.1051/0004-6361/202243269": ("A", "Planck LFI (frequency-dependent)", "planck_lfi"),
    
    # Planck ILC
    "10.1088/1475-7516/2025/12/013": ("A", "Planck ILC (Remazeilles 2025)", "planck_ilc"),
    
    # Ballardini 2025
    "10.1088/1475-7516/2025/09/075": ("A", "Planck PR4 + otras (Ballardini 2025)", "planck_ballardini"),
    
    # SPT
    "10.1103/physrevd.106.042011": ("A", "SPTpol (primaria)", "spt_pol"),
    "10.1103/physrevd.102.083504": ("A", "SPTpol (primaria)", "spt_pol_2"),
    
    # === CATEGORIA C: Joint y forecasts ===
    "10.48550/arxiv.2608.06480": ("C", "Joint ACT+Planck (Qu 2026)", None),
    "10.1088/1475-7516/2025/07/083": ("C", "LiteBIRD forecast", None),
    "10.48550/arxiv.2609.25202": ("C", "Axiogenesis (teorico)", None),
    "10.48550/arxiv.2608.05296": ("C", "3-form dark energy (teorico)", None),
    "10.1088/1475-7516/2023/11/017": ("C", "Axiverse (teorico)", None),
    "10.1088/1475-7516/2021/04/007": ("C", "ALP domain walls (teorico)", None),
    "10.1088/1475-7516/2023/10/007": ("C", "Model dependence (teorico)", None),
    "10.1103/physrevd.101.123529": ("C", "Hubble tension (teorico)", None),
    "10.1103/physrevd.108.063525": ("C", "Gravitational lensing (teorico)", None),
    "10.1103/physrevlett.127.181103": ("C", "Dark matter domination (teorico)", None),
    "10.1088/1475-7516/2022/08/025": ("C", "Monodromic axion (teorico)", None),
    "10.1103/physrevd.104.l101302": ("C", "Electroweak axion (teorico)", None),
    "10.1103/physrevd.106.103529": ("C", "Primordial parity violation (teorico)", None),
    "10.1088/1475-7516/2022/10/043": ("C", "Domain walls (teorico)", None),
    "10.1088/1475-7516/2022/08/033": ("C", "E-mode polarisation (teorico)", None),
    "10.3847/2041-8213/aea401": ("C", "Differential calibration (metodo)", None),
    "10.5281/zenodo.21392357": ("C", "Prediccion geometrica (teorico)", None),
    "10.5281/zenodo.20172373": ("C", "CPQ theory (teorico)", None),
    
    # === CATEGORIA B: Reanalisis ===
    "10.1103/qgnn-6hsf": ("B", "Reanalisis", None),
    "10.48550/arxiv.2607.02664": ("B", "Radio sources (no CMB)", None),
}

def clasificar(doi):
    doi_clean = doi.replace("https://doi.org/", "").lower()
    if doi_clean in MAPEO_DOIS:
        return MAPEO_DOIS[doi_clean]
    return ("B", "Reanalisis o derivado (sin mapeo especifico)", None)


def main():
    print("=" * 60)
    print("  CLASIFICACION PRISMA CON MAPEO Y DEDUPLICACION")
    print("=" * 60)
    
    with open(JSON_FILE, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    
    con_beta = data.get("con_beta", [])
    sin_beta = data.get("sin_beta", [])
    
    print(f"Con beta: {len(con_beta)}")
    print(f"Sin beta: {len(sin_beta)}")
    
    # Clasificar
    clasificados = []
    for m in con_beta:
        doi = m.get("doi", "?")
        titulo = m.get("titulo", "") or ""
        beta = m.get("beta")
        sigma = m.get("sigma")
        categoria, razon, grupo = clasificar(doi)
        
        clasificados.append({
            "id": doi.replace("https://doi.org/", "").replace("/", "_")[:50],
            "doi": doi.replace("https://doi.org/", ""),
            "titulo": titulo,
            "beta": beta,
            "sigma": sigma,
            "categoria": categoria,
            "razon_clasificacion": razon,
            "grupo_dedup": grupo,
            "incluido_sintesis": "si" if (categoria == "A" and sigma is not None) else "no"
        })
    
    # Deduplicar: si un grupo ya fue incluido, marcar duplicado
    grupos_vistos = set()
    for c in clasificados:
        grupo = c["grupo_dedup"]
        if grupo is not None:
            if grupo in grupos_vistos:
                c["incluido_sintesis"] = "duplicado"
                c["razon_clasificacion"] += " (duplicado de " + grupo + ")"
            else:
                grupos_vistos.add(grupo)
    
    from collections import Counter
    contador = Counter(c["categoria"] for c in clasificados)
    print(f"\nCategorias:")
    for cat in ["A", "B", "C"]:
        print(f"  {cat}: {contador.get(cat, 0)}")
    
    # Contar incluidos (A sin duplicar y con sigma)
    incluidos = sum(1 for c in clasificados if c["incluido_sintesis"] == "si")
    print(f"\nIncluidos en sintesis (A, con sigma, sin duplicar): {incluidos}")
    
    # Escribir CSV
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "id", "doi", "titulo", "beta", "sigma", "categoria", "razon_clasificacion", "grupo_dedup", "incluido_sintesis"
        ])
        writer.writeheader()
        writer.writerows(clasificados)
    
    print(f"\nGuardado CSV: {CSV_FILE}")
    
    resumen = {
        "fecha": "2026-10-27",
        "fuente": "OpenAlex API + DeepSeek Harness",
        "flujo": {
            "identificados": 845,
            "candidatos": 253,
            "con_beta": len(con_beta),
            "sin_beta": len(sin_beta)
        },
        "clasificacion": {
            "A_primarias": contador.get("A", 0),
            "B_reanalisis": contador.get("B", 0),
            "C_combinaciones": contador.get("C", 0),
            "incluidos_sintesis": incluidos
        },
        "mediciones": clasificados
    }
    
    with open(RESUMEN_FILE, "w", encoding="utf-8") as fh:
        json.dump(resumen, fh, indent=2, ensure_ascii=False)
    
    print(f"Guardado resumen: {RESUMEN_FILE}")
    
    print(f"\n=== MEDICIONES INCLUIDAS EN SINTESIS ===")
    for c in clasificados:
        if c["incluido_sintesis"] == "si":
            print(f"  {c['doi']} | beta={c['beta']} | sigma={c['sigma']} | {c['razon_clasificacion']}")


if __name__ == "__main__":
    main()