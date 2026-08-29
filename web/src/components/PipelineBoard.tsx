import AutoStoriesRounded from '@mui/icons-material/AutoStoriesRounded'
import CheckRounded from '@mui/icons-material/CheckRounded'
import DataObjectRounded from '@mui/icons-material/DataObjectRounded'
import FactCheckRounded from '@mui/icons-material/FactCheckRounded'
import MovieCreationRounded from '@mui/icons-material/MovieCreationRounded'
import PolicyRounded from '@mui/icons-material/PolicyRounded'
import ReplayRounded from '@mui/icons-material/ReplayRounded'
import ShieldRounded from '@mui/icons-material/ShieldRounded'
import VideoFileRounded from '@mui/icons-material/VideoFileRounded'
import ViewCarouselRounded from '@mui/icons-material/ViewCarouselRounded'
import { Box, ButtonBase, Chip, LinearProgress, Paper, Stack, Typography } from '@mui/material'
import type { PipelineStage, PipelineViewModel, ShotStatus } from '../types/pipeline'

const stageIcons: Record<string, React.ReactNode> = {
  brief: <FactCheckRounded />,
  bible: <AutoStoriesRounded />,
  storyboard: <ViewCarouselRounded />,
  'asset-gate': <ShieldRounded />,
  prompt: <DataObjectRounded />,
  generate: <MovieCreationRounded />,
  qa: <PolicyRounded />,
  repair: <ReplayRounded />,
  assembly: <VideoFileRounded />,
}

const shotStateCopy: Record<ShotStatus['state'], string> = {
  waiting: '等待',
  generating: '生成中',
  passed: 'PASS',
  failed: 'FAIL',
  retrying: 'RETRY',
}

function StageNode({ stage, active }: { stage: PipelineStage; active: boolean }) {
  return (
    <ButtonBase
      className={`stage-node stage-${stage.state} ${active ? 'is-active' : ''}`}
      data-stage={stage.id}
      aria-current={active ? 'step' : undefined}
    >
      <Box className="stage-number">{stage.state === 'passed' ? <CheckRounded /> : stage.index}</Box>
      <Box className="stage-copy">
        <Typography className="stage-eyebrow">{stage.eyebrow}</Typography>
        <Typography className="stage-title">{stage.title}</Typography>
        <Typography className="stage-meta">{stage.meta}</Typography>
      </Box>
      <Box className="stage-icon">{stageIcons[stage.id]}</Box>
    </ButtonBase>
  )
}

function StageRow({ stages, activeStageId }: { stages: PipelineStage[]; activeStageId: string }) {
  return (
    <Box className={`stage-row stage-row-${stages.length}`}>
      {stages.map((stage, index) => (
        <Box className="stage-cell" key={stage.id}>
          <StageNode stage={stage} active={stage.id === activeStageId} />
          {index < stages.length - 1 ? <Box className="stage-connector"><span /></Box> : null}
        </Box>
      ))}
    </Box>
  )
}

function ShotCard({ shot }: { shot: ShotStatus }) {
  return (
    <Box className={`shot-card shot-${shot.state}`}>
      <img src={shot.image} alt={`${shot.id} ${shot.title}`} />
      <Box className="shot-overlay">
        <Stack direction="row" alignItems="center" justifyContent="space-between">
          <Typography className="shot-id">{shot.id}</Typography>
          <Chip size="small" label={shotStateCopy[shot.state]} className="shot-state" />
        </Stack>
        <Typography className="shot-title">{shot.title}</Typography>
        <Typography className="shot-meta">
          Attempt {shot.attempt}{shot.score ? ` · QA ${shot.score}` : ''}
        </Typography>
      </Box>
    </Box>
  )
}

interface PipelineBoardProps {
  model: PipelineViewModel
}

export function PipelineBoard({ model }: PipelineBoardProps) {
  const planningStages = model.stages.slice(0, 4)
  const runtimeStages = model.stages.slice(4)
  const isRetryBeat = model.phase === 'retrying' || model.phase === 'completed'

  return (
    <Paper component="main" className="pipeline-board surface-panel" elevation={0} data-animate="panel">
      <Box className="board-glow" aria-hidden="true" />
      <Box className="pipeline-heading">
        <Box>
          <Typography className="eyebrow">CONTROL PLANE / MOCK RUNTIME</Typography>
          <Typography variant="h2">从创作意图到可交付成片</Typography>
        </Box>
        <Box className={`live-status live-${model.phase}`}>
          <span />
          <Box>
            <Typography>{model.statusLabel}</Typography>
            <Typography>{model.statusDetail}</Typography>
          </Box>
        </Box>
      </Box>

      <Box className="progress-rail">
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography>PIPELINE PROGRESS</Typography>
          <Typography>{model.progress}%</Typography>
        </Stack>
        <LinearProgress variant="determinate" value={model.progress} color={model.phase === 'retrying' ? 'warning' : 'secondary'} />
      </Box>

      <Box className="layer-block planning-layer">
        <Typography className="layer-label">01 · 创意控制层</Typography>
        <StageRow stages={planningStages} activeStageId={model.activeStageId} />
      </Box>

      <Box className="layer-bridge" aria-hidden="true"><span>编译合同 → 生成执行计划</span></Box>

      <Box className="layer-block runtime-layer">
        <Typography className="layer-label">02 · 生成执行层</Typography>
        <StageRow stages={runtimeStages} activeStageId={model.activeStageId} />
      </Box>

      <Box className={`retry-inspector ${isRetryBeat ? 'is-visible' : ''}`}>
        <Box className="retry-headline">
          <Stack direction="row" alignItems="center" spacing={1}>
            <ReplayRounded />
            <Box>
              <Typography className="eyebrow">S03 / SELECTIVE RETRY</Typography>
              <Typography variant="h3">只重跑失败镜头</Typography>
            </Box>
          </Stack>
          <Box className="score-transition">
            <span className="score-fail">{model.retry.scoreBefore}</span>
            <span>→</span>
            <span className={model.retry.scoreAfter ? 'score-pass' : 'score-pending'}>
              {model.retry.scoreAfter ?? '…'}
            </span>
          </Box>
        </Box>
        <Box className="repair-flow">
          <Box><span>01</span><strong>诊断</strong><small>{model.retry.issue}</small></Box>
          <i />
          <Box><span>02</span><strong>修复指令</strong><small>锁定角色与场景锚点</small></Box>
          <i />
          <Box><span>03</span><strong>只重跑 S03</strong><small>Attempt 2 · 成本隔离</small></Box>
        </Box>
        <Typography className="repair-instruction">“{model.retry.repairInstruction}”</Typography>
      </Box>

      <Box className="shot-strip">
        <Box className="shot-strip-heading">
          <Box>
            <Typography className="eyebrow">PROJECT BIBLE / STORYBOARD</Typography>
            <Typography>三镜连续性资产</Typography>
          </Box>
          <Typography>3 SHOTS · 15 SEC · 9:16</Typography>
        </Box>
        <Box className="shot-grid">
          {model.shots.map((shot) => <ShotCard shot={shot} key={shot.id} />)}
        </Box>
      </Box>
    </Paper>
  )
}
