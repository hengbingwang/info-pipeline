---
name: info-pipeline
description: Use when processing information links sent to openclaw bot in Feishu - collecting content into Bitable or running deep analysis on marked records. Triggers on URL messages or "执行深度分析" keyword.
---

# info-pipeline

## Overview

Automated information processing pipeline for openclaw bot. Two modes:
- **收集模式**: User sends URL → fetch content → deduplicate → write to Feishu Bitable
- **深度分析模式**: Scheduled or manual trigger → process all "待沉淀" records → create Feishu Docs

All API credentials are read from environment variables. See `references/feishu-api.md` for full API reference.

## Trigger Detection

```
Message contains URL?
  YES → 收集模式
Message is scheduled task OR contains "执行深度分析"?
  YES → 深度分析模式
```

---

## 模式一：收集模式

**触发**：消息中包含 URL

### 工作流

1. **识别平台** — 根据 URL 特征匹配平台（规则见 `references/content-fetch.md`）
2. **抓取内容** — 调用 Agent-Reach 对应方案获取正文（方案见 `references/content-fetch.md`）
3. **去重检查** — 查询 Bitable，过滤条件：`信息链接 = <URL>`
   - 已存在 → 回复用户"该链接已录入，标题：{标题}"，终止流程
   - 不存在 → 继续
4. **AI 提炼** — 基于正文生成：
   - `信息标题`：简洁准确的标题（≤30字）
   - `信息核心摘要`：核心内容摘要（≤200字）
   - `信息标签`：从 [AI应用, AI技术, 产品, 商业, 技术, 其他] 多选
   - `信息类型`：从 [访谈, 产品分析, 技术解读, 行业观察, 教程] 单选
   - `信息质量等级`：S/A/B/C 初步评估，默认 B
5. **写入 Bitable** — 调用新增记录 API（见 `references/feishu-api.md`），固定字段：
   - `信息来源`：根据平台自动选择
   - `信息链接`：原始 URL
   - `信息记录时间`：当前时间戳（毫秒）
   - `信息沉淀`：默认"不沉淀"
6. **回复确认** — 格式：
   ```
   已录入：{信息标题}
   摘要：{信息核心摘要前100字}...
   标签：{标签列表} | 类型：{类型} | 质量：{等级}
   ```

### 平台与来源映射

| URL 特征 | 信息来源值 |
|----------|-----------|
| `mp.weixin.qq.com` | 微信公众号 |
| `x.com` / `twitter.com` | X |
| `youtube.com` / `youtu.be` | YouTube |
| `xiaoyuzhoufm.com` | 小宇宙 |
| 其他 | 其他 |

---

## 模式二：深度分析模式

**触发**：定时任务 或 消息含"执行深度分析"

### 工作流

1. **查询待处理记录** — 过滤 Bitable：`信息沉淀 = "待沉淀"`（API 见 `references/feishu-api.md`）
2. 若无记录 → 回复"暂无待沉淀内容，无需处理"，终止
3. **对每条记录依次执行**：
   a. 重新抓取原文（调用 Agent-Reach，同收集模式）
   b. 调用深度分析 prompt（见 `references/analysis-prompt.md`）
   c. 在飞书文档空间创建新文档：
      - 标题 = `信息标题`
      - 内容 = 深度分析结果
   d. **若原文非中文**：另创建翻译文档
      - 标题 = `[译] {信息标题}`
      - 内容 = 逐段中文对照翻译
   e. 更新 Bitable 对应行（API 见 `references/feishu-api.md`）：
      - `信息沉淀` → "已沉淀"
      - `深度分析文档` → 新建文档 URL
      - `翻译文档` → 翻译文档 URL（如有，否则留空）
4. **汇总回复**：
   ```
   深度分析完成，共处理 N 条：
   1. {标题} → {文档链接}
   2. ...
   ```

---

## Bitable 字段完整定义

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 信息标题 | 文本 | AI 自动提取，≤30字 |
| 信息来源 | 单选 | 微信公众号 / X / YouTube / 小宇宙 / 其他 |
| 信息链接 | 链接 | 去重主键 |
| 信息记录时间 | 日期时间 | 毫秒时间戳 |
| 信息核心摘要 | 长文本 | ≤200字 |
| 信息标签 | 多选 | AI应用 / AI技术 / 产品 / 商业 / 技术 / 其他 |
| 信息类型 | 单选 | 访谈 / 产品分析 / 技术解读 / 行业观察 / 教程 |
| 信息质量等级 | 单选 | S / A / B / C（默认 B） |
| 信息沉淀 | 单选 | 不沉淀 / 待沉淀 / 已沉淀（默认"不沉淀"） |
| 深度分析文档 | URL | 深度分析完成后自动填写 |
| 翻译文档 | URL | 非中文内容翻译文档 URL |

---

## 环境变量

| 变量名 | 用途 |
|--------|------|
| `FEISHU_APP_ID` | 飞书应用 ID |
| `FEISHU_APP_SECRET` | 飞书应用密钥 |
| `FEISHU_BITABLE_APP_TOKEN` | 多维表格 app_token |
| `FEISHU_BITABLE_TABLE_ID` | 具体表格 table_id |
| `FEISHU_DOCS_FOLDER_TOKEN` | 文档存放目录 folder_token |

---

## References

- `references/feishu-api.md` — Feishu Bitable & Docs API 完整参考（含认证、CRUD、文档创建）
- `references/content-fetch.md` — 平台识别规则 + Agent-Reach 调用方式
- `references/analysis-prompt.md` — 深度分析 prompt（待用户提供）
