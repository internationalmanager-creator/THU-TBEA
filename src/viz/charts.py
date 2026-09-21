"""Graficos Plotly para el dashboard PIR.

Todas las funciones devuelven una figura Plotly lista para
st.plotly_chart(fig, use_container_width=True).
"""
try:
    from .domains import colors_map
except ImportError:
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).parent.parent))
    from viz.domains import colors_map

import plotly.express as px
import plotly.graph_objects as go

TEMPLATE = "plotly_dark"
BG = "#0E1117"
GRID = "rgba(108,92,231,0.1)"


def _layout(h=400):
    return dict(
        template=TEMPLATE, paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family="Inter", color="#FAFAFA", size=12),
        margin=dict(l=40, r=40, t=40, b=40), height=h,
        xaxis=dict(gridcolor=GRID, zeroline=False),
        yaxis=dict(gridcolor=GRID, zeroline=False),
    )


def atlas(df, t):
    """Scatter log-escala de valores por categoria."""
    if df is None or df.empty:
        return None
    df = df.copy()
    df["cat_label"] = df["categoria"].map(t["domain_names"]).fillna(df["categoria"])
    fig = px.scatter(
        df, x="valor_principal", y="cat_label", color="categoria",
        color_discrete_map=colors_map(),
        hover_data={"id": True, "fuente": True, "origen": True,
                    "estatus": True, "valor_principal": ":.4g"},
    )
    fig.update_traces(marker=dict(size=14, line=dict(width=1.5, color="#FAFAFA")))
    fig.update_xaxes(type="log", gridcolor=GRID)
    fig.update_layout(showlegend=False, **_layout(500))
    return fig


def bar_categorias(df, t):
    """Barra horizontal de conteo por categoria."""
    if df is None or df.empty:
        return None
    counts = df.groupby("categoria").size().reset_index(name="n")
    counts["lbl"] = counts["categoria"].map(t["domain_names"]).fillna(counts["categoria"])
    counts = counts.sort_values("n")
    fig = go.Figure(go.Bar(
        x=counts["n"], y=counts["lbl"], orientation="h",
        marker=dict(color=[colors_map().get(c, "#6C5CE7") for c in counts["categoria"]]),
        text=counts["n"], textposition="outside",
    ))
    fig.update_layout(showlegend=False, **_layout(350))
    return fig


def pie_categorias(df, t):
    """Pastel de distribucion proporcional."""
    if df is None or df.empty:
        return None
    counts = df.groupby("categoria").size().reset_index(name="n")
    counts["lbl"] = counts["categoria"].map(t["domain_names"]).fillna(counts["categoria"])
    fig = go.Figure(go.Pie(
        labels=counts["lbl"], values=counts["n"], hole=0.5,
        marker=dict(colors=[colors_map().get(c, "#6C5CE7") for c in counts["categoria"]]),
    ))
    fig.update_layout(showlegend=False, **_layout(400))
    return fig


def gauge_progreso(completadas, total, t):
    """Gauge de progreso de documentacion."""
    pct = (completadas / total * 100) if total > 0 else 0
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=pct,
        title=dict(text=f"{t['kpi_completed']}: {completadas}/{total}",
                   font=dict(size=14, color="#FAFAFA")),
        number=dict(suffix="%", font=dict(size=42, color="#FAFAFA")),
        gauge=dict(axis=dict(range=[0, 100]),
                   bar=dict(color="#6C5CE7"), bgcolor="#1A1D24",
                   borderwidth=0),
    ))
    fig.update_layout(template=TEMPLATE, paper_bgcolor=BG,
                      font=dict(color="#FAFAFA"), height=280,
                      margin=dict(l=20, r=20, t=50, b=20))
    return fig


def timeline_eventos(df_ev):
    """Scatter temporal de eventos coloreado por tipo."""
    if df_ev is None or df_ev.empty:
        return None
    df = df_ev.copy()
    df["ts"] = df["timestamp_utc"]
    fig = px.scatter(
        df, x="ts", y="tipo", color="tipo",
        hover_data={"entidad_id": True, "descripcion": True,
                    "hash": True, "id": True},
    )
    fig.update_traces(marker=dict(size=12, line=dict(width=1, color="#FAFAFA")))
    fig.update_layout(showlegend=False, **_layout(400))
    return fig


if __name__ == "__main__":
    import pandas as pd
    print("=== Test charts.py ===")
    # DataFrame de prueba
    df = pd.DataFrame([
        {"id": "T-001", "categoria": "test", "valor_principal": 100.0,
         "fuente": "x", "origen": "observado", "estatus": "D", "estado": "completado"},
        {"id": "T-002", "categoria": "test", "valor_principal": 250.0,
         "fuente": "x", "origen": "observado", "estatus": "D", "estado": "completado"},
    ])
    t = {"domain_names": {"test": "Test"}, "kpi_completed": "Documented"}
    df_ev = pd.DataFrame([
        {"id": 1, "timestamp_utc": "2026-09-20T00:00:00Z", "tipo": "test",
         "entidad_id": "T-001", "descripcion": "e1", "hash": "abc", "prev_hash": "GENESIS"},
        {"id": 2, "timestamp_utc": "2026-09-20T00:01:00Z", "tipo": "test",
         "entidad_id": "T-002", "descripcion": "e2", "hash": "def", "prev_hash": "abc"},
    ])

    for fn, args, name in [
        (atlas, (df, t), "atlas"),
        (bar_categorias, (df, t), "bar_categorias"),
        (pie_categorias, (df, t), "pie_categorias"),
        (gauge_progreso, (2, 2, t), "gauge_progreso"),
        (timeline_eventos, (df_ev,), "timeline_eventos"),
    ]:
        fig = fn(*args)
        assert fig is not None, f"{name} devolvio None"
        print(f"  {name:<20} OK ({len(fig.data)} traces)")

    # Casos vacios
    empty = pd.DataFrame()
    for fn, args, name in [
        (atlas, (empty, t), "atlas(vacio)"),
        (bar_categorias, (empty, t), "bar_categorias(vacio)"),
        (pie_categorias, (empty, t), "pie_categorias(vacio)"),
        (timeline_eventos, (empty,), "timeline_eventos(vacio)"),
    ]:
        assert fn(*args) is None, f"{name} deberia devolver None"
        print(f"  {name:<20} OK (None)")

    print("=== TEST OK ===")