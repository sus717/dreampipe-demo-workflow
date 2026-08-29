export type DemoPhase = 'waiting' | 'running' | 'retrying' | 'completed'

export type StageState = 'idle' | 'ready' | 'active' | 'warning' | 'failed' | 'passed'

export interface PipelineStage {
  id: string
  index: number
  title: string
  eyebrow: string
  state: StageState
  meta: string
}

export interface ShotStatus {
  id: 'S01' | 'S02' | 'S03'
  title: string
  state: 'waiting' | 'generating' | 'passed' | 'failed' | 'retrying'
  score?: number
  attempt: number
  image: string
}

export interface PipelineViewModel {
  phase: DemoPhase
  statusLabel: string
  statusDetail: string
  progress: number
  readiness: number
  activeStageId: string
  stages: PipelineStage[]
  shots: ShotStatus[]
  assistant: {
    badge: string
    headline: string
    body: string
    action: string
  }
  retry: {
    scoreBefore: number
    scoreAfter?: number
    issue: string
    repairInstruction: string
  }
  runtime: {
    spent: number
    budget: number
    eta: string
    qaPassed: number
    qaTotal: number
  }
  preview: {
    label: string
    image: string
    ready: boolean
  }
}

export interface PipelineSocketEvent {
  type: 'pipeline.snapshot' | 'pipeline.stage' | 'pipeline.error'
  projectId: string
  payload: unknown
}
