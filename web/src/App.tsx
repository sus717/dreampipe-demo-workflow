import { useLayoutEffect, useRef } from 'react'
import { Box } from '@mui/material'
import { gsap } from 'gsap'
import { ContractPanel } from './components/ContractPanel'
import { CopilotPanel } from './components/CopilotPanel'
import { Header } from './components/Header'
import { PipelineBoard } from './components/PipelineBoard'
import { RuntimeRail } from './components/RuntimeRail'
import { IntegrationPanel } from './components/IntegrationPanel'
import { usePipelineDemo } from './hooks/usePipelineDemo'

export function App() {
  const root = useRef<HTMLDivElement>(null)
  const { idea, model, phase, phases, selectPhase, runDemo, performPrimaryAction, setIdea } = usePipelineDemo()

  useLayoutEffect(() => {
    const context = gsap.context(() => {
      const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
      if (reduceMotion) return

      gsap.from('[data-animate="header"]', { y: -18, opacity: 0, duration: 0.55, ease: 'power3.out' })
      gsap.from('[data-animate="panel"]', {
        y: 24,
        opacity: 0,
        duration: 0.72,
        stagger: 0.08,
        delay: 0.12,
        ease: 'power3.out',
      })
      gsap.from('[data-animate="rail"]', { y: 22, opacity: 0, duration: 0.55, delay: 0.38, ease: 'power3.out' })
    }, root)
    return () => context.revert()
  }, [])

  useLayoutEffect(() => {
    const context = gsap.context(() => {
      const activeNode = `[data-stage="${model.activeStageId}"]`
      gsap.fromTo(activeNode, { scale: 0.985 }, { scale: 1, duration: 0.45, ease: 'back.out(2)' })
      gsap.fromTo('.live-status', { opacity: 0.55, x: 6 }, { opacity: 1, x: 0, duration: 0.38 })
      if (model.phase === 'retrying' || model.phase === 'completed') {
        gsap.fromTo('.retry-inspector', { y: 10, opacity: 0.5 }, { y: 0, opacity: 1, duration: 0.48, ease: 'power2.out' })
      }
    }, root)
    return () => context.revert()
  }, [model.activeStageId, model.phase])

  return (
    <Box ref={root} className="app-shell">
      <Box className="ambient-grid" aria-hidden="true" />
      <Header model={model} phase={phase} phases={phases} onPhaseChange={selectPhase} onRunDemo={runDemo} />
      <IntegrationPanel phase={phase} />
      <Box className="workspace-grid">
        <ContractPanel model={model} />
        <PipelineBoard model={model} />
        <CopilotPanel model={model} idea={idea} onIdeaChange={setIdea} onPrimaryAction={performPrimaryAction} />
      </Box>
      <RuntimeRail model={model} />
    </Box>
  )
}
