"""
Mock SSM RWA & CET1 model

I builds a small fictional trading financing book shaped like State Street Markets' real business, then
calculates how much regulatory capital (RWA and the CET1 ratio) it would
need to hold. 
At first stage is under normal conditions
then under a severe recession
finally under a proposed new set of banking rules (Basel III Endgame).

None of the transaction level numbers are State Street's real data they are fictional, scaled down for a learning exercise. 
The formulas, scenario assumptions, and general logic are drawn from State Street's public filings (10-Q, stress test disclosure) and 
from the actual text of the Basel III Endgame proposals.
"""

# Each mock transaction: category, exposure, collateral, haircut, risk
# weight, and whether its collateral is equity-linked (matters later,
# when we run the stress scenario).

rows = [
    ("Repo", 420, 435, 0.02, 0.20, False),
    ("Repo", 310, 318, 0.02, 0.20, False),
    ("Repo", 260, 268, 0.02, 0.20, False),
    ("Repo", 180, 185, 0.02, 0.20, False),
    ("Derivatives", 150, 90, 0.05, 0.50, False),
    ("Derivatives", 130, 70, 0.05, 0.50, False),
    ("Derivatives", 95, 40, 0.05, 0.50, False),
    ("Derivatives", 80, 45, 0.05, 0.20, False),
    ("Loans", 60, 20, 0.10, 1.00, False),
    ("Loans", 45, 15, 0.10, 1.00, False),
    ("Loans", 35, 10, 0.10, 1.00, False),
    ("Securitization", 25, 5, 0.03, 0.75, True),
    ("Securitization", 20, 4, 0.03, 0.75, True),
    ("Indemnified sec. fin.", 300, 315, 0.02, 0.20, True),
    ("Indemnified sec. fin.", 220, 231, 0.02, 0.20, True),
    ("Indemnified sec. fin.", 150, 158, 0.02, 0.20, True),
]

# I picked $24.5M
# because it makes the baseline CET1 ratio land close to State Street's
# actual reported 2Q 2026 ratio (10.8%), as a sanity check on the model
CET1_CAPITAL = 24.5


def rwa_for_row(exposure, collateral, haircut, risk_weight,
                 equity_sensitive=False, equity_shock=0, hc_add=0, rw_add=0):
    """
    One formula the whole project rests on 
    the Basel approach for collateralized transactions: the real risk isn't the
    full amount you lent, it's whatever's left over after subtracting
    the collateral you're holding (discounted a bit for the haircut,
    since collateral can lose value before you can sell it)

        E* = max(0, exposure - collateral * (1 - haircut))
        RWA = E* * risk_weight

    If collateral comfortably covers the exposure
    E* comes out to zero
    meaning this transaction contributes nothing to RWA, no matter how
    large it is on paper
    I believe this is the core idea behind "capital optimization"
    it's about how well collateralized a book is, not how big it is.
    """
    if equity_sensitive:
        # Only equity backed collateral gets hit by an equity market
        # shock: Treasury backed repo collateral wouldn't move the same way.
        collateral = collateral * (1 + equity_shock)  # equity_shock is negative, e.g. -0.5
    haircut = haircut + hc_add
    risk_weight = min(1.0, risk_weight + rw_add)
    e_star = max(0, exposure - collateral * (1 - haircut))
    return e_star * risk_weight


def total_rwa(equity_shock=0, hc_add=0, rw_add=0):
    """Runs every row through the formula above and adds it all up, both
    as a grand total and broken out by category so we can see which
    types of transactions are actually driving the number"""
    total = 0
    by_category = {}
    for cat, exp, coll, hc, rw, eq in rows:
        r = rwa_for_row(exp, coll, hc, rw, eq, equity_shock, hc_add, rw_add)
        total += r
        by_category[cat] = by_category.get(cat, 0) + r
    return total, by_category


def cet1_ratio(capital, rwa):
    """The headline number regulators actually watch: how much loss
    absorbing capital a bank holds relative to its risk-weighted assets."""
    return capital / rwa

# STEP 1 - Baseline: what does this book look like on a normal day?

