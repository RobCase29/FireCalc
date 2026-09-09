export interface Plan {
  capital: number;
  spending: number;
  otherIncome: number;
  years: number;
  inflation: number;
  cashRate: number;
  taxRate: number;
  strcWeight: number;
  sataWeight: number;
  strcPrice: number;
  sataPrice: number;
  strcRate: number;
  sataRate: number;
}
export const DEFAULT_PLAN: Plan = {
  capital: 1000000,
  spending: 5000,
  otherIncome: 2000,
  years: 30,
  inflation: 2.5,
  cashRate: 3.5,
  taxRate: 20,
  strcWeight: 25,
  sataWeight: 15,
  strcPrice: 100,
  sataPrice: 100,
  strcRate: 12,
  sataRate: 13,
};
export function validatePlan(p: Plan): void {
  for (const key of Object.keys(DEFAULT_PLAN) as (keyof Plan)[])
    if (!Number.isFinite(p[key]) || p[key] < 0)
      throw new Error(`Invalid ${key}`);
  if (
    p.strcWeight + p.sataWeight > 100 ||
    p.strcPrice < 1 ||
    p.sataPrice < 1 ||
    p.strcPrice > 1000 ||
    p.sataPrice > 1000 ||
    p.years < 1 ||
    p.years > 50 ||
    !Number.isInteger(p.years) ||
    p.taxRate > 100 ||
    p.inflation > 20 ||
    p.cashRate > 20 ||
    p.strcRate > 30 ||
    p.sataRate > 30 ||
    p.capital > 100000000 ||
    p.spending > 100000000 ||
    p.otherIncome > 100000000
  )
    throw new Error('Invalid plan bounds');
}
export function summarize(p: Plan) {
  validatePlan(p);
  const holdings = [
    {
      ticker: 'STRC',
      name: 'Strategy · semi-monthly',
      capital: (p.capital * p.strcWeight) / 100,
      yield: (p.strcRate * 100) / p.strcPrice,
    },
    {
      ticker: 'SATA',
      name: 'Strive · business daily',
      capital: (p.capital * p.sataWeight) / 100,
      yield: (p.sataRate * 100) / p.sataPrice,
    },
    {
      ticker: 'CASH',
      name: 'Reserve · assumed interest',
      capital: (p.capital * (100 - p.strcWeight - p.sataWeight)) / 100,
      yield: p.cashRate,
    },
  ].map((h) => ({ ...h, monthly: (h.capital * h.yield) / 1200 }));
  const gross = holdings.reduce((sum, h) => sum + h.monthly, 0);
  return {
    holdings,
    gross,
    available: gross * (1 - p.taxRate / 100) + p.otherIncome,
    yield: p.capital ? (gross * 1200) / p.capital : 0,
    cash: holdings[2].capital,
    creditCapital: holdings[0].capital + holdings[1].capital,
  };
}

export interface Stress {
  startYear: number;
  dividendCut: number;
  priceLoss: number;
  pauseMonths: number;
}
export const BASE_STRESS: Stress = {
  startYear: 3,
  dividendCut: 0,
  priceLoss: 0,
  pauseMonths: 0,
};
export const DEFAULT_STRESS: Stress = {
  startYear: 3,
  dividendCut: 30,
  priceLoss: 30,
  pauseMonths: 0,
};
export interface YearResult {
  year: number;
  portfolio: number;
  realPortfolio: number;
  cash: number;
  netDistributions: number;
  otherIncome: number;
  spending: number;
  sales: number;
  unfunded: number;
  monthlyIncome: number;
  monthlySpending: number;
}
export function validateStress(s: Stress): void {
  if (
    ![s.startYear, s.dividendCut, s.priceLoss, s.pauseMonths].every(
      Number.isFinite,
    ) ||
    !Number.isInteger(s.startYear) ||
    s.startYear < 1 ||
    s.startYear > 50 ||
    s.dividendCut < 0 ||
    s.dividendCut > 100 ||
    s.priceLoss < 0 ||
    s.priceLoss > 100 ||
    !Number.isInteger(s.pauseMonths) ||
    s.pauseMonths < 0 ||
    s.pauseMonths > 60
  )
    throw new Error('Invalid stress bounds');
}

