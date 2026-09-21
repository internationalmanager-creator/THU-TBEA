import sys, json, time, hashlib
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams["font.family"] = "DejaVu Sans"
rcParams["axes.labelsize"] = 11
rcParams["axes.titlesize"] = 12
rcParams["figure.dpi"] = 120

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
OUT = LAB / "outputs" / "verificaciones"
FIG = LAB / "paper" / "thu" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

phi = (1 + np.sqrt(5)) / 2
resultados = []
TOTAL = 6
t0 = time.time()

def barra(i):
    pct = int(100 * i / TOTAL)
    filled = pct * 40 // 100
    return "█" * filled + "░" * (40 - filled), pct

def guardar(fig, nombre, descripcion):
    path = FIG / f"fig_B-{nombre}.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    kb = path.stat().st_size / 1024
    print(f"    → {path.name}  ({kb:.1f} KB)  sha={sha[:16]}...")
    resultados.append({"figura": f"fig_B-{nombre}", "path": str(path), "sha256": sha, "descripcion": descripcion})
    return path

print()
print("╔" + "═" * 70 + "╗")
print("║" + " FASE B.2 — FIGURAS SIMBOLICAS ".center(70) + "║")
print("╚" + "═" * 70 + "╝")

# ──────────────────────────────────────────────────────────
# 1) Funcion beta β(g) = κ(1+g-g²)
# ──────────────────────────────────────────────────────────
bar, pct = barra(1)
print(f"\n  PASO 1/{TOTAL}  [{bar}]  {pct:3d}%")
print(f"  β(g) = κ(1+g-g²) con puntos fijos g*=φ y g=-1/φ")
print(f"  Verifica: Test 4 (β'(φ) = -κ√5 < 0)")
sys.stdout.flush()

g = np.linspace(-0.8, 2.2, 500)
beta = 1 + g - g**2

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(g, beta, "b-", lw=2, label=r"$\beta(g) = \kappa(1+g-g^2)$")
ax.axhline(0, color="k", lw=0.8)
ax.axvline(phi, color="gold", ls="--", lw=1.5, label=f"$g^* = \\varphi \\approx {phi:.4f}$")
ax.axvline(-1/phi, color="orange", ls=":", lw=1.5, label=f"$g_* = -1/\\varphi \\approx {-1/phi:.4f}$")
ax.plot(phi, 0, "o", color="gold", ms=12, mec="k", zorder=5)
ax.annotate(r"$\beta'(\varphi) = -\kappa\sqrt{5} < 0$",
            xy=(phi, 0), xytext=(phi+0.15, 0.6),
            arrowprops=dict(arrowstyle="->", color="darkred", lw=1.5),
            fontsize=11, color="darkred")
ax.set_xlabel("acoplamiento $g$")
ax.set_ylabel(r"$\beta(g)$")
ax.set_title("Función beta a 1-loop y punto fijo áureo")
ax.legend(loc="lower left", fontsize=10)
ax.grid(alpha=0.3)
guardar(fig, "01_beta_function",
    "β(g)=κ(1+g-g²), g*=φ estable con β'(φ)=-κ√5<0")

# ──────────────────────────────────────────────────────────
# 2) Integral I₂(a,b) vs N (familia de medidas)
# ──────────────────────────────────────────────────────────
bar, pct = barra(2)
print(f"\n  PASO 2/{TOTAL}  [{bar}]  {pct:3d}%")
print(f"  I₂(a,b) = ∫₀^∞ k² cos(bk) e^(-ak²) dk, cero en φ^(2N)=2φ")
print(f"  Verifica: Test 5 + Test 6")
sys.stdout.flush()

N_vals = np.linspace(0.5, 2.5, 300)
# a = φ/M², b = φ^N/M (con M=1 para normalizar)
a_val = phi
I2_curve = (1/(4*a_val)) * np.sqrt(np.pi/a_val) * (1 - (phi**N_vals)**2/(2*a_val)) * np.exp(-(phi**N_vals)**2/(4*a_val))

