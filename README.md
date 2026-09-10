# SSM Capital & RWA Model — a self-study project

A small, from-scratch model of how a bank turns a portfolio of trading and financing transactions into regulatory capital ratios (RWA, CET1), built using State Street's public disclosures as a reference case. Includes a comparison of the current Basel III framework against the proposed Basel III Endgame reform.

## Files in this repo

- `ssm_rwa_model.py` — the calculation in plain Python, runnable end to end (`python3 ssm_rwa_model.py`)
- `SSM_Capital_RWA_Model.xlsx` — the same logic in Excel, with live formulas across four tabs (Portfolio, Capital_Summary, Stress_Scenario, Basel_III_Endgame)
- `ssm_dashboard.html` — an interactive version with sliders; open directly in a browser
- `sources/` — the underlying public filings referenced throughout (State Street 10-Q, 10-K, stress test disclosure, earnings materials)

## What this shows

- How a fully collateralized transaction can carry $0 in risk-weighted assets, regardless of size
- How a stress scenario erodes that collateral cushion and brings the RWA back
- How the Basel III Endgame proposal adds new capital charges (Operational Risk, CVA) rather than just adjusting existing risk weights, and why that specifically matters for a fee-driven custody bank like State Street

---

# Understanding Capital Optimization at a Custody Bank: A Self-Study Project

## Purpose

I wanted to understand how a bank actually turns a portfolio of trading and financing transactions into the regulatory capital ratios it reports every quarter — RWA, CET1 ratio, stress-tested capital — because reading definitions of these terms wasn't enough to make them click. I decided the only way to really understand the mechanics was to build a small, simplified version of the calculation myself, rather than continue reading about it in the abstract.

I used State Street as my reference case, since it publishes detailed public disclosures (10-Q filings, annual stress test results, earnings releases) and its Markets division is built around a distinctive mix of businesses — repo financing, securities lending, and derivatives — that isn't well represented in generic banking textbooks. I am not affiliated with State Street, and none of the transaction-level figures in this project are theirs; I used their public disclosures only to shape the categories, scenario assumptions, and target ratios that make this exercise realistic rather than arbitrary.

The project also gave me a chance to engage with a live regulatory issue — the Basel III "Endgame" reform currently being re-proposed by U.S. regulators (as of March 2026) — and to see, in a small model, why the specific wording of a capital rule can matter as much as the headline requirement.

## Methodology

I built three versions of the same calculation so I could check them against each other:

1. An Excel workbook with live formulas, so changing an input immediately shows its effect on the output.
2. A Python script performing the identical calculation in code, useful for testing scenarios quickly.
3. An interactive dashboard (HTML, with adjustable sliders) for a more visual, exploratory view of the same mechanics.

All three produced identical results, which served as a basic internal consistency check on the formulas.

### Building a mock portfolio

Because a real trading book is not public information, I constructed a small fictional portfolio of sixteen transactions, structured around the categories that appear in State Street's own regulatory disclosures (specifically, the RWA roll-forward table in its 10-Q):

- **Repo-style transactions** — short-term secured lending, typically collateralized by Treasury securities
- **OTC derivatives** — FX forwards, FX swaps, and interest rate swaps
- **Loans** — a smaller, more traditional corporate lending book
- **Securitization** — asset-backed securities exposures
- **Indemnified securities financing** — lending clients' securities to borrowers, where the bank indemnifies the client against borrower default; this is a defining feature of custody-bank business models

Each transaction was assigned an exposure amount, a collateral amount, a haircut, and a risk weight. The individual figures are fictional, but the relationships between them (for example, that repo transactions are typically over-collateralized while unsecured corporate loans are not) were set deliberately to mirror how these instrument types actually behave.

## Baseline calculation

The calculation rests on the Basel formula for collateralized exposures:

**E\* = MAX(0, Exposure − Collateral × (1 − Haircut))**

This defines the exposure actually at risk as whatever remains after subtracting the value of the collateral held, less a haircut that accounts for the possibility the collateral loses value before it can be liquidated.

Risk-weighted assets are then:

**RWA = E\* × Risk Weight**

where the risk weight is a regulatory multiplier reflecting the riskiness of the counterparty and collateral type.

The clearest result from this step: a transaction can be worth hundreds of millions of dollars and contribute zero to RWA if it is fully collateralized. In this model, all four repo transactions and all three indemnified securities financing transactions produced $0 in RWA at baseline, because collateral was set slightly above exposure — consistent with State Street's own disclosure that it requires collateral "in excess of 100%" for these transaction types. By contrast, three much smaller unsecured corporate loans accounted for nearly half of total baseline RWA. This illustrates the core logic of capital optimization: RWA is driven by how well a position is collateralized, not by its notional size.

