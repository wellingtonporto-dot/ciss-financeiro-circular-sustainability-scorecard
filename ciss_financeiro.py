"""
CiSS Financeiro — Circular Sustainability Scorecard (Setor Financeiro)
========================================================================
Adaptação do CiSS de Porto (2021) ao setor de serviços financeiros,
com aplicação ilustrativa ao Banco da Amazônia (BASA).

Desenvolvido como Apêndice A do artigo submetido ao EnANPAD 2026:
"Conceitos e desafios na mensuração da Sustentabilidade Circular"

Fundamentação:
  - Porto (2021): modelo CiSS original — Coeficiente de Gini / Curva de Lorenz
  - Bocken et al. (2016) e Geissdoerfer et al. (2017): princípios da Economia Circular
  - Kaplan e Norton (1997): Balanced Scorecard Sustentável (camada de interpretação)
  - Resolução CMN 4.945/2021: Política de Responsabilidade Socioambiental do SFN

Dimensões do MBL adaptado ao setor financeiro (3 dimensões):
  Econômico-Financeira · Socioambiental · Governança (ESG)

Normalização por logaritmo natural (Passo 0):
  - ln(valor)       → variáveis abertas positivas (ex.: crédito verde em R$)
  - ln(1 + valor)   → variáveis que podem ser zero (ex.: nº de projetos financiados)
  - sem transf.     → variáveis em escala fechada (ex.: % carteira, scores 0-100)

Interpretação:
  CiSS ∈ [0, 1]
    CiSS → 1 : fluxos de capital equilibrados entre as 3 dimensões
    CiSS → 0 : concentração extrema do desempenho em uma única dimensão
  SC = 1 − CiSS (gap de sustentabilidade circular)

Uso:
  python ciss_financeiro.py               → roda o demo BASA e exibe a curva
  python ciss_financeiro.py --no-plot      → roda sem abrir janela gráfica
  python ciss_financeiro.py --save path    → salva o gráfico no caminho indicado
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


# ── Tipo de escala (determina a normalização a aplicar) ───────────────────────

class ScaleType(Enum):
    """
    OPEN_POSITIVE : variável contínua, sempre > 0, sem teto  → ln(valor)
    OPEN_ZERO     : variável contínua, pode ser 0             → ln(1 + valor)
    CLOSED        : percentual, score ou índice com teto      → sem transformação
    """
    OPEN_POSITIVE = auto()
    OPEN_ZERO     = auto()
    CLOSED        = auto()


# ── Estruturas de dados ───────────────────────────────────────────────────────

@dataclass
class Indicator:
    """
    Um indicador individual dentro de uma dimensão do MBL adaptado ao setor financeiro.

    Parâmetros
    ----------
    name        : nome do indicador
    value       : valor bruto observado (antes da normalização)
    weight      : peso relativo do indicador dentro da dimensão (wj)
    scale_type  : tipo de escala — determina a transformação ln aplicada
    ec_principle: princípio da EC reinterpretado como circularidade de capital
                  ('fechamento', 'desaceleracao' ou 'estreitamento')
    """
    name        : str
    value       : float
    weight      : float
    scale_type  : ScaleType = ScaleType.CLOSED
    ec_principle: str = ""

    @property
    def normalized_value(self) -> float:
        """
        PASSO 0 — Normalização por logaritmo natural.

        Garante comparabilidade entre indicadores financeiros heterogêneos —
        volumes de crédito em R$ (grandezas abertas), percentuais de carteira
        (escala fechada) e scores qualitativos (ISE/B3, GRI) — sem perder a
        interpretação econômica dos dados (Ijiri, 1975 — Axioma 3: aditividade).
        """
        if self.scale_type == ScaleType.OPEN_POSITIVE:
            if self.value <= 0:
                raise ValueError(
                    f"Indicador '{self.name}': escala OPEN_POSITIVE requer valor > 0. "
                    f"Recebido: {self.value}. Use OPEN_ZERO para valores que podem ser 0."
                )
            return math.log(self.value)

        elif self.scale_type == ScaleType.OPEN_ZERO:
            if self.value < 0:
                raise ValueError(
                    f"Indicador '{self.name}': valor negativo não é permitido "
                    f"para escala OPEN_ZERO. Recebido: {self.value}."
                )
            return math.log(1 + self.value)

        else:  # CLOSED
            return self.value


@dataclass
class Dimension:
    """
    Uma dimensão do MBL adaptado ao setor financeiro.

    O score Xi é a média ponderada dos indicadores normalizados.

    Dimensões de referência (CiSS Financeiro — Apêndice A, EnANPAD 2026):
      Econômico-Financeira : crédito verde, carteira sustentável, ROIC, risco socioambiental
      Socioambiental        : inclusão financeira, iniciativas ambientais, benefícios regionais
      Governança (ESG)       : política ESG, reporte GRI/ISE, compliance CMN 4.945/2021
    """
    name       : str
    indicators : list[Indicator]
    score      : float = field(init=False)

    def __post_init__(self):
        self.score = self._compute_score()

    def _compute_score(self) -> float:
        """
        PASSO 1 — Score dimensional Xi.

        Xi = Σ(wj × indicator_norm_j) / Σ wj
        """
        total_w = sum(ind.weight for ind in self.indicators)
        if total_w == 0:
            raise ValueError(f"Dimensão '{self.name}': soma dos pesos é zero.")
        return sum(ind.weight * ind.normalized_value
                   for ind in self.indicators) / total_w


@dataclass
class LorenzRow:
    """Uma linha da tabela Lorenz — corresponde a uma dimensão no rank i."""
    rank     : int
    name     : str
    xi       : float
    pi       : float
    phi_i    : float
    phi_cum  : float
    phi_pair : float
    d_i      : float


@dataclass
class BSCMapping:
    """
    PASSO 8 — Mapeamento da dimensão a uma perspectiva do BSC Sustentável.

    Camada de interpretação estratégica, posterior ao cálculo do CiSS/SC.
    Não altera o núcleo matemático do algoritmo — apenas traduz o
    diagnóstico de desequilíbrio em ação estratégica (Kaplan; Norton, 1997).
    """
    dimension_name      : str
    bsc_perspective     : str
    strategic_indicators: list[str]


@dataclass
class CiSSResult:
    """Resultado completo de um cálculo CiSS Financeiro para uma instituição/período."""
    institution     : str
    year            : int
    n_dimensions    : int
    mean_score      : float
    total_lorenz_sum: float
    ciss            : float
    sc              : float
    lorenz_table    : list[LorenzRow]
    bsc_map         : list[BSCMapping] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"\n{'='*64}",
            f"  CiSS Financeiro — {self.institution}  |  Ano {self.year}",
            f"{'='*64}",
            f"  Dimensões      : {self.n_dimensions}",
            f"  Média (μ)      : {self.mean_score:.6f}",
            f"  Soma de Lorenz : {self.total_lorenz_sum:.6f}",
            f"  CiSS           : {self.ciss:.6f}",
            f"  SC (1 - CiSS)  : {self.sc:.6f}",
            f"\n  {'Rank':<5} {'Dimensão':<24} {'Xi':>10} "
            f"{'Pi':>7} {'Φi':>8} {'ΣΦi':>8} {'|Pi-ΣΦi|':>10}",
            f"  {'-'*70}",
        ]
        for r in self.lorenz_table:
            lines.append(
                f"  {r.rank:<5} {r.name:<24} {r.xi:>10.4f} "
                f"{r.pi:>7.4f} {r.phi_i:>8.4f} {r.phi_cum:>8.4f} {r.d_i:>10.4f}"
            )

        if self.bsc_map:
            lines.append(f"\n  Mapeamento BSC Sustentável (Passo 8):")
            lines.append(f"  {'-'*70}")
            for m in self.bsc_map:
                lines.append(f"  {m.dimension_name:<24} → {m.bsc_perspective}")

        lines.append(f"{'='*64}\n")
        return "\n".join(lines)


# ── Algoritmo principal ───────────────────────────────────────────────────────

def build_lorenz_table(dimensions: list[Dimension]) -> list[LorenzRow]:
    """
    PASSOS 2, 3 e 4 — Ordenação e frações da Curva de Lorenz.

    Passo 2: ordena as dimensões em ordem crescente de Xi.
    Passo 3: Pi = i / n  (fração acumulada de dimensões — eixo X).
    Passo 4: Φi = Xi / ΣXi  (fração individual); ΣΦi acumulado (eixo Y).
    """
    n = len(dimensions)
    if n < 2:
        raise ValueError("O CiSS requer ao menos 2 dimensões.")

    sorted_dims = sorted(dimensions, key=lambda d: d.score)
    total       = sum(d.score for d in sorted_dims)
    if total == 0:
        raise ValueError("Soma dos scores é zero — impossível calcular frações.")

    rows   = []
    phi_prev = 0.0

    for i, dim in enumerate(sorted_dims, start=1):
        pi      = i / n
        phi_i   = dim.score / total
        phi_cum = phi_prev + phi_i
        rows.append(LorenzRow(
            rank=i, name=dim.name, xi=dim.score,
            pi=pi, phi_i=phi_i, phi_cum=phi_cum,
            phi_pair=phi_prev + phi_cum,
            d_i=abs(pi - phi_cum),
        ))
        phi_prev = phi_cum

    return rows


def compute_ciss_financeiro(
    dimensions  : list[Dimension],
    institution : str = "Instituição Financeira",
    year        : int = 0,
    bsc_map     : Optional[list[BSCMapping]] = None,
) -> CiSSResult:
    """
    Função principal — executa os 7 passos matemáticos do CiSS Financeiro
    e, opcionalmente, o Passo 8 (mapeamento BSC).

    Passos
    ------
    0  Normalização por ln               [Indicator.normalized_value]
    1  Score Xi = média ponderada        [Dimension._compute_score]
    2  Ordenação ascendente por Xi       [build_lorenz_table]
    3  Pi = i/n                          [build_lorenz_table]
    4  Φi = Xi/ΣXi; ΣΦi acumulado       [build_lorenz_table]
    5  lorenz_sum = Σ (Φ(i-1) + Φi)     [abaixo]
    6  CiSS = lorenz_sum / n             [abaixo]
    7  SC   = 1 − CiSS                   [abaixo]
    8  Mapeamento BSC Sustentável        [parâmetro bsc_map — opcional]
    """
    n     = len(dimensions)
    table = build_lorenz_table(dimensions)

    lorenz_sum = sum(r.phi_pair for r in table)     # Passo 5
    mean_score = sum(r.xi for r in table) / n
    ciss = lorenz_sum / n                            # Passo 6
    sc   = 1.0 - ciss                                 # Passo 7

    return CiSSResult(
        institution=institution, year=year,
        n_dimensions=n, mean_score=mean_score,
        total_lorenz_sum=lorenz_sum,
        ciss=ciss, sc=sc,
        lorenz_table=table,
        bsc_map=bsc_map or [],
    )


# ── Mapeamento BSC padrão para o setor financeiro ─────────────────────────────

def bsc_mapping_padrao() -> list[BSCMapping]:
    """
    Mapeamento de referência entre as 3 dimensões do CiSS Financeiro
    e as 4 perspectivas do BSC Sustentável (Kaplan; Norton, 1997),
    conforme proposto no Apêndice A do artigo EnANPAD 2026.
    """
    return [
        BSCMapping(
            dimension_name="Econômico-Financeira",
            bsc_perspective="FINANCEIRA — qualidade da alocação de capital sob a ótica da sustentabilidade circular",
            strategic_indicators=["volume de crédito verde", "carteira sustentável (%)", "ROIC ajustado"],
        ),
        BSCMapping(
            dimension_name="Socioambiental",
            bsc_perspective="CLIENTES/STAKEHOLDERS — alinhamento entre produtos financeiros e expectativas sociais",
            strategic_indicators=["inclusão financeira (%)", "iniciativas ambientais", "benefícios regionais"],
        ),
        BSCMapping(
            dimension_name="Governança (ESG)",
            bsc_perspective="PROCESSOS INTERNOS — governança socioambiental nos fluxos operacionais de crédito",
            strategic_indicators=["política ESG", "compliance CMN 4.945/2021", "score GRI/ISE"],
        ),
    ]


# ── Utilitários ───────────────────────────────────────────────────────────────

def lorenz_points(result: CiSSResult) -> tuple[list[float], list[float]]:
    """Retorna (x, y) para plotar a Curva de Lorenz, incluindo a origem (0, 0)."""
    x = [0.0] + [r.pi      for r in result.lorenz_table]
    y = [0.0] + [r.phi_cum for r in result.lorenz_table]
    return x, y


def compare(a: CiSSResult, b: CiSSResult) -> str:
    """Retorna string comparando dois resultados CiSS Financeiro."""
    dc = b.ciss - a.ciss
    ds = b.sc   - a.sc
    dir_ = "melhorou ↑" if ds > 0 else "piorou ↓" if ds < 0 else "estável →"
    return (
        f"\n  Comparação  {a.year} → {b.year}  ({a.institution})\n"
        f"  ΔCiSS : {dc:+.6f}\n"
        f"  ΔSC   : {ds:+.6f}  ({dir_})\n"
    )


# ── Curva de Lorenz ───────────────────────────────────────────────────────────

def plot_lorenz(
    results   : list[CiSSResult],
    title     : str = "Curva de Lorenz — CiSS Financeiro",
    save_path : Optional[str] = None,
) -> None:
    """
    Plota a Curva de Lorenz para um ou mais resultados CiSS Financeiro.

    Cada resultado é desenhado como uma linha colorida com os pontos
    das dimensões anotados. A diagonal de perfeita igualdade serve
    como linha de referência. A área sombreada entre cada curva e a
    diagonal ilustra o grau de desequilíbrio entre dimensões.

    Parâmetros
    ----------
    results   : lista de CiSSResult (uma curva por resultado)
    title     : título do gráfico
    save_path : se fornecido, salva a figura neste caminho; caso contrário, exibe
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec
    except ImportError:
        print("\n  [!] matplotlib não encontrado.")
        print("      Instale com:  pip install matplotlib\n")
        return

    COLOURS = ["#1A3A5C", "#C0392B", "#2D6A4F", "#7B3F00", "#6B2D5E"]
    ALPHAS  = [0.16, 0.13, 0.10, 0.08, 0.06]

    fig = plt.figure(figsize=(13, 7), facecolor="#F7F4EF")
    gs  = GridSpec(1, 2, figure=fig, width_ratios=[2.2, 1],
                   left=0.07, right=0.97, bottom=0.11, top=0.88, wspace=0.07)
    ax  = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    for sp in (ax, ax2):
        sp.set_facecolor("#FDFCFA")
        for s in sp.spines.values():
            s.set_color("#C8C0B4")

    ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1.2,
            color="#A09888", alpha=0.7, label="Igualdade perfeita (referência)",
            zorder=1)

    ax.set_xticks([i/4 for i in range(5)])
    ax.set_yticks([i/4 for i in range(5)])
    ax.grid(True, linestyle=":", linewidth=0.6, color="#DDD8D0", alpha=0.8)

    legend_handles = []

    for idx, result in enumerate(results):
        colour = COLOURS[idx % len(COLOURS)]
        alpha  = ALPHAS[idx  % len(ALPHAS)]
        x, y   = lorenz_points(result)
        label  = (f"{result.institution} {result.year}  "
                  f"(CiSS={result.ciss:.4f}  SC={result.sc:.4f})")

        ax.fill_between(x, y, x, alpha=alpha, color=colour, zorder=2)

        line, = ax.plot(x, y, color=colour, linewidth=2.2,
                        marker="o", markersize=6,
                        markerfacecolor=colour, markeredgewidth=0,
                        zorder=4, label=label)

        for row in result.lorenz_table:
            ox = 0.015 if row.pi < 0.85 else -0.02
            ax.annotate(
                row.name,
                xy=(row.pi, row.phi_cum),
                xytext=(row.pi + ox, row.phi_cum + 0.02),
                fontsize=8, color=colour, alpha=0.9,
                fontfamily="monospace", zorder=5,
            )

        legend_handles.append(line)

    ax.set_xlim(-0.02, 1.06)
    ax.set_ylim(-0.02, 1.10)
    ax.set_xlabel("Pi  —  Fração acumulada de dimensões",
                  fontsize=10, color="#555555", labelpad=8)
    ax.set_ylabel("ΣΦi  —  Fração acumulada dos scores",
                  fontsize=10, color="#555555", labelpad=8)
    ax.set_title(title, fontsize=13, fontweight="bold",
                 color="#1C1A17", pad=14)
    ax.legend(handles=legend_handles, loc="upper left", fontsize=8.5,
              framealpha=0.92, edgecolor="#C8C0B4", fancybox=False)

    # Painel direito — resumo + BSC
    ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
    ax2.set_xticks([]); ax2.set_yticks([])
    ax2.set_title("Resumo", fontsize=10, color="#555555", pad=10, loc="left")

    row_h = 0.09
    top   = 0.93
    col_x = [0.02, 0.42, 0.66, 0.84]
    for cx, hd in zip(col_x, ["Instituição/Ano", "CiSS", "SC", "Dims"]):
        ax2.text(cx, top, hd, fontsize=7.5, fontweight="bold",
                 color="#1A3A5C", va="top", fontfamily="monospace")
    ax2.axhline(y=top - 0.025, xmin=0.02, xmax=0.98,
                color="#C8C0B4", linewidth=0.8)

    for i, result in enumerate(results):
        yp     = top - 0.06 - i * row_h
        colour = COLOURS[i % len(COLOURS)]
        vals   = [f"{result.institution} {result.year}",
                  f"{result.ciss:.4f}", f"{result.sc:.4f}",
                  str(result.n_dimensions)]
        if i % 2 == 0:
            ax2.axhspan(yp - 0.005, yp + row_h * 0.6,
                        xmin=0.01, xmax=0.99,
                        color=colour, alpha=0.06)
        for cx, val in zip(col_x, vals):
            ax2.text(cx, yp, val, fontsize=7.5, color=colour,
                     va="top", fontfamily="monospace")

    note_y = top - 0.06 - len(results) * row_h - 0.06
    note = (
        "Interpretação:\n"
        "CiSS → 1 : fluxos de capital\n"
        "    equilibrados entre dimensões\n"
        "CiSS → 0 : concentração extrema\n"
        "SC = 1 − CiSS (gap circular)"
    )
    ax2.text(0.02, note_y, note, fontsize=7, color="#777777",
             va="top", linespacing=1.6,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#F0EDE8",
                       edgecolor="#C8C0B4", linewidth=0.8))

    fig.text(0.5, 0.025,
             "Fonte: CiSS Financeiro — adaptado de Porto (2021)  |  "
             "Apêndice A, artigo EnANPAD 2026 (setor financeiro / BASA)",
             ha="center", fontsize=7.5, color="#999999")

    plt.tight_layout(rect=[0, 0.04, 1, 1])

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"\n  Gráfico salvo em: {save_path}")
    else:
        plt.show()

    plt.close(fig)


