# info-pipeline

openclaw 机器人的资讯处理自动化 skill，实现从链接收集到深度分析的全流程。

## 功能

### 收集模式
在飞书向 openclaw 发送链接 → 自动抓取内容 → AI 提炼摘要 → 去重录入飞书多维表格

### 深度分析模式
手动发送"执行深度分析"或定时触发 → 处理所有标记为"待沉淀"的记录 → 生成飞书文档

## 文件结构

```
info-pipeline/
├── SKILL.md                    # Skill 主文件，包含触发规则和完整工作流
├── get_field_options.py        # 查询 Bitable 单选/多选字段选项 ID 的工具脚本
└── references/
    ├── feishu-api.md           # 飞书 Bitable & Docs API 完整参考
    ├── content-fetch.md        # 平台识别规则 + Agent-Reach 调用方式
    └── analysis-prompt.md      # 深度分析 prompt（待补充）
```

## 环境变量

在 openclaw 中配置以下变量：

| 变量名 | 说明 |
|--------|------|
| `FEISHU_APP_ID` | 飞书应用 ID |
| `FEISHU_APP_SECRET` | 飞书应用密钥 |
| `FEISHU_BITABLE_APP_TOKEN` | 多维表格 app_token |
| `FEISHU_BITABLE_TABLE_ID` | 具体表格 table_id |
| `FEISHU_DOCS_FOLDER_TOKEN` | 文档存放目录 folder_token |

## 多维表格字段设计

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 信息标题 | 文本 | AI 自动提取 |
| 信息来源 | 单选 | 微信公众号 / X / YouTube / 小宇宙 / 其他 |
| 信息链接 | 链接 | 去重主键 |
| 信息记录时间 | 日期时间 | 自动填写 |
| 信息核心摘要 | 长文本 | 200 字以内 |
| 信息标签 | 多选 | AI应用 / AI技术 / 产品 / 商业 / 技术 / 其他 |
| 信息类型 | 单选 | 访谈 / 产品分析 / 技术解读 / 行业观察 / 教程 |
| 信息质量等级 | 单选 | S / A / B / C |
| 信息沉淀 | 单选 | 不沉淀 / 待沉淀 / 已沉淀 |
| 深度分析文档 | URL | 分析完成后自动填写 |
| 翻译文档 | URL | 非中文内容自动创建 |

## 安装

将整个目录放到 Claude Code 的 skill 目录下：

```bash
cp -r info-pipeline ~/.claude/skills/
```

## 依赖

- openclaw 机器人（飞书应用）
- Agent-Reach skill（独立安装，负责各平台内容抓取）

## 待补充

- [ ] `references/analysis-prompt.md` 正式 prompt 内容
