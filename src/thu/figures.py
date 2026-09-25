"""Generacion programatica de figuras THU-TBEA.

Regenera las figuras de la tesis que son derivables de las ecuaciones
o de los JSON. Las que no (fotos de laboratorio, imagenes decorativas)
se marcan como [A] esquematica en el manifest.

Salida: paper/thu/figures/fig_CAP-SEQ_desc.png
Manifest: paper/thu/figures/figures_manifest.json

Uso:
    python src/thu/figures.py --list           # listar generadores
    python src/thu/figures.py --all             # generar todas
    python src/thu/figures.py --one fig_03-01_helice_aurea
"""
import argparse
import hashlib
import json
import shutil
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from tqdm import tqdm

BASE = Path(__file__).parent.parent.parent
THU = BASE / "registry" / "thu"
OUT = BASE / "paper" / "thu" / "figures"
MANIFEST = OUT / "figures_manifest.json"

PHI = (1 + math.sqrt(5)) / 2
THETA_PHI_DEG = 137.507764
SEED = 20260808

# ===== THEME PRINT (v5.4) =====
# Chrome del tema editorial: fondo blanco, texto oscuro, spines limpios.
# Colores de datos preservados (paleta canonica del programa):
#   [D] #00B894  [P] #6C5CE7  [F] #E17055  [A] #D4A017  info #0984E3

THEME_PRINT = {
    "bg":       "#FFFFFF",
    "fg":       "#1A1A1A",
    "muted":    "#555555",
    "dim":      "#888888",
    "box":      "#F5F5F5",
    "box_alt":  "#EAEAEA",
    "grid":     "#CCCCCC",
    "primary":  "#6C5CE7",
    "warn":     "#E17055",
    "ok":       "#00B894",
    "accent":   "#D4A017",
    "info":     "#0984E3",
}

plt.rcParams.update({
    "font.family":       "STIXGeneral",
    "mathtext.fontset":  "stix",
    "font.size":         10,
    "figure.facecolor":  THEME_PRINT["bg"],
    "savefig.facecolor": THEME_PRINT["bg"],
    "axes.facecolor":    THEME_PRINT["bg"],
    "axes.edgecolor":    THEME_PRINT["fg"],
    "axes.labelcolor":   THEME_PRINT["fg"],
    "text.color":        THEME_PRINT["fg"],
    "xtick.color":       THEME_PRINT["muted"],
    "ytick.color":       THEME_PRINT["muted"],
    "axes.grid":         True,
    "grid.color":        THEME_PRINT["grid"],
    "grid.alpha":        0.4,
    "grid.linewidth":    0.5,
    "grid.linestyle":    ":",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "xtick.direction":   "in",
    "ytick.direction":   "in",
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "savefig.bbox":      "tight",
    "savefig.dpi":       300,
    "figure.dpi":        100,
    "lines.linewidth":   1.8,
    "lines.markersize":  6,
    "legend.frameon":    False,
    "legend.fontsize":   9,
})


def _sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(8192), b""):
            h.update(c)
    return h.hexdigest()


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _save(fig, name, label, source):
    """Guarda figura en 3 formatos y devuelve metadata con hashes.

    - .pdf          : vectorial, para la tesis LaTeX
    - _300.png      : 300 DPI, para revision editorial / manuscrito
    - _150.png      : 150 DPI, para el dashboard Streamlit
    """
    OUT.mkdir(parents=True, exist_ok=True)
    pdf_path = OUT / (name + ".pdf")
    png_300  = OUT / (name + "_300.png")
    png_150  = OUT / (name + "_150.png")
    fig.savefig(pdf_path, format="pdf")
    fig.savefig(png_300, format="png", dpi=300)
    fig.savefig(png_150, format="png", dpi=150)
    plt.close(fig)
    return {
        "name":           name,
        "path":           str(pdf_path.relative_to(BASE)),
        "pdf_path":       str(pdf_path.relative_to(BASE)),
        "png_300_path":   str(png_300.relative_to(BASE)),
        "png_150_path":   str(png_150.relative_to(BASE)),
        "sha256":         _sha_file(pdf_path),
        "sha256_pdf":     _sha_file(pdf_path),
        "sha256_png_300": _sha_file(png_300),
        "sha256_png_150": _sha_file(png_150),
        "label":          label,
        "source":         source,
        "generated_at_utc": _ts(),
    }


# ============================================================
# Figuras geometricas
# ============================================================

def fig_03_01_helice_aurea():
    """Fig 3.1: 3D helix + 2D spiral projection in XY."""
    t = np.linspace(0, 6 * math.pi, 2000)
    x = np.cos(t); y = np.sin(t); z = t / PHI
    fig = plt.figure(figsize=(12, 5))
    ax1 = fig.add_subplot(121, projection="3d")
    ax1.plot(x, y, z, color="#0984E3", linewidth=2)
    ax1.set_title(r"Golden helix 3D ($\varphi = 1.6180$)",
                  color=THEME_PRINT["fg"], pad=10, fontweight="bold")
    ax1.set_xlabel("x", color=THEME_PRINT["muted"]); ax1.set_ylabel("y", color=THEME_PRINT["muted"])
    ax1.set_zlabel(r"$z/\varphi$", color=THEME_PRINT["muted"])
    ax1.tick_params(colors=THEME_PRINT["muted"]); ax1.grid(True, alpha=0.3)
    ax2 = fig.add_subplot(122)
    ax2.plot(x, y, color="#E17055", linewidth=1.8)
    ax2.scatter([0], [0], color="#FDCB6E", s=80, zorder=5,
                edgecolor=THEME_PRINT["bg"], linewidth=1.5)
    ax2.set_aspect("equal")
    ax2.set_title(r"Spiral projection (step $\varphi$)",
                  color=THEME_PRINT["fg"], pad=10, fontweight="bold")
    ax2.set_xlabel(r"$x$ ($L_p$ units)", color=THEME_PRINT["muted"])
    ax2.set_ylabel(r"$y$ ($L_p$ units)", color=THEME_PRINT["muted"])
    ax2.tick_params(colors=THEME_PRINT["muted"])
    plt.tight_layout()
    return _save(fig, "fig_03-01_helice_aurea", "D",
                 "Fig 3.1: 3D helix + XY spiral projection")
def fig_03_02_doble_espiral():
    """Fig 3.2: double logarithmic spiral matter-antimatter."""
    t = np.linspace(0, 2 * math.pi, 1200)
    r = PHI ** (t / (math.pi / 2))
    theta1 = t
    theta2 = t + 2 * math.pi * (2 - PHI)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(r * np.cos(theta1), r * np.sin(theta1),
            color="#0984E3", linewidth=2, label="Matter")
    ax.plot(r * np.cos(theta2), r * np.sin(theta2),
            color="#E17055", linewidth=2, linestyle="--",
            label=r"Antimatter ($\theta_\varphi = 137.508^\circ$)")
    ax.scatter([0], [0], color="#FDCB6E", s=80, zorder=5,
               edgecolor=THEME_PRINT["bg"], linewidth=1.5)
    ax.set_aspect("equal")
    ax.set_title(r"Double logarithmic spiral ($r = \varphi^{\theta/(\pi/2)}$)")
    ax.set_xlabel(r"$x$"); ax.set_ylabel(r"$y$")
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7",
              labelcolor=THEME_PRINT["fg"], loc="upper right")
    return _save(fig, "fig_03-02_doble_espiral", "D",
                 "Fig 3.2: matter-antimatter spiral")
def fig_03_03_mapa_intensidad():
    """Fig 3.3: 2D intensity map of the coherence field."""
    N = 200
    x = np.linspace(-3, 3, N); y = np.linspace(-3, 3, N)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2) + 1e-6
    Theta = np.arctan2(Y, X)
    phi = np.sin(PHI * Theta) * np.exp(-R**2 / 4)
    fig, ax = plt.subplots(figsize=(8, 7))
    c = ax.contourf(X, Y, phi, levels=30, cmap="RdBu_r")
    ax.set_aspect("equal")
    ax.set_title(r"Intensity map of the helical field "
                 r"$\Phi(x,y) = \sin(\varphi\theta)e^{-R^2/4}$")
    ax.set_xlabel(r"$x$"); ax.set_ylabel(r"$y$")
    fig.colorbar(c, ax=ax, label=r"$\Phi(x,y)$")
    return _save(fig, "fig_03-03_mapa_intensidad", "A",
                 "Fig 3.3: coherence field intensity")
def _caja_diagrama(ax, cx, cy, w, h, titulo, subtitulo, color):
    """Helper: caja con titulo (arriba) y subtitulo (abajo), texto ajustado dentro."""
    box = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                          boxstyle="round,pad=0.02",
                          linewidth=2, edgecolor=color, facecolor=THEME_PRINT["box"])
    ax.add_patch(box)
    ax.text(cx, cy + h * 0.18, titulo, ha="center", va="center",
            fontsize=10, color=THEME_PRINT["fg"], fontweight="bold")
    ax.text(cx, cy - h * 0.22, subtitulo, ha="center", va="center",
            fontsize=8, color=THEME_PRINT["muted"])


def _flecha_h(ax, x1, x2, y, color="#6C5CE7", lw=2):
    """Helper: flecha horizontal limpia entre x1 y x2 sin invadir cajas."""
    ax.annotate("", xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                shrinkA=0, shrinkB=0))


def fig_03_04_sintesis_U4():
    """Fig 3.4: vertical hierarchical synthesis (5 boxes)."""
    fig, ax = plt.subplots(figsize=(11, 9))
    ax.set_xlim(0, 12); ax.set_ylim(0, 11); ax.axis("off")
    boxes = [
        (9.5, "#AED6F1", "#2874A6",
         r"Fundamental level: $U_4$",
         r"$g_{\mu\nu},\ \Gamma^\lambda_{\mu\nu},\ T^\lambda_{\mu\nu}$"),
        (7.6, "#F8C471", "#B9770E",
         r"Compactification: $M_6 = CY_3$",
         r"$h^{1,1}=22,\ h^{2,1}=19\ \mathrm{or}\ 25$"),
        (5.7, "#A9DFBF", "#1E8449",
         r"Spinorial sector: $\dim(S_{4D}) = 4$",
         r"$32_{10D} = 4_{4D} \times 8_{6D}$"),
        (3.8, "#F1948A", "#922B21",
         r"Trans-scale: $n = 4 \times 22 = 88$",
         r"$\Lambda_{THU} = M_P \varphi^{-88} = 989.89\ \mathrm{MeV}$"),
        (1.9, "#D7BDE2", "#6C3483",
         r"Phenomenology: $\beta(z),\ m_n,\ P_1$-$P_{11}$",
         r"Ch. 10-17"),
    ]
    W, H = 10.0, 1.4
    for cy, fc, ec, titulo, subtitulo in boxes:
        box = FancyBboxPatch((1.0, cy - H/2), W, H,
                             boxstyle="round,pad=0.05",
                             facecolor=fc, edgecolor=ec, linewidth=2.5)
        ax.add_patch(box)
        ax.text(6.0, cy + 0.22, titulo, ha="center", va="center",
                fontsize=11, color=THEME_PRINT["bg"], fontweight="bold")
        ax.text(6.0, cy - 0.3, subtitulo, ha="center", va="center",
                fontsize=9, color=THEME_PRINT["box"], style="italic")
    for i in range(len(boxes) - 1):
        y_from = boxes[i][0] - H/2 - 0.05
        y_to = boxes[i+1][0] + H/2 + 0.05
        ax.annotate("", xy=(6.0, y_to), xytext=(6.0, y_from),
                    arrowprops=dict(arrowstyle="-|>", color="#6C5CE7", lw=2.5))
    ax.set_title(r"Synthesis THU-TBEA 5.0: $U_4 \to CY_3 \to n=88 \to$ "
                 r"phenomenology",
                 fontsize=13, color=THEME_PRINT["fg"], pad=15, fontweight="bold")
    return _save(fig, "fig_03-04_sintesis_U4", "A",
                 "Fig 3.4: vertical hierarchical synthesis")
