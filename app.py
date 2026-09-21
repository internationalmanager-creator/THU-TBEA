"""PIR Dashboard general (ES/EN/DE).

Ejecutar:
    streamlit run app.py

Secciones:
    1. Inicio       - KPIs y atlas
    2. Atlas        - distribucion log por categoria
    3. Categorias   - bar + pie
    4. Procedencia  - cita, DOI, metodo, hash
    5. Progreso     - gauge de documentacion
    6. Cronologia   - cadena de eventos + verificacion
    7. Metodologia  - marco epistemico, decisiones, log

El dashboard THU-TBEA vive en app_thu.py (separado).
"""
import sys
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE / "src"))

import streamlit as st

from viz.i18n import get_translations, available_languages, language_label
from viz.data_access import (
    get_entidades, get_provenance_by_id, get_provenance_history,
    get_eventos, get_resumen, get_file, verificar_cadena,
)
from viz.styles import inject_css
from viz.charts import (
    atlas, bar_categorias, pie_categorias,
    gauge_progreso, timeline_eventos,
)


st.set_page_config(
    page_title="PIR", page_icon="🔬",
    layout="wide", initial_sidebar_state="expanded",
)


@st.cache_data(ttl=30, show_spinner=False)
def load():
    return {
        "ent": get_entidades(),
        "ev": get_eventos(),
        "res": get_resumen(),
        "log": get_file("registry/epistemic_log.md"),
        "dec": get_file("registry/DECISIONS.md"),
        "hf": get_file("registry/HALLAZGOS_FALSADOS.md"),
        "glos": get_file("registry/GLOSARIO.md"),
    }


def hero(t):
    st.markdown(f"""
    <div class="hero">
        <h1>🔬 {t['title']}</h1>
        <p>{t['subtitle']}</p>
        <p class="tag">{t['tagline']}</p>
    </div>""", unsafe_allow_html=True)


def section(titulo, teoria=None):
    teo = f'<div class="theory">{teoria}</div>' if teoria else ""
    st.markdown(f'<div class="sec"><h2>{titulo}</h2>{teo}</div>',
                unsafe_allow_html=True)


def kpi(label, value, detail=None):
    d = f'<div class="kpi-detail">{detail}</div>' if detail else ""
    st.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>{d}</div>',
        unsafe_allow_html=True,
    )


def render_home(t, data):
    hero(t)
    r = data["res"]
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi(t["kpi_total"], r["total"], t["prog_goal"])
    with c2: kpi(t["kpi_categories"], r["categorias"])
    with c3: kpi(t["kpi_completed"], r["completadas"])
    with c4:
        v = f"{r['rango_ordenes']:.1f}" if r["rango_ordenes"] else "—"
        kpi(t["kpi_orders"], v, "log10 units")
    with c5: kpi(t["kpi_events"], r["eventos"],
                  f"schema v{r['schema_version']}")
    if not data["ent"].empty:
        st.markdown("<br>", unsafe_allow_html=True)
        section(t["atlas_title"], t["atlas_theory"])
        fig = atlas(data["ent"], t)
        if fig:
            st.plotly_chart(fig, width="stretch")


def render_atlas(t, data):
    hero(t)
    section(t["atlas_title"], t["atlas_theory"])
    if data["ent"].empty:
        st.info("No data yet. Registra entidades primero.")
        return
    fig = atlas(data["ent"], t)
    if fig:
        st.plotly_chart(fig, width="stretch")


def render_categorias(t, data):
    hero(t)
    section(t["cat_title"], t["cat_theory"])
    if data["ent"].empty:
        st.info("No data yet.")
        return
    c1, c2 = st.columns([1.3, 1])
    with c1:
        fig = bar_categorias(data["ent"], t)
        if fig:
            st.plotly_chart(fig, width="stretch")
    with c2:
        fig = pie_categorias(data["ent"], t)
        if fig:
            st.plotly_chart(fig, width="stretch")

# === PARTE 2 se agrega a continuacion ===

def render_provenance(t, data):
    hero(t)
    section(t["prov_title"], t["prov_theory"])
    if data["ent"].empty:
        st.info("No data yet.")
        return
    opts = data["ent"]["id"] + " — " + data["ent"]["categoria"]
    sel = st.selectbox(t["prov_select"], opts, index=0)
    eid = sel.split(" — ")[0]
    p = get_provenance_by_id(eid)
    hist = get_provenance_history(eid)
    row = data["ent"][data["ent"]["id"] == eid].iloc[0]

    st.markdown(f"""
    <div class="prov-card">
        <h4>{row['id']} — {row['categoria']}</h4>
        <div style="color:#A0A0A0;font-size:0.85rem;">
            {row['valor_principal']} {row.get('unidad','')}
            · origen: {row['origen']} · [{row['estatus']}]
        </div>
    </div>""", unsafe_allow_html=True)

    if not p:
        st.warning("No provenance")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{t['prov_citation']}**")
        st.markdown(p.get("cita_completa") or "—")
        st.markdown(f"**{t['prov_doi']}**")
        doi = p.get("doi")
        st.markdown(f"[{doi}](https://doi.org/{doi})" if doi else "—")
        st.markdown(f"**{t['prov_method']}**")
        st.markdown(p.get("instrumento") or "—")
    with c2:
        st.markdown(f"**{t['prov_conditions']}**")
        st.markdown(p.get("condiciones") or "—")
        st.markdown(f"**{t['prov_repro']}**")
        st.markdown(p.get("reproducibilidad") or "—")
        st.markdown(f"**{t['prov_version']}**")
        st.markdown(f"v{p.get('version', 1)}")
    st.markdown("---")
    st.markdown(f"**{t['prov_extract']}**")
    st.markdown(f"> {p.get('extracto') or '—'}")

    if hist and len(hist) > 1:
        with st.expander(f"Historial de provenance ({len(hist)} versiones)"):
            for h in hist:
                st.markdown(
                    f"- **v{h['version']}** · `{h['timestamp_utc']}` · "
                    f"hash=`{h['hash_registro'][:16]}...` · "
                    f"prev=`{(h['prev_hash'] or '')[:16]}...`"
                )
                st.caption(f"Cita: {h['cita_completa']}")


