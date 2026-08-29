import CheckCircleRounded from '@mui/icons-material/CheckCircleRounded'
import ErrorOutlineRounded from '@mui/icons-material/ErrorOutlineRounded'
import ExploreRounded from '@mui/icons-material/ExploreRounded'
import Groups2Rounded from '@mui/icons-material/Groups2Rounded'
import PaymentsOutlined from '@mui/icons-material/PaymentsOutlined'
import SmartDisplayOutlined from '@mui/icons-material/SmartDisplayOutlined'
import TimerOutlined from '@mui/icons-material/TimerOutlined'
import { Box, Chip, CircularProgress, Divider, Paper, Stack, Typography } from '@mui/material'
import type { PipelineViewModel } from '../types/pipeline'

const contractRows = [
  { icon: <ExploreRounded />, label: '目的地', value: '福州 · 三坊七巷' },
  { icon: <Groups2Rounded />, label: '受众', value: '18–30 岁城市漫游人群' },
  { icon: <SmartDisplayOutlined />, label: '渠道', value: '抖音 · 竖屏' },
  { icon: <TimerOutlined />, label: '交付', value: '15s · 9:16 · 3 镜' },
  { icon: <PaymentsOutlined />, label: '预算', value: '¥30 CNY' },
]

interface ContractPanelProps {
  model: PipelineViewModel
}

export function ContractPanel({ model }: ContractPanelProps) {
  const waiting = model.phase === 'waiting'

  return (
    <Paper component="aside" className="contract-panel surface-panel" elevation={0} data-animate="panel">
      <Box className="panel-heading">
        <Box>
          <Typography className="eyebrow">PRODUCTION CONTRACT</Typography>
          <Typography variant="h3">生产前置检查</Typography>
        </Box>
        <Box className="panel-menu">•••</Box>
      </Box>

      <Box className="readiness-block">
        <Box className="readiness-ring">
          <CircularProgress variant="determinate" value={100} className="ring-track" size={132} thickness={3.2} />
          <CircularProgress
            variant="determinate"
            value={model.readiness}
            color={waiting ? 'warning' : 'success'}
            size={132}
            thickness={3.2}
          />
          <Box className="ring-label">
            <Typography className="ring-value">{model.readiness}%</Typography>
            <Typography>{waiting ? '3 / 4 READY' : 'READY'}</Typography>
          </Box>
        </Box>
        <Typography className="readiness-copy">
          {waiting ? '创作规则已锁定，参考资产仍在门禁中。' : 'Brief、Bible、分镜与资产均已通过预检。'}
        </Typography>
      </Box>

      <Divider />

      <Stack className="contract-rows">
        {contractRows.map((row) => (
          <Box className="contract-row" key={row.label}>
            <Box className="contract-icon">{row.icon}</Box>
            <Typography className="contract-label">{row.label}</Typography>
            <Typography className="contract-value">{row.value}</Typography>
          </Box>
        ))}
      </Stack>

      <Chip icon={<span>🔥</span>} label="热点适配器 · City Walk" className="trend-chip" />

      <Stack className="gate-list" spacing={0.8}>
        <Box className="gate-item gate-pass">
          <CheckCircleRounded />
          <span>创意合同与三镜分镜已冻结</span>
        </Box>
        <Box className="gate-item gate-pass">
          <CheckCircleRounded />
          <span>品牌红线与 CTA 已校验</span>
        </Box>
        <Box className={`gate-item ${waiting ? 'gate-warn' : 'gate-pass'}`}>
          {waiting ? <ErrorOutlineRounded /> : <CheckCircleRounded />}
          <span>{waiting ? '真实参考素材 URL 待接入' : '演示资产已锁定'}</span>
        </Box>
      </Stack>
    </Paper>
  )
}
