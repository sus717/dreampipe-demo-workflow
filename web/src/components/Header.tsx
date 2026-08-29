import AddRounded from '@mui/icons-material/AddRounded'
import BoltRounded from '@mui/icons-material/BoltRounded'
import ShieldOutlined from '@mui/icons-material/ShieldOutlined'
import { Box, Button, Chip, Stack, ToggleButton, ToggleButtonGroup, Typography } from '@mui/material'
import type { DemoPhase, PipelineViewModel } from '../types/pipeline'

const phaseLabels: Record<DemoPhase, string> = {
  waiting: '资产门禁',
  running: '运行中',
  retrying: '局部重试',
  completed: '已完成',
}

interface HeaderProps {
  model: PipelineViewModel
  phase: DemoPhase
  phases: DemoPhase[]
  onPhaseChange: (phase: DemoPhase) => void
  onRunDemo: () => void
}

export function Header({ model, phase, phases, onPhaseChange, onRunDemo }: HeaderProps) {
  return (
    <Box component="header" className="app-header" data-animate="header">
      <Stack direction="row" alignItems="center" spacing={1.6} className="brand-lockup">
        <Box className="brand-mark" aria-hidden="true">
          <span />
          <span />
        </Box>
        <Box>
          <Typography className="brand-name">DreamPipe</Typography>
          <Typography className="brand-caption">PRODUCTION CONTROL</Typography>
        </Box>
      </Stack>

      <Box className="project-identity">
        <Typography className="project-kicker">内容生产控制塔</Typography>
        <Typography className="project-title">《第七巷今天调休》</Typography>
      </Box>

      <ToggleButtonGroup
        className="phase-switcher"
        exclusive
        size="small"
        value={phase}
        onChange={(_, value: DemoPhase | null) => value && onPhaseChange(value)}
        aria-label="切换演示状态"
      >
        {phases.map((item) => (
          <ToggleButton key={item} value={item} aria-label={phaseLabels[item]}>
            {phaseLabels[item]}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>

      <Stack direction="row" alignItems="center" spacing={1} className="header-actions">
        <Chip
          icon={<ShieldOutlined />}
          label="Demo / Mock"
          variant="outlined"
          className="demo-chip"
        />
        <Button
          variant="contained"
          color="primary"
          startIcon={<BoltRounded />}
          endIcon={<AddRounded />}
          onClick={onRunDemo}
          className="run-button"
        >
          {model.phase === 'completed' ? '重新演示' : '运行全流程'}
        </Button>
      </Stack>
    </Box>
  )
}
