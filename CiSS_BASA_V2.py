
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

PASTA_SCRIPT = os.path.dirname(os.path.abspath(__file__))

ARQUIVO = os.path.join(
    PASTA_SCRIPT,
    "COMPARATIVO BSC BASA ISA.xlsx"
)

# ==========================
# LEITURA DA PLANILHA
# ==========================

df = pd.read_excel(ARQUIVO, header=1)
df = df.dropna(subset=["Indicador"])

anos = [2021, 2022, 2023, 2024]

percentuais = ["%", "Índice", "Indice"]

# ==========================
# NORMALIZAÇÃO
# ==========================

def normalizar(indicador, valor):

    if pd.isna(valor) or valor == "-":
        return np.nan

    valor = float(valor)

    nome = str(indicador)

    if any(p.lower() in nome.lower() for p in percentuais):
        return valor

    if valor == 0:
        return np.log1p(valor)

    if valor < 0:
        return np.nan

    return np.log(valor)

# ==========================
# ESTRUTURAS
# ==========================

resultados = []
scores_all = []

writer = pd.ExcelWriter(
    "Resultados_CiSS_BASA.xlsx",
    engine="openpyxl"
)

# Figura única para todas as curvas
plt.figure(figsize=(12, 10))

# ==========================
# LOOP DOS ANOS
# ==========================

for ano in anos:

    temp = df.copy()

    temp["Normalizado"] = temp.apply(
        lambda r: normalizar(
            r["Indicador"],
            r[ano]
        ),
        axis=1
    )

    temp.to_excel(
        writer,
        sheet_name=f"Normalizados_{ano}",
        index=False
    )

    # Score médio das perspectivas
    scores = (
        temp
        .groupby("Perspectiva BSC")["Normalizado"]
        .mean()
        .sort_values()
    )

    score_reg = {"Ano": ano}

    for k, v in scores.items():
        score_reg[k] = v

    scores_all.append(score_reg)

    # ==========================
    # CURVA DE LORENZ
    # ==========================

    phi = scores.values / scores.values.sum()

    lorenz = np.cumsum(phi)

    n = len(scores)

    x = np.arange(1, n + 1) / n

    x = np.insert(x, 0, 0)
    y = np.insert(lorenz, 0, 0)

    # Área sob a curva
    area = np.trapezoid(y, x)

    ciss = area
    sc = 1 - ciss

    resultados.append(
        {
            "Ano": ano,
            "CiSS": ciss,
            "SC": sc
        }
    )

    pd.DataFrame(
        {
            "P": x,
            "Lorenz": y
        }
    ).to_excel(
        writer,
        sheet_name=f"Lorenz_{ano}",
        index=False
    )

   
    # Curva do ano no gráfico unificado
    plt.plot(
        x,
        y,
        marker="o",
        markersize=4,
        linewidth=1.2,
        label=f"{ano} (CiSS={ciss:.4f})"
    )

# ==========================
# FINALIZAÇÃO DO EXCEL
# ==========================

pd.DataFrame(scores_all).to_excel(
    writer,
    sheet_name="Scores_Perspectivas",
    index=False
)
# ==========================================
# EVOLUÇÃO DAS PERSPECTIVAS
# ==========================================

scores_df = pd.DataFrame(scores_all)

base = scores_df.iloc[0]

for col in scores_df.columns:

    if col != "Ano":

        scores_df[col] = (
            scores_df[col] / base[col]
        ) * 100

plt.figure(figsize=(10,6))

for coluna in scores_df.columns:

    if coluna != "Ano":

        plt.plot(
            scores_df["Ano"],
            scores_df[coluna],
            marker="o",
            linewidth=2,
            label=coluna
        )

plt.title(
    "Evolução das Perspectivas do BSC"
)

plt.xlabel(
    "Ano"
)

plt.ylabel(
    "Score Médio Normalizado"
)

plt.grid(True)

plt.legend()

plt.tight_layout()

plt.savefig(
    "Evolucao_Perspectivas_BSC.png",
    dpi=300
)

plt.close()

pd.DataFrame(resultados).to_excel(
    writer,
    sheet_name="CiSS",
    index=False
)

writer.close()

# ==========================
# GRÁFICO UNIFICADO
# ==========================

plt.plot(
    [0, 1],
    [0, 1],
    "--",
    linewidth=1.5,
    color="black",
    label="Equilíbrio Perfeito"
)

plt.title(
    "Curvas de Lorenz das Perspectivas BSC\nBASA (2021–2024)"
)

plt.xlabel(
    "Participação acumulada das perspectivas"
)

plt.ylabel(
    "Participação acumulada dos scores"
)

plt.xlim(0, 1)
plt.ylim(0, 1)

plt.grid(True)

plt.legend()

plt.tight_layout()

plt.savefig(
    "Lorenz_BASA_2021_2024_Unificado.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

plt.close()

# ==========================
# EVOLUÇÃO DO CiSS
# ==========================

res = pd.DataFrame(resultados)

plt.figure(figsize=(7, 5))

plt.plot(
    res["Ano"],
    res["CiSS"],
    marker="o",
    linewidth=2
)

plt.xticks(anos)
plt.title("Evolução do CiSS")

plt.xlabel("Ano")

plt.ylabel("CiSS")

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "Evolucao_CiSS.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

plt.close()

# ==========================
# EVOLUÇÃO DO SC
# ==========================

plt.figure(figsize=(7,5))

plt.plot(
    res["Ano"],
    res["SC"],
    marker="o",
    linewidth=2
)

plt.xticks(anos)

plt.title("Evolução do SC")

plt.xlabel("Ano")

plt.ylabel("SC")

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "Evolucao_SC.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

plt.close()

# ==========================
# EVOLUÇÃO DAS PERSPECTIVAS
# ==========================

scores_df = pd.DataFrame(scores_all)

plt.figure(figsize=(10, 6))

for coluna in scores_df.columns:

    if coluna != "Ano":

        plt.plot(
            scores_df["Ano"],
            scores_df[coluna],
            marker="o",
            linewidth=2,
            label=coluna
        )

plt.xticks(anos)
plt.title(
    "Evolução das Perspectivas do BSC"
)

plt.xlabel("Ano")

plt.ylabel(
    "Score Médio Normalizado"
)

plt.grid(True)

plt.legend()

plt.tight_layout()

plt.savefig(
    "Evolucao_Perspectivas_BSC.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

plt.close()

# ==========================
# RESULTADOS
# ==========================

print("\nResultados CiSS")

print(res)

print("\nConcluído.")