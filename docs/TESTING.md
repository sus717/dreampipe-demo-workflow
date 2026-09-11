# DreamPipe 集成测试版

在线入口：https://sus717.github.io/dreampipe-demo-workflow/

## 已接通的数据链路

`shared/brief.json` → Brief normalizer → `shared/project_bible.json` / `shared/shots.json` → LangGraph Mock → frontend status contract → React 控制台。

`scripts/export_web_demo.py` 在构建时运行 Python Mock 流水线，校验合同并导出四个状态。页面回放这些状态，不连接在线 Python 服务。导出器只在内存中加入显式演示素材，不修改原始 Brief，不调用收费模型。S03 首次 QA 失败，第二次通过，其他镜头不重生成。

## 建议手动测试

1. 修改创意文本，确认前置检查分数更新；文本只用于规则预检，尚不生成新 Brief 或分镜。
2. 切换资产门禁，确认显示等待资产。
3. 点击运行全流程，观察生成、局部重试和完成状态；所有费用和 QA 均为模拟数据。
4. 在局部重试状态点击执行 S03 Retry，确认只有 S03 达到 Attempt 2。
5. 打开“测试与实现清单”，查看共享分镜、真实 Mock 事件和未实现功能。
6. 下载当前测试数据，检查项目 ID、分镜和 QA 结果。
7. 预览区只有概念图；打开分镜原图可用，视频播放按钮禁用。

## 尚未实现或尚未联调

| 功能 | 当前状态 |
| --- | --- |
| 自然语言创意 → Brief / 新分镜 | 只有前端规则评分与固定创意合同 |
| 素材上传与审核 | 没有上传服务；共享 Brief 的参考素材为空 |
| GLM Prompt 编译 | 有 Python 适配器，网页未调用，真实服务未在本次测试 |
| HappyHorse 视频生成 | 有 Python 适配器，网页未调用，真实服务未在本次测试 |
| Vision QA | 有 Python 实现及隔离测试，网页使用 Mock 分数 |
| HTTP / WebSocket 任务服务 | 尚未实现；已有浏览器 WebSocket 边界未连接页面 |
| 配音、音乐、字幕、最终 MP4 | 尚未实现；assembler 仅生成 Mock manifest，真实图路径也复用了它 |
| 播放 / 视频下载 | 没有真实成片，仅提供概念图和测试 JSON |
| 预算强制限制、真实计费 | 仅展示模拟金额，没有执行级成本门禁 |
| 登录、持久化、多人任务 | 尚未实现 |

前端“爆款概率”是规则启发分，未经统计校准，不能作为真实概率。

## 本地验证

在仓库根目录（Python 3.11+ / Node 22）：

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python -m unittest discover -s tests -v
.\.venv\Scripts\python scripts/export_web_demo.py
cd web
npm ci
npm test
npm run build
npx playwright install chrome
npm run test:e2e
npm run dev -- --port 4279 --strictPort
```

前端测试使用独立的 4279 端口，不复用其他项目服务。网页构建使用相对路径，支持 GitHub Pages 仓库子目录。推送默认分支 `feat/dreampipe-ui-control-tower` 后，Pages workflow 校验 Python、导出状态、测试并构建前端，再发布静态站点。

真实生成需要后续部署 Python 服务并配置服务端密钥。不要将密钥写入 `VITE_*` 或前端源码。
