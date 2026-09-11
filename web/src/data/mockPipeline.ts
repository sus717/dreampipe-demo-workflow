import type { DemoPhase, PipelineStage, PipelineViewModel, ShotStatus } from '../types/pipeline'
import { evaluateIdeaPrecheck } from './ideaPrecheck'
import demo from './pipelineDemo.generated.json'

const images = {
  S01: `${import.meta.env.BASE_URL}assets/S01-crisis.png`,
  S02: `${import.meta.env.BASE_URL}assets/S02-fishball-chase.png`,
  S03: `${import.meta.env.BASE_URL}assets/S03-day-off-reveal.png`,
} as const

export const defaultDemoIdea = '福州三坊七巷 City Walk 15s 竖屏短片：牛导发现三坊七巷只剩六巷，虎纠冲进古巷，结尾反转第七巷今日调休，CTA 来三坊七巷找到你的第七巷。'

const baseStages = [
  ['brief', '需求', 'Brief 解析'],
  ['bible', '约束', 'Project Bible'],
  ['storyboard', '叙事', '三镜分镜'],
  ['asset-gate', '门禁', '素材预检'],
  ['prompt', '编译', 'Prompt 编译'],
  ['generate', '模型', '镜头生成'],
  ['qa', '质检', 'Vision QA'],
  ['repair', '修复', '局部重试'],
  ['assembly', '交付', '成片合成'],
] as const

function stageStates(phase: DemoPhase): PipelineStage[] {
  const stateMap: Record<DemoPhase, Record<string, PipelineStage['state']>> = {
    waiting: {
      brief: 'passed', bible: 'passed', storyboard: 'passed', 'asset-gate': 'warning',
      prompt: 'idle', generate: 'idle', qa: 'idle', repair: 'idle', assembly: 'idle',
    },
    running: {
      brief: 'passed', bible: 'passed', storyboard: 'passed', 'asset-gate': 'passed',
      prompt: 'passed', generate: 'active', qa: 'idle', repair: 'idle', assembly: 'idle',
    },
    retrying: {
      brief: 'passed', bible: 'passed', storyboard: 'passed', 'asset-gate': 'passed',
      prompt: 'passed', generate: 'ready', qa: 'failed', repair: 'active', assembly: 'idle',
    },
    completed: {
      brief: 'passed', bible: 'passed', storyboard: 'passed', 'asset-gate': 'passed',
      prompt: 'passed', generate: 'passed', qa: 'passed', repair: 'passed', assembly: 'passed',
    },
  }

  const stageMeta: Record<string, Record<DemoPhase, string>> = {
    brief: { waiting: '已验证', running: '已验证', retrying: '已验证', completed: '已验证' },
    bible: { waiting: '已冻结', running: '已冻结', retrying: '已冻结', completed: '已冻结' },
    storyboard: { waiting: 'S01–S03', running: 'S01–S03', retrying: 'S01–S03', completed: 'S01–S03' },
    'asset-gate': { waiting: '等待演示资产', running: '资产锁定', retrying: '资产锁定', completed: '资产锁定' },
    prompt: { waiting: '待运行', running: 'v1 已编译', retrying: '生成修复指令', completed: 'v2 已归档' },
    generate: { waiting: '待运行', running: 'S03 生成中', retrying: 'S01 / S02 完成', completed: '3 镜完成' },
    qa: { waiting: '待运行', running: '等待镜头', retrying: 'S03 · 64 FAIL', completed: '3 / 3 PASS' },
    repair: { waiting: '待运行', running: '待运行', retrying: '只重跑 S03', completed: 'S03 · Attempt 2' },
    assembly: { waiting: '待运行', running: '待运行', retrying: '等待 S03', completed: '15s · 9:16' },
  }

  return baseStages.map(([id, eyebrow, title], index) => ({
    id,
    index: index + 1,
    title,
    eyebrow,
    state: stateMap[phase][id],
    meta: stageMeta[id][phase],
  }))
}

