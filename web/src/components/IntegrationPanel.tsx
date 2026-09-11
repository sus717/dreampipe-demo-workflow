import { useState } from 'react'
import { Alert, Box, Button, Dialog, DialogContent, DialogTitle, Stack, Typography } from '@mui/material'
import brief from '../../../shared/brief.json'
import bible from '../../../shared/project_bible.json'
import storyboard from '../../../shared/shots.json'
import demo from '../data/pipelineDemo.generated.json'
import type { DemoPhase } from '../types/pipeline'

export function IntegrationPanel({ phase }: { phase: DemoPhase }) {
  const [open, setOpen] = useState(false)
  const snapshot = demo.snapshots[phase]
  const download = () => {
    const file = new Blob([JSON.stringify({ mode: demo.mode, brief, bible, storyboard, snapshot }, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(file)
    const link = document.createElement('a')
    link.href = url
    link.download = `dreampipe-${phase}.json`
    link.click()
    window.setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
  return <>
    <Alert severity="info" sx={{ mx: 2, mb: 2 }} action={<Button color="inherit" onClick={() => setOpen(true)}>测试与实现清单</Button>}>
      离线集成演示：共享 Brief → 分镜 → Python Mock 流水线 → 页面状态。费用和 QA 为模拟数据，没有真实视频。
    </Alert>
    <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>测试与实现清单</DialogTitle>
      <DialogContent>
        <Stack spacing={2}>
          <Typography>已整合：创意规则预检、共享创意合同、三镜分镜、资产门禁、S03 局部重试与 QA 状态回放。</Typography>
          <Alert severity="warning">未接通：创意自动转 Brief、素材上传、网页发起真实生成、实时进度、真实费用统计、配音、字幕、视频合成与下载。编辑创意只更新预检，不会改写已冻结分镜。</Alert>
          <Typography>GLM、HappyHorse 与真实 QA 已有 Python 适配代码，但本页面未调用，尚未完成真实服务联调。当前规则分数不代表经过验证的爆款概率。</Typography>
          <Typography variant="h6">共享分镜 · {storyboard.target_duration_seconds}s · {storyboard.aspect_ratio}</Typography>
          {storyboard.shots.map((shot) => <Box key={shot.shot_id}>
            <Typography fontWeight={700}>{shot.shot_id} · {shot.duration_seconds}s · {shot.scene}</Typography>
            <Typography>{shot.story_function}</Typography>
            <Typography variant="body2" color="text.secondary">{shot.dialogue.map((line) => `${line.speaker}：${line.line}`).join(' / ')}</Typography>
          </Box>)}
          <Typography variant="h6">当前流水线事件 · {snapshot.status.status}</Typography>
          {snapshot.events.map((event, index) => <Typography variant="body2" key={`${event.node}-${index}`}>{event.node} — {event.message}</Typography>)}
          <Stack direction="row" spacing={2}>
            <Button onClick={download} variant="contained">下载当前测试数据</Button>
            <Button onClick={() => setOpen(false)}>关闭</Button>
          </Stack>
        </Stack>
      </DialogContent>
    </Dialog>
  </>
}