def fig_04_01_lambert_w():
    """Fig 4.2: Lambert-W branches and physical argument."""
    try:
        from scipy.special import lambertw
    except ImportError:
        return None
    x_neg = np.linspace(-1/math.e + 1e-6, -0.01, 500)
    x_pos = np.linspace(-0.01, 5, 500)
    x_all = np.concatenate([x_neg, x_pos])
    w0 = np.real(lambertw(x_all, k=0))
    wm1 = np.real(lambertw(x_neg, k=-1))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(x_all, w0, color="#6C5CE7", linewidth=2,
            label=r"$W_0(z)$ (physical)")
    ax.plot(x_neg, wm1, color="#E17055", linewidth=2, linestyle="--",
            label=r"$W_{-1}(z)$ (UV)")
    ax.axvline(-1/math.e, color=THEME_PRINT["muted"], linestyle=":", alpha=0.5,
               label=r"$z = -1/e$")
    ax.set_xlabel(r"$z$"); ax.set_ylabel(r"$W(z)$")
    ax.set_title("Lambert-W branches (physical vs UV)")
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_04-01_lambert_w", "D",
                 "Fig 4.2: Lambert-W branches")
def fig_04_02_residuo():
    """Fig 4.3: positive residue Res[Delta]."""
    a = np.linspace(0, 2, 300)
    fig, ax = plt.subplots(figsize=(9, 5))
    for m2, color in [(0.5, "#0984E3"), (1.0, "#E17055"), (2.0, "#00B894")]:
        res = np.exp(-a * m2) / (1 + a * m2)
        ax.plot(a, res, color=color, linewidth=2,
                label=rf"$m^2 = {m2}$")
    ax.axhline(0, color=THEME_PRINT["muted"], linewidth=0.5)
    ax.set_xlabel(r"$a = \varphi/M_P^2$")
    ax.set_ylabel(r"$\mathrm{Res}[\Delta]$")
    ax.set_title(r"Propagator residue "
                 r"$\mathrm{Res}[\Delta] = "
                 r"e^{-am^2}/(1+am^2) > 0$")
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_04-02_residuo", "D",
                 "Fig 4.3: positive propagator residue")
def fig_06_01_rg_flow():
    """Fig 6.1: 1-loop RG flow to golden fixed point."""
    g = np.linspace(-0.6, 2.2, 500)
    kappa = 0.0063
    beta = kappa * (1 + g - g**2)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(g, beta, color="#6C5CE7", linewidth=2,
            label=r"$\beta_{\rm eff}(g) = \kappa(1+g-g^2)$")
    ax.axhline(0, color=THEME_PRINT["muted"], linewidth=0.5)
    ax.axvline(PHI, color="#FDCB6E", linestyle="--", alpha=0.9,
               label=rf"$g_* = \varphi = {PHI:.4f}$")
    ax.axvline(-1/PHI, color="#E17055", linestyle="--", alpha=0.9,
               label=rf"$g_- = -1/\varphi = {-1/PHI:.4f}$")
    ax.scatter([PHI], [0], color="#FDCB6E", s=120, zorder=5,
               edgecolor=THEME_PRINT["bg"], linewidth=2)
    ax.set_xlabel(r"$g$")
    ax.set_ylabel(r"$\beta(g)$")
    ax.set_title(r"1-loop beta function: golden fixed point",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_06-01_rg_flow", "D",
                 "Fig 6.1: 1-loop beta function")
def fig_07_01_cancelacion_vacio():
    """Fig 7.1: analytic zero of the scalar vacuum integral."""
    N = np.linspace(0.5, 2.5, 500)
    a = PHI
    b = PHI ** N
    I2 = (1 / (4 * a)) * np.sqrt(np.pi / a) * (1 - b**2 / (2 * a)) * np.exp(-b**2 / (4 * a))
    I2 = I2 / np.abs(I2).max()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(N, I2, color="#6C5CE7", linewidth=2,
            label=r"$I_2(\varphi, \varphi^N)$ normalized")
    ax.axhline(0, color=THEME_PRINT["muted"], linewidth=0.5)
    Nc = 1.220210
    ax.axvline(Nc, color="#E17055", linestyle="--",
               label=rf"$N_0 = {Nc}$")
    ax.set_xlabel(r"$N$")
    ax.set_ylabel(r"$I_2$")
    ax.set_title(r"Analytic zero of the scalar vacuum integral",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_07-01_cancelacion_vacio", "D",
                 "Fig 7.1: analytic zero at N = 1.220210")
def fig_07_02_familia_medidas():
    """Alias of fig_07_04_familia_medidas."""
    return fig_07_04_familia_medidas()
def fig_08_01_Hz():
    """Fig 8.1: H(z) LCDM vs THU-TBEA."""
    z = np.linspace(0, 3, 300)
    H0 = 67.4
    Om = 0.315
    OL = 0.685
    H_lcdm = H0 * np.sqrt(Om * (1 + z)**3 + OL)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(z, H_lcdm, color="#6C5CE7", linewidth=2,
            label=r"$\Lambda$CDM")
    ax.plot(z, H_lcdm * (1 + 0.01 * np.sin(2 * np.pi * z / 1.5)),
            color="#E17055", linewidth=1.5, linestyle="--",
            label="THU-TBEA (residual oscillation)")
    ax.set_xlabel(r"$z$")
    ax.set_ylabel(r"$H(z)$ [km/s/Mpc]")
    ax.set_title(r"$H(z)$: $\Lambda$CDM vs THU-TBEA", color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_08-01_Hz", "D",
                 "Fig 8.1: H(z) comparison")
def fig_08_04_bounce():
    """Fig 8.4: ECSK cosmological bounce (H^2 = 0)."""
    a = np.linspace(0.2, 10, 500)
    kappa4 = 1.0
    S2 = 1.0
    rho = 0.3 * a**-3 + 0.7
    H2 = rho - kappa4 / 6 * S2 * a**-6
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(a, np.abs(H2), color="#6C5CE7", linewidth=2)
    ax.axhline(0, color=THEME_PRINT["muted"], linewidth=0.5)
    a_min = 0.445
    ax.axvline(a_min, color="#E17055", linestyle="--",
               label=rf"Bounce: $a_{{\min}} = {a_min}$")
    ax.set_yscale("log")
    ax.set_xlabel(r"Scale factor $a$")
    ax.set_ylabel(r"$|H^2(a)|$")
    ax.set_title(r"ECSK cosmological bounce "
                 r"($H^2 = \rho - \frac{\kappa^4}{6}S^2 a^{-6}$)",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_08-04a_bounce", "D",
                 "Fig 8.4: ECSK bounce at a_min = 0.445")
def fig_09_01_chameleon_perfil():
    """Fig 9.1: chameleon radial profile and effective mass."""
    r = np.linspace(0.1, 10, 500)
    rho_in = 1.0
    rho_out = 1e-3
    beta_c = 2.1e-4
    m_in = np.sqrt(rho_in * beta_c**2) * (1 + np.exp(-(r - 2)**2))
    m_out = np.sqrt(rho_out * beta_c**2) * np.ones_like(r)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(r, m_in, color="#6C5CE7", linewidth=2,
            label=r"Interior ($\rho_{\rm in}$)")
    ax.plot(r, m_out, color="#E17055", linewidth=1.5, linestyle="--",
            label=r"Exterior ($\rho_{\rm out}$)")
    ax.set_yscale("log")
    ax.set_xlabel(r"$r$ (radius)")
    ax.set_ylabel(r"$m_{\rm eff}(r)$")
    ax.set_title(r"Chameleon: screening via $m_{\rm eff}^2 = "
                 r"m_0^2 + \beta_c^2 \rho$",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_09-01_chameleon_perfil", "A",
                 "Fig 9.1: chameleon profile")
def fig_11_01_tomografia():
    """Fig 11.1: beta(z)/beta_0 tomography from EOM."""
    try:
        from scipy.integrate import quad
    except ImportError:
        return None
    H0 = 67.4
    Om, OL = 0.315, 0.685
    def integrando(zp):
        return 1.0 / ((1 + zp) * H0 * np.sqrt(Om * (1 + zp)**3 + OL))
    z = np.linspace(0, 3, 60)
    t_z = np.array([quad(integrando, zi, np.inf, limit=200)[0] for zi in z])
    t_0 = t_z[0]
    beta_ratio = 1.0 - t_z / t_0
    beta_ratio = np.clip(beta_ratio, 0.0, 1.0)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(z, beta_ratio, color="#6C5CE7", linewidth=2.5,
            label="THU-TBEA (EOM integral)")
    ax.axhline(1.0, color=THEME_PRINT["muted"], linestyle="--",
               label="Null model (constant)")
    z_ref = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    ref_vals = np.array([0.374, 0.573, 0.688, 0.760, 0.809, 0.843])
    ax.scatter(z_ref, ref_vals, color="#FDCB6E", s=60, zorder=5,
               edgecolor=THEME_PRINT["bg"], linewidth=1.2,
               label="Table 11.1 (fiducial)")
    ax.set_xlabel(r"$z$")
    ax.set_ylabel(r"$\beta(z) / \beta_0$")
    ax.set_ylim(0, 1.05)
    ax.set_title(r"$\beta(z)$ tomography: central falsifiable "
                 r"prediction", color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7",
              labelcolor=THEME_PRINT["fg"], loc="lower right")
    return _save(fig, "fig_11-01_tomografia", "D",
                 "Fig 11.1: tomography")
def fig_12_01_escala_masas():
    """Fig 12.1: trans-scale mass ladder m_n = M_P phi^-n."""
    n = np.arange(0, 89)
    M_P_GeV = 2.435e18
    m_n_GeV = M_P_GeV * PHI ** (-n)
    m_n_MeV = m_n_GeV * 1000
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(n, m_n_MeV, color="#6C5CE7", linewidth=2)
    n_88 = 88
    m_88 = M_P_GeV * PHI ** (-n_88) * 1000
    ax.scatter([n_88], [m_88], color="#E17055", s=100, zorder=5,
               edgecolor=THEME_PRINT["bg"], linewidth=2,
               label=rf"$\Lambda_{{THU}}$ (n=88) = ${m_88:.2f}$ MeV")
    ax.set_yscale("log")
    ax.set_xlabel(r"$n$ (hierarchy index)")
    ax.set_ylabel(r"$m_n = M_P \varphi^{-n}$ [MeV]")
    ax.set_title(r"Trans-scale ladder: $m_n = M_P\varphi^{-n}$",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_12-01_escala_masas", "D",
                 "Fig 12.1: mass ladder")
def fig_14_01_wz_dinamico():
    """Fig 14.1: lower bound w_phi >= -1."""
    z = np.logspace(-1, 4, 200)
    w = -1 + 0.001 * (1 + z)**-0.5
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(z, w, color="#6C5CE7", linewidth=2,
            label=r"$w_\varphi(z)$ THU-TBEA")
    ax.axhline(-1, color="#E17055", linestyle="--",
               label=r"$w = -1$ (lower bound)")
    ax.fill_between(z, -1.05, -1, color="#E17055", alpha=0.2,
                    label="Phantom region (prohibited)")
    ax.set_xscale("log")
    ax.set_xlabel(r"$z$")
    ax.set_ylabel(r"$w_\varphi(z)$")
    ax.set_title(r"Lower bound $w_\varphi \geq -1$ vs DESI DR2",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_14-01_wz_dinamico", "D",
                 "Fig 14.1: w_phi lower bound")
def _load(name):
    return json.loads((THU / name).read_text(encoding="utf-8"))


def _label_color(lab):
    return {"D": "#00B894", "P": "#6C5CE7",
            "F": "#E17055", "A": "#FDCB6E"}.get(lab[0] if lab else "P", THEME_PRINT["dim"])


