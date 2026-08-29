import ArrowForwardRounded from '@mui/icons-material/ArrowForwardRounded'
import AutoAwesomeRounded from '@mui/icons-material/AutoAwesomeRounded'
import FullscreenRounded from '@mui/icons-material/FullscreenRounded'
import PlayArrowRounded from '@mui/icons-material/PlayArrowRounded'
import SendRounded from '@mui/icons-material/SendRounded'
import { Box, Button, Chip, IconButton, Paper, Stack, Typography } from '@mui/material'
import type { PipelineViewModel } from '../types/pipeline'

interface CopilotPanelProps {
  model: PipelineViewModel
  onPrimaryAction: () => void
}

export function CopilotPanel({ model, onPrimaryAction }: CopilotPanelProps) {
  return (
    <Box component="aside" className="copilot-column" data-animate="panel">
      <Paper className="copilot-card surface-panel" elevation={0}>
        <Box className="panel-heading copilot-heading">
          <Stack direction="row" alignItems="center" spacing={1}>
            <AutoAwesomeRounded />
            <Box>
              <Typography className="eyebrow">NIU DIRECTOR</Typography>
              <Typography variant="h3">牛导 · 制片监督</Typography>
            </Box>
          </Stack>
          <Chip size="small" label="CONTEXTUAL" />
        </Box>

        <Box className="director-scene">
          <img src="/assets/niulai-character.png" alt="牛导角色" />
          <Box className="director-message">
            <Typography>{model.assistant.headline}</Typography>
            <Typography>{model.assistant.body}</Typography>
          </Box>
        </Box>

        <Chip className="director-badge" label={model.assistant.badge} size="small" />
        <Button
          fullWidth
          variant="outlined"
          color={model.phase === 'retrying' ? 'warning' : 'secondary'}
          endIcon={<ArrowForwardRounded />}
          onClick={onPrimaryAction}
          className="director-action"
        >
          {model.assistant.action}
        </Button>

        <Box className="prompt-shell">
          <Typography>告诉牛导你的想法…</Typography>
          <IconButton size="small" aria-label="发送，暂未接后端" disabled>
            <SendRounded />
          </IconButton>
        </Box>
      </Paper>

      <Paper className={`preview-card surface-panel ${model.preview.ready ? 'preview-ready' : ''}`} elevation={0}>
        <Box className="preview-heading">
          <Stack direction="row" alignItems="center" spacing={1}>
            <span className="preview-dot" />
            <Typography>{model.preview.label}</Typography>
          </Stack>
          <IconButton size="small" aria-label="全屏预览"><FullscreenRounded /></IconButton>
        </Box>
        <Box className="preview-frame">
          <img src={model.preview.image} alt="成片竖屏预览" />
          <Box className="preview-vignette" />
          <Box className="preview-copy">
            <Typography>第七巷今天调休</Typography>
            <Typography>去三坊七巷，找到第七巷</Typography>
          </Box>
          <Button className="play-control" aria-label="播放预览"><PlayArrowRounded /></Button>
        </Box>
        <Box className="preview-footer">
          <Typography>9:16</Typography>
          <Typography>{model.preview.ready ? 'FINAL OUTPUT' : 'MOCK PREVIEW'}</Typography>
          <Typography>00:15</Typography>
        </Box>
      </Paper>
    </Box>
  )
}
