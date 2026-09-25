"""CiSS–SBSC aplicado ao Banco da Amazônia (2021–2024) — versão 3 (especificação corrigida).

Método: normalização pela média do período (x/média; média/x para polaridade negativa),
composição constante das perspectivas (satisfação excluída; eficiência 2023 interpolada),
pesos iguais, CiSS = 1 − Gini (regra dos trapézios). Inclui as especificações de robustez B–D.

Ao executar, o script:
  1. mostra na tela a Tabela 2 (scores, CiSS e Gini) e a Tabela 3 (robustez) do artigo;
  2. salva as tabelas em "Resultados_CiSS_BASA_v3.xlsx" (ou .csv, se não houver openpyxl);
  3. salva as três figuras do artigo (PNG e TIF, 300 dpi, preto e branco) na pasta "figuras"
     e as exibe na tela.
Todos os arquivos são gravados na mesma pasta do script.

Uso:  python CiSS_BASA_v3.py                 (tabelas + figuras exibidas e salvas)
      python CiSS_BASA_v3.py --sem-exibir    (salva as figuras sem abrir janelas)
      python CiSS_BASA_v3.py --sem-figuras   (só as tabelas)
Requisitos: numpy, pandas, matplotlib, pillow (e openpyxl para o Excel)
"""
import os, sys
import numpy as np
import pandas as pd

nan = np.nan
try:
    PASTA = os.path.dirname(os.path.abspath(__file__))
except NameError:                      # Jupyter / console interativo
    PASTA = os.getcwd()

rows=[
("GRI 201-1 Valor Econômico Gerado e Distribuído (R$ bi)",[2.27,2.36,2.62,2.85],"Clientes e Acionistas"),
("Dividendos+JCP (R$ bi)",[0.203667,0.311643,0,0],"Clientes e Acionistas"),
("Valor de Mercado (R$ bi)",[1.22,2.80,5.33,4.82],"Clientes e Acionistas"),
("Número de Clientes (mil)",[618,654,690,1078.9],"Clientes e Acionistas"),
("Energia consumida (MWh)",[11980,11895,11750,11680],"Sustentabilidade"),
("Emissões Escopo 1",[1420,1408,1389,1375],"Sustentabilidade"),
("Emissões Escopo 2",[3050,2995,2972,2950],"Sustentabilidade"),
("Emissões Escopo 3",[4601,4588,4550,4520],"Sustentabilidade"),
("Novas contratações (nº)",[289,276,281,295],"Processos Internos"),
("Rotatividade (%)",[9.4,9.3,9.2,9.1],"Processos Internos"),
("Índice de satisfação dos clientes (%)",[38.25,67,67,nan],"Processos Internos"),
("Indice de Eficiencia Operacional (%)",[59,45.35,nan,30.5],"Processos Internos"),
("Horas de treinamento/empregado (h)",[28,29,30,31],"Aprendizado e Crescimento"),
("Mulheres na força de trabalho (%)",[37,37,38,39],"Aprendizado e Crescimento"),
("Mulheres em cargos de liderança (%)",[31,32,33,34],"Aprendizado e Crescimento"),
("Número de empregados",[2818,2867,2835,2869],"Aprendizado e Crescimento"),
("Lucro Líquido (R$ bi)",[0.7378,1.1223,1.345,1.1],"Financeira"),
("Patrimônio Líquido (R$ bi)",[2.9,4.8,5.9,6.5],"Financeira"),
("Ativos Totais (R$ bi)",[26.0,34.6,45.2,54.3],"Financeira"),
("ROE (%)",[30.5,38.11,25.1,18.2],"Financeira"),
]

NEG=["Energia","Emissões","Rotatividade","Eficiencia"]
ANOS=[2021,2022,2023,2024]

def ciss(scores):
    s=np.sort(np.asarray(scores,float)); phi=np.r_[0,np.cumsum(s/s.sum())]; n=len(s)
    gini=1-np.sum(phi[:-1]+phi[1:])/n
    return 1-gini

