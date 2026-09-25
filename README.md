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

## Versões do script

| Arquivo | Situação | Descrição |
|---|---|---|
| `CiSS_BASA_V3.py` | **Atual (v1.1.0)** | Normalização pela média do período com correção de polaridade; composição constante das perspectivas; CiSS = 1 − Gini (0 a 1); especificações de robustez A–D; gera tabelas (Excel) e figuras (PNG/TIF, 300 dpi, P&B). |
| `CiSS_BASA_V2.py` | Anterior (v1.0.x) | Mantido para reprodutibilidade dos resultados da dissertação e dos congressos. Equivale à especificação D da V3. Requer a planilha `COMPARATIVO BSC BASA ISA.xlsx`. |

### Como executar a V3
    pip install -r requirements.txt
    python CiSS_BASA_V3.py              # tabelas + figuras (exibidas e salvas)
    python CiSS_BASA_V3.py --sem-exibir # salva as figuras sem abrir janelas
    python CiSS_BASA_V3.py --sem-figuras

No Python/Spyder:
    import runpy
    runpy.run_path(r"caminho\para\CiSS_BASA_V3.py", run_name="__main__")

Os dados de entrada (Relatórios do Banco da Amazônia, 2021–2024) estão embutidos no script.