base_rwa, base_by_cat = total_rwa()
print("=== Baseline ===")
print("Total RWA:", round(base_rwa, 1))
print("CET1 Ratio:", round(cet1_ratio(CET1_CAPITAL, base_rwa) * 100, 1), "%")
for cat, val in base_by_cat.items():
    print(" ", cat, ":", round(val, 1))

print(
    "\n Notice Repo and Indemnified sec. fin. both show $0.0M RWA here, even though they're the largest dollar amounts in "
    "the whole book. That's because I set their collateral slightly above the exposure, which mean fully collateralized, so there's technically "
    "nothing left to charge capital against. Meanwhile Loans, the smallest category by dollar amount, is one of the biggest "
    "contributors to RWA, simply because it's barely collateralized."
)

# STEP 2 - Stress test: what happens in a severe recession?

# These three shocks are a simplified stand in for State Street's actual
# 2025 "Severely Adverse" stress scenario: unemployment hits 10%, GDP
# shrinks 7.8%, and equity markets fall 50%.

stress_rwa, stress_by_cat = total_rwa(equity_shock=-0.50, hc_add=0.05, rw_add=0.10)
stress_capital = CET1_CAPITAL + 1.5 - 3.0 - 1.0  # net income - losses, illustrative
print("\n=== Stress (Severely Adverse) ===")
print("Total RWA:", round(stress_rwa, 1))
print("Stressed CET1 Capital:", round(stress_capital, 1))
print("Stressed CET1 Ratio:", round(cet1_ratio(stress_capital, stress_rwa) * 100, 1), "%")
for cat, val in stress_by_cat.items():
    print(" ", cat, ":", round(val, 1))

print(
    "\n This is the part I found most convincing. Repo and Indemnified sec. fin. jump from $0.0M to real, nonzero RWA "
    "under stress, not because the transactions changed, but because the equity shock eats into their collateral cushion. The 'free' "
    "capital treatment at baseline was only free because markets were calm. Even so, the stressed ratio (5.7%) stays above the 4.5% "
    "regulatory floor, which is the whole point of a stress test proving the bank survives a bad scenario, not just a normal one."
)

# STEP 3 - Basel III Endgame: what if the capital rules themselves change?

# Important correction from an earlier version: 
# Endgame
# does NOT mainly cut existing risk weights. It adds two capital charges
# that don't exist yet under the current standardized approach. Modeling
# it as a flat risk-weight discount (my first attempt) was the wrong
# mechanism entirely

# New charge #1: Operational Risk RWA, via the "Business Indicator"
# The Business Indicator is built mostly from INCOME, not the balance
# sheet which matters a lot for a fee driven custody bank like State
# Street. These are mock revenue figures, not State Street's real ones.
# So we use Net instead of Gross

BI_INTEREST_INCOME = 5.0   # a rough stand in for net interest income
BI_FEE_INCOME = 20.0       # sized to reflect a fee heavy, custody style business
BI_FEE_EXPENSE = 12.0      # the cost of actually providing those fee services
BI_FINANCIAL = 2.0         # a small trading P&L component

MARGINAL_COEFFICIENT = 0.12  # the real rule uses tiered 12%/15%/18% buckets which simplified to one here
ILM = 1.0                    # the proposal floors this multiplier at 1, so it can't be reduced further

# This one line is the entire difference between the 2023 draft and the
# 2026 reproposal: does the "services leg" get measured gross (fee
# income plus fee expenses, no netting) or net (income minus expenses)?
services_leg_gross = BI_FEE_INCOME + BI_FEE_EXPENSE   # 2023 draft
services_leg_net = BI_FEE_INCOME - BI_FEE_EXPENSE     # 2026 reproposal

bi_2023 = services_leg_gross + BI_INTEREST_INCOME + BI_FINANCIAL
bi_2026 = services_leg_net + BI_INTEREST_INCOME + BI_FINANCIAL

# Operational Risk RWA = 12.5 x BI x marginal coefficient x loss multiplier
op_rwa_2023 = 12.5 * bi_2023 * MARGINAL_COEFFICIENT * ILM
op_rwa_2026 = 12.5 * bi_2026 * MARGINAL_COEFFICIENT * ILM

