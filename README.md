# RWA & CET1 Model — State Street Markets (Mock)

## Purpose

A small project I built to understand how a bank actually turns a portfolio of trades into a capital ratio. I made up a fictional trading and financing book shaped like State Street Markets' real business, then worked through how much regulatory capital it would need to hold first on a normal day, then in a severe recession, and finally under a new set of capital rules regulators are proposing (Basel III Endgame).

Reading about RWA and CET1 wasn't enough for to understand.

## What's fictional vs. real

Made up: repo, derivatives, loans, securitizations, indemnified securities financing.

Real: the formulas, the scenario assumptions, and the rule logic, all pulled from State Street's public filings (10-Q, stress test disclosure) and the actual Basel III Endgame proposals. I also set the CET1 capital figure so the baseline ratio lands close to State Street's real reported ratio (10.8%), just as a sanity check that the model behaves the way a real bank's numbers would.

## What's inside

| File | What it covers |
|---|---|
| Python model | Runs all three scenarios end to end and prints the results |
| Baseline tab | RWA and CET1 ratio under normal conditions, plus a check against the real number |
| Stress tab | Same book under a severe recession (unemployment 10%, GDP -7.8%, equities -50%) |
| Basel III Endgame tab | The two new capital charges Endgame adds, compared across current rules and both Endgame versions |

## The headline finding

Both Endgame versions leave this mock bank worse off than current Basel III — that's expected, since Endgame adds new charges rather than removing anything. What's interesting is how much worse, and why.

Under the 2023 draft, the stressed ratio falls to 4.7%, just 0.2 points above the regulatory floor. Under the 2026 re-proposal, the same stress scenario lands at 5.1%, a noticeably bigger buffer. Nothing about the portfolio changes between those two numbers — the entire swing comes from one accounting choice, whether fee income is measured gross or net of expenses.

That's why a fee-heavy institution like State Street cares so specifically about this one detail, more than about Basel III Endgame in general.

## Screenshots & charts

Screenshots of the four Excel tabs are below, along with a few charts comparing RWA and CET1 ratio across frameworks. *(Charts to be added directly in Excel.)*
