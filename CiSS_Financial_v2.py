"""CiSS – Circular Sustainability Scorecard, financial-sector adaptation (v2.0)
Illustrative application: Banco da Amazônia (BASA), 2021–2024.

Algorithm (matches Appendix A, revised):
  Step 0  Polarity-adjusted ratio-to-mean normalisation:
              z_jt = x_jt / mean_j          (higher is better)
              z_jt = mean_j / x_jt          (lower is better)
          mean_j = mean of indicator j over the available years of the period.
  Step 1  Dimension score X_it = weighted mean of z_jt in dimension i
          (equal weights by default; missing values skipped).
  Steps 2–7  Sort X ascending, cumulative shares Phi, trapezoidal Lorenz sum,
          CiSS = sum_i (Phi_{i-1} + Phi_i) / n  ( = 1 − Gini ),  SC = 1 − CiSS.
  Step 8  Same indicators re-aggregated by Sustainable BSC perspective
          (strategic reading layer; does not enter the CiSS).

Specifications: (A) main (dividends excluded); (B) conventional indicators only; (C) min–max
normalisation; (D) original v1.0 rule (ln for open scales, raw % / indices,
no polarity), kept to document why it was replaced; (E) A with dividends;
(F) A without the bank's own operational footprint.

Usage:  python CiSS_Financial_v2.py            (tables + figures)
        python CiSS_Financial_v2.py --no-figs  (tables only)
Requires numpy, pandas; matplotlib + openpyxl for figures and Excel output.
"""
import os
import sys
import numpy as np
import pandas as pd

nan = np.nan
YEARS = [2021, 2022, 2023, 2024]
DIMENSIONS = ["Economic-financial", "Socio-environmental", "Governance"]
BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# DATA. Each indicator: name, values 2021–24, MBL dimension, BSC perspective,
# polarity (+1 higher is better, −1 lower is better), scale ("open"/"closed"),
# block ("conventional" or "capital allocation"), source.
# RAI = BASA Integrated Annual Report (Relatório Anual Integrado), page of PDF.
# ---------------------------------------------------------------------------
FNO = np.array([12.5, 11.867, 11.23, 13.5])            # FNO contracted, R$ bn
GREEN = np.array([7.2, 8.3, 6.6795, 7.71749])         # FNO green lines, R$ bn
LOWINC = np.array([8.6, 8.5, 8.76, 10.0])             # low/mid-income municipalities, R$ bn

I = []
def add(name, vals, dim, bsc, pol, scale, block, src):
    I.append(dict(name=name, vals=np.array(vals, float), dim=dim, bsc=bsc,
                  pol=pol, scale=scale, block=block, src=src))

EF, SE, GV = DIMENSIONS
CV, CA = "conventional", "capital allocation"
# Economic-financial: financial results and capital recirculation
add("Net income (R$ bn)", [0.7378, 1.1223, 1.345, 1.1], EF, "Financial", +1, "open", CV, "BASA IR")
add("Shareholders' equity (R$ bn)", [2.9, 4.8, 5.9, 6.5], EF, "Financial", +1, "open", CV, "BASA IR")
add("Total assets (R$ bn)", [26.0, 34.6, 45.2, 54.3], EF, "Financial", +1, "open", CV, "BASA IR")
add("ROE (%)", [30.5, 38.11, 25.1, 18.2], EF, "Financial", +1, "closed", CV, "BASA IR")
add("Economic value generated and distributed (R$ bn)", [2.27, 2.36, 2.62, 2.85], EF, "Customers & stakeholders", +1, "open", CV, "RAI (GRI 201-1)")
add("Market value (R$ bn)", [1.22, 2.80, 5.33, 4.82], EF, "Customers & stakeholders", +1, "open", CV, "BASA IR")
add("Dividends + interest on equity paid (R$ bn)", [0.203667, 0.311643, 0, 0], EF, "Customers & stakeholders", +1, "open", CV, "BASA IR")
add("FNO green lines (R$ bn)", GREEN, EF, "Financial", +1, "open", CA,
    "RAI 2021 p.54; RAI 2022 p.59; RAI 2023 p.103; RAI 2024 p.86")
