import {
  DEFAULT_PLAN,
  summarize,
  project,
  validatePlan,
  type Plan,
} from './retirement';

interface Tool {
  name: string;
  title: string;
  description: string;
  inputSchema: object;
  annotations: { readOnlyHint: boolean; untrustedContentHint: boolean };
  execute(input: unknown): unknown;
}
export interface ModelContext {
  registerTool(
    tool: Tool,
    options: { signal: AbortSignal },
  ): void | Promise<void>;
}
export function registerPlanTools(
  context: ModelContext,
  read: () => Plan,
  write: (plan: Plan) => void,
) {
  const lifecycle = new AbortController();
  const snapshot = () => {
    const plan = read();
    const result = summarize(plan);
    const projection = project(plan);
    return {
      plan,
      monthlyCashAvailable: result.available,
      firstUnfundedMonth: projection.firstUnfundedMonth,
      endingPortfolio: projection.ending.portfolio,
    };
  };
  const tools: Tool[] = [
    {
      name: 'read_retirement_plan',
      title: 'Read retirement plan',
      description:
        'Read the visible FireCalc inputs and deterministic base-case results. Illustrative model, not financial advice.',
      inputSchema: {
        type: 'object',
        properties: {},
        additionalProperties: false,
      },
      annotations: { readOnlyHint: true, untrustedContentHint: false },
      execute: () => snapshot(),
    },
    {
      name: 'configure_retirement_plan',
      title: 'Configure retirement plan',
      description:
        'Update any combination of the visible retirement inputs and return recalculated results. Allocations must total at most 100%; no trades or financial-service writes occur.',
      inputSchema: {
        type: 'object',
        properties: Object.fromEntries(
          Object.keys(DEFAULT_PLAN).map((k) => [k, { type: 'number' }]),
        ),
        additionalProperties: false,
      },
      annotations: { readOnlyHint: false, untrustedContentHint: false },
      execute(input) {
        if (!input || typeof input !== 'object' || Array.isArray(input))
          throw new Error('Expected a plan parameter object');
        const patch = input as Record<string, unknown>;
        for (const [key, value] of Object.entries(patch))
          if (
            !Object.prototype.hasOwnProperty.call(DEFAULT_PLAN, key) ||
            typeof value !== 'number'
          )
            throw new Error('Unknown or nonnumeric plan parameter');
        const next = { ...read(), ...patch } as Plan;
        validatePlan(next);
        write(next);
        return snapshot();
      },
    },
  ];
  for (const tool of tools) {
    try {
      void Promise.resolve(
        context.registerTool(tool, { signal: lifecycle.signal }),
      ).catch(() => {});
    } catch {
      /* Optional browser feature; the visible calculator remains usable. */
    }
  }
  return () => lifecycle.abort();
}