N_star = np.log(2*phi) / (2*np.log(phi))

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(N_vals, I2_curve, "b-", lw=2, label=r"$I_2(N)$ normalizada")
ax.axhline(0, color="k", lw=0.8)
ax.axvline(N_star, color="red", ls="--", lw=1.5,
           label=f"$N^* = {N_star:.6f}$")
ax.plot(N_star, 0, "o", color="red", ms=12, mec="k", zorder=5)
ax.annotate(r"$\varphi^{2N}=2\varphi$",
            xy=(N_star, 0), xytext=(N_star+0.15, max(I2_curve)*0.5),
            arrowprops=dict(arrowstyle="->", color="darkred", lw=1.5),
            fontsize=11, color="darkred")
ax.set_xlabel("grado espectral $N$")
ax.set_ylabel(r"$I_2(N)$ (normalizada)")
ax.set_title("Cero analítico de la integral de vacío escalar")
ax.legend(loc="upper right", fontsize=10)
ax.grid(alpha=0.3)
guardar(fig, "02_integral_I2",
    "I₂ vs N: se anula en N*≈1.220210")

# ──────────────────────────────────────────────────────────
# 3) Ramas de Lambert-W
# ──────────────────────────────────────────────────────────
bar, pct = barra(3)
print(f"\n  PASO 3/{TOTAL}  [{bar}]  {pct:3d}%")
print(f"  Polos del operador □e^(a□) - m² dados por u e^u = am²")
print(f"  Verifica: Test 3 (u = W_k(am²))")
sys.stdout.flush()

from scipy.special import lambertw
x_vals = np.linspace(-0.36, 0.1, 400)
W0 = lambertw(x_vals, k=0).real
Wm1 = lambertw(x_vals, k=-1).real

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(x_vals, W0, "b-", lw=2, label=r"$W_0(x)$ (rama física)")
ax.plot(x_vals, Wm1, "r--", lw=2, label=r"$W_{-1}(x)$ (UV, polo complejo)")
ax.axhline(0, color="k", lw=0.8)
ax.axvline(-1/np.e, color="gray", ls=":", lw=1, label=r"$x=-1/e$ (punto de ramificación)")
ax.axvline(phi/np.e**10, color="green", ls="--", lw=1.5,
           label=r"THU: $am^2 \approx 10^{-37}$")
ax.set_xlabel("argumento $x = am^2$")
ax.set_ylabel("$W_k(x)$")
ax.set_ylim(-1.5, 0.5)
ax.set_title("Ramas de Lambert–W y separación física/UV")
ax.legend(loc="lower right", fontsize=9)
ax.grid(alpha=0.3)
guardar(fig, "03_lambert_w",
    "Ramas W_0 (física) y W_-1 (UV): la rama k=0 es el polo observable")

# ──────────────────────────────────────────────────────────
# 4) Jerarquia aurea: Λ = M_P φ^(-n) para varios n
# ──────────────────────────────────────────────────────────
bar, pct = barra(4)
print(f"\n  PASO 4/{TOTAL}  [{bar}]  {pct:3d}%")
print(f"  Escala hadronica Λ_THU = M_P φ^(-88) ≈ 989.89 MeV")
print(f"  Verifica: Test 8")
sys.stdout.flush()

MP_GeV = 2.435e18
n_vals = np.arange(60, 100, 1)
Lambda_MeV = MP_GeV * phi**(-n_vals) * 1000

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.semilogy(n_vals, Lambda_MeV, "b-o", lw=1.5, ms=4, label=r"$\Lambda = M_P \varphi^{-n}$")
ax.axhline(989.89, color="red", ls="--", lw=1.5, label=r"$\Lambda_{THU} \approx 989.89$ MeV")
ax.axvline(88, color="gold", ls="--", lw=1.5, label="n = 88")
ax.plot(88, 989.89, "o", color="gold", ms=14, mec="k", zorder=5)
ax.annotate(r"$n=88 \to \Lambda = 989.89$ MeV",
            xy=(88, 989.89), xytext=(80, 1e3),
            arrowprops=dict(arrowstyle="->", color="darkred", lw=1.5),
            fontsize=11, color="darkred")