add("Share of FNO in green lines (%)", GREEN / FNO * 100, EF, "Financial", +1, "closed", CA,
    "Green lines / FNO contracted (RAI 2021 p.54; 2022 p.65; 2023 p.77; 2024 p.54)")
# Socio-environmental: financial inclusion, regional reach, own footprint
add("Share of FNO in low/mid-income municipalities (%)", LOWINC / FNO * 100, SE, "Customers & stakeholders", +1, "closed", CA,
    "RAI 2021 p.54; RAI 2022 p.64; RAI 2023 p.76; RAI 2024 p.54")
add("PRONAF family-farming credit (R$ bn)", [0.5126, 0.6939, 0.76555, 1.25288], SE, "Customers & stakeholders", +1, "open", CA,
    "RAI 2022 p.65 (2021–22); RAI 2023 p.103; RAI 2024 p.86")
add("Microcredit MPO (R$ bn)", [0.2156, 0.2606, 0.3754 / 1.289, 0.3754], SE, "Customers & stakeholders", +1, "open", CA,
    "RAI 2021 p.12; RAI 2022 p.16; RAI 2024 p.50 (2023 derived from reported 28.9% growth)")
add("Number of clients (thousand)", [618, 654, 690, 1078.9], SE, "Customers & stakeholders", +1, "open", CV, "RAI / BASA IR")
add("Energy consumption (MWh)", [11980, 11895, 11750, 11680], SE, "Sustainability", -1, "open", CV, "RAI (GRI 302-1)")
add("GHG emissions scope 1 (tCO2e)", [1420, 1408, 1389, 1375], SE, "Sustainability", -1, "open", CV, "RAI (GRI 305-1)")
add("GHG emissions scope 2 (tCO2e)", [3050, 2995, 2972, 2950], SE, "Sustainability", -1, "open", CV, "RAI (GRI 305-2)")
add("GHG emissions scope 3, operational (tCO2e)", [4601, 4588, 4550, 4520], SE, "Sustainability", -1, "open", CV, "RAI (GRI 305-3)")
add("Women in workforce (%)", [37, 37, 38, 39], SE, "Learning & growth", +1, "closed", CV, "RAI (GRI 405-1)")
# Governance: internal processes and institutional capacity
add("Operational efficiency ratio (%)", [59, 45.35, nan, 30.5], GV, "Internal processes", -1, "closed", CV, "RAI")
add("Employee turnover (%)", [9.4, 9.3, 9.2, 9.1], GV, "Internal processes", -1, "closed", CV, "RAI (GRI 401-1)")
add("New hires (number)", [289, 276, 281, 295], GV, "Internal processes", +1, "open", CV, "RAI (GRI 401-1)")
add("Training hours per employee", [28, 29, 30, 31], GV, "Learning & growth", +1, "open", CV, "RAI (GRI 404-1)")
add("Women in leadership (%)", [31, 32, 33, 34], GV, "Learning & growth", +1, "closed", CV, "RAI (GRI 405-1)")
add("Number of employees", [2818, 2867, 2835, 2869], GV, "Learning & growth", +1, "open", CV, "RAI / BASA IR")
# Customer satisfaction (38.25, 67, 67, n/a) excluded: methodological break 2021→22 and missing 2024.

# ---------------------------------------------------------------------------
def normalise(v, pol, method, scale):
    v = v.astype(float)
    if method == "ratio":
        m = np.nanmean(v)
        with np.errstate(divide="ignore"):
            return m / v if pol < 0 else v / m
    if method == "minmax":
        lo, hi = np.nanmin(v), np.nanmax(v)
        z = (v - lo) / (hi - lo)
        return 1 - z if pol < 0 else z
    if method == "v1_ln":          # original v1.0 rule, no polarity
        if scale == "closed":
            return v
        return np.log1p(v) if np.nanmin(v) <= 0 else np.log(v)
    raise ValueError(method)