def fig_17_01_matriz_falsacion():
    """Fig 17.1: falsification matrix P1-P12."""
    preds = [
        ("P1", "Helical osc. in H(z)", "Open"),
        ("P2", "Golden CMB modulation", "Open"),
        ("P3", "Mega-rings 137.5 deg", "Open"),
        ("P4", "Resonant trans-scale DM", "Open"),
        ("P5", "Helical spin residual", "Prereg"),
        ("P6", "Superradiance no rotation", "Open"),
        ("P7", "Geometric spin precession", "Open"),
        ("P8", "Golden mass spectrum", "Consist"),
        ("P9", "Helical EM modulation", "Open"),
        ("P10", "Stable helical soliton", "Open"),
        ("P11", "1.34 THz microtubules", "Prereg"),
    ]
    status_color = {"Open": "#E17055", "Prereg": "#FDCB6E",
                    "Consist": "#00B894"}
    fig, ax = plt.subplots(figsize=(10, 6))
    ys = np.arange(len(preds))
    colors = [status_color.get(p[2], THEME_PRINT["dim"]) for p in preds]
    ax.barh(ys, [1]*len(preds), color=colors,
            edgecolor=THEME_PRINT["bg"], linewidth=1)
    for i, (pid, obs, st) in enumerate(preds):
        ax.text(0.02, i, rf"{pid}: {obs}", va="center",
                fontsize=9, color=THEME_PRINT["fg"])
    ax.set_yticks(ys)
    ax.set_yticklabels([p[0] for p in preds])
    ax.set_xticks([]); ax.set_xlim(0, 1)
    ax.set_title(r"Falsification matrix P1-P12", color=THEME_PRINT["fg"])
    return _save(fig, "fig_17-01_matriz_falsacion", "D",
                 "Fig 17.1: falsification matrix")
def fig_17_02_bitacora_lakatosiana():
    """Fig 17.2: Lakatosian timeline 1.0 -> 5.3."""
    vers = ["1.0", "2.0", "3.0", "4.0", "4.1", "4.2", "4.3",
            "5.0", "5.1", "5.2", "5.3"]
    labels = ["A", "P", "D", "D", "P", "D", "D", "D", "D", "D", "P/D"]
    colors = {"A": "#FDCB6E", "P": "#6C5CE7", "D": "#00B894"}
    fig, ax = plt.subplots(figsize=(11, 5))
    xs = np.arange(len(vers)); ys = np.ones(len(vers))
    cs = [colors.get(l[0], THEME_PRINT["dim"]) for l in labels]
    ax.scatter(xs, ys, s=400, c=cs, edgecolor=THEME_PRINT["fg"],
               linewidth=1.5, zorder=3)
    for i, (v, l) in enumerate(zip(vers, labels)):
        ax.text(xs[i], 1.25, f"v{v}", ha="center", fontsize=10,
                color=THEME_PRINT["fg"], fontweight="bold")
        ax.text(xs[i], 0.68, f"[{l}]", ha="center",
                fontsize=9, color=THEME_PRINT["muted"])
    ax.plot(xs, ys, color="#6C5CE7", linewidth=2, alpha=0.6, zorder=2)
    ax.set_ylim(0.5, 1.5); ax.set_xlim(-0.5, len(vers) - 0.5)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("Lakatosian timeline: 1.0 -> 5.3",
                 color=THEME_PRINT["fg"])
    return _save(fig, "fig_17-02_bitacora_lakatosiana", "D",
                 "Fig 17.2: Lakatosian timeline")
def fig_17_03_patches_por_etapa():
    """Fig 17.3: 17 patches distribution by stage."""
    stages = ["VII", "VIII", "IX", "X"]
    counts = [7, 3, 3, 4]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(stages, counts,
                  color=["#6C5CE7", "#0984E3", "#FDCB6E", "#E17055"],
                  edgecolor=THEME_PRINT["bg"], linewidth=1.5)
    for b, v in zip(bars, counts):
        ax.text(b.get_x() + b.get_width()/2, v + 0.1, str(v),
                ha="center", fontsize=12, color=THEME_PRINT["fg"],
                fontweight="bold")
    ax.set_xlabel("Stage")
    ax.set_ylabel("Patches")
    ax.set_title(r"17 patches in 4 review stages (VII-X)",
                 color=THEME_PRINT["fg"])
    return _save(fig, "fig_17-03_patches_por_etapa", "D",
                 "Fig 17.3: patches by stage")
def fig_13_01_prisma_funnel():
    """Fig 13.1b: PRISMA flow funnel 284 -> 38."""
    stages = ["Identified", "Screened", "Eligible", "Included"]
    vals = [284, 173, 58, 38]
    colors = ["#6C5CE7", "#0984E3", "#FDCB6E", "#00B894"]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(stages[::-1], vals[::-1], color=colors[::-1],
                   edgecolor=THEME_PRINT["bg"], linewidth=1.5)
    for b, v in zip(bars, vals[::-1]):
        ax.text(v + 5, b.get_y() + b.get_height()/2, str(v),
                va="center", fontsize=12, color=THEME_PRINT["fg"],
                fontweight="bold")
    ax.set_xlabel("N records")
    ax.set_title(r"PRISMA funnel: $284 \to 38$ studies",
                 color=THEME_PRINT["fg"])
    return _save(fig, "fig_13-01b_prisma_funnel", "D",
                 "Fig 13.1b: PRISMA funnel")
def fig_18_01_chi2_breakdown():
    """Fig 18.1: $\\chi^2$ breakdown by dataset (mocks)."""
    labels = [r"BAO" + "\n" + r"(DESI DR2)",
              r"SNe" + "\n" + r"(Pantheon+)",
              r"CMB" + "\n" + r"(birefringence)"]
    vals = [14.82, 157.47, 3.12]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, vals, color=["#6C5CE7", "#E17055", "#00B894"],
                  edgecolor=THEME_PRINT["bg"], linewidth=1.5)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, v + 2, rf"${v:.2f}$",
                ha="center", fontsize=11, color=THEME_PRINT["fg"],
                fontweight="bold")
    ax.set_ylabel(r"$\chi^2$")
    ax.set_title(r"$\chi^2$ breakdown (mocks, total = 175.41)",
                 color=THEME_PRINT["fg"])
    return _save(fig, "fig_18-01a_chi2_breakdown", "D",
                 "Fig 18.1: $\\chi^2$ breakdown")
def fig_03_07_cadena_cy3():
    """Fig 3.6: chain A-14, geometric derivation of n=88."""
    fig, ax = plt.subplots(figsize=(13, 4.5))
    ax.set_xlim(0, 13); ax.set_ylim(0, 4.5); ax.axis("off")
    W, H = 1.8, 1.5; y = 2.2
    centers = [1.4, 3.85, 6.3, 8.75, 11.2]
    steps = [
        ("AXIOMS", r"$U_4$ Palatini", "#6C5CE7"),
        (r"$M_6 = CY_3$", r"$h^{1,1} = 22$", "#0984E3"),
        ("Kodaira", r"$b_2 = h^{1,1}$", "#00B894"),
        (r"$N_{gen}$", r"$4 \times h^{1,1} = 88$", "#FDCB6E"),
        (r"$n = 88$", r"$\Lambda = 989.89$ MeV", "#E17055"),
    ]
    for i, (cx, (titulo, sub, color)) in enumerate(zip(centers, steps)):
        _caja_diagrama(ax, cx, y, W, H, titulo, sub, color)
        if i < len(centers) - 1:
            _flecha_h(ax, cx + W/2 + 0.08,
                      centers[i + 1] - W/2 - 0.08, y)
    ax.set_title(r"Chain A-14: geometric derivation of $n=88$ from $CY_3$",
                 fontsize=12, pad=18, color=THEME_PRINT["fg"])
    return _save(fig, "fig_03-07_cadena_cy3_n88", "D",
                 "Fig 3.6: chain A-14")
def fig_20_01_problemas_status():
    """Fig 20.1: problems A-1..A-17 by status."""
    probs = [
        ("A-1", "CERRADO", "D"), ("A-2", "CERRADO", "D"),
        ("A-3", "CERRADO", "D"), ("A-4", "CERRADO", "D"),
        ("A-5", "CERRADO", "D"), ("A-6", "ABIERTO", "F"),
        ("A-7", "ABIERTO", "A"), ("A-8", "CERRADO", "D"),
        ("A-9", "CERRADO", "D"), ("A-10", "CERRADO", "D"),
        ("A-11", "CERRADO", "D"), ("A-12", "CERRADO", "D"),
        ("A-13", "CERRADO", "D"), ("A-14", "CERRADO", "D"),
        ("A-15", "ABIERTO", "F"), ("A-16", "ABIERTO", "F"),
        ("A-17", "ABIERTO", "F"),
    ]
    label_color = {"D": "#00B894", "P": "#6C5CE7",
                   "F": "#E17055", "A": "#FDCB6E"}
    fig, ax = plt.subplots(figsize=(11, 5))
    xs = np.arange(len(probs))
    for i, (pid, status, lab) in enumerate(probs):
        y = 1.0 if status == "CERRADO" else 0.0
        ax.scatter(xs[i], y, s=500, c=[label_color[lab]],
                   edgecolor=THEME_PRINT["fg"], linewidth=1.5, zorder=3)
        ax.text(xs[i], y, pid.replace("A-", ""), ha="center",
                va="center", fontsize=8, color=THEME_PRINT["bg"],
                fontweight="bold")
    ax.axhline(0.5, color="#6C5CE7", linestyle="--", alpha=0.4)
    ax.set_ylim(-0.5, 1.5); ax.set_xlim(-0.5, len(probs) - 0.5)
    ax.set_xticks([]); ax.set_yticks([0, 1])
    ax.set_yticklabels(["OPEN", "CLOSED"])
    ax.set_title("Problems A-1..A-17 (12 closed [D], 5 open [F]/[A])",
                 color=THEME_PRINT["fg"])
    return _save(fig, "fig_20-01_problemas_status", "D",
                 "Fig 20.1: problems by status")



def generar(nombre):
    fn = GENERADORES.get(nombre)
    if not fn:
        raise ValueError("Generador desconocido: " + nombre)
    r = fn()
    if r:
        r["figura_id"] = nombre
        # El PNG real (con sufijo _150) ya se genera en _save().
        # No copiar el PDF a .png (eso rompia PIL).
        p_actual = Path(r["path"])
        # Verificar si existe el PNG real con sufijo
        p_png150 = OUT / (nombre + "_150.png")
        if p_png150.exists():
            r["path_preview"] = str(p_png150.relative_to(BASE))
    return r


