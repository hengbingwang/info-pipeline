# 内容获取参考

## 平台识别规则

根据 URL 字符串特征判断平台，按优先级顺序匹配：

| 优先级 | URL 特征 | 平台 | Agent-Reach 方案 | 信息来源值 |
|--------|---------|------|-----------------|-----------|
| 1 | 含 `mp.weixin.qq.com` | 微信公众号 | camoufox | 微信公众号 |
| 2 | 含 `x.com` 或 `twitter.com` | X / Twitter | xreach | X |
| 3 | 含 `youtube.com` 或 `youtu.be` | YouTube | yt-dlp 字幕 | YouTube |
| 4 | 含 `xiaoyuzhoufm.com` | 小宇宙 | 通用网页 | 小宇宙 |
| 5 | 其他所有 URL | 通用网页 | Jina Reader | 其他 |

---

## Agent-Reach 调用方式

Agent-Reach 是独立 skill，已安装在 openclaw，直接调用，勿重复实现。

### 微信公众号（camoufox 方案）

```
调用 Agent-Reach skill，指定方案：camoufox
输入：微信公众号文章 URL
输出：
  - title: 文章标题
  - content: 正文 markdown
  - author: 作者/公众号名称
  - publish_time: 发布时间
```

微信公众号需绕过防抓取机制，camoufox 方案通过伪装浏览器指纹实现。

### X / Twitter（xreach 方案）

```
调用 Agent-Reach skill，指定方案：xreach
输入：推文或用户主页 URL
输出：
  - content: 推文正文（含转推内容）
  - author: 用户名
  - created_at: 发布时间
  - media_urls: 媒体链接列表（如有）
```

### YouTube（yt-dlp 字幕方案）

```
调用 Agent-Reach skill，指定方案：yt-dlp 字幕
输入：YouTube 视频 URL
输出：
  - title: 视频标题
  - description: 视频描述
  - transcript: 字幕文本（优先中文 → 英文 → 自动生成）
  - duration: 时长（秒）
  - channel: 频道名称
```

无字幕的视频仅返回标题和描述。

### 小宇宙播客（通用网页方案）

```
调用 Agent-Reach skill，指定方案：通用网页
输入：小宇宙单集 URL
输出：
  - title: 节目标题
  - content: 节目简介 + Shownotes
  - publish_time: 发布时间
```

小宇宙无音频转录，仅抓取页面文字内容。

### 通用网页（Jina Reader 方案）

```
调用 Agent-Reach skill，指定方案：Jina Reader
输入：任意网页 URL
输出：
  - title: 页面标题
  - content: 清理后的正文 markdown（去除导航、广告等噪声）
  - url: 原始 URL
```

适用于文章、博客、技术文档类页面；对登录墙、付费墙内容无效。

---

## 返回内容处理

获取内容后，传给 AI 提炼步骤的格式：

```
平台：{platform}
标题：{title}
正文：{content}
作者：{author}（如有）
发布时间：{publish_time}（如有）
```

**正文截断**：正文超过 8000 字时，取前 6000 字 + "...（内容已截断）"用于 AI 提炼；深度分析模式尽量获取完整内容。

**语言检测**：统计正文中中文字符占比，低于 30% 视为非中文内容，深度分析时需额外创建翻译文档。

---

## 抓取失败处理

| 失败原因 | 处理方式 |
|----------|---------|
| 登录墙/付费墙 | 告知用户"该链接需要登录，无法自动获取内容"，跳过 |
| 超时（>30s） | 告知用户"内容获取超时"，跳过 |
| 返回内容为空 | 告知用户"未能获取有效内容"，跳过 |
| Agent-Reach 调用失败 | 记录错误，告知用户具体错误信息，跳过该链接 |