def especificacao(modo="A"):
    P={}
    for nome,vals,persp in rows:
        v=np.array(vals,float)
        if modo=="D":
            z=np.array([x if np.isnan(x) else (x if any(k in nome for k in ["%","Índice","Indice"]) else (np.log1p(x) if x==0 else np.log(x))) for x in v])
            P.setdefault(persp,[]).append(z); continue
        if "satisfação" in nome:
            if modo in ("A","C"): continue
            v[3]=v[2]
        if "Eficiencia" in nome: v[2]=(v[1]+v[3])/2
        neg=any(k in nome for k in NEG)
        if modo=="C":
            z=(v-v.min())/(v.max()-v.min()); z=1-z if neg else z
        else:
            m=v.mean(); z=m/v if neg else v/m
        P.setdefault(persp,[]).append(z)
    S=pd.DataFrame({p:np.nanmean(np.vstack(z),axis=0) for p,z in P.items()},index=ANOS).T
    return S,[ciss(S[a]) for a in ANOS]


# ==========================================================
# TABELAS DE RESULTADOS
# ==========================================================
ESPEC = {
    "A": "(A) Principal: razão à média, polaridade, composição constante",
    "B": "(B) A + satisfação dos clientes (último valor repetido)",
    "C": "(C) Min-max no período, polaridade",
    "D": "(D) Logaritmo e percentuais brutos, sem polaridade (versão 2)",
}
ORDEM = ["Financeira", "Clientes e Acionistas", "Processos Internos",
         "Aprendizado e Crescimento", "Sustentabilidade"]

def tabela2():
    S, C = especificacao("A")
    t = S.loc[ORDEM, ANOS].copy()
    t.loc["CiSS (1 − Gini)"] = C
    t.loc["Gini (= SC)"] = 1 - np.array(C)
    t.index.name = "Perspectiva"
    return t

def tabela3():
    linhas = {}
    for m, rotulo in ESPEC.items():
        c = especificacao(m)[1]
        c = [round(v, 4) for v in c]     # Δ calculado sobre os valores publicados (4 casas)
        linhas[rotulo] = c + [round(c[-1] - c[0], 4)]
    t = pd.DataFrame.from_dict(linhas, orient="index", columns=ANOS + ["Δ 2021–24"])
    t.index.name = "Especificação"
    return t

def imprimir(titulo, t):
    print("\n" + titulo)
    print("=" * len(titulo))
    with pd.option_context("display.width", 200, "display.max_columns", 20,
                           "display.max_colwidth", 70):
        print(t.to_string(float_format=lambda v: f"{v:.4f}".replace(".", ",")))

def salvar_tabelas(t2, t3):
    xlsx = os.path.join(PASTA, "Resultados_CiSS_BASA_v3.xlsx")
    try:
        with pd.ExcelWriter(xlsx) as w:
            t2.round(4).to_excel(w, sheet_name="Tabela2_scores_CiSS")
            t3.round(4).to_excel(w, sheet_name="Tabela3_robustez")
        return xlsx
    except Exception:                  # sem openpyxl: grava CSV (padrão brasileiro)
        for nome, t in (("Tabela2_scores_CiSS", t2), ("Tabela3_robustez", t3)):
            t.round(4).to_csv(os.path.join(PASTA, nome + ".csv"), sep=";", decimal=",", encoding="utf-8-sig")
        return os.path.join(PASTA, "Tabela2_scores_CiSS.csv / Tabela3_robustez.csv")

# ==========================================================
# FIGURAS (preto e branco, 300 dpi) — numeração do artigo
# ==========================================================
def _fmt(casas):
    import matplotlib.ticker as mt
    return mt.FuncFormatter(lambda v, p: f"{v:.{casas}f}".replace(".", ","))

def _salvar(fig, pasta, nome):
    os.makedirs(pasta, exist_ok=True)
    fig.savefig(os.path.join(pasta, nome + ".png"), dpi=300)
    from PIL import Image
    png = os.path.join(pasta, nome + ".png")
    # TIF em tons de cinza (sem canal alfa), 300 dpi, como exige a revista
    Image.open(png).convert("L").save(os.path.join(pasta, nome + ".tif"), dpi=(300, 300), compression="tiff_lzw")

