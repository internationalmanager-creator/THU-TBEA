"""Graficos Plotly especificos para THU-TBEA.

Devuelve figuras listas para st.plotly_chart(fig, use_container_width=True).
"""
try:
    from .loader import label_color
except ImportError:
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).parent.parent))
    from thu.loader import label_color

import plotly.express as px
import plotly.graph_objects as go

BG = "#0E1117"
GRID = "rgba(108,92,231,0.1)"
TEMPLATE = "plotly_dark"


def _layout(h=420):
    return dict(
        template=TEMPLATE, paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family="Inter", color="#FAFAFA", size=12),
        margin=dict(l=50, r=40, t=50, b=50), height=h,
        xaxis=dict(gridcolor=GRID, zeroline=False),
        yaxis=dict(gridcolor=GRID, zeroline=False),
    )


def problems_bar(problems, t):
    """Barra por etiqueta de problema."""
    if not problems:
        return None
    labels = {}
    for p in problems:
        lab = p["label"]
        labels[lab] = labels.get(lab, 0) + 1
    keys = list(labels.keys())
    vals = [labels[k] for k in keys]
    fig = go.Figure(go.Bar(
        x=keys, y=vals,
        marker_color=[label_color(k) for k in keys],
        text=vals, textposition="outside",
    ))
    fig.update_layout(showlegend=False, **_layout(320))
    return fig


def problems_timeline(problems):
    """Cada problema como punto en el eje A-N coloreado por etiqueta."""
    if not problems:
        return None
    xs = [p["id"] for p in problems]
    ys = ["CERRADO" if p["status"] == "CERRADO" else "ABIERTO" for p in problems]
    colors = [label_color(p["label"]) for p in problems]
    fig = go.Figure(go.Scatter(
        x=xs, y=ys, mode="markers+text",
        marker=dict(size=22, color=colors, line=dict(color="#FAFAFA", width=1.5)),
        text=[p["id"] for p in problems], textposition="middle center",
        textfont=dict(color="#0E1117", size=9, family="Inter"),
        hovertext=[f"{p['id']} — {p['title']}" for p in problems],
        hoverinfo="text",
    ))
    fig.update_layout(showlegend=False, **_layout(280))
    return fig


def versions_timeline(versions):
    """Linea temporal de desplazamientos."""
    vs = versions["versions"]
    if not vs:
        return None
    xs = [v["v"] for v in vs]
    ys = list(range(len(xs)))
    labels = [v["label"] for v in vs]
    colors = [label_color(l) for l in labels]
    titles = [f"{v['v']} ({v['epoch']}): {v['title']}" for v in vs]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="lines+markers",
        line=dict(color="#6C5CE7", width=2),
        marker=dict(size=18, color=colors, line=dict(color="#FAFAFA", width=1.5)),
        text=titles, hoverinfo="text",
    ))
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(showlegend=False, **_layout(320))
    return fig


def epistemic_pie(matrix, t):
    """Distribucion de etiquetas en la matriz epistemica."""
    rows = matrix["rows"]
    if not rows:
        return None
    counts = {}
    for r in rows:
        first = r["label"][0]
        counts[first] = counts.get(first, 0) + 1
    keys = list(counts.keys())
    vals = [counts[k] for k in keys]
    fig = go.Figure(go.Pie(
        labels=keys, values=vals, hole=0.5,
        marker=dict(colors=[label_color(k) for k in keys]),
        textinfo="label+value",
    ))
    fig.update_layout(showlegend=False, **_layout(340))
    return fig


def prisma_funnel(prisma):
    """Embudo PRISMA."""
    flow = prisma["flow"]
    etapas = ["identified", "screened", "eligible", "included"]
    labels = {"identified": "Identificados", "screened": "Cribados",
              "eligible": "Elegibles", "included": "Incluidos"}
    vals = [flow[e] for e in etapas]
    fig = go.Figure(go.Funnel(
        y=[labels[e] for e in etapas], x=vals,
        textinfo="value+percent initial",
        marker=dict(color=["#6C5CE7", "#0984E3", "#FDCB6E", "#00B894"]),
    ))
    fig.update_layout(showlegend=False, **_layout(360))
    return fig


def chi2_breakdown(datasets):
    """Barras de chi2 por dataset."""
    bd = datasets["chi2_breakdown"]
    keys = [k for k in ["BAO", "SNe_PantheonPlus", "CMB_birefringence"] if k in bd]
    vals = [bd.get(k, 0) for k in keys]
    fig = go.Figure(go.Bar(
        x=keys, y=vals, text=vals, textposition="outside",
        marker_color=["#6C5CE7", "#E17055", "#00B894"],
    ))
    fig.update_layout(showlegend=False, **_layout(320))
    return fig


def patches_by_stage(patches):
    """Distribucion de parches por etapa."""
    counts = {}
    for p in patches["patches"]:
        st = p["stage"]
        counts[st] = counts.get(st, 0) + 1
    keys = sorted(counts.keys())
    vals = [counts[k] for k in keys]
    fig = go.Figure(go.Bar(
        x=keys, y=vals, text=vals, textposition="outside",
        marker_color=["#6C5CE7", "#0984E3", "#FDCB6E", "#E17055"][:len(keys)],
    ))
    fig.update_layout(showlegend=False, **_layout(280))
    return fig


if __name__ == "__main__":
    import json
    from pathlib import Path
    print("=== Test charts.py ===")
    THU = Path("registry/thu")
    probs = json.loads((THU / "problems.json").read_text(encoding="utf-8"))["problems"]
    vers = json.loads((THU / "versions.json").read_text(encoding="utf-8"))
    matrix = json.loads((THU / "epistemic_matrix.json").read_text(encoding="utf-8"))
    prisma = json.loads((THU / "prisma.json").read_text(encoding="utf-8"))
    datasets = json.loads((THU / "datasets.json").read_text(encoding="utf-8"))
    patches = json.loads((THU / "patches.json").read_text(encoding="utf-8"))

    t = {"domain_names": {}, "kpi_completed": "x"}

    for fn, args, name in [
        (problems_bar, (probs, t), "problems_bar"),
        (problems_timeline, (probs,), "problems_timeline"),
        (versions_timeline, (vers,), "versions_timeline"),
        (epistemic_pie, (matrix, t), "epistemic_pie"),
        (prisma_funnel, (prisma,), "prisma_funnel"),
        (chi2_breakdown, (datasets,), "chi2_breakdown"),
        (patches_by_stage, (patches,), "patches_by_stage"),
    ]:
        fig = fn(*args)
        assert fig is not None, f"{name} devolvio None"
        print(f"  {name:<22} OK ({len(fig.data)} traces)")

    # Casos vacios
    for fn, args, name in [
        (problems_bar, ([], t), "problems_bar([])"),
        (problems_timeline, ([],), "problems_timeline([])"),
        (versions_timeline, ({"versions": []},), "versions_timeline([])"),
        (epistemic_pie, ({"rows": []}, t), "epistemic_pie([])"),
    ]:
        assert fn(*args) is None, f"{name} deberia devolver None"
        print(f"  {name:<22} OK (None)")

    print("=== TEST OK ===")