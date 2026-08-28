# Pod 3 → Pod 2：创意文件接入约定

## 固定项目上下文

- `project_id`：`dreampipe-demo-fuzhou-sanfangqixiang-niulai-20260828`
- MVP：1 个主题、15 秒、9:16、3 个镜头、1 个视频模型、1 条 CTA
- 视频模型：`happyhorse-1.1-i2v`

## Pod 2 交付

请提交并维护：

- `shared/project_bible.json`：通过 `shared/schemas/project_bible.schema.json`
- `shared/shots.json`：通过 `shared/schemas/shots.schema.json`

文件的 `project_id` 必须一致。镜头的 `shot_id` 发布后不得在重试时改变。

## 职责边界

Pod 2 输出模型无关的创意信息：故事、角色、场景、视觉规则、镜头、时长、动作、连续性和 QA 目标。Pod 3 将其编译为 HappyHorse 专用 Prompt，并负责生成、状态、QA、重试和合成。

`prompt`、`negative_prompt`、`model_hint` 属于模型专用字段，不应成为 Pod 2 的必填分镜交付。最终共享 Schema 须经 1/2/3 号位共同冻结后再修改。

## 真实调用限制

真实生成需要可公开访问的 `http(s)` 参考图片 URL。API Key、私有素材、本地 `.env`、`.libtv/` 和生成输出不得提交。
