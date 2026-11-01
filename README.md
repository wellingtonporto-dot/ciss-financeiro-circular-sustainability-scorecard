# CiSS Financial – Circular Sustainability Scorecard for the Financial Sector (v2.0.0)

CiSS Financial adapts the Circular Sustainability Scorecard (Porto, 2021) to financial institutions. It measures how evenly an institution's performance is distributed across three dimensions — economic-financial, socio-environmental and governance — using the Lorenz curve and the Gini coefficient. Circularity is reinterpreted as the recirculation of capital: what the institution finances, not only its own operational footprint.

This repository contains the algorithm and the data of the illustrative application to Banco da Amazônia (BASA), 2021–2024, reported in the article *Beyond ESG Disclosure: Adapting the Circular Sustainability Scorecard to Assess the Legitimacy of Capital Allocation in Financial Institutions* (under review).

## Contents

| File | Description |
|---|---|
| `CiSS_Financial_v2.py` | The algorithm and the illustrative application. Produces the result tables and figures. |
| `data/indicators_BASA_2021_2024.csv` | The 24 indicators, 2021–2024, with dimension, BSC perspective, polarity, use in the main specification and source. |
| `CiSS_Financial_v2_results.xlsx` | Expected results: indicators, CiSS by year, robustness checks and BSC perspective scores. |
| `requirements.txt` | Python dependencies. |
| `CITATION.cff` | How to cite this repository. |
| `LICENSE` | Creative Commons Attribution 4.0 International (CC BY 4.0), as in earlier versions. |

## How to run

Python 3.10 or later.

```bash
pip install -r requirements.txt
python CiSS_Financial_v2.py            # tables on screen, Excel file and figures/
python CiSS_Financial_v2.py --no-figs  # tables and Excel only
```

The script prints three tables and writes `CiSS_Financial_v2_results.xlsx`. Without `--no-figs` it also writes three figures to `figures/`: dimension scores, evolution of the CiSS, and Lorenz curves for 2021 and 2024.

## Algorithm (summary)

The full description is in Appendix A of the article.

1. **Step 0 – Normalization.** Each indicator is divided by its mean over the period (z = x / mean). Indicators in which lower is better (energy, emissions, efficiency ratio, staff turnover) are inverted (z = mean / x). Missing years are skipped when computing the mean.
2. **Step 1 – Dimension scores.** Each dimension score is the mean of its normalized indicators (equal weights by default).
3. **Steps 2–5 – Lorenz curve.** Dimension scores are sorted in ascending order and their cumulative shares Φ are computed.
4. **Steps 6–7 – CiSS and SC.** CiSS = (1/n) Σ (Φᵢ₋₁ + Φᵢ) = 1 − Gini; SC = 1 − CiSS.
5. **Step 8 – BSC reading layer.** The same indicators are re-aggregated by Sustainable BSC perspective. These scores do not enter the CiSS.

CiSS measures **balance, not level**. Because each indicator is centred on its own period mean, the CiSS compares the institution with its own trajectory and values close to 1 are expected. The mean of the dimension scores is reported alongside it as a level indicator.

## Results of the illustrative application (main specification)

| | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|
| Mean dimension score (level) | 0.8692 | 0.9888 | 1.0361 | 1.1188 |
| CiSS (= 1 − Gini) | 0.9558 | 0.9836 | 0.9763 | 0.9888 |

Robustness specifications: (B) conventional indicators only; (C) min–max normalization; (D) the version 1.0 rule; (E) including dividends; (F) excluding the bank's own operational footprint.

## Data

- **Conventional indicators (18 used, plus dividends reported but excluded from the main specification):** financial results, operational footprint and people management. Sources: BASA integrated annual reports 2021–2024 (GRI 201-1, 302-1, 305-1 to 305-3, 401-1, 404-1, 405-1) and BASA investor-relations results releases and historical series, 4Q21–4Q24.
- **Capital-allocation indicators (5):** credit in FNO green lines, share of FNO credit in green lines, share of FNO credit in low- and middle-income municipalities, PRONAF family-farming credit and productive microcredit (MPO). The CSV gives the report and page for each value.
- **Excluded series:**
  - Dividends and interest on equity: they measure shareholder remuneration, not capital circularity. Their effect is reported in specification E.
  - Customer satisfaction: the series breaks between 2021 and 2022 and has no 2024 value.

