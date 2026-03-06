# 飞书 API 参考

凭证全部读取环境变量，不硬编码。

---

## 1. 获取 tenant_access_token

每次调用业务 API 前先获取 token（有效期 2 小时，建议缓存）。

```http
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
Content-Type: application/json

{
  "app_id": "${FEISHU_APP_ID}",
  "app_secret": "${FEISHU_APP_SECRET}"
}
```

**响应：**
```json
{
  "code": 0,
  "msg": "ok",
  "tenant_access_token": "t-xxx",
  "expire": 7200
}
```

后续请求 Header：`Authorization: Bearer {tenant_access_token}`

---

## 2. Bitable — 查询记录

```http
GET https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records
Authorization: Bearer {token}
```

**Query 参数：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `filter` | 过滤条件 | `CurrentValue.[信息沉淀]="待沉淀"` |
| `page_size` | 每页记录数，最大 500 | `500` |
| `page_token` | 翻页 token | 上次响应返回 |
| `field_names` | 指定返回字段，逗号分隔 | `信息标题,信息链接` |

**过滤器示例：**
```
# 查询"待沉淀"记录
filter=CurrentValue.[信息沉淀]="待沉淀"

# 去重检查——查询特定 URL
filter=CurrentValue.[信息链接]="https://example.com/article"
```

**响应结构：**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "record_id": "recXXXXXX",
        "fields": {
          "信息标题": "标题文本",
          "信息链接": {"link": "https://...", "text": "https://..."},
          "信息沉淀": {"id": "optXXX", "text": "待沉淀"}
        }
      }
    ],
    "page_token": "...",
    "has_more": false,
    "total": 5
  }
}
```

**翻页处理（伪代码）：**
```python
records, page_token = [], None
while True:
    params = {"filter": filter_expr, "page_size": 500}
    if page_token:
        params["page_token"] = page_token
    resp = GET /records, params=params
    records.extend(resp.data.items)
    if not resp.data.has_more:
        break
    page_token = resp.data.page_token
```

---

## 3. Bitable — 新增记录

```http
POST https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records
Authorization: Bearer {token}
Content-Type: application/json

{
  "fields": {
    "信息标题": "文章标题",
    "信息来源": {"id": "optXXXXXX"},
    "信息链接": {"link": "https://...", "text": "https://..."},
    "信息记录时间": 1700000000000,
    "信息核心摘要": "摘要内容...",
    "信息标签": [{"id": "optXXX"}, {"id": "optYYY"}],
    "信息类型": {"id": "optZZZ"},
    "信息质量等级": {"id": "optAAA"},
    "信息沉淀": {"id": "optBBB"}
  }
}
```

**字段类型写入格式：**

| 字段类型 | 写入格式 |
|----------|---------|
| 文本/长文本 | `"字符串"` |
| 单选 | `{"id": "选项ID"}` 或 `{"text": "选项名"}` |
| 多选 | `[{"id": "选项ID1"}, {"id": "选项ID2"}]` |
| 链接 | `{"link": "https://...", "text": "显示文本"}` |
| 日期时间 | 毫秒时间戳（整数） |
| URL | `"https://..."` |

> 单选/多选推荐用选项 ID 而非 text，避免名称不匹配写入失败。

**获取字段及选项 ID：**
```http
GET https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields
Authorization: Bearer {token}
```

响应中 `type=3`（单选）/ `type=4`（多选）字段的 `property.options` 包含各选项的 `id` 和 `name`。

---

## 4. Bitable — 更新记录

```http
PUT https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "fields": {
    "信息沉淀": {"id": "opt已沉淀ID"},
    "深度分析文档": "https://...",
    "翻译文档": "https://..."
  }
}
```

只传需要更新的字段，其余保持不变。

---

## 5. 飞书文档 — 创建文档

```http
POST https://open.feishu.cn/open-apis/docx/v1/documents
Authorization: Bearer {token}
Content-Type: application/json

{
  "folder_token": "${FEISHU_DOCS_FOLDER_TOKEN}",
  "title": "文档标题"
}
```

**响应：**
```json
{
  "code": 0,
  "data": {
    "document": {
      "document_id": "docXXXXXX",
      "title": "文档标题"
    }
  }
}
```

文档 URL：`https://bytedance.feishu.cn/docx/{document_id}`

---

## 6. 飞书文档 — 写入内容（块操作）

### 在文档末尾追加块

```http
POST https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children
Authorization: Bearer {token}
Content-Type: application/json

{
  "children": [
    {
      "block_type": 3,
      "heading1": {
        "elements": [{"text_run": {"content": "核心观点"}}]
      }
    },
    {
      "block_type": 2,
      "text": {
        "elements": [{"text_run": {"content": "正文段落内容..."}}]
      }
    }
  ],
  "index": -1
}
```

**常用 block_type：**

| block_type | 说明 |
|-----------|------|
| 2 | Text（普通段落） |
| 3 | Heading1 |
| 4 | Heading2 |
| 5 | Heading3 |
| 12 | BulletedList（无序列表） |
| 13 | OrderedList（有序列表） |
| 22 | Divider（分割线） |

一次请求最多追加 50 个块。将深度分析结果按段落拆分，标题用 Heading 块，正文用 Text 块，批量写入。

---

## 错误处理

| code | 含义 | 处理 |
|------|------|------|
| 0 | 成功 | — |
| 99991400 | token 无效或过期 | 重新获取 token |
| 99991663 | 权限不足 | 检查应用权限配置 |
| 1254002 | 记录不存在 | 检查 record_id |
| 1254301 | 字段值格式错误 | 检查写入格式 |

所有接口 HTTP 状态均为 200，通过 `code` 字段判断成功/失败。
