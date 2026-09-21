"""CSS y utilidades visuales. Colores vienen de domains.py."""
try:
    from .domains import colors_map
except ImportError:
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).parent.parent))
    from viz.domains import colors_map

DOMAIN_COLORS = colors_map()

CUSTOM_CSS = """
<style>
.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #6C5CE7 100%);
    padding: 40px; border-radius: 18px; margin-bottom: 25px;
    box-shadow: 0 15px 45px rgba(108,92,231,0.3);
}
.hero h1 { color:#fff; font-size:2.2rem; margin:0 0 8px; font-weight:800; }
.hero p { color:rgba(255,255,255,0.9); font-size:1.1rem; margin:0; }
.hero .tag { margin-top:10px; font-size:0.9rem; font-style:italic; opacity:0.85; }

.kpi { background: linear-gradient(145deg,#1A1D24,#232733);
       border-radius:14px; padding:20px;
       border-left:4px solid #6C5CE7; height:100%; }
.kpi-label { color:#A0A0A0; font-size:0.8rem; text-transform:uppercase;
             letter-spacing:0.1em; margin-bottom:6px; }
.kpi-value { color:#FAFAFA; font-size:2rem; font-weight:700; line-height:1; }
.kpi-detail { color:#6C5CE7; font-size:0.85rem; margin-top:4px; }

.sec { border-bottom:2px solid rgba(108,92,231,0.3);
       padding-bottom:10px; margin-bottom:20px; }
.sec h2 { color:#FAFAFA; font-size:1.5rem; margin:0; }
.sec .theory { color:#A0A0A0; font-size:0.9rem; margin-top:6px;
               font-style:italic; line-height:1.5; }

.prov-card { background:#1A1D24; border-radius:12px; padding:20px;
             border-left:4px solid #6C5CE7; margin:15px 0; }

.chain-ok { background:rgba(0,184,148,0.15); border-left:4px solid #00B894;
            padding:12px 16px; border-radius:8px; color:#00B894;
            font-weight:600; }
.chain-bad { background:rgba(225,112,85,0.15); border-left:4px solid #E17055;
             padding:12px 16px; border-radius:8px; color:#E17055;
             font-weight:600; }

.footer { text-align:center; color:#636E72; padding:25px 0;
          border-top:1px solid rgba(108,92,231,0.15); margin-top:30px;
          font-size:0.85rem; }
#MainMenu {visibility:hidden;} footer {visibility:hidden;}
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


if __name__ == "__main__":
    print("=== Test styles.py ===")
    print(f"  DOMAIN_COLORS: {len(DOMAIN_COLORS)} dominios")
    for code, color in list(DOMAIN_COLORS.items())[:3]:
        print(f"    {code:<18} {color}")
    print(f"  CUSTOM_CSS: {len(CUSTOM_CSS)} chars")
    assert "linear-gradient" in CUSTOM_CSS
    assert "kpi-value" in CUSTOM_CSS
    assert len(DOMAIN_COLORS) == 8
    print("=== TEST OK ===")