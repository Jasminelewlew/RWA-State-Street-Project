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

## What I find interesting
 
Two things stood out while building this.
 
**1.$0 RWA** 
At baseline, four repo transactions and three indemnified securities financing transactions, some of the largest dollar amounts in the whole book carry exactly $0 in RWA. Not because they're low-risk on paper, but because they're collateralized slightly above 100%, so once you subtract collateral from exposure there's nothing left to charge capital against. Meanwhile three small unsecured loans, tiny by comparison, end up driving nearly half of total RWA. It made the core idea click for me: capital requirements track how well a position is collateralized, not how big it is. And that "free" treatment only holds up when markets are calm and run the same book through a stress scenario and the equity shock take into that collateral cushion, and the RWA comes right back.
 
**2. Why State Street pushed back on the original Endgame proposal.** 
At first, I assumed Endgame would just tweak existing risk weights, which turned out to be wrong. It actually adds a brand new charge: Operational Risk RWA, calculated off something called the Business Indicator, which is built mostly from fee income rather than lending activity. That matters a lot for a custody bank like State Street, which makes most of its money from fees, not interest. The 2023 draft measured that fee income on a gross basis (income plus expenses, no netting), which hits a fee heavy bank especially hard. State Street flagged this directly in its own filings.
 
The 2026 re-proposal doesn't get rid of the charge. It's still there and Endgame is still net-net a bigger capital burden than today's rules. But it does soften this one piece, letting fee income be measured net instead of gross, and that single change moved my model's stressed ratio from 4.7% (uncomfortably close to the 4.5% floor) up to 5.1%. Nothing about the underlying business changed, just the accounting treatment of one input. That's the part that made this proposal feel less like regulators backing off and more like regulators listening to one very specific, well-argued complaint.
 
## The headline finding
 
Both Endgame versions leave this mock bank worse off than current Basel III which expected, since Endgame adds new charges rather than removing anything. What's interesting is how much worse, and why.
 
Under the 2023 draft, the stressed ratio falls to 4.7%, just 0.2 points above the regulatory floor. Under the 2026 re-proposal, the same stress scenario lands at 5.1%, a noticeably bigger buffer. Nothing about the portfolio changes between those two numbers. The entire swing comes from one accounting choice: whether fee income is measured gross or net of expenses.
 
That's what institution like State Street will care in more details , more than about Basel III Endgame in general.

## The math behind it
 
Everything runs off two formulas, the standard Basel approach for collateralized exposures:
 
**E\* = MAX(0, Exposure − Collateral × (1 − Haircut))**
 
That's the exposure actually at risk, whatever's left after subtracting the collateral you hold, discounted a bit for the haircut, since collateral can lose value before you're able to sell it.
 
**RWA = E\* × Risk Weight**
 
The risk weight is just a regulator set multiplier for how risky that counterparty or collateral type is considered.
 
Under stress, 3 things shift before those formulas run again: equity linked collateral gets cut by the equity shock (-50%), haircuts widen by 5 points, and risk weights climb by 10 points.
 
For the Basel III Endgame side, the new Operational Risk charge is:
 
**Operational Risk RWA = 12.5 × Business Indicator × Marginal Coefficient × Internal Loss Multiplier**
 
where the Business Indicator is just interest income + services income + financial income, and the only thing that changes between the 2023 draft and the 2026 re-proposal is whether the services leg nets out fee expenses or not.
 
## Sources
 
| Source | Used for |
|---|---|
| State Street 10-Q, June 30 2026 | Transaction categories, RWA roll-forward, indemnified securities financing figures |
| State Street 2025 Dodd-Frank Act Stress Test Disclosure | Severely Adverse scenario assumptions (unemployment, GDP, equity decline) |
| State Street 2Q26 Earnings Release Addendum | Real CET1 ratio and RWA, used to calibrate the baseline |
| State Street SEC filings (10-K) | State Street's disclosed concerns about how Endgame treats fee income |
| Federal Reserve press release, March 19 2026 | Announcement of the Basel III Endgame re-proposal |
 

## Screenshots & charts

Screenshots of the four Excel tabs are below, along with a few charts comparing RWA and CET1 ratio across frameworks. *(Charts to be added directly in Excel.)*
