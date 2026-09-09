# FireCalc — Digital Credit Retirement

An income-first rebuild of RobCase29/FireCalc focused on STRC, SATA, and a cash reserve. It models retirement starting now: monthly spending, other after-tax income, inflation, distributions, cash reserves, and preferred-share sales. It is an independent scenario calculator, not an issuer promotion or a recommendation to buy these securities.

## Development

Use Node 22.13+ (Node 22 LTS recommended), then `npm ci` and `npm run dev`. Run `npm test`, `npm run typecheck`, and `npm run build` before delivery. No financial API keys are needed. Personal inputs remain in page state and reset on reload.

## Product scope

- Allocations totaling at most 100%, with the remainder in cash.
- Editable prices and dividend rates; price and rate are deliberately separate.
- Monthly income, spending coverage, and capital required to cover the initial spending gap.
- A 1–50 year monthly ledger with inflation and sale-driven dividend reduction.
- Dividend cuts, payment pauses, price declines, and combined stress cases.
- Nominal and inflation-adjusted principal, with no invented probability of success.
- Sources and model limitations in the interface.

## Dated data

Checked September 9, 2026. **No live quote feed.** Purchase-price defaults of $100 are illustrative. Annual rate defaults are 12% for STRC and 13% for SATA, on a $100 stated amount. Actual yields vary with purchase price. The default cash interest rate is an assumption, not a market quote.

- [Strategy STRC terms](https://www.strategy.com/strc/learn): September 2026 rate, semi-monthly cadence, perpetual structure, and risk notes.
- [Strive August 13 SEC filing](https://www.sec.gov/Archives/edgar/data/1920406/000162828026056908/asst-20260813.htm): September 2026 SATA rate and daily declaration. The declared $0.0516 × 21 business days differs slightly from annual-rate/12 due to rounding; the planner uses the annual-rate calculation.
- [Strive risk disclosure](https://www.sec.gov/Archives/edgar/data/1920406/000095010326007179/dp246652_fwp.htm): residual-asset claim, not collateralized bitcoin.
- [IRS distributions guidance](https://www.irs.gov/taxtopics/tc404): nondividend distributions and cost-basis reduction.

## Calculation contract

At entry, allocated capital / purchase price sets fractional modeled shares. Monthly preferred dividends = shares × $100 × annual rate / 12. Monthly cash interest = opening cash × annual cash rate / 12. Apply the selected tax haircut to dividends and interest only, add other after-tax income, then pay spending. Surplus accumulates in cash; a deficit uses cash then proportional sales of preferred holdings at modeled prices. Those sales reduce subsequent dividends. A remaining gap is unfunded spending, not a negative portfolio.

Year-one spending uses today's input; spending then grows annually with inflation. Other income stays nominally flat. Real year-end portfolio = nominal portfolio / (1 + inflation)^year. Prices stay flat in the base case. Stress begins at the start of the selected year, changes both preferred holdings, and leaves cash intact. Price declines and rate cuts persist. A pause resumes at the cut rate without assumed arrears collection. A 100% price decline models total permanent loss of preferred holdings and all their future payouts.

The model excludes appreciation, calls/redemptions, fees, spreads, taxes on sales, basis tracking, RMDs, account-specific tax rules, intra-month payout timing, and contractual arrears/penalty mechanics. It does not estimate default probabilities, correlate a bitcoin price path, run historical backtests, or extrapolate the current rates as a forecast. Scenarios can understate actual loss.

## Verification

Unit tests cover yield on stated amount, taxes, zero assets, exhaustion timing, inflation, proportional sales, dividend cuts, pauses, price shocks, total loss, required capital, bounds, and wealth conservation. TypeScript and production build are separate checks. Browser UI QA has not been requested. An optional imperative WebMCP surface reads/configures the same visible plan where supported; no supported live WebMCP validation context was available, so its browser integration is not claimed verified.

## Repository transition

This replaces the old Python/Streamlit app, overlapping calculator implementations, and checked-in virtual environment. Those files remain recoverable in Git history. The new runtime does not depend on GitPython. Review and merge the rebuild branch to update the default branch; deploying this preview alone does not resolve alerts on the old default branch. Any old Streamlit deployment should be retired or redirected separately when switching over.

## Dependency maintenance

The patched toolchain uses a narrow `sharp` 0.35.4 override because the current worker tooling still pins an affected patch release. Remove the override when upstream resolves to a patched version. The full dependency audit returned zero known vulnerabilities at delivery. Weekly grouped dependency PRs and CI checks are configured.