function shotStates(phase: DemoPhase): ShotStatus[] {
  const mutable: ShotStatus[] = [
    { id: 'S01', title: '六巷危机', state: 'waiting', attempt: 1, image: images.S01 },
    { id: 'S02', title: '鱼丸追逐', state: 'waiting', attempt: 1, image: images.S02 },
    { id: 'S03', title: '第七巷调休', state: 'waiting', attempt: 1, image: images.S03 },
  ]

  if (phase === 'running') {
    mutable[0] = { ...mutable[0], state: 'passed', score: 94 }
    mutable[1] = { ...mutable[1], state: 'passed', score: 92 }
    mutable[2] = { ...mutable[2], state: 'generating' }
  }
  if (phase === 'retrying') {
    mutable[0] = { ...mutable[0], state: 'passed', score: 94 }
    mutable[1] = { ...mutable[1], state: 'passed', score: 92 }
    mutable[2] = { ...mutable[2], state: 'retrying', score: 64 }
  }
  if (phase === 'completed') {
    mutable[0] = { ...mutable[0], state: 'passed', score: 94 }
    mutable[1] = { ...mutable[1], state: 'passed', score: 92 }
    mutable[2] = { ...mutable[2], state: 'passed', score: 88, attempt: 2 }
  }

  return mutable
}

const stateCopy: Record<DemoPhase, Omit<PipelineViewModel, 'phase' | 'ideaPrecheck' | 'stages' | 'shots'>> = {
  waiting: {
    statusLabel: '等待资产',
    statusDetail: '创作合同已冻结，WebSocket 后端尚未接入',
    progress: 37,
    readiness: 75,
    activeStageId: 'asset-gate',
    assistant: {
      badge: '生产预检',
      headline: '先补演示资产，再开始生成。',
      body: '本地概念图可用于 Mock 演示；真实运行仍需要可访问的参考素材 URL。',
      action: '载入演示资产',
    },
    retry: {
      scoreBefore: 64,
      issue: '角色与场景连续性待验证',
      repairInstruction: '锁定首帧角色比例，并保留烟台山日落地标。',
    },
    runtime: { spent: 0, budget: 30, eta: '--:--', qaPassed: 0, qaTotal: 3 },
    preview: { label: 'Storyboard ready', image: images.S01, ready: false },
  },
  running: {
    statusLabel: '生产运行中',
    statusDetail: 'Mock Runtime · S03 正在生成',
    progress: 63,
    readiness: 100,
    activeStageId: 'generate',
    assistant: {
      badge: '牛导正在盯片',
      headline: '前两镜稳定，最后一镜正在出片。',
      body: '我会重点检查第七巷的石质轮廓、花衬衫与烟台山背景。',
      action: '查看分镜约束',
    },
    retry: {
      scoreBefore: 64,
      issue: '等待 S03 首次 QA',
      repairInstruction: '生成完成后自动比对角色、地点与 CTA 安全区。',
    },
    runtime: { spent: 14.2, budget: 30, eta: '00:24', qaPassed: 2, qaTotal: 3 },
    preview: { label: 'Shot 02 ready', image: images.S02, ready: false },
  },
  retrying: {
    statusLabel: '局部修复中',
    statusDetail: 'S03 首次 QA 失败 · 只重跑一个镜头',
    progress: 87,
    readiness: 100,
    activeStageId: 'repair',
    assistant: {
      badge: '牛导建议',
      headline: '别整条重做，只修 S03。',
      body: '第七巷的轮廓漂移，且烟台山被弱化。已生成定向修复指令。',
      action: '执行 S03 Retry',
    },
    retry: {
      scoreBefore: 64,
      issue: 'CHARACTER_DRIFT · LOCATION_WEAK',
      repairInstruction: '锁定第七巷的石质 7 轮廓、花衬衫和墨镜；强化烟台山日落与闽江背景。',
    },
    runtime: { spent: 18.6, budget: 30, eta: '00:18', qaPassed: 2, qaTotal: 3 },
    preview: { label: 'Shot 03 · Attempt 1', image: images.S03, ready: false },
  },
  completed: {
    statusLabel: '模拟完成',
    statusDetail: 'S03 Attempt 2 通过 · 15 秒成片就绪',
    progress: 100,
    readiness: 100,
    activeStageId: 'assembly',
    assistant: {
      badge: '交付检查完成',
      headline: '三镜通过，荒诞感保住了。',
      body: '角色、地点、CTA 安全区与预算均通过演示门槛，可进入现场播放。',
      action: '重新演示流程',
    },
    retry: {
      scoreBefore: 64,
      scoreAfter: 88,
      issue: 'S03 已修复并归档',
      repairInstruction: '只重跑 S03，其他镜头与既有成本保持不变。',
    },
    runtime: { spent: 22.4, budget: 30, eta: 'READY', qaPassed: 3, qaTotal: 3 },
    preview: { label: 'Preview ready · 00:15', image: images.S03, ready: true },
  },
}