/** Monthly cash-flow ledger. Distributions go to cash; deficits consume cash then sell both preferred holdings pro rata. */
export function project(p: Plan, stress: Stress = BASE_STRESS) {
  validatePlan(p);
  validateStress(stress);
  const start = summarize(p);
  let cash = start.cash;
  let strcShares = start.holdings[0].capital / p.strcPrice;
  let sataShares = start.holdings[1].capital / p.sataPrice;
  let firstUnfundedMonth: number | null = null;
  let firstSaleMonth: number | null = null;
  let totalUnfunded = 0;
  const rows: YearResult[] = [
    {
      year: 0,
      portfolio: p.capital,
      realPortfolio: p.capital,
      cash,
      netDistributions: 0,
      otherIncome: 0,
      spending: 0,
      sales: 0,
      unfunded: 0,
      monthlyIncome: start.available,
      monthlySpending: p.spending,
    },
  ];
  for (let year = 1; year <= p.years; year++) {
    let netDistributions = 0,
      sales = 0,
      unfunded = 0;
    const monthlySpending = p.spending * (1 + p.inflation / 100) ** (year - 1);
    let portfolio = cash + strcShares * p.strcPrice + sataShares * p.sataPrice;
    for (let monthOfYear = 0; monthOfYear < 12; monthOfYear++) {
      const month = (year - 1) * 12 + monthOfYear;
      const eventMonth = (stress.startYear - 1) * 12;
      const affected = month >= eventMonth;
      const priceFactor = affected ? 1 - stress.priceLoss / 100 : 1;
      const paused = affected && month < eventMonth + stress.pauseMonths;
      const dividendFactor =
        paused || (affected && stress.priceLoss === 100)
          ? 0
          : affected
            ? 1 - stress.dividendCut / 100
            : 1;
      const dividends =
        ((strcShares * p.strcRate + sataShares * p.sataRate) / 12) *
        dividendFactor;
      const interest = (cash * p.cashRate) / 1200;
      const net = (dividends + interest) * (1 - p.taxRate / 100);
      netDistributions += net;
      cash += net + p.otherIncome - monthlySpending;
      const creditValue =
        (strcShares * p.strcPrice + sataShares * p.sataPrice) * priceFactor;
      if (cash < 0) {
        const sale = Math.min(-cash, creditValue);
        if (sale > 0) {
          firstSaleMonth ??= month + 1;
          const remainingFraction = 1 - sale / creditValue;
          strcShares *= remainingFraction;
          sataShares *= remainingFraction;
          sales += sale;
          cash += sale;
        }
        if (cash < -0.000001) {
          firstUnfundedMonth ??= month + 1;
          unfunded += -cash;
        }
        cash = Math.max(0, cash);
      }
      portfolio =
        cash +
        (strcShares * p.strcPrice + sataShares * p.sataPrice) * priceFactor;
    }
    totalUnfunded += unfunded;
    rows.push({
      year,
      portfolio,
      realPortfolio: portfolio / (1 + p.inflation / 100) ** year,
      cash,
      netDistributions,
      otherIncome: p.otherIncome * 12,
      spending: monthlySpending * 12,
      sales,
      unfunded,
      monthlyIncome: netDistributions / 12 + p.otherIncome,
      monthlySpending,
    });
  }
  return {
    rows,
    firstUnfundedMonth,
    firstSaleMonth,
    totalUnfunded,
    ending: rows[rows.length - 1],
  };
}

export function capitalForIncome(p: Plan) {
  const netYield = (summarize(p).yield / 100) * (1 - p.taxRate / 100);
  const gap = Math.max(0, p.spending - p.otherIncome) * 12;
  return gap === 0 ? 0 : netYield > 0 ? gap / netYield : null;
}