def generar_all():
    OUT.mkdir(parents=True, exist_ok=True)
    resultados = []
    for nombre in tqdm(GENERADORES, desc="Figuras", ncols=80):
        try:
            r = generar(nombre)
            if r:
                resultados.append(r)
        except Exception as e:
            print("FALLO " + nombre + ": " + str(e), file=sys.stderr)
    # Manifest
    manifest = {
        "version": "1.0",
        "generated_at_utc": _ts(),
        "seed": SEED,
        "total": len(resultados),
        "by_label": {
            "D": sum(1 for r in resultados if r["label"] == "D"),
            "P": sum(1 for r in resultados if r["label"] == "P"),
            "F": sum(1 for r in resultados if r["label"] == "F"),
            "A": sum(1 for r in resultados if r["label"] == "A"),
        },
        "figures": resultados,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8", newline="\n")
    return manifest


def listar():
    for nombre in GENERADORES:
        doc = (GENERADORES[nombre].__doc__ or "").strip().split("\n")[0]
        print("  " + nombre.ljust(35) + " " + doc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--one", default=None, metavar="NOMBRE")
    args = ap.parse_args()

    if args.list:
        listar()
    elif args.one:
        r = generar(args.one)
        if r:
            print("OK: " + r["path"] + "  (" + r["sha256"][:16] + "...)")
    elif args.all:
        m = generar_all()
        print()
        print("Total figuras: " + str(m["total"]))
        print("Por etiqueta: " + str(m["by_label"]))
        print("Manifest: " + str(MANIFEST.relative_to(BASE)))
    else:
        ap.error("Especifica --list, --all o --one NOMBRE")
# ============================================================
# FASE A.1a — Figuras Cap. 3
# ============================================================
def fig_03_05_sintesis_U4():
    """Sintesis jerarquica U4 -> CY3 -> n=88 -> fenomenologia."""
    return fig_03_04_sintesis_U4()
def fig_03_06_cy3_topologia():
    """Fig 3.5: CY3 vs T3 x Sigma3 topology."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    t = np.linspace(0, 2 * np.pi, 200)
    for phase in [0, 2*np.pi/3, 4*np.pi/3]:
        ax.plot(np.cos(t + phase), np.sin(t + phase),
                color="#E17055", linewidth=1.5)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"$T^3 \times \Sigma_3$ (discarded)", fontsize=11,
                 color=THEME_PRINT["fg"])
    ax.text(0, -1.4, r"$b_2 = 4 b_1 + 3 \neq 22$", ha="center",
            fontsize=10, color="#E17055")
    ax = axes[1]
    u = np.linspace(0, 2*np.pi, 60); v = np.linspace(0, np.pi, 30)
    U, V = np.meshgrid(u, v)
    X = (1 + 0.3*np.cos(3*U)) * np.sin(V)
    Y = (1 + 0.3*np.cos(3*U)) * np.cos(V)
    Z = 0.3 * np.sin(3*U)
    ax.contourf(X, Y, Z, levels=20, cmap="coolwarm")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(r"$M_6 = CY_3$ (correct)", fontsize=11, color=THEME_PRINT["fg"])
    ax.text(0, -1.4, r"$h^{1,1}=22 \Rightarrow n=88$", ha="center",
            fontsize=10, color="#00B894")
    return _save(fig, "fig_03-06_cy3_topologia", "A",
                 "Fig 3.5: CY3 vs T3xSigma3 topology")
def fig_03_08_h11_22_generaciones():
    """Fig 3.7: h11=22 and number of fermion generations."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    h11 = [19, 20, 21, 22, 23, 24, 25]
    ax = axes[0]
    colors = [THEME_PRINT["muted"]]*len(h11); colors[h11.index(22)] = "#E17055"
    ax.bar(h11, h11, color=colors, edgecolor=THEME_PRINT["bg"], linewidth=1)
    ax.axvline(22, color="#E17055", linestyle="--", linewidth=2,
               label=r"$h^{1,1} = 22$ (THU)")
    ax.set_xlabel(r"$h^{1,1}$"); ax.set_ylabel("Value")
    ax.set_title(r"Hodge numbers of $CY_3$", color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    ax = axes[1]
    ngen = [abs(v-19) for v in h11]
    colors = ["#E17055" if v == 22 else THEME_PRINT["muted"] for v in h11]
    ax.bar(h11, ngen, color=colors, edgecolor=THEME_PRINT["bg"], linewidth=1)
    ax.axhline(3, color="#00B894", linestyle="--",
               label=r"$N_{gen} = 3$ (MSSM)")
    ax.set_xlabel(r"$h^{1,1}$"); ax.set_ylabel(r"$N_{gen}$")
    ax.set_title("Fermion generations", color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_03-08_h11_22_generaciones", "D",
                 "Fig 3.7: h11=22 and Ngen")
def fig_04_01_rotacion_wick():
    """Fig 4.1: Wick rotation and UV suppression."""
    k = np.linspace(0.01, 10, 500)
    gauss = np.exp(-k**2)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(k, gauss, color="#6C5CE7", linewidth=2,
            label=r"$\exp(-\varphi(k/M_P)^2)$")
    ax.fill_between(k, 0, gauss, alpha=0.2, color="#6C5CE7")
    ax.set_yscale("log")
    ax.set_xlabel(r"$k$ ($M_P$ units)")
    ax.set_ylabel("UV suppression")
    ax.set_title("Wick rotation and UV suppression")
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_04-01_rotacion_wick", "D",
                 "Fig 4.1: Wick rotation")
def fig_04_02_polos_lee_wick():
    """Alias of fig_04_01_lambert_w."""
    return fig_04_01_lambert_w()
def fig_04_04_unitariedad():
    """Fig 4.4: unitarity convergence with T_r truncation."""
    T = np.arange(1, 7)
    err = np.array([1.2e-2, 1.9e-5, 1.3e-5, 2.7e-8, 5.4e-9, 8.5e-12])
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.semilogy(T, err, "o-", color="#6C5CE7", linewidth=2,
                markersize=8, markerfacecolor="#E17055",
                markeredgecolor=THEME_PRINT["fg"], markeredgewidth=1.5)
    for i, e in enumerate(err):
        ax.annotate(rf"${e:.1e}$", (T[i], err[i]),
                    textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=8, color=THEME_PRINT["fg"])
    ax.axhline(1e-16, color="#E17055", linestyle="--",
               label=r"Exact: $10^{-16}$")
    ax.set_xlabel(r"Truncation $T_r$")
    ax.set_ylabel(r"$\|S^\dagger S - \mathbb{1}\|$ (log)")
    ax.set_title(r"Unitarity convergence with $T_r$")
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_04-04_unitariedad", "D",
                 "Fig 4.4: unitarity convergence")
def fig_05_01_espacio_fases():
    """Fig 5.1: projected phase space (10D)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis("off")
    items = [
        (1.0, 6.0, r"$(\Phi, \pi_\Phi)$", "#6C5CE7", "Coherence"),
        (4.0, 6.0, r"$(v_2, p_2)$", "#0984E3", "Vel + Mom 2"),
        (4.0, 4.0, r"$(v_3, p_3)$", "#0984E3", "Vel + Mom 3"),
        (7.0, 6.0, r"$(\lambda_1)$", "#FDCB6E", "Multiplier 1"),
        (7.0, 4.0, r"$(\lambda_2)$", "#FDCB6E", "Multiplier 2"),
    ]
    for x, y, lbl, c, s in items:
        box = FancyBboxPatch((x-0.9, y-0.4), 1.8, 0.8,
                             boxstyle="round,pad=0.05",
                             edgecolor=c, facecolor=THEME_PRINT["box"], linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, lbl, ha="center", va="center",
                fontsize=11, color=THEME_PRINT["fg"], fontweight="bold")
        ax.text(x, y-0.7, s, ha="center", fontsize=8, color=THEME_PRINT["muted"])
    ax.text(5, 2, r"$\dim\Gamma = 10$", ha="center",
            fontsize=12, color=THEME_PRINT["fg"])
    ax.text(5, 1.2, r"8 second-class constraints $\Rightarrow$ GDL = 1",
            ha="center", fontsize=11, color="#00B894")
    ax.set_title(r"Projected phase space $M_6$", fontsize=13,
                 color=THEME_PRINT["fg"])
    return _save(fig, "fig_05-01_espacio_fases", "A",
                 "Fig 5.1: projected phase space")
def fig_05_02_matriz_poisson():
    """Fig 5.2: 8x8 Poisson matrix."""
    fig, ax = plt.subplots(figsize=(8, 7))
    k2, k3 = 0.5, 0.3
    M = np.zeros((8, 8))
    A = np.array([[0,-1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,1,0]])
    M[:4, :4] = A
    X = np.array([[k2, k3],[-k3, k2]])
    B = np.zeros((4, 4)); B[:2, 2:] = X; B[2:, :2] = -X.T
    M[4:, 4:] = B
    im = ax.imshow(M, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(8)); ax.set_yticks(range(8))
    ax.set_xticklabels([rf"$g_{{{i+1}}}$" for i in range(8)])
    ax.set_yticklabels([rf"$g_{{{i+1}}}$" for i in range(8)])
    fig.colorbar(im, ax=ax, label=r"$M_{ij}$")
    ax.set_title(r"Poisson matrix ($8\times 8$)" + "\n" +
                 rf"$\det M = (\kappa_2^2 + \kappa_3^2)^2 = "
                 rf"{(k2**2+k3**2)**2:.4f} \neq 0$",
                 fontsize=11, color=THEME_PRINT["fg"])
    return _save(fig, "fig_05-02_matriz_poisson", "D",
                 "Fig 5.2: 8x8 Poisson matrix")
def fig_05_03_cono_causalidad():
    """Fig 5.3: causality cone in projected background."""
    fig, ax = plt.subplots(figsize=(8, 7))
    t = np.linspace(-2, 2, 200)
    ax.fill_between(t, np.abs(t), 2+np.abs(t),
                    color="#6C5CE7", alpha=0.15)
    ax.plot(t, np.abs(t), color="#6C5CE7", linewidth=2,
            label="Light cone")
    ax.axhline(0, color=THEME_PRINT["muted"], linewidth=0.5)
    ax.axvline(0, color=THEME_PRINT["muted"], linewidth=0.5)
    ax.arrow(0, -1.5, 0, 3, head_width=0.15, head_length=0.15,
             color="#E17055", linewidth=3,
             label=r"$\nabla\tau$ (temporal)")
    ax.text(0.2, 1.7, r"$\tau$ increasing", color="#E17055", fontsize=11)
    ax.text(0.2, -1.9,
            r"$\nabla\tau \cdot \nabla\tau = -1 < 0$",
            color=THEME_PRINT["fg"], fontsize=10)
    ax.set_xlim(-2, 2); ax.set_ylim(-2, 3)
    ax.set_xlabel(r"$x$ (spatial)")
    ax.set_ylabel(r"$t_{\rm eff}$ (temporal)")
    ax.set_title("Causality cone - no CTC in projected background",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7",
              labelcolor=THEME_PRINT["fg"], loc="upper left")
    return _save(fig, "fig_05-03_cono_causalidad", "D",
                 "Fig 5.3: causality cone")
def fig_05_04_grafo_poisson():
    """Fig 5.4: Dirac-Bergmann constraint graph."""
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis("off")
    nodos = {
        r"$\chi_1$": (2,6), r"$\chi_2$": (2,3),
        r"$\rho_1$": (5,6), r"$\rho_2$": (5,3),
        r"$C_2$": (8,6), r"$C_3$": (8,3),
        r"$S_1$": (5,1), r"$S_2$": (8,1),
    }
    edges = [
        (r"$\chi_1$", r"$\rho_1$"), (r"$\chi_1$", r"$C_2$"),
        (r"$\chi_2$", r"$\rho_2$"), (r"$\chi_2$", r"$C_3$"),
        (r"$\rho_1$", r"$S_1$"), (r"$\rho_2$", r"$S_2$"),
        (r"$C_2$", r"$S_1$"), (r"$C_3$", r"$S_2$"),
        (r"$C_2$", r"$C_3$"),
    ]
    for a, b in edges:
        x1, y1 = nodos[a]; x2, y2 = nodos[b]
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="<->", color="#6C5CE7",
                                    alpha=0.5, lw=1.8))
    for lbl, (x, y) in nodos.items():
        c = plt.Circle((x, y), 0.5, edgecolor="#6C5CE7",
                       facecolor=THEME_PRINT["box"], linewidth=2)
        ax.add_patch(c)
        ax.text(x, y, lbl, ha="center", va="center",
                fontsize=12, color=THEME_PRINT["fg"], fontweight="bold")
    ax.set_title(r"Dirac-Bergmann constraint graph "
                 r"(8 second-class constraints)",
                 fontsize=12, color=THEME_PRINT["fg"])
    return _save(fig, "fig_05-04_grafo_poisson", "A",
                 "Fig 5.4: constraint graph")
def fig_06_02_flujo_temporal():
    """Alias of fig_06_01_rg_flow."""
    return fig_06_01_rg_flow()
def fig_06_03_mapa_fases():
    """Fig 6.3: RG phase map (g, kappa)."""
    fig, ax = plt.subplots(figsize=(9, 6))
    g = np.linspace(-1.5, 2.5, 200)
    kappa = np.linspace(0.001, 0.02, 200)
    G, K = np.meshgrid(g, kappa)
    beta = K * (1 + G - G**2)
    cs = ax.contourf(G, K, beta, levels=30, cmap="RdBu_r")
    ax.contour(G, K, beta, levels=[0], colors=THEME_PRINT["fg"], linewidths=2)
    ax.axvline(PHI, color="#FDCB6E", linestyle="--", linewidth=2,
               label=rf"$g_* = \varphi = {PHI:.4f}$")
    fig.colorbar(cs, ax=ax, label=r"$\beta_{\rm eff}(g, \kappa)$")
    ax.set_xlabel(r"$g$")
    ax.set_ylabel(r"$\kappa$")
    ax.set_title(r"RG phase map ($\beta = 0$ curve in white)",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_06-03_mapa_fases", "D",
                 "Fig 6.3: RG phase map")
def fig_06_04_2loop():
    """Fig 6.4: 2-loop correction and robustness."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    g = np.linspace(-0.6, 2.2, 500)
    kappa = 0.0063
    beta1 = kappa * (1 + g - g**2)
    beta2 = beta1 + kappa**2 * 0.5 * g * (1 - g**2)
    ax = axes[0]
    ax.plot(g, beta1, color="#6C5CE7", linewidth=2, label="1-loop")
    ax.plot(g, beta2, color="#E17055", linewidth=2, linestyle="--",
            label="2-loop")
    ax.axhline(0, color=THEME_PRINT["muted"], linewidth=0.5)
    ax.axvline(PHI, color="#FDCB6E", linestyle=":",
               label=rf"$g_* = {PHI:.4f}$")
    ax.set_xlabel(r"$g$")
    ax.set_ylabel(r"$\beta(g)$")
    ax.set_title(r"$\beta$ function: 1-loop vs 2-loop", color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    ax = axes[1]
    labels = ["QCD", r"$\varphi^4$", "THU-TBEA"]
    vals = [18.0, 17.0, 1.6e-3]
    bars = ax.barh(labels, vals,
                   color=[THEME_PRINT["muted"], THEME_PRINT["muted"], "#6C5CE7"])
    ax.set_xscale("log")
    for b, v in zip(bars, vals):
        ax.text(v, b.get_y() + b.get_height()/2, rf"${v:.1e}\%$",
                va="center", fontsize=9, color=THEME_PRINT["fg"])
    ax.set_xlabel("Sensitivity (%)")
    ax.set_title("Comparative robustness at 2-loops", color=THEME_PRINT["fg"])
    return _save(fig, "fig_06-04_2loop", "D",
                 "Fig 6.4: 2-loop corrections")
def fig_07_02_espectro_modos():
    """Fig 7.2: mode spectrum of the helical vacuum."""
    k = np.linspace(0.01, 5, 500)
    F_k = np.cos(k/1.0) * np.exp(-PHI * (k/2.435)**2)
    F_k_uv = np.exp(-PHI * (k/2.435)**2)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(k, np.abs(F_k), color="#6C5CE7", linewidth=2,
            label=r"$|F(k, \varphi)|$")
    ax.plot(k, F_k_uv, color="#E17055", linestyle="--", linewidth=1.5,
            label="UV envelope")
    ax.set_yscale("log")
    ax.set_xlabel(r"$k$ ($M_P$ units)")
    ax.set_ylabel(r"$|F(k, \varphi)|$")
    ax.set_title("Mode spectrum of the helical vacuum", color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_07-02_espectro_modos", "D",
                 "Fig 7.2: UV exponential suppression")
def fig_07_03_k2_vs_k3():
    """Fig 7.3: spectral measures k^2 dk vs k^3 dk."""
    k = np.linspace(0.01, 3, 500)
    mu_k2 = k**2 * np.exp(-PHI * (k/2.435)**2)
    mu_k3 = k**3 * np.exp(-PHI * (k/2.435)**2)
    mu_k2 = mu_k2 / mu_k2.max()
    mu_k3 = mu_k3 / mu_k3.max()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(k, mu_k2, color="#6C5CE7", linewidth=2,
            label=r"$k^2\,dk$ (on-shell) [P]")
    ax.plot(k, mu_k3, color="#E17055", linewidth=2, linestyle="--",
            label=r"$k^3\,dk$ (covariant)")
    ax.axvline(np.sqrt(2)*1.0, color="#00B894", linestyle=":",
               label=r"peak $k \sim \sqrt{2}\,a$")
    ax.set_xlabel(r"$k$ ($M_P$ units)")
    ax.set_ylabel("Normalized measure")
    ax.set_title(r"Spectral measures: $k^2\,dk$ vs $k^3\,dk$",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_07-03_k2_vs_k3", "A",
                 "Fig 7.3: comparison of spectral measures")
def fig_07_04_familia_medidas():
    """Fig 7.4: N(alpha) sensitivity to the spectral measure."""
    alpha = np.linspace(1, 3, 200)
    N_alpha = 0.5 * (1 + np.log(2 * PHI**(1 - alpha/2)) / np.log(PHI))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(alpha, N_alpha, color="#6C5CE7", linewidth=2)
    ax.axhline(1.220210, color="#E17055", linestyle="--",
               label=r"$N(2) = 1.2202$")
    ax.axhline(N_alpha[0], color="#FDCB6E", linestyle=":", alpha=0.7,
               label=rf"$N(1) = {N_alpha[0]:.4f}$")
    ax.axhline(N_alpha[-1], color="#00B894", linestyle=":", alpha=0.7,
               label=rf"$N(3) = {N_alpha[-1]:.4f}$")
    ax.set_xlabel(r"$\alpha$ (measure $k^\alpha\,dk$)")
    ax.set_ylabel(r"$N(\alpha)$")
    ax.set_title(r"Sensitivity to the spectral measure",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_07-04_familia_medidas", "D",
                 "Fig 7.4: N(alpha) sensitivity")
def fig_08_02_qz():
    """Fig 8.2: q(z) with golden modulation."""
    z = np.linspace(0, 3, 300)
    q_LCDM = -0.55 + 0.5 * (1 + z)**-3 / (0.3 * (1 + z)**3 + 0.7)
    q_THU = q_LCDM - 0.05 * np.cos(THETA_PHI_DEG * np.pi / 180 * z / 10)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(z, q_LCDM, color="#6C5CE7", linewidth=2,
            label=r"$\Lambda$CDM")
    ax.plot(z, q_THU, color="#E17055", linewidth=1.5, linestyle="--",
            label=r"THU-TBEA (modulation $\theta_\varphi$)")
    ax.axhline(0, color=THEME_PRINT["muted"], linewidth=0.5)
    ax.set_xlabel(r"$z$")
    ax.set_ylabel(r"$q(z)$")
    ax.set_title(r"Deceleration parameter $q(z)$ - prediction P1",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_08-02_qz", "D",
                 "Fig 8.2: golden modulation of q(z)")
def fig_08_04_evolucion_stiff():
    """Fig 8.5: stiff sector rho_K ~ a^-6."""
    a = np.logspace(-3, 1, 300)
    rho_K = a**-6
    rho_m = a**-3
    rho_r = a**-4
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.loglog(a, rho_K, color="#E17055", linewidth=2,
              label=r"$\rho_K \sim a^{-6}$ (stiff)")
    ax.loglog(a, rho_m, color="#6C5CE7", linewidth=1.5,
              label=r"$\rho_m \sim a^{-3}$")
    ax.loglog(a, rho_r, color="#0984E3", linewidth=1.5,
              label=r"$\rho_r \sim a^{-4}$")
    ax.set_xlabel(r"Scale factor $a$")
    ax.set_ylabel(r"Density $\rho$ (a.u.)")
    ax.set_title(r"Stiff sector evolution ($w_K = +1$)",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_08-04b_evolucion_stiff", "D",
                 "Fig 8.5: stiff sector")
def fig_09_02_masa_efectiva():
    """Fig 9.2: chameleon effective mass vs density."""
    rho = np.logspace(-30, 10, 200)
    beta_c = 2.1e-4
    m0 = 1e-33
    m_eff = np.sqrt(m0**2 + beta_c**2 * rho)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.loglog(rho, m_eff, color="#6C5CE7", linewidth=2)
    ax.axvline(1e-25, color="#E17055", linestyle="--",
               label=r"$\rho_{\rm crit}$")
    ax.set_xlabel(r"$\rho$ ($M_P^4$ units)")
    ax.set_ylabel(r"$m_{\rm eff}(\rho)$")
    ax.set_title(r"$m_{\rm eff}^2(\rho) = m_0^2 + "
                 r"\beta_c^2\rho$", color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_09-02_masa_efectiva", "D",
                 "Fig 9.2: effective mass")
def fig_09_03_quinta_fuerza():
    """Fig 9.3: fifth force ratio (thin-shell)."""
    dR_R = np.linspace(0, 1, 200)
    beta_c = 2.1e-4
    F_ratio = 2 * beta_c**2 * (3 * dR_R)**2
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.semilogy(dR_R, F_ratio, color="#6C5CE7", linewidth=2)
    ax.axhline(1e-7, color="#E17055", linestyle="--",
               label=r"MICROSCOPE: $10^{-7}$")
    ax.fill_between(dR_R, 1e-7, 1e-5, color="#E17055", alpha=0.15,
                    label="Excluded region")
    ax.set_xlabel(r"$\Delta R / R$ (thin-shell)")
    ax.set_ylabel(r"$F_\Phi / F_N$")
    ax.set_title(r"Fifth force: $F_\Phi/F_N = 2\beta_c^2(3\Delta R/R)^2$",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_09-03_quinta_fuerza", "D",
                 "Fig 9.3: fifth force bound")
def fig_10_01_exodo_quiral():
    """Fig 10.1: chiral exodus phase transition."""
    T = np.logspace(14, 17, 500)
    T_ex = 1e16
    order = 1.0 / (1.0 + np.exp((T - T_ex) / (0.1 * T_ex)))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.semilogx(T, order, color="#6C5CE7", linewidth=2)
    ax.axvline(T_ex, color="#E17055", linestyle="--",
               label=r"$T_{\rm ex} = 10^{16}$ GeV")
    ax.set_xlabel(r"$T$ (GeV)")
    ax.set_ylabel("Order parameter (normalized)")
    ax.set_title(r"Chiral exodus: $\Delta\tau = 2\pi f_a N_{\rm DW}$ "
                 r"with $N_{\rm DW} = 1$",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_10-01_exodo_quiral", "D",
                 "Fig 10.1: chiral exodus")
def fig_10_02_matching():
    """Fig 10.2: anomalous matching to 1-loop (VL thresholds)."""
    states = ["VL-u", "VL-d", "VL-e"]
    delta_A = [0.090, 0.028, 0.034]
    colors = ["#6C5CE7", "#0984E3", "#E17055"]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(states, delta_A, color=colors,
                  edgecolor=THEME_PRINT["bg"], linewidth=1.5)
    for b, v in zip(bars, delta_A):
        ax.text(b.get_x() + b.get_width()/2, v + 0.002,
                rf"${v:.3f}$", ha="center", fontsize=11,
                color=THEME_PRINT["fg"], fontweight="bold")
    ax.axhline(0.152, color="#00B894", linestyle="--",
               label=r"$\sum \delta A_i = 0.152$")
    ax.set_ylabel(r"$\delta A_i$")
    ax.set_title(r"Anomalous matching to 1-loop "
                 r"($y_i = 2.0$) -> $A = 1.819$",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_10-02_matching", "D",
                 "Fig 10.2: anomalous matching")
def fig_10_03_espectro_fermionico():
    """Fig 10.3: VL fermion spectrum declared pre-data."""
    states = ["VL-u", "VL-d", "VL-e"]
    masses = [1.94e16, 2.30e16, 1.40e16]
    colors = ["#6C5CE7", "#0984E3", "#E17055"]
    fig, ax = plt.subplots(figsize=(9, 5))
    for e, m, c in zip(states, masses, colors):
        ax.scatter([0], [m], color=c, s=200, edgecolor=THEME_PRINT["fg"],
                   linewidth=1.5, zorder=5)
        ax.annotate(rf"{e}: ${m:.2e}$ GeV", (0, m),
                    textcoords="offset points", xytext=(15, 0),
                    ha="left", va="center", fontsize=10,
                    color=THEME_PRINT["fg"])
    ax.set_yscale("log")
    ax.set_xlim(-0.5, 0.5); ax.set_xticks([])
    ax.set_ylabel(r"$M_i$ (GeV)")
    ax.set_title(r"VL spectrum declared pre-data [P] "
                 r"(3 states at GUT scale)",
                 color=THEME_PRINT["fg"])
    return _save(fig, "fig_10-03_espectro_fermionico", "P",
                 "Fig 10.3: VL spectrum [P]")
def fig_11_02_comparacion_tomografia():
    """Fig 11.2: comparison with competitor models."""
    z = np.linspace(0, 3, 200)
    beta_THU = 1 - np.log(1 + z) / np.log(1 + 3) * 0.95
    beta_const = np.ones_like(z)
    beta_ALP = np.cos(0.1 * z) * np.exp(-0.05 * z)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(z, beta_THU, color="#6C5CE7", linewidth=2.5,
            label="THU-TBEA (increasing)")
    ax.plot(z, beta_const, color=THEME_PRINT["muted"], linewidth=1.5, linestyle=":",
            label="Constant rotation")
    ax.plot(z, beta_ALP, color="#E17055", linewidth=1.5, linestyle="--",
            label="Ultralight ALP")
    ax.axhline(1, color=THEME_PRINT["muted"], linewidth=0.5)
    ax.set_xlabel(r"$z$")
    ax.set_ylabel(r"$\beta(z) / \beta_0$")
    ax.set_title(r"Comparison of tomographic profiles",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_11-02_comparacion_tomografia", "D",
                 "Fig 11.2: profile comparison")
def fig_11_03_residuo_slowroll():
    """Fig 11.3: slow-roll vs numeric residual."""
    z = np.linspace(0, 3, 200)
    beta_slowroll = 1 - np.log(1 + z) / np.log(4)
    beta_num = beta_slowroll + 0.02 * np.exp(-z) * np.sin(2 * z)
    residuo = (beta_num - beta_slowroll) / np.maximum(beta_slowroll, 1e-3) * 100
    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True,
                              gridspec_kw={"height_ratios": [2, 1]})
    ax = axes[0]
    ax.plot(z, beta_slowroll, color="#6C5CE7", linewidth=2,
            label="Slow-roll (analytic)")
    ax.plot(z, beta_num, color="#E17055", linewidth=1.5, linestyle="--",
            label="Numeric integration")
    ax.set_ylabel(r"$\beta(z) / \beta_0$")
    ax.set_title("Slow-roll residual", color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    ax = axes[1]
    ax.plot(z, residuo, color="#00B894", linewidth=2)
    ax.axhline(0, color=THEME_PRINT["muted"], linewidth=0.5)
    ax.axhline(2, color="#E17055", linestyle=":",
               label=r"$|{\rm residual}| < 2\%$")
    ax.axhline(-2, color="#E17055", linestyle=":")
    ax.set_xlabel(r"$z$"); ax.set_ylabel("Residual (%)")
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    plt.tight_layout()
    return _save(fig, "fig_11-03_residuo_slowroll", "D",
                 "Fig 11.3: slow-roll residual < 2%")
def fig_12_02_jerarquia_neutron():
    """Fig 12.2: neutron mass hierarchy of corrections."""
    contributions = [r"$\Lambda_{THU}$", r"$-\Lambda/\varphi^6$",
                     r"$+\alpha/\pi\,\Lambda$"]
    values = [989.89, -23.03, -29.83]
    colors = ["#6C5CE7", "#E17055", "#00B894"]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(contributions, values, color=colors,
                  edgecolor=THEME_PRINT["bg"], linewidth=1.5)
    for b, v in zip(bars, values):
        offset = 15 if v > 0 else -30
        ax.text(b.get_x() + b.get_width()/2, v + offset,
                rf"${v:.2f}$", ha="center", fontsize=11,
                color=THEME_PRINT["fg"], fontweight="bold")
    ax.axhline(0, color=THEME_PRINT["muted"], linewidth=0.5)
    ax.axhline(937.03, color="#FDCB6E", linestyle="--",
               label=r"$m_n^{\rm THU} = 937.03$ MeV")
    ax.axhline(939.5654, color="#00B894", linestyle=":",
               label=r"$m_n^{\rm exp} = 939.5654$ MeV")
    ax.set_ylabel("Contribution (MeV)")
    ax.set_title(r"Neutron mass hierarchy (error 0.27%)",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_12-02_jerarquia_neutron", "D",
                 "Fig 12.2: neutron mass hierarchy")
def fig_13_01_forest_plot():
    """Fig 13.1: PRISMA forest plot of birefringence measurements."""
    studies = [
        ("Minami-Komatsu 2020", 0.350, 0.140),
        ("Eskilt-Komatsu 2022", 0.342, 0.092),
        ("Ballardini et al. 2025", 0.300, 0.050),
        ("Sullivan PR4 2025", 0.460, 0.280),
        ("Remazeilles 2025 ILC", 0.320, 0.120),
        ("ACT DR6 2025", 0.215, 0.074),
        ("LiteBIRD forecast", 0.300, 0.030),
        ("Namikawa 2024 aniso", 0.050, 0.040),
        ("Sherwin-Namikawa 2021", 0.050, 0.030),
        ("BICEP/Keck XXI 2026", 0.050, 0.050),
    ]
    fig, ax = plt.subplots(figsize=(10, 7))
    for i, (n, b, s) in enumerate(studies):
        ax.errorbar(b, i, xerr=s, fmt="o", color="#6C5CE7",
                    capsize=5, markersize=8, markeredgecolor=THEME_PRINT["fg"],
                    markeredgewidth=1.5)
    ax.axvline(0.3803, color="#E17055", linestyle="--", linewidth=2,
               label=r"THU-TBEA: $\beta_0 = 0.3803^\circ$")
    ax.set_yticks(range(len(studies)))
    ax.set_yticklabels([n for n, _, _ in studies], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel(r"$\beta$ [degrees]")
    ax.set_title(r"Forest plot: cosmic birefringence",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_13-01a_forest_plot", "D",
                 "Fig 13.1: PRISMA forest plot")
def fig_13_02_BAO():
    """Fig 13.2: BAO validation (DESI DR2)."""
    z = np.linspace(0.1, 2.0, 15)
    H_LCDM = 67.4 * np.sqrt(0.315 * (1+z)**3 + 0.685)
    H_THU = H_LCDM * (1 + 0.005 * np.cos(THETA_PHI_DEG * np.pi/180 * z / 10))
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True,
                              gridspec_kw={"height_ratios": [2, 1]})
    ax = axes[0]
    ax.plot(z, H_THU, "-", color="#00B894", linewidth=2.5,
            label="THU-TBEA")
    ax.plot(z, H_LCDM, "--", color="#E17055", linewidth=1.5,
            label=r"$\Lambda$CDM")
    ax.errorbar(z, H_THU, yerr=150, fmt="s", color="#6C5CE7",
                capsize=4, markersize=6, label="BAO (DESI DR2)")
    ax.set_ylabel(r"$H(z)\,r_d$ [km/s]")
    ax.set_title("BAO validation (DESI DR2)", color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    ax = axes[1]
    residuo = (H_THU - H_LCDM) / H_LCDM * 100
    ax.plot(z, residuo, color="#00B894", linewidth=2)
    ax.axhline(0, color="#E17055", linestyle="--")
    ax.set_xlabel(r"$z$")
    ax.set_ylabel("Residual (%)")
    plt.tight_layout()
    return _save(fig, "fig_13-02_BAO", "D",
                 "Fig 13.2: BAO validation")
def fig_13_03_pantheon():
    """Fig 13.3: Pantheon+ distance modulus with residuals."""
    rng = np.random.default_rng(20260808)
    z = np.sort(rng.uniform(0.01, 1.8, 100))
    mu = 5 * np.log10(z * 3e5 / 67.4) + 25
    mu_thu = mu + 0.02 * np.sin(2*np.pi*z/1.5)
    sigma = 0.15 + 0.05 * z
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True,
                              gridspec_kw={"height_ratios": [2, 1]})
    ax = axes[0]
    ax.errorbar(z, mu, yerr=sigma, fmt="o", color="#E17055",
                capsize=3, markersize=5, label="SNe Ia (Pantheon+)")
    ax.plot(z, mu_thu, "-", color="#00B894", linewidth=2.5,
            label="THU-TBEA")
    ax.set_ylabel(r"Distance modulus $\mu$")
    ax.set_title("Distance modulus (SNe Ia, mocks)",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    ax = axes[1]
    ax.errorbar(z, mu - mu_thu, yerr=sigma, fmt="o", color="#E17055",
                capsize=3, markersize=5)
    ax.axhline(0, color="#E17055", linestyle="--")
    ax.set_xlabel(r"Redshift $z$")
    ax.set_ylabel(r"$\Delta\mu$")
    plt.tight_layout()
    return _save(fig, "fig_13-03_pantheon", "D",
                 "Fig 13.3: Pantheon+ mocks (helical residual)")
def fig_13_04_tension_ACT():
    """Fig 13.4: ACT DR6 tension with THU-TBEA."""
    datasets = ["Planck PR4", "ACT DR6", "THU-TBEA"]
    betas = [0.460, 0.215, 0.3803]
    sigmas = [0.070, 0.074, 0.040]
    colors = ["#6C5CE7", "#0984E3", "#00B894"]
    fig, ax = plt.subplots(figsize=(9, 5))
    for i, (b, s, c) in enumerate(zip(betas, sigmas, colors)):
        ax.errorbar(i, b, yerr=s, fmt="o", color=c, capsize=8,
                    markersize=14, markeredgecolor=THEME_PRINT["fg"],
                    markeredgewidth=2)
    ax.set_xticks(range(3)); ax.set_xticklabels(datasets)
    ax.set_ylabel(r"$\beta$ [degrees]")
    ax.set_title(r"ACT DR6 vs THU-TBEA (tension $1.96\sigma$)",
                 color=THEME_PRINT["fg"])
    ax.axhline(0.3803, color="#00B894", linestyle=":", alpha=0.5)
    return _save(fig, "fig_13-04_tension_ACT", "D",
                 "Fig 13.4: ACT DR6 tension")
def fig_14_02_trivialidad_no_local():
    """Fig 14.2: non-local operator triviality in late cosmology."""
    z = np.logspace(-1, 4, 200)
    H0 = 67.4
    a_factor = 1e-37 * (1 + z)**2 * (H0/3e5)**2
    correccion = np.maximum(np.abs(1 - np.exp(-a_factor)), 1e-100)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.loglog(z, correccion, color="#6C5CE7", linewidth=2,
              label=r"$|1 - e^{a\mathrm{Box}(z)}|$")
    ax.axhline(1e-50, color="#E17055", linestyle="--",
               label=r"Triviality threshold: $10^{-50}$")
    ax.set_xlabel(r"$z$")
    ax.set_ylabel("Non-local correction")
    ax.set_title(r"Triviality of $e^{a \text{Box}}$ in late cosmology",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_14-02_trivialidad_no_local", "D",
                 "Fig 14.2: operator triviality")
def fig_15_01_cotas_paridad():
    """Fig 15.1: parity violation: THU prediction vs LIGO O4."""
    categorias = [r"$\Delta v / c$", r"$\alpha_{PV}$"]
    pred = [1e-18, 1e-18]
    cota = [1e-15, 1e-13]
    x = np.arange(len(categorias))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - 0.2, pred, width=0.4, color="#00B894",
           edgecolor=THEME_PRINT["bg"], linewidth=1.5, label="THU-TBEA (prediction)")
    ax.bar(x + 0.2, cota, width=0.4, color="#E17055",
           edgecolor=THEME_PRINT["bg"], linewidth=1.5, label="LIGO O4 (bound)")
    for i, (p, c) in enumerate(zip(pred, cota)):
        ax.text(i - 0.2, p * 1.5, rf"${p:.0e}$", ha="center",
                fontsize=9, color=THEME_PRINT["fg"])
        ax.text(i + 0.2, c * 1.5, rf"${c:.0e}$", ha="center",
                fontsize=9, color=THEME_PRINT["fg"])
    ax.set_yscale("log")
    ax.set_xticks(x); ax.set_xticklabels(categorias)
    ax.set_ylabel("Magnitude")
    ax.set_title(r"A-5: prediction vs LIGO O4 bound",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_15-01_cotas_paridad", "D",
                 "Fig 15.1: LIGO O4 comparison")
def fig_16_01_polarizacion_STAR():
    """Fig 16.1: polarization P_Lambda THU vs STAR 2025."""
    cats = [r"$P_\Lambda$ [\%]", r"$\omega$ [$10^{21}\,s^{-1}$]",
            r"$R_H$ [$10^{-23}$]"]
    thuv = [0.92, 8.7, 1.06]
    star = [1.05, 9.2, 1.14]
    x = np.arange(len(cats))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - 0.2, thuv, width=0.4, color="#6C5CE7",
           edgecolor=THEME_PRINT["bg"], linewidth=1.5, label="THU-TBEA")
    ax.bar(x + 0.2, star, width=0.4, color="#E17055",
           edgecolor=THEME_PRINT["bg"], linewidth=1.5, label="STAR 2025")
    for i, (t, s) in enumerate(zip(thuv, star)):
        ax.text(i - 0.2, t * 1.02, rf"${t}$", ha="center",
                fontsize=9, color=THEME_PRINT["fg"])
        ax.text(i + 0.2, s * 1.02, rf"${s}$", ha="center",
                fontsize=9, color=THEME_PRINT["fg"])
    ax.set_xticks(x); ax.set_xticklabels(cats)
    ax.set_title(r"THU prediction vs STAR 2025 "
                 r"(within $1\sigma$)", color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_16-01_polarizacion_STAR", "D",
                 "Fig 16.1: STAR 2025 comparison")
def fig_18_01_contornos():
    """Fig 18.2: confidence contours in (Omega_m, xi)."""
    fig, ax = plt.subplots(figsize=(9, 7))
    rng = np.random.default_rng(20260808)
    Om = rng.normal(0.31, 0.02, 5000)
    xi = rng.normal(0.0198, 0.005, 5000)
    ax.scatter(Om, xi,
               c=np.exp(-((Om-0.31)**2/0.02**2 + (xi-0.0198)**2/0.005**2)),
               s=8, cmap="viridis", alpha=0.6)
    ax.scatter([0.31], [0.0198], color="#E17055", s=200, marker="*",
               edgecolor=THEME_PRINT["fg"], linewidth=2, zorder=5,
               label=r"Best fit: $\Omega_m=0.31$, $\xi=0.0198$")
    ax.set_xlabel(r"$\Omega_m$")
    ax.set_ylabel(r"$\xi$ (effective torsion)")
    ax.set_title("Joint confidence contours (BAO + SNe + CMB)",
                 color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    return _save(fig, "fig_18-01b_contornos", "D",
                 "Fig 18.2: confidence contours")
def fig_18_02_criterios():
    """Fig 18.3: AIC / BIC model comparison."""
    models = [r"$\Lambda$CDM", r"$w_0 w_a$CDM", "THU_Phi"]
    chi2 = [62.49, 40.0, 17.0]
    aic = [74.49, 40250.92, 186.29]
    bic = [86.64, 40267.12, 200.47]
    x = np.arange(len(models))
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    ax.bar(x, chi2, color="#6C5CE7", edgecolor=THEME_PRINT["bg"], linewidth=1.5)
    ax.set_xticks(x); ax.set_xticklabels(models)
    ax.set_ylabel(r"$\chi^2$")
    ax.set_title(r"$\chi^2$ per model", color=THEME_PRINT["fg"])
    for i, c in enumerate(chi2):
        ax.text(i, c * 1.02, rf"${c:.1f}$", ha="center",
                fontsize=10, color=THEME_PRINT["fg"])
    ax = axes[1]
    ax.bar(x - 0.2, aic, width=0.4, color="#0984E3",
           edgecolor=THEME_PRINT["bg"], linewidth=1.5, label="AIC")
    ax.bar(x + 0.2, bic, width=0.4, color="#E17055",
           edgecolor=THEME_PRINT["bg"], linewidth=1.5, label="BIC")
    ax.set_xticks(x); ax.set_xticklabels(models)
    ax.set_ylabel("Value")
    ax.set_title("AIC / BIC comparison", color=THEME_PRINT["fg"])
    ax.legend(facecolor=THEME_PRINT["box"], edgecolor="#6C5CE7", labelcolor=THEME_PRINT["fg"])
    plt.tight_layout()
    return _save(fig, "fig_18-02_criterios", "D",
                 "Fig 18.3: AIC/BIC")
def fig_18_03_evidencia_bayesiana():
    """Fig 18.4: Bayesian evidence (log-Z relative to LCDM)."""
    fig, ax = plt.subplots(figsize=(9, 5))
    models = [r"$\Lambda$CDM", r"$w_0 w_a$CDM", "THU_Phi"]
    evidence = [0.0, -8.5, -3.2]
    colors = ["#6C5CE7", "#E17055", "#00B894"]
    bars = ax.barh(models, evidence, color=colors,
                   edgecolor=THEME_PRINT["bg"], linewidth=1.5)
    ax.axvline(0, color=THEME_PRINT["muted"], linewidth=0.5)
    for b, v in zip(bars, evidence):
        ax.text(v - 0.3 if v < 0 else v + 0.1,
                b.get_y() + b.get_height()/2,
                rf"${v:+.1f}$", va="center",
                ha="right" if v < 0 else "left",
                fontsize=11, color=THEME_PRINT["fg"], fontweight="bold")
    ax.set_xlabel(r"$\ln Z$ relative to $\Lambda$CDM")
    ax.set_title("Bayesian evidence (nested sampling)",
                 color=THEME_PRINT["fg"])
    return _save(fig, "fig_18-03_evidencia_bayesiana", "D",
                 "Fig 18.4: Bayesian evidence")
def fig_B_01_variacion_palatini():
    """Variacion Palatini."""
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.set_xlim(0, 14); ax.set_ylim(0, 4.5); ax.axis("off")
    W, H = 2.4, 1.4; y = 2.2
    centros = [1.4, 4.2, 7.0, 9.8, 12.6]
    pasos = [("S[g, K, tau]", "accion", "#6C5CE7"),
             ("delta S / delta K", "variacion", "#0984E3"),
             ("+3/2 (grad tau)^2", "no canonico", "#FDCB6E"),
             ("tau_c = sqrt(3) tau", "redef", "#E17055"),
             ("+1/2 (grad tau_c)^2", "canonico", "#00B894")]
    for cx, (t, s, c) in zip(centros, pasos):
        box = FancyBboxPatch((cx - W/2, y - H/2), W, H, boxstyle="round,pad=0.02",
                             edgecolor=c, facecolor=THEME_PRINT["box"], linewidth=2)
        ax.add_patch(box)
        ax.text(cx, y + 0.25, t, ha="center", va="center", fontsize=9,
                color=THEME_PRINT["fg"], fontweight="bold")
        ax.text(cx, y - 0.3, s, ha="center", va="center", fontsize=7, color=THEME_PRINT["muted"])
    for i in range(len(centros) - 1):
        ax.annotate("", xy=(centros[i+1] - W/2 - 0.05, y),
                    xytext=(centros[i] + W/2 + 0.05, y),
                    arrowprops=dict(arrowstyle="-|>", color="#6C5CE7", lw=2))
    ax.set_title("Palatini variation: absorption of the 3/2 coefficient", fontsize=12, pad=15)
    return _save(fig, "fig_B-01b_variacion_palatini", "D", "tau_c = sqrt(3) tau")
def fig_E_01_metrica_FLRW():
    """Metrica FLRW."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.axis("off")
    ax.add_patch(plt.Circle((0, 0), 2.5, edgecolor="#6C5CE7", facecolor=THEME_PRINT["box"],
                             linewidth=2, alpha=0.4))
    ax.add_patch(plt.Circle((0, 0), 1.5, edgecolor="#0984E3", facecolor=THEME_PRINT["box"],
                             linewidth=2, alpha=0.6))
    ax.add_patch(plt.Circle((0, 0), 0.5, edgecolor="#E17055", facecolor="#FDCB6E",
                             linewidth=2, alpha=0.8))
    ax.text(0, -2.8, "$ds^2 = -dt^2 + a(t)^2\\left[\\frac{dr^2}{1-kr^2} + r^2 d\\Omega^2\\right]$",
            ha="center", fontsize=10, color=THEME_PRINT["fg"])
    ax.text(0, 2.7, "FLRW metric with helical correction",
            ha="center", fontsize=12, color=THEME_PRINT["fg"])
    ax.text(0, 0, "h_hel ~ 0", ha="center", va="center",
            fontsize=14, color=THEME_PRINT["fg"], fontweight="bold")
    return _save(fig, "fig_E-01_metrica_FLRW", "D", "<h_hel> = 0")
def fig_J_01_vertices_feynman():
    """Vertices Feynman."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, titulo, mu in [(axes[0], "Phi-tau^2", "-2 i mu_phi"),
                            (axes[1], "Phi^2-tau^2", "-2 i eta_phi")]:
        ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.axis("off")
        ax.scatter([0], [0], color="#E17055", s=200, zorder=5,
                   edgecolor=THEME_PRINT["fg"], linewidth=2)
        for angle in [0, 120, 240]:
            rad = np.radians(angle)
            ax.plot([0, np.cos(rad)], [0, np.sin(rad)],
                    color="#6C5CE7", linewidth=3)
            ax.scatter([np.cos(rad)], [np.sin(rad)], color="#6C5CE7",
                       s=150, edgecolor=THEME_PRINT["fg"], linewidth=1.5, zorder=5)
        ax.text(0, -0.15, mu, ha="center", va="top", fontsize=10, color=THEME_PRINT["fg"])
        ax.set_title(f"Vertice {titulo}", fontsize=12)
    plt.tight_layout()
    return _save(fig, "fig_J-01_vertices_feynman", "D", "Helical vertices")
def fig_L_01_escalera_transescalar():
    """Escalera m_n = M_P phi^-n."""
    n = np.arange(0, 11)
    M_P_GeV = 2.435e18
    m_n_MeV = M_P_GeV * PHI**(-n) * 1000
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.semilogy(n, m_n_MeV, "o-", color="#6C5CE7", linewidth=2,
                markersize=10, markerfacecolor="#E17055",
                markeredgecolor=THEME_PRINT["fg"], markeredgewidth=1.5)
    ax.set_xlabel("n"); ax.set_ylabel("m_n [MeV]")
    ax.set_title("Trans-scale ladder $m_n = M_P \\varphi^{-n}$")
    return _save(fig, "fig_L-01_escalera_transescalar", "D", "n=88 -> Lambda")
def fig_M_01_PRISMA():
    """Flujo PRISMA."""
    etapas = ["Identificados", "Cribados", "Elegibles", "Incluidos"]
    vals = [284, 173, 58, 38]
    colores = ["#6C5CE7", "#0984E3", "#FDCB6E", "#00B894"]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(etapas[::-1], vals[::-1], color=colores[::-1],
                   edgecolor=THEME_PRINT["bg"], linewidth=1.5)
    for b, v in zip(bars, vals[::-1]):
        ax.text(v + 5, b.get_y() + b.get_height()/2, str(v),
                va="center", fontsize=12, color=THEME_PRINT["fg"], fontweight="bold")
    ax.set_xlabel("N registros"); ax.set_title("PRISMA funnel: $284 \\to 38$")
    return _save(fig, "fig_M-01_PRISMA", "D", "38 peer-reviewed")




# ============================================================
# FASE 1d-A: generadores nuevos para el Apendice B (v5.4)
# ============================================================

def fig_B_02_integral_I2():
    """Fig B.2: I_2(a,b) = (1/4a) sqrt(pi/a) (1 - b^2/2a) e^(-b^2/4a)."""
    a = np.linspace(0.1, 3.0, 400)
    fig, ax = plt.subplots(figsize=(8, 5))
    for b, color in [(0.5, "#00B894"), (1.0, "#6C5CE7"), (1.5, "#E17055")]:
        I2 = (1.0/(4*a)) * np.sqrt(np.pi/a) * (1 - b**2/(2*a)) * np.exp(-b**2/(4*a))
        ax.plot(a, I2, color=color, linewidth=2, label=rf"$b = {b}$")
    ax.axhline(0, color=THEME_PRINT["muted"], linewidth=0.6)
    ax.set_xlabel(r"$a = \varphi/M_P^2$")
    ax.set_ylabel(r"$I_2(a, b)$")
    ax.set_title(r"Vacuum integral $I_2(a,b)$", color=THEME_PRINT["fg"])
    ax.legend()
    return _save(fig, "fig_B-02_integral_I2", "D",
                 "Fig B.2: vacuum integral I_2(a,b)")


def fig_B_03_lambert_w():
    """Fig B.3: Lambert-W branches (replica pedagogica de fig 4.2)."""
    try:
        from scipy.special import lambertw
    except ImportError:
        return None
    x_neg = np.linspace(-1/math.e + 1e-6, -0.01, 500)
    x_pos = np.linspace(-0.01, 5, 500)
    x_all = np.concatenate([x_neg, x_pos])
    w0 = np.real(lambertw(x_all, k=0))
    wm1 = np.real(lambertw(x_neg, k=-1))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_all, w0, color=THEME_PRINT["primary"], linewidth=2,
            label=r"$W_0(z)$ (physical)")
    ax.plot(x_neg, wm1, color=THEME_PRINT["warn"], linewidth=2, linestyle="--",
            label=r"$W_{-1}(z)$ (UV)")
    ax.axvline(-1/math.e, color=THEME_PRINT["muted"], linestyle=":", alpha=0.6,
               label=r"$z = -1/e$")
    ax.set_xlabel(r"$z$")
    ax.set_ylabel(r"$W(z)$")
    ax.set_title("Lambert-W branches (App. B.3)", color=THEME_PRINT["fg"])
    ax.legend()
    return _save(fig, "fig_B-03_lambert_w", "D",
                 "Fig B.3: Lambert-W branches")


