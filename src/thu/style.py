"""CSS para el dashboard THU-TBEA."""
try:
    from .loader import label_color
except ImportError:
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).parent.parent))
    from thu.loader import label_color

THU_CSS = """
<style>
.thu-hero {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #6C5CE7 100%);
    padding: 42px; border-radius: 20px; margin-bottom: 25px;
    box-shadow: 0 20px 60px rgba(108,92,231,0.35);
    position: relative; overflow: hidden;
}
.thu-hero::before {
    content: ""; position: absolute; top: -50%; right: -20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(253,203,110,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.thu-hero h1 { color:#fff; font-size:2.3rem; margin:0 0 8px; font-weight:800; letter-spacing:-0.5px; }
.thu-hero p { color:rgba(255,255,255,0.9); font-size:1.1rem; margin:0; }
.thu-hero .tag { margin-top:12px; font-size:0.9rem; font-style:italic; opacity:0.85; }

.thu-kpi { background: linear-gradient(145deg,#1A1D24,#232733);
       border-radius:14px; padding:18px; height:100%;
       border-left:4px solid #6C5CE7; }
.thu-kpi-label { color:#A0A0A0; font-size:0.78rem; text-transform:uppercase;
             letter-spacing:0.08em; margin-bottom:6px; }
.thu-kpi-value { color:#FAFAFA; font-size:1.8rem; font-weight:700; line-height:1; }
.thu-kpi-detail { color:#6C5CE7; font-size:0.82rem; margin-top:4px; }

.thu-sec { border-bottom:2px solid rgba(108,92,231,0.3);
       padding-bottom:10px; margin-bottom:20px; }
.thu-sec h2 { color:#FAFAFA; font-size:1.4rem; margin:0; }
.thu-sec .theory { color:#A0A0A0; font-size:0.9rem; margin-top:6px;
               font-style:italic; line-height:1.5; }

.thu-badge-D { background:rgba(0,184,148,0.18); color:#00B894;
    padding:2px 10px; border-radius:10px; font-weight:700; font-size:0.8rem;
    border:1px solid #00B894; display:inline-block; }
.thu-badge-P { background:rgba(108,92,231,0.18); color:#6C5CE7;
    padding:2px 10px; border-radius:10px; font-weight:700; font-size:0.8rem;
    border:1px solid #6C5CE7; display:inline-block; }
.thu-badge-F { background:rgba(225,112,85,0.18); color:#E17055;
    padding:2px 10px; border-radius:10px; font-weight:700; font-size:0.8rem;
    border:1px solid #E17055; display:inline-block; }
.thu-badge-A { background:rgba(253,203,110,0.18); color:#FDCB6E;
    padding:2px 10px; border-radius:10px; font-weight:700; font-size:0.8rem;
    border:1px solid #FDCB6E; display:inline-block; }

.thu-card { background:#1A1D24; border-radius:12px; padding:16px;
    border-left:4px solid #6C5CE7; margin:10px 0; }
.thu-eq { background:#0f1219; border-radius:10px; padding:16px 20px;
    font-family: 'Cambria Math', 'Latin Modern Math', serif;
    font-size:1.05rem; color:#FAFAFA; border-left:3px solid #FDCB6E;
    margin:12px 0; overflow-x:auto; }
.thu-footer { text-align:center; color:#636E72; padding:25px 0;
    border-top:1px solid rgba(108,92,231,0.15); margin-top:30px;
    font-size:0.85rem; }
#MainMenu {visibility:hidden;} footer {visibility:hidden;}

/* === Ecuaciones LaTeX nativas (st.latex) === */
div[data-testid="stLatex"] {
    background: #0f1219 !important;
    padding: 18px 22px !important;
    border-radius: 10px !important;
    border-left: 3px solid #FDCB6E !important;
    margin: 14px 0 !important;
    overflow-x: auto !important;
}
div[data-testid="stLatex"] > div {
    color: #FAFAFA !important;
    font-size: 1.05rem !important;
}
/* KaTeX override para consistencia con dark theme */
div[data-testid="stLatex"] .katex {
    color: #FAFAFA !important;
    font-size: 1.1em !important;
}
div[data-testid="stLatex"] .katex-display {
    margin: 0 !important;
}
/* Evitar que st.latex ocupe todo el ancho con scroll horizontal feo */
div[data-testid="stLatex"] .katex-display > .katex {
    white-space: normal !important;
    overflow-x: auto !important;
}

</style>
"""


def inject():
    import streamlit as st
    st.markdown(THU_CSS, unsafe_allow_html=True)


def badge(label):
    """HTML badge para etiqueta epistemica."""
    first = (label or "P")[0]
    return f'<span class="thu-badge-{first}">{label}</span>'


if __name__ == "__main__":
    print("=== Test style.py ===")
    print(f"  THU_CSS: {len(THU_CSS)} chars")
    for lab in ("D", "P", "F", "A"):
        b = badge(lab)
        assert "thu-badge-" in b
        assert lab in b
    # Casos raros
    assert badge("D (dado g_star)").startswith('<span class="thu-badge-D">')
    assert "thu-badge-P" in badge("")
    assert "thu-badge-P" in badge(None)
    print("  badges: D/P/F/A OK")
    print("  badge('D (dado g_star)') OK")
    print("  badge(None) fallback OK")
    assert "linear-gradient" in THU_CSS
    assert "thu-hero" in THU_CSS
    assert "thu-eq" in THU_CSS
    print("=== TEST OK ===")