def gerar_figuras(pasta, exibir=True):
    import matplotlib
    if not exibir:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    S, C = especificacao("A")

    # Figura 1 — scores das perspectivas
    estilos = {"Financeira": ("-", "o"), "Clientes e Acionistas": ("--", "s"),
               "Processos Internos": ("-.", "^"), "Aprendizado e Crescimento": (":", "D"),
               "Sustentabilidade": ((0, (5, 2, 1, 2)), "v")}
    fig, ax = plt.subplots(figsize=(6.3, 3.9))
    for p, (ls, mk) in estilos.items():
        ax.plot(ANOS, S.loc[p, ANOS], color="black", ls=ls, marker=mk, ms=6, mfc="white", lw=1.2, label=p)
    ax.axhline(1, color="0.6", lw=0.8)
    ax.set_xticks(ANOS); ax.set_xlabel("Ano"); ax.set_ylabel("Score da perspectiva (média do período = 1)")
    ax.yaxis.set_major_formatter(_fmt(2)); ax.set_ylim(0.7, 1.35); ax.grid(axis="y", color="0.9", lw=0.6)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left", ncol=2)
    fig.tight_layout(); _salvar(fig, pasta, "Figura1_perspectivas_BSC")

    # Figura 2 — evolução do CiSS
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.plot(ANOS, C, color="black", lw=1.6, marker="o", ms=6)
    for x, c in zip(ANOS, C):
        ax.annotate(f"{c:.4f}".replace(".", ","), (x, c), textcoords="offset points",
                    xytext=(0, -16) if x == 2023 else (0, 8), ha="center", fontsize=9)
    ax.set_xticks(ANOS); ax.set_xlabel("Ano"); ax.set_ylabel("CiSS (1 − Gini)")
    ax.set_ylim(0.945, 0.975); ax.yaxis.set_major_formatter(_fmt(3)); ax.grid(axis="y", color="0.85", lw=0.6)
    fig.tight_layout(); _salvar(fig, pasta, "Figura2_evolucao_CiSS")

    # Figura 3 — curvas de Lorenz 2021 e 2024
    def lorenz(a):
        s = np.sort(S[a].values); return np.linspace(0, 1, len(s) + 1), np.r_[0, np.cumsum(s / s.sum())]
    series = [(2021, "--", "o"), (2024, "-", "s")]
    fig, ax = plt.subplots(figsize=(4.6, 4.4))
    ax.plot([0, 1], [0, 1], color="0.55", lw=1, label="Equilíbrio perfeito")
    for a, ls, mk in series:
        x, y = lorenz(a)
        ax.plot(x, y, color="black", ls=ls, marker=mk, ms=5, mfc="white", lw=1.2,
                label=f"{a} (CiSS = {C[ANOS.index(a)]:.4f})".replace(".", ","))
    ax.set_xlabel("Proporção acumulada das perspectivas"); ax.set_ylabel("Proporção acumulada dos scores")
    ax.set_aspect("equal"); ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.xaxis.set_major_formatter(_fmt(1)); ax.yaxis.set_major_formatter(_fmt(1))
    ins = ax.inset_axes([0.55, 0.08, 0.4, 0.4])
    ins.plot([0, 1], [0, 1], color="0.55", lw=1)
    for a, ls, mk in series:
        x, y = lorenz(a); ins.plot(x, y, color="black", ls=ls, marker=mk, ms=4, mfc="white", lw=1)
    ins.set_xlim(0.15, 0.45); ins.set_ylim(0.1, 0.4); ins.tick_params(labelsize=6)
    ins.xaxis.set_major_formatter(_fmt(1)); ins.yaxis.set_major_formatter(_fmt(2)); ins.set_title("detalhe", fontsize=7)
    fig.tight_layout(); _salvar(fig, pasta, "Figura3_curvas_Lorenz")
    if exibir:
        plt.show()   # abre as três janelas; feche-as para encerrar
    plt.close("all")
    return pasta


if __name__ == "__main__":
    t2, t3 = tabela2(), tabela3()
    imprimir("Tabela 2 – Scores das perspectivas, CiSS e Gini (especificação principal)", t2)
    imprimir("Tabela 3 – CiSS (1 − Gini) segundo especificações alternativas", t3)
    print("\nTabelas salvas em:", salvar_tabelas(t2, t3))
    if "--sem-figuras" not in sys.argv:
        pasta = gerar_figuras(os.path.join(PASTA, "figuras"), exibir="--sem-exibir" not in sys.argv)
        print("Figuras salvas em:", pasta)