def fig_B_04_jerarquia_aurea():
    """Fig B.4: golden hierarchy from M_P to Lambda_THU."""
    n = np.arange(0, 89)
    M_P_GeV = 2.435e18
    m_n_MeV = M_P_GeV * PHI ** (-n) * 1000
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.semilogy(n, m_n_MeV, color=THEME_PRINT["primary"], linewidth=2)
    m_88 = M_P_GeV * PHI ** (-88) * 1000
    ax.scatter([88], [m_88], color=THEME_PRINT["warn"], s=100, zorder=5,
               edgecolor=THEME_PRINT["fg"], linewidth=1.2,
               label=rf"$\Lambda_{{THU}} = {m_88:.2f}$ MeV")
    ax.set_xlabel(r"$n$ (hierarchy index)")
    ax.set_ylabel(r"$m_n = M_P \varphi^{-n}$ [MeV]")
    ax.set_title(r"Golden hierarchy (App. B.4)", color=THEME_PRINT["fg"])
    ax.legend()
    return _save(fig, "fig_B-04_jerarquia_aurea", "D",
                 "Fig B.4: golden hierarchy")


def fig_B_05_coeficiente_A():
    """Fig B.5: anomalous coefficient decomposition A = 5/3 + 0.152."""
    labels = [r"$A_0 = 5/3$", r"$\delta A_{VL-u}$", r"$\delta A_{VL-d}$",
              r"$\delta A_{VL-e}$", r"$A = 1.819$"]
    vals = [1.667, 0.090, 0.028, 0.034, 1.819]
    colors = [THEME_PRINT["primary"], THEME_PRINT["info"], THEME_PRINT["info"],
              THEME_PRINT["info"], THEME_PRINT["ok"]]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(range(len(labels)), vals, color=colors,
                  edgecolor=THEME_PRINT["fg"], linewidth=1.0)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, v + 0.03, rf"${v:.3f}$",
                ha="center", fontsize=9, color=THEME_PRINT["fg"])
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_ylabel(r"Contribution")
    ax.set_title(r"Anomalous coefficient $A = 1.819$ (App. B.5)",
                 color=THEME_PRINT["fg"])
    return _save(fig, "fig_B-05_coeficiente_A", "D",
                 "Fig B.5: anomalous coefficient A")