def render_progreso(t, data):
    hero(t)
    section(t["prog_title"], t["prog_theory"])
    r = data["res"]
    fig = gauge_progreso(r["completadas"], r["total"] or 1, t)
    st.plotly_chart(fig, width="stretch")


def render_chronolog(t, data):
    hero(t)
    section(t["chrono_title"], t["chrono_theory"])

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button(t["chrono_verify"], width="stretch"):
            with st.spinner("..."):
                ok, idx, eid = verificar_cadena()
            if ok:
                st.markdown(
                    f'<div class="chain-ok">{t["chrono_chain_ok"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chain-bad">'
                    f'{t["chrono_chain_broken"].format(eid=eid)}</div>',
                    unsafe_allow_html=True,
                )
    with c2:
        if st.button(t["chrono_export"], width="stretch"):
            import chronolog
            p = chronolog.exportar()
            st.success(f"→ {p}")

    ev = data["ev"]
    if ev.empty:
        st.info("No events yet.")
        return

    n = st.slider(t["chrono_show"], 5,
                   max(5, min(len(ev), 500)),
                   min(50, len(ev)), step=5)
    ev_show = ev.tail(n)

    fig = timeline_eventos(ev_show)
    if fig:
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")
    cols_ev = [c for c in ["id", "timestamp_utc", "tipo", "entidad_id",
                            "descripcion", "hash"] if c in ev_show.columns]
    st.dataframe(ev_show[cols_ev], width="stretch", height=400)


def render_method(t, data):
    hero(t)
    section(t["method_epistemic"],
            "Marco Lakatosiano con etiquetado [D]/[P]/[F]/[A]")
    st.markdown("""
- **[D] Derived** — follows from mathematics or data
- **[P] Postulated** — ingredient, not derived
- **[F] Frontier** — open problem
- **[A] Analogy** — suggests, does not validate
""")
    section(t["method_lakatos"], "MSRP: hard core, protective belt, heuristics")
    section(t["method_fair"], "Findable · Accessible · Interoperable · Reusable")
    section(t["method_audit"],
            "H(x) = SHA256(x_bytes); chain H_i depends on H_{i-1}")
    section(t["method_privacy"])
    st.warning(t["privacy_text"])

    section("Glosario")
    with st.expander("GLOSARIO.md"):
        st.markdown(data["glos"] or "—")

    section(t["method_decisions"])
    with st.expander("DECISIONS.md"):
        st.markdown(data["dec"] or "—")

    section(t["method_log"])
    with st.expander("epistemic_log.md"):
        st.markdown(data["log"] or "—")

    section("Hallazgos Falsados")
    with st.expander("HALLAZGOS_FALSADOS.md"):
        st.markdown(data["hf"] or "—")


SECTIONS = {
    "home":        ("nav_home",        render_home),
    "atlas":       ("nav_atlas",       render_atlas),
    "categorias":  ("nav_categories",  render_categorias),
    "provenance":  ("nav_provenance",  render_provenance),
    "progress":    ("nav_progress",    render_progreso),
    "chronolog":   ("nav_chronolog",   render_chronolog),
    "method":      ("nav_method",      render_method),
}


def main():
    inject_css()
    data = load()

    if "lang" not in st.session_state:
        st.session_state.lang = "es"
    st.sidebar.selectbox(
        "🌐 Language / Idioma / Sprache",
        available_languages(),
        format_func=language_label,
        key="lang",
    )
    t = get_translations(st.session_state.lang)

    st.sidebar.markdown("---")
    if st.sidebar.button(f"🔄 {t['reload']}", width="stretch"):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.markdown(f"**{t['nav_section']}**")
    if "sec" not in st.session_state:
        st.session_state.sec = "home"

    for sid, (label_key, _) in SECTIONS.items():
        active = st.session_state.sec == sid
        if st.sidebar.button(
            t[label_key],
            key=f"btn_{sid}",
            width="stretch",
            type="primary" if active else "secondary",
        ):
            if not active:
                st.session_state.sec = sid
                st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<small>PIR · CC-BY-4.0<br/>"
        "DOI: <code>pendiente</code><br/>"
        "Repo: <code>privado</code></small>",
        unsafe_allow_html=True,
    )

    _, fn = SECTIONS[st.session_state.sec]
    fn(t, data)

    st.markdown(
        f'<div class="footer">{t["footer"]} · v0.7.0 · '
        f'schema v{data["res"]["schema_version"]}</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()