All reports are publicly available at <https://ri.bancoamazonia.com.br>.

### Known data issues

- **FNO green lines, 2023.** The 2023 report gives R$ 6.68 bn in its table by programme (p. 103) and R$ 5.9 bn in the text (p. 76). The table value is used.
- **FNO contracted, 2024.** The 2024 percentages imply a base below the reported R$ 13.5 bn total. The reported total is used.
- **Microcredit (MPO), 2023.** Derived from the 28.9% growth the 2024 report gives for 2024 over 2023.
- **Efficiency ratio, 2023.** Not reported, so it is skipped in the mean.
- **Scope 3 emissions.** The values cover the bank's operations only, not the emissions it finances.

## Changes from earlier versions

- Normalization by the natural logarithm, with percentages left untransformed, was replaced by a polarity-adjusted ratio-to-mean normalization. The old rule mixed scales and ignored polarity; it is kept as robustness specification D.
- Indicators are now mapped explicitly to three dimensions and five BSC perspectives, instead of being matched by keywords.
- The CiSS is computed as (1/n) Σ (Φᵢ₋₁ + Φᵢ) = 1 − Gini. Computing it as the area under the Lorenz curve, as a numerical `trapz` routine does, halves the index.
- Added the illustrative application to BASA, with capital-allocation indicators and robustness specifications.

## Previous versions in this repository

Earlier scripts are kept in the repository so that the results of earlier studies remain reproducible. Each release and its Zenodo version keep a fixed copy of the code used at that time.

| File | Release | Used in | Method |
|---|---|---|---|
| `CiSS_Financial_v2.py` | **v2.0.0 (current)** | *Beyond ESG Disclosure* (under review) | Ratio-to-mean normalization with polarity, 3 MBL dimensions, CiSS = 1 − Gini, capital-allocation indicators |
| `CiSS_BASA_V3.py` (+ `Figura1–3` .png/.tif) | v1.1.0 | Empirical study of Banco da Amazônia (conference paper; under review in another journal) | Ratio-to-mean normalization with polarity, 5 Sustainable BSC perspectives, CiSS = 1 − Gini, robustness specifications A–D |
| `CiSS_BASA_V2.py` | v1.0.2 | Dissertation and conference results | Natural log and raw percentages (equivalent to specification D of V3); requires the spreadsheet `COMPARATIVO BSC BASA ISA.xlsx`, not included |
| `ciss_financeiro.py` (+ `lorenz_ciss_financeiro.png`) | v1.0.0 | EnANPAD 2026 paper (Appendix A) | Conceptual demo with illustrative data |

To use the exact code of an earlier study, download the corresponding release on GitHub or the corresponding version on Zenodo.

## Use of AI tools

ChatGPT (OpenAI) helped write earlier versions of the code. Claude (Anthropic) wrote, standardized and debugged version 2.0 and helped collect figures from the bank's public reports. The authors checked every value against its source.

## How to cite

See `CITATION.cff`, or cite as:

Souza, I. C. G. de, Porto, W. S., & Souza, J. A. de. (2026). *CiSS Financial – Circular Sustainability Scorecard for the Financial Sector* (Version 2.0.0) [Computer software and dataset]. Zenodo. https://doi.org/10.5281/zenodo.23852741

## Reference

Porto, W. S. (2021). *CiSS – Circular Sustainability Scorecard: Desafios e perspectivas de uma métrica integrada para sustentabilidade circular* [Doctoral dissertation, Universidade Federal de Pernambuco].

## Contact

Wellington Silva Porto – wsporto@unir.br – Programa de Pós-Graduação em Administração e Contabilidade (PPGAC), Universidade Federal de Rondônia (UNIR), Vilhena, Brazil.