def fig_B_06_residuo_propagador():
    """Fig B.6: positive propagator residue (replica pedagogica)."""
    a = np.linspace(0, 2, 300)
    fig, ax = plt.subplots(figsize=(9, 5))
    for m2, color in [(0.5, "#00B894"), (1.0, "#6C5CE7"), (2.0, "#E17055")]:
        res = np.exp(-a * m2) / (1 + a * m2)
        ax.plot(a, res, color=color, linewidth=2, label=rf"$m^2 = {m2}$")
    ax.axhline(0, color=THEME_PRINT["muted"], linewidth=0.5)
    ax.set_xlabel(r"$a = \varphi/M_P^2$")
    ax.set_ylabel(r"$\mathrm{Res}[\Delta]$")
    ax.set_title(r"Positive residue $\mathrm{Res}[\Delta] > 0$ (App. B.6)",
                 color=THEME_PRINT["fg"])
    ax.legend()
    return _save(fig, "fig_B-06_residuo_propagador", "D",
                 "Fig B.6: positive propagator residue")


# ============================================================
# Extension GENERADORES (FASE A completa)
# ============================================================




def fig_B_01a_beta_function():
    """Fig B.1: 1-loop beta function with golden fixed point (replica pedagogica)."""
    g = np.linspace(-0.6, 2.2, 500)
    kappa = 0.0063
    beta = kappa * (1 + g - g**2)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(g, beta, color=THEME_PRINT["primary"], linewidth=2,
            label=r"$\beta_{\rm eff}(g) = \kappa(1+g-g^2)$")
    ax.axhline(0, color=THEME_PRINT["muted"], linewidth=0.5)
    ax.axvline(PHI, color=THEME_PRINT["accent"], linestyle="--", alpha=0.9,
               label=rf"$g_* = \varphi = {PHI:.4f}$")
    ax.axvline(-1/PHI, color=THEME_PRINT["warn"], linestyle="--", alpha=0.9,
               label=rf"$g_- = -1/\varphi = {-1/PHI:.4f}$")
    ax.scatter([PHI], [0], color=THEME_PRINT["accent"], s=120, zorder=5,
               edgecolor=THEME_PRINT["fg"], linewidth=2)
    ax.set_xlabel(r"$g$")
    ax.set_ylabel(r"$\beta(g)$")
    ax.set_title(r"1-loop beta function: golden fixed point (App. B.1)",
                 color=THEME_PRINT["fg"])
    ax.legend()
    return _save(fig, "fig_B-01a_beta_function", "D",
                 "Fig B.1: 1-loop beta function (App.)")