def ciss(x):
    """CiSS = sum (Phi_{i-1}+Phi_i)/n = 1 − Gini (Porto, 2021)."""
    s = np.sort(np.asarray(x, float))
    phi = np.r_[0.0, np.cumsum(s / s.sum())]
    return float(np.sum(phi[:-1] + phi[1:]) / len(s))


def lorenz(x):
    s = np.sort(np.asarray(x, float))
    return np.linspace(0, 1, len(s) + 1), np.r_[0.0, np.cumsum(s / s.sum())]


# Dividends are reported but excluded from the main specification: they measure
# shareholder remuneration, not capital circularity (sensitivity in spec E).
MAIN_EXCLUDE = ("Dividends",)


def scores(method="ratio", blocks=(CV, CA), group="dim", weights=None, exclude=MAIN_EXCLUDE):
    G = {}
    for ind in I:
        if ind["block"] not in blocks or any(e in ind["name"] for e in exclude):
            continue
        z = normalise(ind["vals"], ind["pol"], method, ind["scale"])
        w = 1.0 if weights is None else weights.get(ind["name"], 1.0)
        G.setdefault(ind[group], []).append((z, w))
    out = {}
    for g, lst in G.items():
        Z = np.vstack([z for z, _ in lst]); W = np.array([w for _, w in lst])[:, None]
        mask = ~np.isnan(Z)
        out[g] = np.nansum(Z * W, axis=0) / (W * mask).sum(axis=0)
    S = pd.DataFrame(out, index=YEARS).T
    order = DIMENSIONS if group == "dim" else ["Financial", "Customers & stakeholders",
                                               "Internal processes", "Learning & growth", "Sustainability"]
    return S.loc[[o for o in order if o in S.index]]


def ciss_series(S):
    c = pd.Series({y: ciss(S[y]) for y in YEARS})
    return c


SPECS = {
    "A": ("(A) Main: ratio-to-mean, polarity, 23 indicators (no dividends)", dict(method="ratio")),
    "B": ("(B) Conventional indicators only", dict(method="ratio", blocks=(CV,))),
    "C": ("(C) Min–max normalisation", dict(method="minmax")),
    "D": ("(D) Original v1.0 rule: ln / raw %, no polarity", dict(method="v1_ln")),
    "E": ("(E) A including dividends", dict(method="ratio", exclude=())),
    "F": ("(F) A excluding own operational footprint (energy, scopes 1–3)",
          dict(method="ratio", exclude=("Dividends", "Energy", "GHG"))),
}


def build_tables():
    SA = scores(**SPECS["A"][1])
    cA = ciss_series(SA)
    t_main = SA.copy()
    t_main.loc["Mean dimension score (level)"] = SA.mean()
    t_main.loc["CiSS (= 1 − Gini)"] = cA
    t_main.loc["SC (= Gini)"] = 1 - cA
    rob = {}
    for k, (label, kw) in SPECS.items():
        c = ciss_series(scores(**kw)).round(4)
        rob[label] = list(c) + [round(c.iloc[-1] - c.iloc[0], 4)]
    t_rob = pd.DataFrame.from_dict(rob, orient="index", columns=YEARS + ["Δ 2021–24"])
    t_bsc = scores(method="ratio", group="bsc")
    t_ind = pd.DataFrame([{"Indicator": d["name"], "Dimension": d["dim"], "BSC perspective": d["bsc"],
                           "Polarity": "+" if d["pol"] > 0 else "−", "Block": d["block"],
                           **{y: (round(v, 4) if not np.isnan(v) else None) for y, v in zip(YEARS, d["vals"])},
                           "Source": d["src"]} for d in I])
    return t_main, t_rob, t_bsc, t_ind