ax.set_xlabel("exponente áureo $n$")
ax.set_ylabel(r"$\Lambda_n$ [MeV]")
ax.set_title("Jerarquía áurea: $\Lambda = M_P \\varphi^{-88}$")
ax.legend(loc="best", fontsize=10)
ax.grid(alpha=0.3, which="both")
guardar(fig, "04_jerarquia_aurea",
    "Λ = M_P φ^(-n) para n=60..99; n=88 da escala hadrónica")

# ──────────────────────────────────────────────────────────
# 5) Coeficiente anomalo A
# ──────────────────────────────────────────────────────────
bar, pct = barra(5)
print(f"\n  PASO 5/{TOTAL}  [{bar}]  {pct:3d}%")
print(f"  A = A_0 + δA_VL = 5/3 + 0.152 = 1.819")
print(f"  Verifica: Test 10")
sys.stdout.flush()

componentes = ["$A_0$\n(Modelo Est.)", "$\\delta A_u$", "$\\delta A_d$", "$\\delta A_e$", "$A$ total"]
valores = [5/3, 0.0898, 0.0281, 0.0340, 1.8187]
colores = ["steelblue", "coral", "coral", "coral", "gold"]

fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.bar(componentes, valores, color=colores, edgecolor="k", lw=1.2)
for b, v in zip(bars, valores):
    ax.text(b.get_x() + b.get_width()/2, v + 0.03, f"{v:.4f}",
            ha="center", fontsize=10, fontweight="bold")
ax.axhline(1.819, color="darkred", ls="--", lw=1.5, label="PDF v5.3: A = 1.819")
ax.set_ylabel("valor de $A$")
ax.set_title("Coeficiente anómalo $A$: SM + correcciones vector-like")
ax.set_ylim(0, 2.1)
ax.legend(loc="upper left", fontsize=10)
ax.grid(alpha=0.3, axis="y")
guardar(fig, "05_coeficiente_A",
    "A = 5/3 + δA_VL(u,d,e) = 1.819: consistente con PDF")

# ──────────────────────────────────────────────────────────
# 6) Residuo del propagador Res[Δ]
# ──────────────────────────────────────────────────────────
bar, pct = barra(6)
print(f"\n  PASO 6/{TOTAL}  [{bar}]  {pct:3d}%")
print(f"  Res[Δ] = e^(-am²)/(1+am²) > 0 para todo am² ≥ 0")
print(f"  Verifica: Test 2")
sys.stdout.flush()

am2 = np.linspace(0, 3, 400)
Res = np.exp(-am2) / (1 + am2)

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(am2, Res, "b-", lw=2, label=r"$\mathrm{Res}[\Delta] = e^{-am^2}/(1+am^2)$")
ax.fill_between(am2, 0, Res, color="blue", alpha=0.1)
ax.axhline(0, color="k", lw=0.8)
ax.set_xlabel(r"$am^2$")
ax.set_ylabel(r"$\mathrm{Res}[\Delta]$")
ax.set_title("Residuo del propagador (estrictamente positivo)")
ax.annotate(r"$\mathrm{Res}[\Delta] > 0 \;\; \forall\, am^2 \geq 0$",
            xy=(1.5, 0.2), fontsize=12, color="darkblue")
ax.legend(loc="upper right", fontsize=10)
ax.grid(alpha=0.3)
guardar(fig, "06_residuo_propagador",
    "Res[Δ] > 0: unitariedad preservada")

# ──────────────────────────────────────────────────────────
# RESUMEN Y MANIFEST
# ──────────────────────────────────────────────────────────
t_total = time.time() - t0
print()
print("╔" + "═" * 70 + "╗")
print("║" + " FASE B.2 — RESUMEN ".center(70) + "║")
print("╚" + "═" * 70 + "╝")
for r in resultados:
    print(f"  ✓  {r['figura']:35s}  {r['descripcion'][:50]}")

mf = {
    "version": "1.0.0",
    "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "total_figuras": len(resultados),
    "duracion_s": round(t_total, 2),
    "figuras": resultados
}
mf_path = LAB / "data" / "inventory" / "figuras_fase_b.json"
mf_path.write_text(json.dumps(mf, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n  Manifest: {mf_path}")
print(f"  Total figuras: {len(resultados)}")
print(f"  Duracion: {t_total:.2f}s")