# ── Demo — exemplo ilustrativo do setor financeiro (BASA) ─────────────────────

def _demo(show_plot: bool = True, save_path: Optional[str] = None) -> None:
    """
    Reproduz um exemplo ilustrativo do CiSS Financeiro aplicado a uma
    instituição financeira de fomento regional, conforme proposto no
    Apêndice A do artigo EnANPAD 2026.

    Os valores são ILUSTRATIVOS — destinados a demonstrar o funcionamento
    do algoritmo. A aplicação empírica real ao BASA é etapa de pesquisa
    futura, dependente de dados institucionais primários.
    """

    print("\n" + "="*64)
    print("  AVISO: dados ilustrativos para demonstração do algoritmo.")
    print("  Aplicação empírica real depende de dados institucionais do BASA.")
    print("="*64)

    # ── Dimensão Econômico-Financeira ────────────────────────────────
    dim_econ_2024 = Dimension(
        name="Econômico-Financeira",
        indicators=[
            Indicator("Volume crédito verde (R$)",      850_000_000, weight=0.35,
                      scale_type=ScaleType.OPEN_POSITIVE, ec_principle="estreitamento"),
            Indicator("Carteira sustentável (%)",        22.5,        weight=0.30,
                      scale_type=ScaleType.CLOSED,        ec_principle="estreitamento"),
            Indicator("ROIC ajustado (%)",                9.8,        weight=0.20,
                      scale_type=ScaleType.CLOSED,        ec_principle="estreitamento"),
            Indicator("Risco socioambiental (score 0-100)", 68.0,     weight=0.15,
                      scale_type=ScaleType.CLOSED,        ec_principle="estreitamento"),
        ]
    )

    # ── Dimensão Socioambiental ───────────────────────────────────────
    dim_socioamb_2024 = Dimension(
        name="Socioambiental",
        indicators=[
            Indicator("Inclusão financeira (%)",          34.2,       weight=0.30,
                      scale_type=ScaleType.CLOSED,         ec_principle="fechamento"),
            Indicator("Iniciativas ambientais (n)",        12,        weight=0.35,
                      scale_type=ScaleType.OPEN_ZERO,      ec_principle="desaceleracao"),
            Indicator("Benefícios sociais regionais (R$)",  18_500_000, weight=0.35,
                      scale_type=ScaleType.OPEN_POSITIVE,  ec_principle="fechamento"),
        ]
    )

    # ── Dimensão Governança (ESG) ─────────────────────────────────────
    dim_gov_2024 = Dimension(
        name="Governança (ESG)",
        indicators=[
            Indicator("Score GRI (0-100)",                  61.0,     weight=0.30,
                      scale_type=ScaleType.CLOSED,           ec_principle="estreitamento"),
            Indicator("Score ISE/B3 (0-1)",                   0.0,     weight=0.30,
                      scale_type=ScaleType.CLOSED,           ec_principle="estreitamento"),
            Indicator("Compliance CMN 4.945/2021 (%)",       72.0,     weight=0.40,
                      scale_type=ScaleType.CLOSED,           ec_principle="estreitamento"),
        ]
    )

    bsc = bsc_mapping_padrao()

    result_2024 = compute_ciss_financeiro(
        [dim_econ_2024, dim_socioamb_2024, dim_gov_2024],
        institution="Banco Regional (ilustrativo)",
        year=2024,
        bsc_map=bsc,
    )

    print(result_2024.summary())

    print("  Valores normalizados por ln (Passo 0):")
    for dim in [dim_econ_2024, dim_socioamb_2024, dim_gov_2024]:
        print(f"\n  [{dim.name}]  Xi = {dim.score:.4f}")
        for ind in dim.indicators:
            print(f"    {ind.name:<34} bruto={ind.value:>14.2f}  "
                  f"ln_norm={ind.normalized_value:>8.4f}  "
                  f"escala={ind.scale_type.name:<14}  "
                  f"EC={ind.ec_principle}")

    if show_plot:
        print("\n  Abrindo Curva de Lorenz...")
        print("  (feche a janela para encerrar)\n")
        plot_lorenz(
            results=[result_2024],
            title="Curva de Lorenz — CiSS Financeiro  |  Exemplo Ilustrativo (BASA)",
            save_path=save_path,
        )


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args      = sys.argv[1:]
    show      = "--no-plot" not in args
    save_path = None

    if "--save" in args:
        idx = args.index("--save")
        if idx + 1 < len(args):
            save_path = args[idx + 1]
            show      = False

    _demo(show_plot=show, save_path=save_path)