export const demoOrder: DemoPhase[] = ['waiting', 'running', 'retrying', 'completed']

export function getMockPipeline(phase: DemoPhase, idea = defaultDemoIdea): PipelineViewModel {
  const snapshot = demo.snapshots[phase]
  const status = snapshot.status
  const model: PipelineViewModel = {
    phase,
    ...stateCopy[phase],
    ideaPrecheck: evaluateIdeaPrecheck(idea),
    stages: stageStates(phase),
    shots: shotStates(phase),
  }
  // Use the Python graph's contract for runtime facts, keeping UI copy separate.
  model.progress = status.progress.percent
  model.runtime.spent = snapshot.cost.spent_cny
  model.runtime.qaPassed = status.qa.summary.passed
  model.runtime.eta = phase === 'completed' ? 'MOCK' : '--:--'
  model.shots = model.shots.map((shot) => {
    const qa = status.qa.shots.find((item) => item.shot_id === shot.id)
    const retry = status.retry.shots.find((item) => item.shot_id === shot.id)
    return { ...shot, attempt: retry?.attempt ?? 1,
      score: qa && 'overall' in qa.scores ? qa.scores.overall : undefined,
      state: qa?.status === 'PASS' ? 'passed' : retry?.status === 'RETRYING' ? 'retrying' : phase === 'running' ? 'generating' : 'waiting' }
  })
  const failed = demo.snapshots.retrying.status.qa.shots.find((shot) => shot.shot_id === 'S03')!
  model.retry.scoreBefore = failed.scores.overall
  model.retry.scoreAfter = phase === 'completed' ? demo.snapshots.completed.status.qa.shots.find((shot) => shot.shot_id === 'S03')!.scores.overall : undefined
  model.retry.issue = phase === 'completed' ? 'S03 已通过 Mock QA' : failed.failure_codes.join(' · ')
  model.retry.repairInstruction = failed.repair_instruction
  model.stages = model.stages.map((stage) => stage.id === 'qa' ? {
    ...stage, meta: phase === 'retrying' ? `S03 · ${model.retry.scoreBefore} FAIL` : phase === 'completed' ? '3 / 3 PASS' : '等待 QA',
  } : stage)
  model.preview.ready = false
  model.preview.label = '分镜概念图 · 非生成视频'
  model.statusDetail = phase === 'completed' ? 'Mock 流水线已通过 · 尚未生成真实成片' : `Python Mock 状态回放 · ${status.current_step}`
  if (phase === 'completed') {
    model.assistant.headline = '三镜通过 Mock QA，可继续检查未实现项。'
    model.assistant.body = '此处只有概念图和状态回放。真实视频、配音与成片合成尚未接入网页。'
  }
  if (phase === 'running') {
    model.assistant.headline = '三镜模拟生成完成，等待 Mock QA。'
    model.assistant.body = '状态来自共享分镜驱动的 Python 流水线，不代表真实模型调用。'
  }
  return model
}
