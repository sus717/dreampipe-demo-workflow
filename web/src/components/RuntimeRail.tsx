import AutoFixHighRounded from '@mui/icons-material/AutoFixHighRounded'
import CurrencyYenRounded from '@mui/icons-material/CurrencyYenRounded'
import DataObjectRounded from '@mui/icons-material/DataObjectRounded'
import HubOutlined from '@mui/icons-material/HubOutlined'
import PolicyRounded from '@mui/icons-material/PolicyRounded'
import SmartDisplayOutlined from '@mui/icons-material/SmartDisplayOutlined'
import { Box, LinearProgress, Typography } from '@mui/material'
import type { PipelineViewModel } from '../types/pipeline'

interface RuntimeRailProps {
  model: PipelineViewModel
}

export function RuntimeRail({ model }: RuntimeRailProps) {
  const spentPercent = Math.round((model.runtime.spent / model.runtime.budget) * 100)

  return (
    <Box component="footer" className="runtime-rail" data-animate="rail">
      <Box className="runtime-cell runtime-reserved">
        <HubOutlined />
        <Box><Typography>WebSocket API</Typography><Typography>RESERVED · 未接后端</Typography></Box>
      </Box>
      <Box className="runtime-cell runtime-ready">
        <DataObjectRounded />
        <Box><Typography>GLM Compiler</Typography><Typography>MOCK CONTRACT</Typography></Box>
      </Box>
      <Box className="runtime-cell runtime-ready">
        <SmartDisplayOutlined />
        <Box><Typography>HappyHorse</Typography><Typography>ADAPTER RESERVED</Typography></Box>
      </Box>
      <Box className="runtime-cell">
        <PolicyRounded />
        <Box className="runtime-progress-copy">
          <Typography>QA Gate {model.runtime.qaPassed}/{model.runtime.qaTotal}</Typography>
          <LinearProgress variant="determinate" value={(model.runtime.qaPassed / model.runtime.qaTotal) * 100} color="success" />
        </Box>
      </Box>
      <Box className="runtime-cell">
        <CurrencyYenRounded />
        <Box className="runtime-progress-copy">
          <Typography>Cost Gate ¥{model.runtime.spent.toFixed(2)} / ¥{model.runtime.budget}</Typography>
          <LinearProgress variant="determinate" value={spentPercent} color="warning" />
        </Box>
      </Box>
      <Box className={`runtime-cell runtime-eta runtime-${model.phase}`}>
        <AutoFixHighRounded />
        <Box><Typography>{model.phase === 'completed' ? 'Mock completed' : 'Pipeline ETA'}</Typography><Typography>{model.runtime.eta}</Typography></Box>
      </Box>
    </Box>
  )
}
