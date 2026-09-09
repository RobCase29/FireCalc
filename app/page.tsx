'use client';

import { useState } from 'react';
import { usePlanTools } from '@/hooks/use-plan-tools';
import {
  Flame,
  ArrowUpRight,
  RotateCcw,
  SlidersHorizontal,
  CircleDollarSign,
  ShieldCheck,
  Info,
} from 'lucide-react';
import { Slider } from '@/components/ui/slider';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import {
  Table,
  TableHeader,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
} from '@/components/ui/table';
import {
  DEFAULT_PLAN,
  DEFAULT_STRESS,
  type Stress,
  summarize,
  capitalForIncome,
  type Plan,
} from '@/lib/retirement';
import { NumberField, money } from '@/components/plan-fields';
import {
  RetirementProjection,
  StressLab,
  InstrumentResearch,
} from '@/components/retirement-views';

export default function Home() {
  const [plan, setPlan] = useState<Plan>(DEFAULT_PLAN);
  const [stress, setStress] = useState<Stress>(DEFAULT_STRESS);
  usePlanTools(plan, setPlan);
  const update = (key: keyof Plan, value: number) =>
    setPlan((p) => ({ ...p, [key]: value }));
  const result = summarize(plan);
  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="FireCalc home">
          <span className="brand-mark">
            <Flame size={21} />
          </span>
          FireCalc
          <span className="brand-divider" />{' '}
          <span className="brand-caption">DIGITAL CREDIT</span>
        </a>
        <span className="snapshot">
          <span />
          Terms checked September 9, 2026
        </span>
      </header>
      <div className="workspace">
        <aside className="plan-panel">
          <div className="panel-heading">
            <SlidersHorizontal size={18} />
            <h2>Your retirement plan</h2>
            <button
              className="icon-button"
              onClick={() => {
                setPlan(DEFAULT_PLAN);
                setStress(DEFAULT_STRESS);
              }}
              aria-label="Reset to example plan"
              title="Reset example"
            >
              <RotateCcw size={16} />
            </button>
          </div>
          <p className="muted small">Start with an example. Make it yours.</p>
          <div className="fields">
            <NumberField
              label="Investable portfolio"
              value={plan.capital}
              onChange={(n) => update('capital', n)}
              step={10000}
            />
            <NumberField
              label="Monthly spending"
              value={plan.spending}
              onChange={(n) => update('spending', n)}
            />
            <NumberField
              label="Other monthly income, after tax"
              value={plan.otherIncome}
              onChange={(n) => update('otherIncome', n)}
            />
          </div>
          <div className="section-label">
            PORTFOLIO MIX <span>100%</span>
          </div>
          <div className="allocation-control">
            <div>
              <span>
                <i className="dot strc" />
                STRC <small>Strategy</small>
              </span>
              <b>{plan.strcWeight}%</b>
            </div>
            <Slider
              aria-label="STRC allocation percent"
              value={[plan.strcWeight]}
              min={0}
              max={100}
              step={1}
              onValueChange={(v) =>
                setPlan((p) => ({
                  ...p,
                  strcWeight: Number(Array.isArray(v) ? v[0] : v),
                  sataWeight: Math.min(
                    p.sataWeight,
                    100 - Number(Array.isArray(v) ? v[0] : v),
                  ),
                }))
              }
            />
          </div>
          <div className="allocation-control sata-control">
            <div>
              <span>
                <i className="dot sata" />
                SATA <small>Strive</small>
              </span>
              <b>{plan.sataWeight}%</b>
            </div>
            <Slider
              aria-label="SATA allocation percent"
              value={[plan.sataWeight]}
              min={0}
              max={100}
              step={1}
              onValueChange={(v) =>
                setPlan((p) => ({
                  ...p,
                  sataWeight: Number(Array.isArray(v) ? v[0] : v),
                  strcWeight: Math.min(
                    p.strcWeight,
                    100 - Number(Array.isArray(v) ? v[0] : v),
                  ),
                }))
              }
            />
          </div>
          <div className="cash-row">
            <span>
              <i className="dot cash" />
              Cash reserve
            </span>
            <b>{100 - plan.strcWeight - plan.sataWeight}%</b>
          </div>
          <p className="small muted">
            Illustrative mix, not an allocation recommendation. Increasing one
            holding may reduce the other.
          </p>
          <details className="assumptions">
            <summary>Planning assumptions</summary>
            <div className="fields">
              <NumberField
                label="Years in retirement"
                value={plan.years}
                onChange={(n) => update('years', Math.round(n))}
                prefix="Y"
                min={1}
                max={50}
                step={1}
              />
              <NumberField
                label="Annual inflation"
                value={plan.inflation}
                onChange={(n) => update('inflation', n)}
                prefix="%"
                max={20}
                step={0.5}
              />
              <NumberField
                label="Cash interest assumption"
                value={plan.cashRate}
                onChange={(n) => update('cashRate', n)}
                prefix="%"
                max={20}
                step={0.25}
              />
              <NumberField
                label="Cash-flow tax haircut"
                value={plan.taxRate}
                onChange={(n) => update('taxRate', n)}
                prefix="%"
                max={100}
                step={1}
              />
              <p className="small muted">
                A simplified reduction in dividends and interest. Actual tax
                treatment and return of capital depend on your account and tax
                basis.
              </p>
            </div>
          </details>
          <details className="assumptions">
            <summary>Prices & dividend rates</summary>
            <div className="fields">
              <NumberField
                label="STRC purchase price / share"
                value={plan.strcPrice}
                onChange={(n) => update('strcPrice', n)}
                min={1}
                max={1000}
                step={0.25}
              />
              <NumberField
                label="STRC annual rate on $100"
                value={plan.strcRate}
                onChange={(n) => update('strcRate', n)}
                prefix="%"
                max={30}
                step={0.25}
              />
              <NumberField
                label="SATA purchase price / share"
                value={plan.sataPrice}
                onChange={(n) => update('sataPrice', n)}
                min={1}
                max={1000}
                step={0.25}
              />
              <NumberField
                label="SATA annual rate on $100"
                value={plan.sataRate}
                onChange={(n) => update('sataRate', n)}
                prefix="%"
                max={30}
                step={0.25}
              />
              <p className="small muted">
                Prices default to $100 for illustration. Update them to your own
                purchase assumptions. September issuer rates: STRC 12%; SATA
                13%.
              </p>
            </div>
          </details>
          <div className="private-note">
            <ShieldCheck size={17} />
            <span>
              Your figures stay in this page.
              <br />
              No account or brokerage connection.
            </span>
          </div>
        </aside>
        <main className="results-panel">
          <div className="page-heading">
            <div>
              <p className="eyebrow">RETIREMENT, RECONSIDERED</p>
              <h1>Let your capital pay you.</h1>
              <p>Explore the income. Understand what it takes to last.</p>
            </div>
            <span className="example-tag">ILLUSTRATIVE PLAN</span>
          </div>
          <Tabs defaultValue="income" className="main-tabs">
            <TabsList variant="line" className="tab-list">
              <TabsTrigger value="income">
                <CircleDollarSign size={16} />
                Income plan
              </TabsTrigger>
              <TabsTrigger value="stress">Stress test</TabsTrigger>
              <TabsTrigger value="research">The instruments</TabsTrigger>
            </TabsList>
            <TabsContent value="income">
              <div className="income-hero">
                <div>
                  <p>MONTHLY CASH AVAILABLE</p>
                  <div className="hero-value">
                    {money(result.available)}
                    <span>/ mo</span>
                  </div>
                  <span>After the tax haircut, including other income</span>
                </div>
                <div className="coverage">
                  <span className="coverage-number">
                    {plan.spending === 0
                      ? '—'
                      : Math.round((result.available / plan.spending) * 100) +
                        '%'}
                  </span>
                  <span>of your spending covered</span>
                  <div className="coverage-track">
                    <span
                      style={{
                        width: `${plan.spending ? Math.min(100, (result.available / plan.spending) * 100) : 100}%`,
                      }}
                    />
                  </div>
                  <b>
                    {money(Math.abs(result.available - plan.spending))}{' '}
                    {result.available >= plan.spending
                      ? 'monthly surplus'
                      : 'monthly gap'}
                  </b>
                </div>
              </div>
              <div className="stat-grid">
                <div>
                  <span>Portfolio cash yield</span>
                  <strong>
                    {result.yield.toFixed(2)}
                    <small>%</small>
                  </strong>
                  <p>Before tax · not total return</p>
                </div>
                <div>
                  <span>Digital credit exposure</span>
                  <strong>{money(result.creditCapital)}</strong>
                  <p>
                    {plan.strcWeight + plan.sataWeight}% across two related risk
                    profiles
                  </p>
                </div>
                <div>
                  <span>Starting cash reserve</span>
                  <strong>{money(result.cash)}</strong>
                  <p>
                    {plan.spending
                      ? (result.cash / plan.spending).toFixed(1) +
                        ' months of full spending'
                      : 'No spending entered'}
                  </p>
                </div>
              </div>
              <section className="surface">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">YOUR INCOME ENGINE</p>
                    <h2>Every dollar has a job.</h2>
                  </div>
                  <span className="small muted">Monthly averages</span>
                </div>
                <div className="mix-bar" aria-label="Portfolio allocation">
                  <span style={{ width: `${plan.strcWeight}%` }} />
                  <span style={{ width: `${plan.sataWeight}%` }} />
                  <span
                    style={{
                      width: `${100 - plan.strcWeight - plan.sataWeight}%`,
                    }}
                  />
                </div>
                <Table className="holdings-table">
                  <TableHeader>
                    <TableRow>
                      <TableHead>Holding</TableHead>
                      <TableHead>Capital</TableHead>
                      <TableHead>Cash yield</TableHead>
                      <TableHead>Gross / month</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {result.holdings.map((h) => (
                      <TableRow key={h.ticker}>
                        <TableCell>
                          <div className="holding-name">
                            <i className={`dot ${h.ticker.toLowerCase()}`} />
                            <b>{h.ticker}</b>
                            <span>{h.name}</span>
                          </div>
                        </TableCell>
                        <TableCell>{money(h.capital)}</TableCell>
                        <TableCell>{h.yield.toFixed(2)}%</TableCell>
                        <TableCell>{money(h.monthly)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                <p className="small muted footnote">
                  <Info size={14} />
                  Purchase assumptions: STRC ${plan.strcPrice.toFixed(2)} · SATA
                  ${plan.sataPrice.toFixed(2)}. Edit prices and rates in the
                  plan. Defaults are illustrative prices and September rate
                  snapshots, not live quotes.
                </p>
              </section>
              <div className="insight">
                <div className="insight-icon">
                  <ArrowUpRight size={23} />
                </div>
                <div>
                  <h3>A higher payout changes the income equation.</h3>
                  <p>
                    It can reduce the capital needed to fund a spending gap. But
                    a payout is only useful while it is paid—and principal can
                    fall even as dividends arrive.
                  </p>
                </div>
              </div>
              <section className="capital-target">
                <div>
                  <p className="eyebrow">THE INCOME TARGET</p>
                  <h2>
                    {capitalForIncome(plan) === null
                      ? 'No income at these settings'
                      : money(capitalForIncome(plan)!)}
                    <span> capital to cover today’s gap</span>
                  </h2>
                  <p>
                    At this mix, price, and tax haircut. Assumes payouts hold;
                    excludes future inflation and principal losses.
                  </p>
                </div>
              </section>
              <RetirementProjection plan={plan} />
            </TabsContent>
            <TabsContent value="stress">
              <StressLab plan={plan} stress={stress} setStress={setStress} />
            </TabsContent>
            <TabsContent value="research">
              <InstrumentResearch />
            </TabsContent>
          </Tabs>
          <footer className="footer">
            FireCalc is an independent planning tool, unaffiliated with Strategy
            or Strive. Scenarios are illustrations, not forecasts or investment
            advice.
          </footer>
        </main>
      </div>
    </div>
  );
}
