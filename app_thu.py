"""THU-TBEA 5.4 — Dashboard Streamlit dedicado.

Ejecutar:
    streamlit run app_thu.py

13 secciones navegables:
    1. Vision general      KPIs + ecuaciones + jerarquia + estado Lakatos
    2. Problemas A-1..A-17
    3. Predicciones P1-P11
    4. Parches (Etapas VII-X)
    5. Bitacora Lakatosiana 1.0 -> 5.3
    6. Matriz epistemica (27 filas)
    7. Glosario (37 simbolos)
    8. Referencias (68)
    9. Revision PRISMA (284 -> 38)
    10. Datasets + pipeline
    11. Estructura de la tesis (21 caps + 10 ap.)
    12. Anexos V5.0 (dinamicos)
    13. Compilar y descargar (LaTeX -> PDF)
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE / "src"))

import streamlit as st

from thu import loader as L
from thu import i18n_thu as I
from thu import charts as C
from thu import style as S

ANNEXES_FILE = BASE / "registry" / "thu" / "annexes.json"
DIST_DIR = BASE / "paper" / "thu" / "dist"
SRC_DIR = BASE / "paper" / "thu" / "src"

st.set_page_config(page_title="THU-TBEA 5.4", page_icon="🌀",
                   layout="wide", initial_sidebar_state="expanded")

# ============================================================
# Helpers
# ============================================================

def hero(t):
    st.markdown(
        f'<div class="thu-hero">'
        f'<h1>🌀 {t["title"]}</h1>'
        f'<p>{t["subtitle"]}</p>'
        f'<p class="tag">{t["tagline"]}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

def section(title, theory=None):
    teo = f'<div class="theory">{theory}</div>' if theory else ""
    st.markdown(f'<div class="thu-sec"><h2>{title}</h2>{teo}</div>',
                unsafe_allow_html=True)

def kpi(label, value, detail=None):
    d = f'<div class="thu-kpi-detail">{detail}</div>' if detail else ""
    st.markdown(
        f'<div class="thu-kpi"><div class="thu-kpi-label">{label}</div>'
        f'<div class="thu-kpi-value">{value}</div>{d}</div>',
        unsafe_allow_html=True,
    )

def eq(latex):
    r"""Renderiza una ecuacion con st.latex nativo.
    Acepta \[...\], $$...$$, $...$ o LaTeX puro sin delimitadores.
    """
    s = latex.strip()
    # Prefijos: 2 backslash (raw), 1 backslash (del LaTeX), $$, $
    for pre in ("\\\\[", "\\[", "$$", "$"):
        if s.startswith(pre):
            s = s[len(pre):].strip()
            break
    for suf in ("\\\\]", "\\]", "$$", "$"):
        if s.endswith(suf):
            s = s[:-len(suf)].strip()
            break
    st.latex(s)

def badge(label):
    return S.badge(label)

# ============================================================
# Seccion 1: Overview
# ============================================================

def render_overview(t):
    hero(t)
    s = L.stats()
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: kpi(t["kpi_version"], s["version"], "family 4.3 -> 5.4")
    with c2: kpi(t["kpi_closed"], s["problems_closed"], f"de {s['problems_total']}")
    with c3: kpi(t["kpi_open"], s["problems_open"], "[F] y [A]")
    with c4: kpi(t["kpi_predictions"], s["predictions"], f"{s['preds_prereg']} pre-reg")
    with c5: kpi(t["kpi_refs"], s["refs"], f"{s['chapters']} caps + {s['appendices']} ap.")
    with c6: kpi(t["kpi_patches"], s["patches"], "4 etapas")

    st.markdown("<br>", unsafe_allow_html=True)
    section("Ecuaciones centrales", "Formalizacion del nucleo geometrico (v5.3)")
    cA, cB = st.columns(2)
    with cA:
        st.markdown("**Torsion axial de Palatini**")
        eq(r"\[ T_{\lambda\mu\nu} = \frac{1}{M_P}\varepsilon_{\lambda\mu\nu\rho}\nabla^{\rho}\tau \]")
        st.markdown("**Redefinicion canonica**")
        eq(r"\[ \tau_c \equiv \sqrt{3}\,\tau \;\Longrightarrow\; +\tfrac{1}{2}(\nabla\tau_c)^2 \]")
    with cB:
        st.markdown("**Punto fijo aureo**")
        eq(r"\[ \beta_{\text{eff}}(g) = \kappa(1+g-g^2), \quad g_\star = \varphi \]")
        st.markdown("**Residuo del propagador no local**")
        eq(r"\[ \mathrm{Res}[\Delta] = \frac{e^{-am^2}}{1+am^2} > 0 \]")

    st.markdown("---")
    section("Jerarquia THU-TBEA", "Del nucleo geometrico a la fenomenologia")
    st.markdown(
        "```\n"
        "U4  ->  M6 = CY3 (h^{1,1}=22)  ->  n_eff = 4 x 22 = 88\n"
        "           |\n"
        "Lambda_THU = M_P * phi^{-88}  ~  989.89 MeV\n"
        "           |\n"
        "beta(z) tomografia  |  m_n  |  P1-P11\n"
        "```"
    )

    st.markdown("---")
    section("Estado del programa (Lakatos MSRP)",
            "Cada version se evalua por su capacidad predictiva nueva")
    probs = L.problems()["problems"]
    cL, cR = st.columns(2)
    with cL:
        fig = C.problems_timeline(probs)
        if fig: st.plotly_chart(fig, use_container_width=True)
    with cR:
        fig = C.problems_bar(probs, t)
        if fig: st.plotly_chart(fig, use_container_width=True)

# ============================================================
# Seccion 2: Problems
# ============================================================

def render_problems(t):
    hero(t)
    section(t["problems_title"], t["problems_theory"])
    probs = L.problems()["problems"]

    filt = st.radio(
        "Filtro",
        ["Todos", "Solo cerrados [D]", "Solo abiertos [F]/[A]"],
        horizontal=True, label_visibility="collapsed",
    )
    if filt == "Solo cerrados [D]":
        probs = [p for p in probs if p["status"] == "CERRADO"]
    elif filt == "Solo abiertos [F]/[A]":
        probs = [p for p in probs if p["status"] == "ABIERTO"]

    for p in probs:
        color = L.label_color(p["label"])
        st.markdown(
            f'<div class="thu-card" style="border-left-color:{color};">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<div>'
            f'<span style="color:#A0A0A0;font-size:0.85rem;">{p["id"]}</span>'
            f'&nbsp;<strong style="color:#FAFAFA;font-size:1.05rem;">{p["title"]}</strong>'
            f'</div>'
            f'<div>{badge(p["label"])}</div>'
            f'</div>'
            f'<div style="color:#A0A0A0;font-size:0.88rem;margin-top:8px;">'
            f'{p["justification"]}</div>'
            f'<div style="color:#636E72;font-size:0.78rem;margin-top:6px;">'
            f'{t["chapter"]} {p["chapter"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ============================================================
# Seccion 3: Predictions
# ============================================================

def render_predictions(t):
    hero(t)
    section(t["preds_title"], t["preds_theory"])
    preds = L.predictions()["predictions"]

    rows = []
    for p in preds:
        rows.append({
            "ID": p["id"],
            t["observable"]: p["observable"],
            t["arbiter"]: p["arbiter"],
            t["falsif"]: p["falsification"],
            t["status"]: p["status"],
            t["chapter"]: p.get("chapter", "—"),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Detalles con valor pre-registrado")
    con_valor = [p for p in preds if any(k.startswith("value_") for k in p)]
    if not con_valor:
        st.info("Ninguna prediccion tiene valor numerico pre-registrado en esta version.")
    for p in con_valor:
        st.markdown(f"**{p['id']}** — {p['observable']}")
        for k, v in p.items():
            if k.startswith("value_"):
                st.markdown(f"- `{k}` = `{v}`")

# === PARTE 2 se agrega a continuacion ===

# ============================================================
# Seccion 4: Patches
# ============================================================

def render_patches(t):
    hero(t)
    section(t["patches_title"], t["patches_theory"])
    data = L.patches()
    fig = C.patches_by_stage(data)
    if fig: st.plotly_chart(fig, use_container_width=True)

    stages = data["stages"]
    stage_names = {k: f"Etapa {k} — {v['label']}" for k, v in stages.items()}
    sel = st.selectbox("Etapa", list(stages.keys()),
                       format_func=lambda k: stage_names[k])
    for p in data["patches"]:
        if p["stage"] != sel:
            continue
        st.markdown(
            f'<div class="thu-card">'
            f'<div style="display:flex;justify-content:space-between;">'
            f'<strong>Patch {p["n"]} — {p["location"]}</strong>'
            f'{badge(p["label"])}'
            f'</div>'
            f'<div style="margin-top:8px;">'
            f'<span style="color:#E17055;">x {t["before"]}:</span> '
            f'<code style="color:#E17055;">{p["before"]}</code></div>'
            f'<div style="margin-top:4px;">'
            f'<span style="color:#00B894;">v {t["after"]}:</span> '
            f'<code style="color:#00B894;">{p["after"]}</code></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ============================================================
# Seccion 5: Versions
# ============================================================

def render_versions(t):
    hero(t)
    section(t["versions_title"], t["versions_theory"])
    data = L.versions()
    fig = C.versions_timeline(data)
    if fig: st.plotly_chart(fig, use_container_width=True)
    for v in data["versions"]:
        st.markdown(
            f'<div class="thu-card">'
            f'<div style="display:flex;justify-content:space-between;">'
            f'<strong>v{v["v"]} — {v["epoch"]}</strong>{badge(v["label"])}'
            f'</div>'
            f'<div style="color:#A0A0A0;font-size:0.9rem;margin-top:6px;">'
            f'{v["title"]}</div>'
            f'<div style="color:#636E72;font-size:0.78rem;margin-top:4px;">'
            f'tipo: {v["type"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ============================================================
# Seccion 6: Epistemic matrix
# ============================================================

def render_epistemic(t):
    hero(t)
    section(t["epistemic_title"], t["epistemic_theory"])
    data = L.epistemic_matrix()
    c1, c2 = st.columns([2, 1])
    with c1:
        rows = [{"Claim": r["claim"], "Label": r["label"],
                 "Chapter": r["chapter"]} for r in data["rows"]]
        st.dataframe(rows, use_container_width=True, hide_index=True)
    with c2:
        fig = C.epistemic_pie(data, t)
        if fig: st.plotly_chart(fig, use_container_width=True)

# ============================================================
# Seccion 7: Glossary
# ============================================================

def render_glossary(t):
    hero(t)
    section(t["glossary_title"])
    data = L.glossary()

    for grupo in ("geometry", "constants", "observables"):
        if grupo not in data:
            continue
        st.markdown(f"#### {grupo.title()}")
        # Header
        h1, h2, h3, h4, h5 = st.columns([2, 3, 1, 1, 2])
        with h1: st.markdown("**Simbolo**")
        with h2: st.markdown("**Significado**")
        with h3: st.markdown("**Dim.**")
        with h4: st.markdown("**Def.**")
        with h5: st.markdown("**Valor**")
        st.markdown("---")
        for r in data[grupo]:
            c1, c2, c3, c4, c5 = st.columns([2, 3, 1, 1, 2])
            with c1:
                # Usar sym_latex si existe, sino sym envuelto en $
                latex = r.get("sym_latex") or ("$" + str(r.get("sym", "")) + "$")
                st.markdown(latex)
            with c2: st.markdown(str(r.get("meaning", "—")))
            with c3: st.markdown(str(r.get("dim", "—")))
            with c4: st.markdown(str(r.get("def", "—")))
            with c5: st.markdown(str(r.get("value", "—")))
        st.markdown("")



def render_refs(t):
    hero(t)
    section(t["refs_title"])
    data = L.references()

    # Merge con doi_registry.json
    doi_by_key = {}
    try:
        import json as _json
        from pathlib import Path as _P
        dr_path = _P(__file__).parent / "registry" / "thu" / "doi_registry.json"
        if dr_path.exists():
            dr = _json.loads(dr_path.read_text(encoding="utf-8"))
            for e in dr.get("entries", []):
                k = e.get("key") or e.get("bibkey") or ""
                d = e.get("doi") or ""
                if k and d:
                    doi_by_key[k] = d
    except Exception as _e:
        pass

    refs = data["refs"]
    tags = sorted({r.get("tag", "otros") for r in refs})
    sel = st.multiselect("Filtrar por tag", tags, default=[])
    if sel:
        refs = [r for r in refs if r.get("tag") in sel]

    # Contar con/sin DOI
    n_con_doi = sum(1 for r in refs if r.get("doi") or doi_by_key.get(r.get("key", "")))
    n_sin_doi = len(refs) - n_con_doi
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total", len(refs))
    with c2: st.metric("Con DOI", n_con_doi)
    with c3: st.metric("Sin DOI", n_sin_doi)

    rows = []
    for r in refs:
        key = r.get("key") or r.get("bibkey") or ""
        doi = r.get("doi") or doi_by_key.get(key, "")
        rows.append({
            "#": r["n"],
            t["authors"]: r["authors"],
            t["year"]: r.get("year", "—"),
            t["journal"]: r.get("journal") or r.get("title", ""),
            "Tag": r.get("tag", ""),
            "DOI": doi if doi else "—",
        })
    st.dataframe(rows, use_container_width=True, hide_index=True, height=600)



def render_prisma(t):
    hero(t)
    section(t["prisma_title"], t["prisma_theory"])
    data = L.prisma()
    c1, c2 = st.columns([1, 1])
    with c1:
        fig = C.prisma_funnel(data)
        if fig: st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("**PICO**")
        for k, v in data["question_pico"].items():
            st.markdown(f"- **{k}**: {v}")
        st.markdown("**Bases**")
        for b in data["search"]["bases"]:
            st.markdown(f"- {b}")
        st.markdown(f"**Periodo**: {data['search']['period'][0]} – {data['search']['period'][1]}")

# ============================================================
# Seccion 10: Datasets
# ============================================================

def render_datasets(t):
    hero(t)
    section(t["datasets_title"], t["datasets_theory"])
    data = L.datasets()
    rows = [{"Dataset": d["name"], "Tipo": d["type"],
             "SHA-256 (trunc)": d["sha256_trunc"],
             "Ano": d["year"], "Ref": f"[{d['ref']}]",
             "N": d["n"]} for d in data["datasets"]]
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.markdown(f"**Semilla global**: `{data['seed_global']}`")
    st.markdown("**Modulos del pipeline**")
    for m in data["pipeline_modules"]:
        st.markdown(f"- `{m}`")

    fig = C.chi2_breakdown(data)
    if fig: st.plotly_chart(fig, use_container_width=True)
    if data["chi2_breakdown"].get("warning"):
        st.warning(data["chi2_breakdown"]["warning"])

# ============================================================
# Seccion 11: Sections (estructura)
# ============================================================

def render_sections(t):
    hero(t)
    section(t["sections_title"])
    data = L.sections()
    st.markdown("### Capitulos")
    rows = [{"Cap.": c["n"], "Titulo": c["title"],
             "Parte": c["part"],
             "Paginas": f"{c['pages'][0]}-{c['pages'][-1]}"}
            for c in data["chapters"]]
    st.dataframe(rows, use_container_width=True, hide_index=True, height=400)
    st.markdown("### Apendices")
    rows = [{"Letra": a["letter"], "Titulo": a["title"],
             "Paginas": f"{a['pages'][0]}-{a['pages'][-1]}"}
            for a in data["appendices"]]
    st.dataframe(rows, use_container_width=True, hide_index=True)

# === PARTE 3 se agrega a continuacion ===

# ============================================================
# Seccion 12: Anexos V5.0
# ============================================================

def _kpi_simple(label, value):
    st.markdown(
        f'<div class="thu-kpi"><div class="thu-kpi-label">{label}</div>'
        f'<div class="thu-kpi-value">{value}</div></div>',
        unsafe_allow_html=True,
    )

def render_annexes(t):
    hero(t)
    section(t["annexes_title"], t["annexes_theory"])

    try:
        data = json.loads(ANNEXES_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        st.error(f"No se puede leer annexes.json: {e}")
        return

    anexos = data.get("annexes", [])
    c1, c2, c3, c4 = st.columns(4)
    with c1: _kpi_simple("Total anexos", len(anexos))
    with c2: _kpi_simple("[D] derivados", sum(1 for a in anexos if a["label"] == "D"))
    with c3: _kpi_simple("[P] postulados", sum(1 for a in anexos if a["label"] == "P"))
    with c4: _kpi_simple("[F]/[A]", sum(1 for a in anexos if a["label"] in ("F", "A")))

    st.markdown("---")
    if not anexos:
        st.info("No hay anexos registrados todavia. "
                "Usa `python src/thu/annex.py nuevo --titulo ...` "
                "o el formulario de abajo.")
    else:
        for a in anexos:
            color = L.label_color(a["label"])
            st.markdown(
                f'<div class="thu-card" style="border-left-color:{color};">'
                f'<div style="display:flex;justify-content:space-between;">'
                f'<div><span style="color:#A0A0A0;font-size:0.82rem;">'
                f'{a["id"]} · V5.0</span>&nbsp;<strong>{a["titulo"]}</strong></div>'
                f'<div>{S.badge(a["label"])}</div></div>'
                f'<div style="color:#636E72;font-size:0.78rem;margin-top:4px;">'
                f'{a["timestamp_utc"]} · cap. {a["capitulo_origen"]} · '
                f'sha256 <code>{a["sha256"][:16]}...</code></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            with st.expander("Ver detalle"):
                st.markdown("**Hallazgo**")
                st.markdown(a["hallazgo"])
                st.markdown("**Impacto epistemico**")
                st.markdown(a["impacto_epistemico"])
                if a.get("ecuaciones"):
                    st.markdown("**Ecuaciones**")
                    for e in a["ecuaciones"]:
                        st.latex(e)

    st.markdown("---")
    with st.expander("Anadir nuevo anexo V5.0"):
        st.markdown(
            "Formulario rapido. Para control total:\n\n"
            "```\npython src/thu/annex.py nuevo --titulo \"...\" "
            "--capitulo \"12\" --label D --hallazgo \"...\" --impacto \"...\"\n```"
        )
        with st.form("form_anexo"):
            titulo = st.text_input("Titulo del anexo")
            capitulo = st.text_input("Capitulo de origen (o 'nuevo')", value="12")
            label = st.selectbox("Etiqueta epistemica", ["D", "P", "F", "A"])
            hallazgo = st.text_area("Hallazgo", height=120)
            impacto = st.text_area("Impacto epistemico", height=80)
            ecuacion = st.text_area("Ecuacion LaTeX (opcional, sin $)", height=60)
            submit = st.form_submit_button("Registrar anexo", type="primary")

            if submit:
                if not titulo or not hallazgo or not impacto:
                    st.error("Titulo, hallazgo e impacto son obligatorios.")
                else:
                    try:
                        from thu import annex as A
                        ecuaciones = [ecuacion.strip()] if ecuacion.strip() else None
                        a = A.nuevo(titulo, capitulo, label, hallazgo,
                                     impacto, ecuaciones=ecuaciones)
                        st.success(f"Creado {a['id']} — hash {a['sha256'][:16]}...")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# ============================================================
# Seccion 13: Compilar y descargar
# ============================================================

def render_downloads(t):
    hero(t)
    section(t["downloads_title"], t["downloads_theory"])

    from thu import latex_compile, latex_builder

    diag = latex_compile.doctor()
    c1, c2, c3 = st.columns(3)
    with c1: _kpi_simple("Motor LaTeX", diag["motor"] or "NO DISPONIBLE")
    with c2: _kpi_simple("Archivos .tex", len(diag["tex_files"]))
    with c3: _kpi_simple("PDFs generados", len(diag["pdfs_generados"]))

    if not diag["motor"]:
        st.error("**No hay motor LaTeX instalado.**")
        for k, v in diag["instalar"].items():
            st.markdown(f"- **{k}**: `{v}`")

    st.markdown("---")
    # === Abrir PDFs generados (D-38) ===
    dist = BASE / "paper" / "thu" / "dist"
    if dist.exists():
        st.markdown("### 0. PDFs disponibles")
        for lang_code, lang_name in [("es","Espanol"), ("en","English"), ("de","Deutsch")]:
            pdf = dist / f"tesis_{lang_code}.pdf"
            if pdf.exists():
                mb = round(pdf.stat().st_size / (1024*1024), 2)
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{lang_name}** - `{pdf.name}` ({mb} MB)")
                with c2:
                    with open(pdf, "rb") as fh:
                        st.download_button(
                            f"Descargar {lang_code.upper()}",
                            data=fh.read(),
                            file_name=pdf.name,
                            mime="application/pdf",
                            key=f"dl_{lang_code}"
                        )
        st.markdown("---")

    st.markdown("### 1. Generar archivos LaTeX (.tex)")
    cA, cB, cC, cD = st.columns(4)
    with cA:
        if st.button("Generar ES", use_container_width=True):
            p = latex_builder.build("es")
            st.success(f"-> {p.name} ({p.stat().st_size} B)")
    with cB:
        if st.button("Generar EN", use_container_width=True):
            p = latex_builder.build("en")
            st.success(f"-> {p.name} ({p.stat().st_size} B)")
    with cC:
        if st.button("Generar DE", use_container_width=True):
            p = latex_builder.build("de")
            st.success(f"-> {p.name} ({p.stat().st_size} B)")
    with cD:
        if st.button("Generar todo", use_container_width=True, type="primary"):
            paths = latex_builder.build_all()
            st.success(f"Generados {len(paths)} .tex")

    st.markdown("---")
    st.markdown("### 2. Compilar a PDF")
    cA, cB, cC, cD = st.columns(4)
    disabled = not diag["motor"]
    with cA:
        if st.button("Compilar ES", use_container_width=True, disabled=disabled):
            r = latex_compile.compilar("es", force=True)
            st.success(r["pdf"] if r["status"] == "OK" else r["razon"])
    with cB:
        if st.button("Compilar EN", use_container_width=True, disabled=disabled):
            r = latex_compile.compilar("en", force=True)
            st.success(r["pdf"] if r["status"] == "OK" else r["razon"])
    with cC:
        if st.button("Compilar DE", use_container_width=True, disabled=disabled):
            r = latex_compile.compilar("de", force=True)
            st.success(r["pdf"] if r["status"] == "OK" else r["razon"])
    with cD:
        if st.button("Compilar todo", use_container_width=True, type="primary",
                     disabled=disabled):
            rs = latex_compile.compilar_all(force=True)
            for r in rs:
                st.write(f"[{r['lang']}] {r['status']} — {r.get('pdf') or r.get('razon')}")

    st.markdown("---")
    st.markdown("### 3. Descargar PDFs")
    for lang in ("es", "en", "de"):
        pdf = DIST_DIR / f"tesis_{lang}.pdf"
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            if pdf.exists():
                size_kb = pdf.stat().st_size / 1024
                st.markdown(f"**{lang.upper()}** — `{pdf.name}` · {size_kb:.1f} KB")
            else:
                st.markdown(f"**{lang.upper()}** — *(no generado)*")
        with col2:
            if pdf.exists():
                with open(pdf, "rb") as f:
                    st.download_button(f"PDF {lang.upper()}", data=f.read(),
                                       file_name=pdf.name, mime="application/pdf",
                                       use_container_width=True,
                                       key=f"dl_pdf_{lang}")
        with col3:
            if pdf.exists():
                import hashlib
                h = hashlib.sha256()
                with open(pdf, "rb") as f:
                    for c in iter(lambda: f.read(8192), b""):
                        h.update(c)
                st.caption(f"sha256: {h.hexdigest()[:12]}...")

    st.markdown("---")
    st.markdown("### 4. Descargar fuentes .tex")
    for lang in ("es", "en", "de"):
        tex = SRC_DIR / f"tesis_{lang}.tex"
        col1, col2 = st.columns([3, 1])
        with col1:
            if tex.exists():
                st.markdown(f"**{lang.upper()}** — `{tex.name}` · {tex.stat().st_size} B")
            else:
                st.markdown(f"**{lang.upper()}** — *(no generado)*")
        with col2:
            if tex.exists():
                with open(tex, "rb") as f:
                    st.download_button(f".tex {lang.upper()}", data=f.read(),
                                       file_name=tex.name, mime="text/x-tex",
                                       use_container_width=True,
                                       key=f"dl_tex_{lang}")

# ============================================================
# Router y main
# ============================================================

# ============================================================
# Seccion 15: Atlas de figuras (imagen + ecuacion + teoria + demo)
# ============================================================
def _chapter_of(nombre):
    """Extrae el prefijo del capitulo del nombre (fig_03-01 -> Cap. 3)."""
    import re as _re
    m = _re.match(r"fig_([A-Z0-9]+)-", nombre)
    if not m:
        return "?"
    return m.group(1)




def _find_figure_image(name_or_path):
    """Devuelve el path al PNG real (con sufijo _150 o _300).
    Acepta nombre simple, .png, .pdf, o path completo."""
    from pathlib import Path as _P
    figs = _P(__file__).parent / "paper" / "thu" / "figures"
    # Extraer solo el stem (sin extension ni directorios)
    base = _P(str(name_or_path)).stem
    for suffix in ["_150.png", "_300.png", ".png", ".pdf"]:
        p = figs / (base + suffix)
        if p.exists():
            try:
                with open(p, "rb") as f:
                    h = f.read(4)
                if h == b"%PDF" and suffix == ".png":
                    continue
            except Exception:
                continue
            return p
    return None


def render_figures(t):
    hero(t)
    section(t["figures_title"], t["figures_theory"])

    from thu import figures as FIG
    meta_all = L.figure_metadata(lang=st.session_state.get("lang", "es")).get("figures", {})

    todos = sorted(FIG.GENERADORES.keys())
    total = len(todos)

    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        sel_etq = st.selectbox(t["figures_filter_label"],
                               ["Todas", "D", "P", "F", "A"],
                               index=0)
    with c2:
        chapters = sorted({_chapter_of(n) for n in todos})
        sel_cap = st.selectbox(t["figures_filter_chapter"],
                               ["Todos"] + chapters, index=0)
    with c3:
        st.metric(t["figures_total"], total)

    filtrados = []
    for n in todos:
        if sel_cap != "Todos" and _chapter_of(n) != sel_cap:
            continue
        if sel_etq != "Todas":
            m = meta_all.get(n, {})
            th = m.get("theory", "").lower()
            lab = "D"
            if "[p]" in th or "postulad" in th:
                lab = "P"
            elif "[f]" in th:
                lab = "F"
            elif "[a]" in th:
                lab = "A"
            if lab != sel_etq:
                continue
        filtrados.append(n)

    n_filt = len(filtrados)
    if n_filt == 0:
        st.info("Sin figuras con esos filtros.")
        return

    per_page = 6
    n_pages = max(1, (n_filt + per_page - 1) // per_page)

    if "fig_page" not in st.session_state:
        st.session_state.fig_page = 1
    if st.session_state.fig_page > n_pages:
        st.session_state.fig_page = 1

    cA, cB, cC = st.columns([1, 3, 1])
    with cA:
        if st.button(t["figures_prev"], key="fig_prev",
                     disabled=(st.session_state.fig_page <= 1),
                     use_container_width=True):
            st.session_state.fig_page -= 1
            st.rerun()
    with cB:
        st.markdown(
            f"<div style='text-align:center;color:#A0A0A0;padding-top:8px;'>"
            f"{t['figures_page']} {st.session_state.fig_page} "
            f"{t['figures_of']} {n_pages} - {n_filt} figuras</div>",
            unsafe_allow_html=True,
        )
    with cC:
        if st.button(t["figures_next"], key="fig_next",
                     disabled=(st.session_state.fig_page >= n_pages),
                     use_container_width=True):
            st.session_state.fig_page += 1
            st.rerun()

    ini = (st.session_state.fig_page - 1) * per_page
    fin = min(ini + per_page, n_filt)
    pagina = filtrados[ini:fin]

    for nombre in pagina:
        m = meta_all.get(nombre, {})
        png = BASE / "paper" / "thu" / "figures" / (nombre + ".png")
        st.markdown(f"### `{nombre}`")
        if m.get("equation") and not m["equation"].startswith("(alias"):
            try:
                st.latex(m["equation"])
            except Exception:
                st.code(m["equation"])
        cols = st.columns([2, 1])
        with cols[0]:
            if png.exists():
                _img = _find_figure_image(png)
                if _img:
                    st.image(str(_img), use_container_width=True)
                else:
                    st.warning("PNG no encontrado para: " + str(png))
            else:
                st.warning(f"PNG ausente: {png.name}")
        with cols[1]:
            if m.get("theory"):
                st.markdown(f"**{t['figures_theory_label']}**")
                st.markdown(m["theory"])
            if m.get("demo"):
                st.markdown(f"**{t['figures_demo']}**")
                st.markdown(m["demo"])
        st.markdown("---")

def render_derivaciones(t):
    """Sección 15: Derivaciones simbólicas con desarrollo paso a paso."""
    hero(t)
    section(t["derivations_title"], t["derivations_theory"])
    
    # Importar derivaciones
    import sys
    sys.path.insert(0, str(BASE / "src"))
    from thu import derivaciones as DER
    
    # Ejecutar derivaciones con barra de progreso
    if "derivaciones_cargadas" not in st.session_state:
        with st.spinner("Ejecutando derivaciones simbólicas..."):
            DER.ejecutar_todas()
            st.session_state.derivaciones_cargadas = True
            st.session_state.derivaciones = DER.DERIVACIONES
    
    derivs = st.session_state.derivaciones
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        labels = ["Todas", "D", "P", "A"]
        label_sel = st.selectbox("Filtrar por etiqueta", labels)
    with col2:
        caps = ["Todos", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "14", "15", "16", "17", "18"]
        cap_sel = st.selectbox("Filtrar por capítulo", caps)
    
    # Filtrar
    filtered = derivs
    if label_sel != "Todas":
        filtered = [d for d in filtered if d["label"] == label_sel]
    if cap_sel != "Todos":
        filtered = [d for d in filtered if cap_sel in d["referencia"]]
    
    st.info(f"Mostrando {len(filtered)} de {len(derivs)} derivaciones")
    
    # Mostrar cada derivación
    for der in filtered:
        with st.expander(f"{der['nombre']} [{der['label']}]"):
            st.markdown(f"**{t['derivations_reference']}**: {der['referencia']}")
            st.markdown(f"**{t['derivations_falsification']}**: {der['falsacion']}")
            
            st.markdown(f"### {t['derivations_steps']}")
            for i, paso in enumerate(der['pasos'], 1):
                st.markdown(f"{i}. {paso}")
            
            st.markdown(f"### {t['derivations_result']}")
            st.latex(der['latex_resultado'])
    
    # Resumen de etiquetas
    st.markdown("---")
    st.markdown(f"### {t['derivations_summary']}")
    labels_count = {}
    for d in derivs:
        labels_count[d['label']] = labels_count.get(d['label'], 0) + 1
    for label, count in sorted(labels_count.items()):
        st.markdown(f"- **[{label}]**: {count} derivaciones")

SECTIONS = {
    "overview": ("nav_overview",   render_overview),
    "derivations": ("nav_derivations", render_derivaciones),
    "problems": ("nav_problems",   render_problems),
    "predictions": ("nav_predictions", render_predictions),
    "patches": ("nav_patches",    render_patches),
    "versions": ("nav_versions",   render_versions),
    "epistemic": ("nav_epistemic",  render_epistemic),
    "glossary": ("nav_glossary",   render_glossary),
    "refs": ("nav_refs",       render_refs),
    "prisma": ("nav_prisma",     render_prisma),
    "datasets": ("nav_datasets",   render_datasets),
    "sections": ("nav_sections",   render_sections),
    "annexes": ("nav_annexes",    render_annexes),
    "downloads": ("nav_downloads",  render_downloads),
    "figures": ("nav_figures", render_figures),
}

def main():
    S.inject()

    if "lang" not in st.session_state:
        st.session_state.lang = "es"
    st.sidebar.selectbox("Idioma / Language / Sprache", I.available(),
                          format_func=I.lang_label, key="lang")
    t = I.get(st.session_state.lang)

    st.sidebar.markdown("---")
    if st.sidebar.button("Recargar", use_container_width=True):
        L.clear_cache()
        st.rerun()

    st.sidebar.markdown("**Seccion**")
    if "sec" not in st.session_state:
        st.session_state.sec = "overview"

    for sid, (label_key, _) in SECTIONS.items():
        active = st.session_state.sec == sid
        if st.sidebar.button(t[label_key], key=f"btn_{sid}",
                              use_container_width=True,
                              type="primary" if active else "secondary"):
            if not active:
                st.session_state.sec = sid
                st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <small>
        <b>Erick Duque</b><br>
        <i>Investigador Independiente</i><br>
        ORCID: <code>0009-0004-1245-5464</code><br>
        Correo: <code>international_manager@comllcusa.com</code><br>
        <br>
        <b>THU-TBEA 5.4</b><br>
        Version 5.4 &middot; 2026-09-24<br>
        DOI: <code>10.5281/zenodo.22949313</code><br>
        Repo: <a href='https://github.com/internationalmanager-creator/THU-TBEA'>GitHub</a>
        </small>
        """,
        unsafe_allow_html=True,
    )

    _, fn = SECTIONS[st.session_state.sec]
    fn(t)

    st.markdown(
        f'<div class="thu-footer">{t["footer"]}</div>',
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    # Auto-abrir navegador solo la primera vez (guard en variable de entorno)
    import os, webbrowser, threading
    if not os.environ.get("THU_BROWSER_OPENED"):
        os.environ["THU_BROWSER_OPENED"] = "1"
        threading.Timer(2.5, lambda: webbrowser.open("http://localhost:8501")).start()
    main()