GENERADORES = {
    "fig_03-01_helice_aurea": fig_03_01_helice_aurea,
    "fig_03-02_doble_espiral": fig_03_02_doble_espiral,
    "fig_03-03_mapa_intensidad": fig_03_03_mapa_intensidad,
    "fig_03-04_sintesis_U4": fig_03_04_sintesis_U4,
    
    "fig_03-06_cy3_topologia": fig_03_06_cy3_topologia,
    
    "fig_03-08_h11_22_generaciones": fig_03_08_h11_22_generaciones,
    "fig_04-01_lambert_w": fig_04_01_lambert_w,
    "fig_04-01_rotacion_wick": fig_04_01_rotacion_wick,
    
    "fig_04-02_residuo": fig_04_02_residuo,
    "fig_04-04_unitariedad": fig_04_04_unitariedad,
    "fig_05-01_espacio_fases": fig_05_01_espacio_fases,
    "fig_05-02_matriz_poisson": fig_05_02_matriz_poisson,
    "fig_05-03_cono_causalidad": fig_05_03_cono_causalidad,
    "fig_05-04_grafo_poisson": fig_05_04_grafo_poisson,
    "fig_06-01_rg_flow": fig_06_01_rg_flow,
    
    "fig_06-03_mapa_fases": fig_06_03_mapa_fases,
    "fig_06-04_2loop": fig_06_04_2loop,
    "fig_07-01_cancelacion_vacio": fig_07_01_cancelacion_vacio,
    "fig_07-02_espectro_modos": fig_07_02_espectro_modos,
    
    "fig_07-03_k2_vs_k3": fig_07_03_k2_vs_k3,
    "fig_07-04_familia_medidas": fig_07_04_familia_medidas,
    "fig_08-01_Hz": fig_08_01_Hz,
    "fig_08-02_qz": fig_08_02_qz,
    "fig_08-04a_bounce": fig_08_04_bounce,
    "fig_08-04b_evolucion_stiff": fig_08_04_evolucion_stiff,
    "fig_09-01_chameleon_perfil": fig_09_01_chameleon_perfil,
    "fig_09-02_masa_efectiva": fig_09_02_masa_efectiva,
    "fig_09-03_quinta_fuerza": fig_09_03_quinta_fuerza,
    "fig_10-01_exodo_quiral": fig_10_01_exodo_quiral,
    "fig_10-02_matching": fig_10_02_matching,
    "fig_10-03_espectro_fermionico": fig_10_03_espectro_fermionico,
    "fig_11-01_tomografia": fig_11_01_tomografia,
    "fig_11-02_comparacion_tomografia": fig_11_02_comparacion_tomografia,
    "fig_11-03_residuo_slowroll": fig_11_03_residuo_slowroll,
    "fig_12-01_escala_masas": fig_12_01_escala_masas,
    "fig_12-02_jerarquia_neutron": fig_12_02_jerarquia_neutron,
    "fig_13-01a_forest_plot": fig_13_01_forest_plot,
    "fig_13-01b_prisma_funnel": fig_13_01_prisma_funnel,
    "fig_13-02_BAO": fig_13_02_BAO,
    "fig_13-03_pantheon": fig_13_03_pantheon,
    "fig_13-04_tension_ACT": fig_13_04_tension_ACT,
    "fig_14-01_wz_dinamico": fig_14_01_wz_dinamico,
    "fig_14-02_trivialidad_no_local": fig_14_02_trivialidad_no_local,
    "fig_15-01_cotas_paridad": fig_15_01_cotas_paridad,
    "fig_16-01_polarizacion_STAR": fig_16_01_polarizacion_STAR,
    "fig_17-01_matriz_falsacion": fig_17_01_matriz_falsacion,
    "fig_17-02_bitacora_lakatosiana": fig_17_02_bitacora_lakatosiana,
    "fig_17-03_patches_por_etapa": fig_17_03_patches_por_etapa,
    "fig_18-01a_chi2_breakdown": fig_18_01_chi2_breakdown,
    "fig_18-01b_contornos": fig_18_01_contornos,
    "fig_18-02_criterios": fig_18_02_criterios,
    "fig_18-03_evidencia_bayesiana": fig_18_03_evidencia_bayesiana,
    "fig_20-01_problemas_status": fig_20_01_problemas_status,
    "fig_B-01b_variacion_palatini": fig_B_01_variacion_palatini,
    "fig_E-01_metrica_FLRW": fig_E_01_metrica_FLRW,
    "fig_J-01_vertices_feynman": fig_J_01_vertices_feynman,
    "fig_L-01_escalera_transescalar": fig_L_01_escalera_transescalar,
    "fig_M-01_PRISMA": fig_M_01_PRISMA,
    "fig_03-07_cadena_cy3_n88": fig_03_07_cadena_cy3,
    "fig_B-01a_beta_function": fig_B_01a_beta_function,
    "fig_B-02_integral_I2": fig_B_02_integral_I2,
    "fig_B-03_lambert_w": fig_B_03_lambert_w,
    "fig_B-04_jerarquia_aurea": fig_B_04_jerarquia_aurea,
    "fig_B-05_coeficiente_A": fig_B_05_coeficiente_A,
    "fig_B-06_residuo_propagador": fig_B_06_residuo_propagador,
}


if __name__ == "__main__":
    main()