**Baseline results:**

| Metric | Value |
|---|---|
| Total RWA | $226.7M |
| CET1 Capital (assumption) | $24.5M |
| CET1 Ratio | 10.8% |

The CET1 Capital assumption was deliberately set so the resulting ratio would land close to State Street's actual reported 2Q 2026 CET1 ratio (also 10.8%). This was used purely as a calibration check, to confirm the mechanics of the model behave sensibly relative to a real, disclosed figure, despite the difference in scale.

## Stress testing

Regulators require large banks to project their capital ratios under a hypothetical severe recession. State Street's 2025 Dodd-Frank Act stress test disclosure specifies the "Severely Adverse" scenario assumptions: unemployment reaching 10%, GDP contracting 7.8%, and equity markets falling 50%.

I applied a simplified version of this shock to the mock portfolio:

- Collateral values cut by 50% wherever the collateral is equity-linked
- Haircuts increased by 5 percentage points, reflecting reduced collateral liquidity in a crisis
- Risk weights increased by 10 percentage points across the portfolio, reflecting broad credit deterioration under high unemployment

**Stressed results:**

| Metric | Value |
|---|---|
| Total RWA | $382.6M |
| Stressed CET1 Capital | $22.0M |
| Stressed CET1 Ratio | 5.7% |

The most notable outcome of this step: the repo and indemnified securities financing categories, which contributed $0 to RWA at baseline, generated $14.5M and $102.8M respectively under stress. The equity market shock erodes the collateral cushion that made these transactions "free" from a capital perspective at baseline; nothing about the transactions themselves changed, only the value of what backs them. The resulting 5.7% ratio remains above the 4.5% regulatory minimum, consistent with the outcome State Street itself reported in its actual 2025 disclosure.

## Basel III vs. Basel III Endgame

This comparison was the primary focus of the project, and it required revising an initial, incorrect assumption.

### An initial misstep

My first approach was to assume Endgame would simply lower risk weights on derivatives and securitization exposures by some percentage. This is a reasonable guess, but it does not reflect how the reform actually works, and it missed the aspect most relevant to a custody bank specifically.

### What Endgame actually introduces

Basel III Endgame does not primarily revise existing risk weights. It introduces two capital charges that do not currently exist under the standardized approach:

1. **Operational Risk RWA**, calculated from a "Business Indicator" (BI) — a formula based on a bank's income, particularly fee income, rather than its balance sheet.
2. **CVA (Credit Valuation Adjustment) RWA** — a new charge for the risk that a derivatives counterparty's mark-to-market value moves adversely before a position can be closed out.

### Relevance to a custody bank's business model

This is the detail the initial approach missed. Custody banks such as State Street derive most revenue from fees — servicing fees, management fees, FX trading fees — rather than lending interest. In its public SEC filings, State Street raised specific concerns about this: the original 2023 Endgame proposal measured fee income and fee expenses within the Business Indicator on a gross basis, with no netting, which would disproportionately affect fee-heavy institutions relative to traditional lending banks.

The March 2026 re-proposal responds directly to that concern, allowing the "services leg" of the Business Indicator to be measured on a net basis (fee income less fee expenses) instead of gross — a specific, targeted concession for institutions built like State Street.

### Applying this to the model

A mock Business Indicator was constructed using the following illustrative inputs:

| Input | Value |
|---|---|
| Interest income | $5.0M |
| Fee income | $20.0M |
| Fee expenses | $12.0M |
| Financial component | $2.0M |

Under the **2023 draft** (gross treatment), the services leg equals $20.0M + $12.0M = $32.0M, producing a total Business Indicator of $39.0M.

Under the **2026 re-proposal** (net treatment), the services leg equals $20.0M − $12.0M = $8.0M, producing a total Business Indicator of $15.0M.

Applying the Operational Risk RWA formula (RWA = 12.5 × BI × marginal coefficient × loss multiplier) and an illustrative CVA charge on the derivatives book produces the following comparison:

| Scenario | Total RWA | CET1 Ratio |
|---|---|---|
| Current Basel III — Baseline | $226.7M | 10.8% |
| Current Basel III — Stressed | $382.6M | 5.7% |
| Endgame 2023 draft — Baseline | $305.1M | 8.0% |
| Endgame 2023 draft — Stressed | $466.9M | **4.7%** |
| Endgame 2026 re-proposal — Baseline | $269.1M | 9.1% |
| Endgame 2026 re-proposal — Stressed | $430.9M | 5.1% |

### Key finding

