"""Analisis exploratorio + verificacion de integridad de cadena.

Aplica metricas basicas sobre el corpus:
    1. Distribucion logaritmica
    2. Ratios consecutivos por grupo
    3. Verificacion de la cadena cronografica

Referencia teorica:
    Para un conjunto {f_i}, la distribucion log10(f_i) revela estructura
    en escala de ordenes de magnitud. El CV de ratios consecutivos mide
    la dispersion relativa:
        CV = std(f_{n+1}/f_n) / mean(f_{n+1}/f_n)
    CV bajo indica organizacion cuantizada, alto indica dispersion.
"""
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "src"))

import numpy as np
import pandas as pd
import db_manager
from tqdm import tqdm


def ratios_consecutivos(freqs):
    freqs = sorted(freqs)
    return np.array([freqs[i+1] / freqs[i] for i in range(len(freqs) - 1)])


def verificar_integridad():
    print("\n" + "=" * 70)
    print("INTEGRIDAD CRIPTOGRAFICA")
    print("=" * 70)
    ok, idx, eid = db_manager.verificar_cadena_eventos()
    if ok:
        n = len(db_manager.listar_eventos())
        print(f"CADENA DE EVENTOS: OK ({n} eventos)")
    else:
        print(f"CADENA DE EVENTOS: ROTA en indice {idx} (id={eid})")


def analisis_distribucion(df):
    print("\n" + "=" * 70)
    print("ANALISIS 1 - DISTRIBUCION LOGARITMICA")
    print("=" * 70)
    logs = np.log10(df["valor_principal"].values)
    print(f"N = {len(logs)}")
    print(f"Rango log10: {logs.min():.2f} a {logs.max():.2f} "
          f"({logs.max()-logs.min():.2f} ordenes)")
    print(f"Media: {logs.mean():.2f} | Mediana: {np.median(logs):.2f} "
          f"| Std: {logs.std():.2f}")


def analisis_ratios(df, grupo_col="categoria"):
    print("\n" + "=" * 70)
    print("ANALISIS 2 - RATIOS CONSECUTIVOS POR GRUPO")
    print("=" * 70)
    grupos = df[grupo_col].unique()
    resultados = []
    with tqdm(total=len(grupos), desc="Grupos", ncols=80) as pbar:
        for g in grupos:
            sub = df[df[grupo_col] == g].sort_values("valor_principal")
            if len(sub) < 3:
                pbar.update(1); continue
            ratios = ratios_consecutivos(sub["valor_principal"].values)
            if len(ratios) < 2:
                pbar.update(1); continue
            media = float(ratios.mean()); std = float(ratios.std())
            cv = std / media if media > 0 else 0
            resultados.append({"grupo": g, "N": len(sub), "media": media,
                                "std": std, "cv": cv})
            pbar.update(1); pbar.set_postfix_str(g[:20])
    if resultados:
        rd = pd.DataFrame(resultados).sort_values("cv")
        print(rd.to_string(index=False))
    return resultados


def main():
    print("ANALISIS EXPLORATORIO PIR v2")
    db_manager.inicializar_db()
    verificar_integridad()
    df = pd.DataFrame(db_manager.listar_entidades())
    print(f"\nCorpus: {len(df)} entidades")
    if df.empty:
        print("Sin datos. Registra entidades primero.")
        return
    analisis_distribucion(df)
    analisis_ratios(df)


if __name__ == "__main__":
    main()