import { startTransition, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { demoOrder, getMockPipeline } from '../data/mockPipeline'
import type { DemoPhase } from '../types/pipeline'

export function usePipelineDemo() {
  const [phase, setPhase] = useState<DemoPhase>('retrying')
  const timers = useRef<number[]>([])
  const model = useMemo(() => getMockPipeline(phase), [phase])

  const clearTimers = useCallback(() => {
    timers.current.forEach(window.clearTimeout)
    timers.current = []
  }, [])

  const selectPhase = useCallback((next: DemoPhase) => {
    clearTimers()
    startTransition(() => setPhase(next))
  }, [clearTimers])

  const runDemo = useCallback(() => {
    clearTimers()
    setPhase('waiting')
    const sequence: Array<[DemoPhase, number]> = [
      ['running', 900],
      ['retrying', 2500],
      ['completed', 4800],
    ]
    timers.current = sequence.map(([next, delay]) => window.setTimeout(() => {
      startTransition(() => setPhase(next))
    }, delay))
  }, [clearTimers])

  const performPrimaryAction = useCallback(() => {
    if (phase === 'completed') {
      selectPhase('retrying')
      return
    }
    if (phase === 'retrying') {
      selectPhase('completed')
      return
    }
    runDemo()
  }, [phase, runDemo, selectPhase])

  useEffect(() => clearTimers, [clearTimers])

  return { model, phase, phases: demoOrder, selectPhase, runDemo, performPrimaryAction }
}
