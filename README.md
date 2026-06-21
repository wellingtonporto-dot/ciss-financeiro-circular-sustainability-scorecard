# CiSS Financeiro — Circular Sustainability Scorecard (Setor Financeiro)

Computational algorithm adapting the Circular Sustainability Scorecard (CiSS)
to the financial sector, illustrated with a regional development bank example (BASA).

## Description
Adapted from Porto (2021), with three MBL dimensions tailored to financial
institutions — Economic-Financial, Socio-environmental, and Governance (ESG) —
plus a Balanced Scorecard Sustainable mapping layer (Kaplan; Norton, 1997).
Submitted as Appendix A to the EnANPAD 2026 article on circular sustainability
measurement challenges.

⚠️ **Note**: the demo uses illustrative data only. Empirical application to
real financial institutions is part of future research.

## Requirements
- Python 3.8+
- matplotlib (`pip install matplotlib`)

## Usage
\`\`\`bash
python ciss_financeiro.py              # runs illustrative demo + Lorenz curve
python ciss_financeiro.py --no-plot    # runs without opening chart
python ciss_financeiro.py --save fig.png  # saves chart as PNG
\`\`\`

## Citation
> Author (2026). CiSS Financeiro — Circular Sustainability Scorecard (Setor
> Financeiro) [Software]. Zenodo. https://doi.org/[DOI ADICIONADO APÓS DEPÓSITO]

## License
Creative Commons Attribution 4.0 International (CC BY 4.0)
