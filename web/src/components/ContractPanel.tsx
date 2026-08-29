import CheckCircleRounded from '@mui/icons-material/CheckCircleRounded'
import ErrorOutlineRounded from '@mui/icons-material/ErrorOutlineRounded'
import LocalFireDepartmentRounded from '@mui/icons-material/LocalFireDepartmentRounded'
import SpeedRounded from '@mui/icons-material/SpeedRounded'
import TokenRounded from '@mui/icons-material/TokenRounded'
import { Box, Chip, CircularProgress, Divider, LinearProgress, Paper, Stack, Typography } from '@mui/material'
import type { PipelineViewModel } from '../types/pipeline'

interface ContractPanelProps {
  model: PipelineViewModel
}

const verdictCopy = {
  ready: '可以开跑',
  revise: '建议微调',
  risky: '先别生成',
} as const

export function ContractPanel({ model }: ContractPanelProps) {
  const precheck = model.ideaPrecheck
  const risky = precheck.verdict === 'risky'
  const revise = precheck.verdict === 'revise'
  const ringColor = risky ? 'error' : revise ? 'warning' : 'success'

  return (
    <Paper component="aside" className="contract-panel surface-panel" elevation={0} data-animate="panel">
      <Box className="panel-heading">
        <Box>
          <Typography className="eyebrow">IDEA PRECHECK</Typography>
          <Typography variant="h3">创意前置检查</Typography>
        </Box>
        <Box className="panel-menu">•••</Box>
      </Box>

      <Box className="readiness-block">
        <Box className="readiness-ring">
          <CircularProgress variant="determinate" value={100} className="ring-track" size={132} thickness={3.2} />
          <CircularProgress
            variant="determinate"
            value={precheck.overallScore}
            color={ringColor}
            size={132}
            thickness={3.2}
          />
          <Box className="ring-label">
            <Typography className="ring-value">{precheck.overallScore}</Typography>
            <Typography>{verdictCopy[precheck.verdict]}</Typography>
          </Box>
        </Box>
        <Typography className="readiness-copy">
          预计 {precheck.estimatedTokens} tokens，先判断是否值得进入生成流程。
        </Typography>
      </Box>

      <Divider />

      <Box className="idea-card">
        <Typography className="idea-label">用户想法</Typography>
        <Typography className="idea-copy">{precheck.idea}</Typography>
      </Box>

      <Stack className="score-list">
        <Box className="score-row">
          <Box className="score-title"><TokenRounded /><Typography>Token 成本</Typography></Box>
          <Typography className="score-value">{precheck.tokenLoadScore}</Typography>
          <LinearProgress variant="determinate" value={precheck.tokenLoadScore} color={precheck.tokenLoadScore < 70 ? 'warning' : 'success'} />
        </Box>
        <Box className="score-row">
          <Box className="score-title"><LocalFireDepartmentRounded /><Typography>爆款概率</Typography></Box>
          <Typography className="score-value">{precheck.viralScore}</Typography>
          <LinearProgress variant="determinate" value={precheck.viralScore} color={precheck.viralScore < 70 ? 'warning' : 'secondary'} />
        </Box>
      </Stack>

      <Chip icon={<SpeedRounded />} label="进入生成前先省一次试错成本" className="trend-chip" />

      <Stack className="gate-list" spacing={0.8}>
        {precheck.highlights.map((item) => (
          <Box className="gate-item gate-pass" key={item}>
            <CheckCircleRounded />
            <span>{item}</span>
          </Box>
        ))}
        {precheck.warnings.slice(0, 2).map((item) => (
          <Box className="gate-item gate-warn" key={item}>
            <ErrorOutlineRounded />
            <span>{item}</span>
          </Box>
        ))}
      </Stack>
    </Paper>
  )
}