# New charge #2: CVA, a brand new charge on derivatives specifically
CVA_PCT = 0.20  # illustrative, not an official regulatory formula
cva_base = base_by_cat["Derivatives"] * CVA_PCT
cva_stress = stress_by_cat["Derivatives"] * CVA_PCT

print("\n=== Basel III Endgame - Business Indicator & Operational Risk ===")
print("BI 2023 draft (gross services leg):", round(bi_2023, 1))
print("BI 2026 re-proposal (net services leg):", round(bi_2026, 1))
print("Op Risk RWA 2023 draft:", round(op_rwa_2023, 1))
print("Op Risk RWA 2026 re-proposal:", round(op_rwa_2026, 1))
print("CVA RWA baseline:", round(cva_base, 1), "| stressed:", round(cva_stress, 1))

print(
    "\n This Operational Risk RWA and CVA RWA are ADDED on top of the credit-risk RWA calculated earlier. They're "
    "not a replacement or a discount on it. Operational risk measures a completely different kind of danger (internal failures, fraud, "
    "legal costs) that has nothing to do with whether a counterparty repays a loan, so it has to be counted separately and summed. "
    "Notice the gross vs net choice alone swings Operational Risk RWA from $58.5M down to $22.5M. the underlying fee income and "
    "expenses didn't change at all, only how the rule measures them."
)

# --- Put it all together: total RWA and CET1 ratio under each framework ---
rwa_current_base, rwa_current_stress = base_rwa, stress_rwa
rwa_eg23_base = base_rwa + cva_base + op_rwa_2023
rwa_eg23_stress = stress_rwa + cva_stress + op_rwa_2023
rwa_eg26_base = base_rwa + cva_base + op_rwa_2026
rwa_eg26_stress = stress_rwa + cva_stress + op_rwa_2026

print("\n=== Basel III Endgame comparison ===")
print("Scenario, RWA ($M), CET1 Ratio")
print("Current Basel III - Baseline:", round(rwa_current_base, 1), round(cet1_ratio(CET1_CAPITAL, rwa_current_base) * 100, 1), "%")
print("Current Basel III - Stressed:", round(rwa_current_stress, 1), round(cet1_ratio(stress_capital, rwa_current_stress) * 100, 1), "%")
print("Endgame 2023 draft - Baseline:", round(rwa_eg23_base, 1), round(cet1_ratio(CET1_CAPITAL, rwa_eg23_base) * 100, 1), "%")
print("Endgame 2023 draft - Stressed:", round(rwa_eg23_stress, 1), round(cet1_ratio(stress_capital, rwa_eg23_stress) * 100, 1), "%")
print("Endgame 2026 re-proposal - Baseline:", round(rwa_eg26_base, 1), round(cet1_ratio(CET1_CAPITAL, rwa_eg26_base) * 100, 1), "%")
print("Endgame 2026 re-proposal - Stressed:", round(rwa_eg26_stress, 1), round(cet1_ratio(stress_capital, rwa_eg26_stress) * 100, 1), "%")
print("\nRegulatory minimum (Basel III): 4.5% - same floor applies under all frameworks")

print(
    "\n Both Endgame versions leave this mock bank "
    "worse off than under current Basel III, that's expected, since "
    "Endgame adds charges rather than removing them. What the "
    "comparison actually shows is how much WORSE. Under the harsher "
    "2023 draft, the stressed ratio falls to 4.7% which is just 0.2 points "
    "above the regulatory floor. Under the 2026 reproposal, the same "
    "stress scenario lands at 5.1%, a meaningfully larger buffer, "
    "purely from the gross to net change in how fee income is measured. "
    "Nothing about the underlying portfolio changed between those two "
    "rows, only an accounting choice did, and it moved the ratio by "
    "0.4 points. That's the whole story of why a fee heavy institution "
    "like State Street cares so specifically about this one detail of "
    "the rule, rather than Basel III Endgame in general."
)