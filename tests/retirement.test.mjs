import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  DEFAULT_PLAN,
  BASE_STRESS,
  DEFAULT_STRESS,
  summarize,
  project,
  capitalForIncome,
  validatePlan,
} from '../lib/retirement.ts';
const near = (a, b) => assert.ok(Math.abs(a - b) < 0.001, `${a} != ${b}`);
const plan = (v) => ({ ...DEFAULT_PLAN, ...v });
test('rate on stated amount is different from yield at purchase price', () => {
  const r = summarize(
    plan({
      capital: 80000,
      strcWeight: 100,
      sataWeight: 0,
      strcPrice: 80,
      strcRate: 12,
      taxRate: 0,
      otherIncome: 0,
    }),
  );
  near(r.yield, 15);
  near(r.gross, 1000);
  near(r.available, 1000);
});
test('tax haircut and outside income are applied exactly once', () => {
  near(summarize(DEFAULT_PLAN).available, 6700);
});
test('zero portfolio remains valid, including an unfunded first month', () => {
  const r = project(plan({ capital: 0, otherIncome: 0, spending: 1000 }));
  assert.equal(r.firstUnfundedMonth, 1);
  near(r.ending.portfolio, 0);
});
test('zero spending and zero capital can be fully funded by zero income', () => {
  const p = plan({ capital: 0, spending: 0, otherIncome: 0 });
  assert.equal(project(p).firstUnfundedMonth, null);
  near(capitalForIncome(p), 0);
});
test('exact exhaustion in final month is not an unfunded payment', () => {
  const p = plan({
    capital: 12000,
    spending: 1000,
    otherIncome: 0,
    years: 1,
    cashRate: 0,
    strcWeight: 0,
    sataWeight: 0,
    inflation: 0,
  });
  const r = project(p);
  near(r.ending.portfolio, 0);
  assert.equal(r.firstUnfundedMonth, null);
  assert.equal(project({ ...p, years: 2 }).firstUnfundedMonth, 13);
});
test('inflation starts with year two spending and respects actual horizon', () => {
  const r = project(plan({ spending: 1000, inflation: 10, years: 2 }));
  assert.equal(r.rows.length, 3);
  near(r.rows[1].spending, 12000);
  near(r.rows[2].spending, 13200);
  near(r.ending.realPortfolio, r.ending.portfolio / 1.21);
});
test('cash deficits sell preferred holdings and reduce future distributions', () => {
  const r = project(
    plan({
      capital: 12000,
      strcWeight: 100,
      sataWeight: 0,
      strcRate: 0,
      otherIncome: 0,
      cashRate: 0,
      inflation: 0,
      spending: 1000,
      years: 2,
    }),
  );
  assert.equal(r.firstSaleMonth, 1);
  assert.equal(r.firstUnfundedMonth, 13);
  near(r.rows[1].sales, 12000);
});
test('price decline does not directly reduce dividends per surviving share', () => {
  const p = plan({
    capital: 100000,
    strcWeight: 100,
    sataWeight: 0,
    spending: 0,
    otherIncome: 0,
    cashRate: 0,
    taxRate: 0,
    years: 1,
  });
  const base = project(p),
    shock = project(p, { ...BASE_STRESS, startYear: 1, priceLoss: 30 });
  near(base.ending.netDistributions, shock.ending.netDistributions);
  near(base.ending.portfolio - shock.ending.portfolio, 30000);
});
test('dividend cut changes cash payouts but not the price of remaining shares', () => {
  const p = plan({
    capital: 100000,
    strcWeight: 100,
    sataWeight: 0,
    spending: 0,
    otherIncome: 0,
    cashRate: 0,
    taxRate: 0,
    years: 1,
  });
  const r = project(p, { ...BASE_STRESS, startYear: 1, dividendCut: 50 });
  near(r.ending.netDistributions, 6000);
  near(r.ending.portfolio, 106000);
});
test('payment pause resumes without inventing catch-up payments', () => {
  const p = plan({
    capital: 100000,
    strcWeight: 100,
    sataWeight: 0,
    spending: 0,
    otherIncome: 0,
    cashRate: 0,
    taxRate: 0,
    years: 2,
  });
  const r = project(p, { ...BASE_STRESS, startYear: 1, pauseMonths: 12 });
  near(r.rows[1].netDistributions, 0);
  near(r.rows[2].netDistributions, 12000);
});
test('a complete loss eliminates affected shares and dividends', () => {
  const r = project(
    plan({ capital: 100000, strcWeight: 100, sataWeight: 0, otherIncome: 0 }),
    { ...BASE_STRESS, startYear: 1, priceLoss: 100 },
  );
  near(r.ending.portfolio, 0);
  near(r.rows[1].netDistributions, 0);
  assert.equal(r.firstUnfundedMonth, 1);
});
test('initial income capital target handles zero yield and 100% tax haircut', () => {
  assert.equal(capitalForIncome(plan({ taxRate: 100 })), null);
  near(capitalForIncome(DEFAULT_PLAN), (3000 * 12) / 0.0564);
});
test('monthly ledger conserves wealth and never double counts sale proceeds', () => {
  const p = plan({ spending: 20000, years: 10 });
  const r = project(p);
  const net = r.rows.reduce(
    (n, row) =>
      n + row.netDistributions + row.otherIncome - row.spending + row.unfunded,
    0,
  );
  near(r.ending.portfolio, p.capital + net);
  assert.ok(
    r.rows.every(
      (row) => row.portfolio >= 0 && row.cash >= 0 && row.unfunded >= 0,
    ),
  );
});
test('combined stress cannot improve the default portfolio outcome', () => {
  assert.ok(
    project(DEFAULT_PLAN, DEFAULT_STRESS).ending.portfolio <
      project(DEFAULT_PLAN).ending.portfolio,
  );
});
test('invalid plans and stress settings fail intentionally', () => {
  for (const invalid of [
    { strcWeight: 101 },
    { sataPrice: 0 },
    { capital: NaN },
    { years: 1.5 },
    { years: 51 },
    { taxRate: 101 },
    { strcRate: 31 },
  ])
    assert.throws(() => validatePlan(plan(invalid)));
  assert.throws(() =>
    project(DEFAULT_PLAN, { ...DEFAULT_STRESS, pauseMonths: -1 }),
  );
});
