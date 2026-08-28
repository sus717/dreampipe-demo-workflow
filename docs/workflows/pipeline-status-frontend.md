# Pod 3 → Pod 4：前端 Pipeline 状态接口

## 文件

- `shared/schemas/pipeline_status.schema.json`：前端只读状态合同
- `examples/pipeline-status.retrying.mock.json`：QA 失败并进入重试
- `examples/pipeline-status.completed.mock.json`：成功与最终 MP4 返回
- `examples/pipeline-status.failed.mock.json`：模型或服务错误

## MVP 数据方式

前端不能直接调用 LangGraph、百炼或视频模型。后端保存 Job 后提供：

```text
GET /api/projects/{project_id}/pipeline-status
```

流程处于 `QUEUED`、`RUNNING`、`RETRYING` 时，前端每 2 秒轮询；处于
`SUCCEEDED`、`FAILED`、`CANCELLED` 时停止。成功后播放
`final_output.video_url`，失败时展示 `error.message` 与重试提示。

后端用 `dreampipe.status_view.build_pipeline_status(job, events)` 将内部
LangGraph Job 投影为这个 JSON。响应不能包含 API Key、百炼原始响应、Prompt
全文或私有素材路径。

若时间允许可以额外增加 SSE 实时推送，但 HTTP 轮询是 MVP 必备降级方案，且不改变
本 JSON 合同。

## 字段

| 字段 | 前端用途 |
|---|---|
| `status` | 排队、运行、重试、成功、失败、取消 |
| `current_step` | 当前流程节点与步骤高亮 |
| `progress` | 总进度 |
| `retry` | 各镜头尝试次数与修复提示 |
| `qa` | 分数、失败码、修复建议 |
| `error` | 可安全展示的错误信息 |
| `final_output` | 最终 MP4、封面、时长、画幅 |
