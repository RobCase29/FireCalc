'use client';
import { useEffect, useRef, type Dispatch, type SetStateAction } from 'react';
import { flushSync } from 'react-dom';
import { registerPlanTools, type ModelContext } from '@/lib/webmcp';
import { type Plan } from '@/lib/retirement';

export function usePlanTools(
  plan: Plan,
  setPlan: Dispatch<SetStateAction<Plan>>,
) {
  const current = useRef(plan);
  useEffect(() => {
    current.current = plan;
  }, [plan]);
  useEffect(() => {
    const context = (document as Document & { modelContext?: ModelContext })
      .modelContext;
    if (!context?.registerTool) return;
    return registerPlanTools(
      context,
      () => current.current,
      (next) => {
        flushSync(() => setPlan(next));
        current.current = next;
      },
    );
  }, [setPlan]);
}
