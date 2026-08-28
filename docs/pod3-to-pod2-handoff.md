# Pod 3 → Pod 2 交接说明

## 固定项目上下文

- `project_id`: `dreampipe-demo-fuzhou-sanfangqixiang-niulai-20260828`
- MVP：1 个商品、15 秒、9:16、3 个镜头、1 个视频模型、1 条 CTA
- 视频模型：`happyhorse-1.1-i2v`

## Pod 2 需要提供的文件

请继续维护仓库已有的共享合同，不要改名或新增运行时专属字段：

- `shared/project_bible.json`：必须通过 `shared/schemas/project_bible.schema.json`
- `shared/shots.json`：必须通过 `shared/schemas/shots.schema.json`

两个文件的 `project_id` 必须一致，并与 `shared/brief.json` 相同。Shot ID 一旦发布即稳定；重试只增加 generation attempt，不改变 Shot ID。

## Pod 3 已提供的运行时接口

- `src/dreampipe/adapters/video_provider.py`：Provider 协议
- `src/dreampipe/adapters/bailian_happyhorse_adapter.py`：HappyHorse-1.1-I2V 百炼适配器
- `schemas/v1/dreampipe-job.schema.json`：LangGraph 运行时 Job 合同
- `run_pipeline.py`：Mock/HappyHorse 入口

Pod 2 的 Project Bible 和 Shot List 会由后续编排节点映射到运行时 Job；Pod 3 不会覆盖 Pod 2 的创意字段。Prompt 编译器只补充模型语法，并保留产品不变量、品牌规则、镜头时长和连续性约束。

## HappyHorse 调用约束

真实调用需要环境变量 `BAILIAN_API_KEY`，并且商品参考图必须是百炼可访问的 `http(s)` URL。API Key、私有素材、本地 `.env`、`.libtv/` 和生成输出不得提交。

## 验证

```powershell
$env:PYTHONPATH = ".venv_lib;src"
python -m unittest discover -s tests -v
python run_pipeline.py shared/brief.json --provider mock
```

当前 Mock 流程会验证 QA 失败 → Prompt 修复 → 单镜头重试 → 完成的闭环。