Under the 2023 draft, the stressed CET1 ratio falls to 4.7% — only 0.2 percentage points above the 4.5% regulatory floor. Given this is a small, illustrative model, the exact figure should not be over-interpreted, but the direction is informative: it is broadly consistent with why the banking industry opposed the 2023 draft, and with the specific concern State Street raised about the treatment of fee income.

Under the 2026 re-proposal, the same stress scenario produces a 5.1% ratio — a meaningfully larger buffer, driven entirely by the change in how fee income is measured within the Business Indicator. No assumption about the underlying portfolio changed between these two scenarios; only the accounting treatment of a single input did. This is the clearest illustration in the project of how a technical drafting choice in a capital rule can materially affect an institution's reported safety margin.

## Limitations

- The real Business Indicator formula applies tiered marginal coefficients (12% / 15% / 18%, depending on the size of the BI); this model simplifies to a single 12% bucket.
- Changes to standardized credit risk weights under Endgame were not modeled; the focus here was on the operational risk and CVA components, which represent the larger and more custody-bank-specific impact.
- The CVA charge (20% of Derivatives RWA) is an illustrative assumption, not a regulatory formula.
- All dollar figures are fictional and scaled down for illustration. Nothing in this report reflects State Street's actual balance sheet, revenue, or capital position.

## Conclusion

This project shows, at a small scale, how collateralization — not transaction size — drives regulatory capital requirements, and how a specific rule-drafting choice (measuring fee income gross versus net) can move a stressed capital ratio close to its regulatory floor for a fee-based institution. Building the calculation from scratch, rather than reading about it, was what made these relationships legible.

## Next steps

- Finalize the interactive dashboard and add a walkthrough with screenshots
- Extend the model to incorporate the tiered Business Indicator coefficients in place of the single-bucket simplification
- Adapt this report into a shorter slide format for presentation purposes

---

## Appendix

### A. Sources

| Source | Used for |
|---|---|
| State Street 10-Q, June 30 2026 | RWA roll-forward categories, indemnified securities financing figures, repo/securities lending structure |
| State Street 2025 Dodd-Frank Act Stress Test Disclosure | Severely Adverse scenario assumptions (unemployment, GDP, equity market decline) |
| State Street 2Q26 Earnings Release Addendum | Real CET1 ratio and RWA figures used for baseline calibration |
| State Street SEC filings (10-K, FY2024/FY2025) | State Street's disclosed position on the Basel III Endgame proposal and its concerns regarding operational risk treatment of fee income |
| Federal Reserve press release, March 19 2026 | Basel III Endgame re-proposal announcement |

### B. Full mock portfolio (16 transactions)

| Category | Exposure ($M) | Collateral ($M) | Haircut | Risk Weight |
|---|---|---|---|---|
| Repo | 420 | 435 | 2% | 20% |
| Repo | 310 | 318 | 2% | 20% |
| Repo | 260 | 268 | 2% | 20% |
| Repo | 180 | 185 | 2% | 20% |
| Derivatives | 150 | 90 | 5% | 50% |
| Derivatives | 130 | 70 | 5% | 50% |
| Derivatives | 95 | 40 | 5% | 50% |
| Derivatives | 80 | 45 | 5% | 20% |
| Loans | 60 | 20 | 10% | 100% |
| Loans | 45 | 15 | 10% | 100% |
| Loans | 35 | 10 | 10% | 100% |
| Securitization | 25 | 5 | 3% | 75% |
| Securitization | 20 | 4 | 3% | 75% |
| Indemnified sec. financing | 300 | 315 | 2% | 20% |
| Indemnified sec. financing | 220 | 231 | 2% | 20% |
| Indemnified sec. financing | 150 | 158 | 2% | 20% |

Category-level RWA totals (baseline and stressed) are shown in the Baseline and Stress Testing sections above.

### C. Formula reference

- Exposure at risk: E\* = MAX(0, Exposure − Collateral × (1 − Haircut))
- Risk-weighted assets: RWA = E\* × Risk Weight
- CET1 Ratio: CET1 Capital ÷ Total RWA
- Operational Risk RWA (Endgame): 12.5 × Business Indicator × Marginal Coefficient × Internal Loss Multiplier
- Business Indicator: Interest leg + Services leg + Financial leg
  - Services leg, 2023 draft: Fee income + Fee expenses (gross)
  - Services leg, 2026 re-proposal: Fee income − Fee expenses (net)

### D. Screenshots

*(To be added: Excel Portfolio tab, Capital_Summary tab, Stress_Scenario tab, Basel_III_Endgame tab, and the interactive dashboard, once finalized.)*