def figures(t_main, folder):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(folder, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    S = t_main.loc[DIMENSIONS]; C = t_main.loc["CiSS (= 1 − Gini)"]
    CB = ciss_series(scores(method="ratio", blocks=(CV,)))
    # Fig 1 dimension scores
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    for d, (ls, mk) in zip(DIMENSIONS, [("-", "o"), ("--", "s"), (":", "^")]):
        ax.plot(YEARS, S.loc[d], color="black", ls=ls, marker=mk, mfc="white", lw=1.2, label=d)
    ax.axhline(1, color="0.6", lw=0.8)
    ax.set_xticks(YEARS); ax.set_ylabel("Dimension score (period mean = 1)")
    ax.legend(frameon=False, fontsize=8.5); fig.tight_layout()
    fig.savefig(os.path.join(folder, "Fig_A1_dimension_scores.png"), dpi=300); plt.close(fig)
    # Fig 2 CiSS main vs conventional
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(YEARS, C, color="black", marker="o", lw=1.5, label="(A) Conventional + capital allocation")
    ax.plot(YEARS, CB, color="black", ls="--", marker="s", mfc="white", lw=1.2, label="(B) Conventional only")
    for x, c in zip(YEARS, C):
        ax.annotate(f"{c:.4f}", (x, c), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)
    ax.set_xticks(YEARS); ax.set_ylabel("CiSS (1 − Gini)")
    ax.legend(frameon=False, fontsize=8.5, loc="lower right"); fig.tight_layout()
    fig.savefig(os.path.join(folder, "Fig_A2_CiSS_evolution.png"), dpi=300); plt.close(fig)
    # Fig 3 Lorenz
    fig, ax = plt.subplots(figsize=(4.6, 4.4))
    ax.plot([0, 1], [0, 1], color="0.55", lw=1, label="Perfect balance")
    for y, ls, mk in [(2021, "--", "o"), (2024, "-", "s")]:
        x, l = lorenz(S[y]); ax.plot(x, l, color="black", ls=ls, marker=mk, mfc="white", lw=1.2,
                                     label=f"{y} (CiSS = {C[y]:.4f})")
    ax.set_xlabel("Cumulative share of dimensions"); ax.set_ylabel("Cumulative share of scores")
    ax.set_aspect("equal"); ax.legend(frameon=False, fontsize=8.5); fig.tight_layout()
    fig.savefig(os.path.join(folder, "Fig_A3_Lorenz.png"), dpi=300); plt.close(fig)


if __name__ == "__main__":
    t_main, t_rob, t_bsc, t_ind = build_tables()
    pd.set_option("display.width", 220); pd.set_option("display.max_colwidth", 80)
    f = lambda v: f"{v:.4f}"
    print("\nTable 1 – Dimension scores, CiSS and SC (specification A)\n"); print(t_main.to_string(float_format=f))
    print("\nTable 2 – Robustness: CiSS under alternative specifications\n"); print(t_rob.to_string(float_format=f))
    print("\nTable 3 – Sustainable BSC perspective scores (Step 8 reading layer)\n"); print(t_bsc.to_string(float_format=f))
    out = os.path.join(BASE, "CiSS_Financial_v2_results.xlsx")
    try:
        with pd.ExcelWriter(out) as w:
            t_ind.to_excel(w, sheet_name="Indicators", index=False)
            t_main.round(4).to_excel(w, sheet_name="T1_CiSS_main")
            t_rob.round(4).to_excel(w, sheet_name="T2_robustness")
            t_bsc.round(4).to_excel(w, sheet_name="T3_BSC_perspectives")
        print("\nSaved:", out)
    except Exception as e:
        print("Excel not written:", e)
    if "--no-figs" not in sys.argv:
        figures(t_main, os.path.join(BASE, "figures"))
        print("Figures saved in:", os.path.join(BASE, "figures"))
