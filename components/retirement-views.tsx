'use client';

import { useMemo, useState, type Dispatch, type SetStateAction } from 'react';
import { ArrowUpRight, Activity, BookOpen, Info } from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Switch } from '@/components/ui/switch';
import {
  Table,
  TableHeader,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
} from '@/components/ui/table';
import { NumberField, money } from '@/components/plan-fields';
import {
  project,
  type Plan,
  type Stress,
  type YearResult,
} from '@/lib/retirement';

const shortMoney = (n: number) =>
  Math.abs(n) >= 1000000
    ? `$${(n / 1000000).toFixed(1)}m`
    : `$${Math.round(n / 1000)}k`;
const when = (month: number | null, years: number) =>
  month === null
    ? `None in ${years} years`
    : `Year ${Math.ceil(month / 12)}, month ${((month - 1) % 12) + 1}`;

function Chart({
  data,
  mode = 'income',
}: {
  data: Record<string, number>[];
  mode?: 'income' | 'capital';
}) {
  const income = mode === 'income';
  return (
    <div
      className="projection-chart"
      role="img"
      aria-label={
        income
          ? 'Monthly income and spending by retirement year. Exact values are in the yearly ledger below.'
          : 'Base case and stress case portfolio value by retirement year. Exact values are in the stress ledger below.'
      }
    >
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={data}
          margin={{ top: 15, right: 12, left: 5, bottom: 5 }}
          accessibilityLayer
        >
          <defs>
            <linearGradient
              id={income ? 'incomeFill' : 'capitalFill'}
              x1="0"
              y1="0"
              x2="0"
              y2="1"
            >
              <stop offset="0%" stopColor="#128b85" stopOpacity={0.13} />
              <stop offset="100%" stopColor="#128b85" stopOpacity={0.01} />
            </linearGradient>
          </defs>
          <CartesianGrid
            stroke="#e6edf2"
            vertical={false}
            strokeDasharray="3 4"
          />
          <XAxis
            dataKey="year"
            tickLine={false}
            axisLine={false}
            minTickGap={35}
            tick={{ fill: '#6b7c8d', fontSize: 12 }}
            tickFormatter={(n) => `Yr ${n}`}
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            tick={{ fill: '#6b7c8d', fontSize: 12 }}
            tickFormatter={shortMoney}
            width={65}
            domain={[0, 'auto']}
          />
          <Tooltip
            formatter={(v, name) => [money(Number(v)), name]}
            labelFormatter={(v) => `Retirement year ${v}`}
            contentStyle={{
              border: '1px solid #dce5ed',
              borderRadius: 9,
              fontSize: 14,
            }}
          />
          <Area
            type="linear"
            dataKey={income ? 'income' : 'base'}
            name={income ? 'Cash available / month' : 'Base case'}
            stroke="#087e83"
            strokeWidth={2.5}
            fill={`url(#${income ? 'incomeFill' : 'capitalFill'})`}
            isAnimationActive={false}
          />
          <Line
            type="linear"
            dataKey={income ? 'spending' : 'stress'}
            name={income ? 'Spending / month' : 'Stress case'}
            stroke={income ? '#b48b42' : '#c46548'}
            strokeWidth={2.5}
            strokeDasharray={income ? '5 5' : undefined}
            dot={false}
            isAnimationActive={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

function Ledger({ rows }: { rows: YearResult[] }) {
  return (
    <details className="ledger">
      <summary>Open the yearly cash-flow ledger</summary>
      <Table className="holdings-table ledger-table">
        <TableHeader>
          <TableRow>
            <TableHead>Year</TableHead>
            <TableHead>Net payouts¹</TableHead>
            <TableHead>Other income</TableHead>
            <TableHead>Spending</TableHead>
            <TableHead>Shares sold²</TableHead>
            <TableHead>Unfunded</TableHead>
            <TableHead>End portfolio</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.slice(1).map((r) => (
            <TableRow key={r.year}>
              <TableCell>{r.year}</TableCell>
              <TableCell>{money(r.netDistributions)}</TableCell>
              <TableCell>{money(r.otherIncome)}</TableCell>
              <TableCell>{money(r.spending)}</TableCell>
              <TableCell>{money(r.sales)}</TableCell>
              <TableCell className={r.unfunded > 0 ? 'loss' : ''}>
                {money(r.unfunded)}
              </TableCell>
              <TableCell>{money(r.portfolio)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <p className="small muted">
        Nominal dollars. ¹ Dividends and cash interest after the tax haircut. ²
        Sale proceeds fund spending; they are not investment income.
      </p>
    </details>
  );
}

export function RetirementProjection({ plan }: { plan: Plan }) {
  const base = useMemo(() => project(plan), [plan]);
  return (
    <section className="surface projection-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">THE LONG VIEW</p>
          <h2>Will the income keep up?</h2>
        </div>
        <span className="horizon-tag">{plan.years} years</span>
      </div>
      <div className="chart-legend">
        <span>
          <i className="dot strc" />
          Cash available
        </span>
        <span>
          <i className="dot sata" />
          Spending with inflation
        </span>
      </div>
      <Chart
        data={base.rows.slice(1).map((r) => ({
          year: r.year,
          income: r.monthlyIncome,
          spending: r.monthlySpending,
        }))}
      />
      <div className="projection-stats">
        <div>
          <span>First shares sold</span>
          <b>{when(base.firstSaleMonth, plan.years)}</b>
        </div>
        <div>
          <span>First unfunded spending</span>
          <b className={base.firstUnfundedMonth ? 'loss' : ''}>
            {when(base.firstUnfundedMonth, plan.years)}
          </b>
        </div>
        <div>
          <span>Ending value in today’s dollars</span>
          <b>{money(base.ending.realPortfolio)}</b>
        </div>
      </div>
      <p className="model-note">
        Base case: rates and share prices stay flat. Spending rises{' '}
        {plan.inflation}% a year; other income stays flat. Surplus goes to cash.
        Shortfalls use cash, then sell preferred shares proportionally—reducing
        future payouts.
      </p>
      <Ledger rows={base.rows} />
    </section>
  );
}

const presets: Record<string, Omit<Stress, 'startYear'>> = {
  'Dividend cut': { dividendCut: 30, priceLoss: 0, pauseMonths: 0 },
  'Payment pause': { dividendCut: 0, priceLoss: 0, pauseMonths: 12 },
  'Price shock': { dividendCut: 0, priceLoss: 30, pauseMonths: 0 },
  Combined: { dividendCut: 30, priceLoss: 30, pauseMonths: 0 },
};

export function StressLab({
  plan,
  stress,
  setStress,
}: {
  plan: Plan;
  stress: Stress;
  setStress: Dispatch<SetStateAction<Stress>>;
}) {
  const [real, setReal] = useState(true);
  const effectiveStress = {
    ...stress,
    startYear: Math.min(stress.startYear, plan.years),
  };
  const base = useMemo(() => project(plan), [plan]);
  const scenario = project(plan, effectiveStress);
  const preset =
    Object.entries(presets).find(
      ([, v]) =>
        v.dividendCut === stress.dividendCut &&
        v.priceLoss === stress.priceLoss &&
        v.pauseMonths === stress.pauseMonths,
    )?.[0] ?? 'Custom';
  const value = real ? 'realPortfolio' : 'portfolio';
  const shockYear = scenario.rows[effectiveStress.startYear];
  return (
    <>
      <section className="surface stress-config">
        <div className="section-heading">
          <div>
            <p className="eyebrow">PRESSURE TEST YOUR PLAN</p>
            <h2>What if the income changes?</h2>
          </div>
          <Activity className="accent-icon" size={24} />
        </div>
        <p className="body-copy">
          Apply a hypothetical shock to both preferred holdings. Cash is not
          subject to the price shock.
        </p>
        <RadioGroup
          aria-label="Stress scenario preset"
          className="preset-options"
          value={preset}
          onValueChange={(v) => {
            const selected = presets[String(v)];
            if (selected) setStress((s) => ({ ...s, ...selected }));
          }}
        >
          {Object.keys(presets).map((name) => (
            <label
              key={name}
              className={preset === name ? 'preset active' : 'preset'}
            >
              <RadioGroupItem value={name} />
              {name}
            </label>
          ))}
        </RadioGroup>
        <div className="stress-inputs">
          <NumberField
            label="Dividend reduction"
            prefix="%"
            value={stress.dividendCut}
            max={100}
            step={5}
            onChange={(n) => setStress((s) => ({ ...s, dividendCut: n }))}
          />
          <NumberField
            label="Permanent price decline"
            prefix="%"
            value={stress.priceLoss}
            max={100}
            step={5}
            onChange={(n) => setStress((s) => ({ ...s, priceLoss: n }))}
          />
          <NumberField
            label="Months without payouts"
            prefix="M"
            value={stress.pauseMonths}
            max={60}
            step={1}
            onChange={(n) =>
              setStress((s) => ({ ...s, pauseMonths: Math.round(n) }))
            }
          />
          <NumberField
            label="Shock starts in year"
            prefix="Y"
            value={effectiveStress.startYear}
            min={1}
            max={plan.years}
            step={1}
            onChange={(n) =>
              setStress((s) => ({ ...s, startYear: Math.round(n) }))
            }
          />
        </div>
        <p className="small muted">
          Cuts and price declines persist from the start of the selected year. A
          pause resumes at the reduced rate, without assumed arrears recovery. A
          100% price loss models permanent loss of both holdings and their
          payouts.
        </p>
      </section>
      <div className="stress-summary">
        <div>
          <span>Cash available in shock year</span>
          <strong>
            {money(shockYear.monthlyIncome)}
            <small> / mo avg.</small>
          </strong>
          <p>Spending: {money(shockYear.monthlySpending)} / mo</p>
        </div>
        <div>
          <span>First unfunded spending</span>
          <strong className={scenario.firstUnfundedMonth ? 'loss' : ''}>
            {when(scenario.firstUnfundedMonth, plan.years)}
          </strong>
          <p>Base case: {when(base.firstUnfundedMonth, plan.years)}</p>
        </div>
      </div>
      <section className="surface">
        <div className="section-heading">
          <div>
            <p className="eyebrow">PRINCIPAL UNDER PRESSURE</p>
            <h2>The same plan. A different path.</h2>
          </div>
          <label className="real-toggle">
            <Switch checked={real} onCheckedChange={setReal} />
            Today’s dollars
          </label>
        </div>
        <div className="chart-legend">
          <span>
            <i className="dot strc" />
            Base case
          </span>
          <span>
            <i className="dot stress-dot" />
            Stress case
          </span>
        </div>
        <Chart
          mode="capital"
          data={base.rows.map((r, i) => ({
            year: r.year,
            base: r[value],
            stress: scenario.rows[i][value],
          }))}
        />
        <div className="projection-stats">
          <div>
            <span>Base case ending portfolio</span>
            <b>{money(base.ending[value])}</b>
          </div>
          <div>
            <span>Stress case ending portfolio</span>
            <b>{money(scenario.ending[value])}</b>
          </div>
          <div>
            <span>First shares sold under stress</span>
            <b>{when(scenario.firstSaleMonth, plan.years)}</b>
          </div>
        </div>
        <p className="model-note">
          {real
            ? 'Chart and ending values are adjusted for inflation.'
            : 'Chart and ending values are nominal.'}{' '}
          Lines join year-end observations; the modeled shock happens
          immediately. These are scenarios, not probabilities, historical
          backtests, or worst-case limits.
        </p>
        <Ledger rows={scenario.rows} />
      </section>
      <div className="insight risk-insight">
        <Info size={22} />
        <div>
          <h3>Two tickers still share a major risk.</h3>
          <p>
            Both issuers depend on bitcoin treasury economics and access to
            capital. Splitting the allocation does not remove that shared
            exposure. A deep or prolonged shock can be worse than the examples
            here.
          </p>
        </div>
      </div>
    </>
  );
}

const source = {
  strc: 'https://www.strategy.com/strc/learn',
  sata: 'https://www.sec.gov/Archives/edgar/data/1920406/000162828026056908/asst-20260813.htm',
  sataRisk:
    'https://www.sec.gov/Archives/edgar/data/1920406/000095010326007179/dp246652_fwp.htm',
  tax: 'https://www.irs.gov/taxtopics/tc404',
};
function SourceLink({
  href,
  children,
}: {
  href: string;
  children: React.ReactNode;
}) {
  return (
    <a className="source-link" href={href} target="_blank" rel="noreferrer">
      {children}
      <ArrowUpRight size={14} />
    </a>
  );
}

export function InstrumentResearch() {
  return (
    <>
      <div className="research-intro">
        <p className="eyebrow">THE BUILDING BLOCKS</p>
        <h2>Digital credit. Real-world cash flow.</h2>
        <p>
          Here, “digital credit” means preferred equity issued by bitcoin
          treasury companies. The attraction is dollar income; the obligation
          sits with the issuer.
        </p>
      </div>
      <div className="instrument-grid">
        <article className="surface instrument-card">
          <div className="instrument-title">
            <i className="dot strc" />
            <h3>STRC</h3>
            <span>STRATEGY</span>
          </div>
          <div className="instrument-rate">
            12.00<span>%</span>
          </div>
          <p>September 2026 annual rate on $100 stated amount</p>
          <dl>
            <div>
              <dt>Payment cadence</dt>
              <dd>Semi-monthly</dd>
            </div>
            <div>
              <dt>Rate</dt>
              <dd>Variable; adjusted monthly</dd>
            </div>
            <div>
              <dt>Maturity</dt>
              <dd>Perpetual</dd>
            </div>
          </dl>
          <p className="instrument-note">
            The issuer targets trading near $100. That is an objective, not a
            price guarantee. There is no direct collateral claim on its bitcoin.
          </p>
          <SourceLink href={source.strc}>Issuer terms & risk notes</SourceLink>
        </article>
        <article className="surface instrument-card">
          <div className="instrument-title">
            <i className="dot sata" />
            <h3>SATA</h3>
            <span>STRIVE</span>
          </div>
          <div className="instrument-rate gold">
            13.00<span>%</span>
          </div>
          <p>September 2026 annual rate on $100 stated amount</p>
          <dl>
            <div>
              <dt>Payment cadence</dt>
              <dd>Each business day</dd>
            </div>
            <div>
              <dt>Rate</dt>
              <dd>Variable</dd>
            </div>
            <div>
              <dt>Maturity</dt>
              <dd>Perpetual</dd>
            </div>
          </dl>
          <p className="instrument-note">
            September’s declared daily payout is $0.0516 per share across 21
            business days. Daily payment does not mean a higher annual rate.
          </p>
          <SourceLink href={source.sata}>September SEC declaration</SourceLink>
        </article>
      </div>
      <section className="surface research-notes">
        <div className="section-heading">
          <div>
            <p className="eyebrow">READ THE WHOLE EQUATION</p>
            <h2>What matters in retirement.</h2>
          </div>
          <BookOpen size={24} className="accent-icon" />
        </div>
        <div className="research-row">
          <span>01</span>
          <div>
            <h3>Income yield is not total return.</h3>
            <p>
              The calculator divides annual cash per share by your purchase
              price. Total return also includes the change in share value. A
              high payout can coexist with a capital loss.
            </p>
          </div>
        </div>
        <div className="research-row">
          <span>02</span>
          <div>
            <h3>Preferred does not mean protected principal.</h3>
            <p>
              These securities are not insured deposits or direct claims on a
              pool of bitcoin. Both have claims on residual company assets, and
              neither promises a maturity-date repayment.
            </p>
            <div className="source-links">
              <SourceLink href={source.strc}>Strategy disclosures</SourceLink>
              <SourceLink href={source.sataRisk}>
                Strive SEC disclosures
              </SourceLink>
            </div>
          </div>
        </div>
        <div className="research-row">
          <span>03</span>
          <div>
            <h3>Return of capital is not permanently tax-free income.</h3>
            <p>
              For a U.S. taxable account, a nondividend distribution generally
              reduces cost basis. Further distributions after basis reaches zero
              can be capital gains. This model uses your chosen cash-flow tax
              haircut and does not calculate basis, sale taxes, RMDs, or
              account-specific tax rules.
            </p>
            <SourceLink href={source.tax}>
              IRS treatment of distributions
            </SourceLink>
          </div>
        </div>
        <div className="research-row">
          <span>04</span>
          <div>
            <h3>Today’s payout has to fund tomorrow’s prices.</h3>
            <p>
              The base case holds rates flat to make the assumptions visible.
              Inflation raises spending, while selling shares to bridge a gap
              reduces future dividends. Neither the base case nor the shock
              cases estimate a probability of retirement success.
            </p>
          </div>
        </div>
      </section>
      <details className="surface methodology">
        <summary>How the calculator works</summary>
        <div>
          <p>
            Retirement starts now. Capital is allocated once; unallocated money
            becomes cash. Fractional shares are allowed for modeling. STRC and
            SATA dividends are calculated as shares × $100 × annual rate ÷ 12;
            actual payment-date rounding and daily timing are not simulated.
          </p>
          <p>
            Each month, cash earns the entered annual interest rate ÷ 12.
            Dividends and interest receive the tax haircut, other after-tax
            income is added, and spending is paid. Surplus stays in cash. Cash
            runs down before preferred shares are sold proportionally at modeled
            prices. Unfunded spending is recorded when those resources are
            insufficient.
          </p>
          <p>
            Spending steps up with inflation each year; other income stays
            constant. Preferred prices stay at purchase price in the base case.
            There is no assumed bitcoin price growth, share-price appreciation,
            reinvestment into preferreds, rebalancing, or automatic redemption.
            Price shocks persist. Missed dividends and any contractual accrual
            or penalty are excluded from available cash, with no assumed
            catch-up payment.
          </p>
          <p>
            Rate snapshots were checked September 9, 2026. Purchase prices
            default to an illustrative $100 and must be updated by the user.
            Results are hypothetical and omit fees, spreads, and taxes on asset
            sales. Reloading resets the example; inputs are not saved or sent to
            a financial service.
          </p>
        </div>
      </details>
    </>
  );
}
