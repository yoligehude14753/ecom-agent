# EcomAgent — AI 智能电商自动化平台

> **开源自托管的 AI 跨境电商全链路自动化平台，自带 LLM 集成，数据不出本地。**

EcomAgent 将亚马逊 FBA/FBM 卖家的完整工作流自动化 —— 从选品到 Listing 生成，再到竞品监控和广告优化，全部在一个自托管平台中完成。无订阅费，数据不上传到任何第三方。

## 为什么选择 EcomAgent？

| | SaaS 工具（Jungle Scout、Helium 10…） | **EcomAgent** |
|---|---|---|
| 价格 | $99–$499/月 | **免费开源** |
| 数据归属 | 存储在对方服务器 | **保留在本地** |
| AI 模型 | 内置黑盒 | **自带 Key**（OpenAI / Claude / Gemini / Ollama）|
| 平台支持 | 固定 | **插件化适配器，可扩展** |
| 二次开发 | 不可能 | **Fork 随意改** |

## 功能模块

### AI 选品引擎
- 抓取亚马逊 Best Sellers / Movers & Shakers，覆盖 10+ 类目
- LLM 从三个维度打分：竞争度、利润空间、趋势热度
- 按综合评分筛选，快速找到机会品
- 结果可导出 CSV

### Listing 智能生成
- 输入关键词或 ASIN，一键生成完整 Listing
- 输出：标题 / 5 个卖点 / 产品描述 / 后台关键词 / A+ 内容草稿
- 字符数实时验证，符合亚马逊规范
- 支持 6 个市场语言：英 / 德 / 法 / 西 / 意 / 日

### Review 智能分析
- 爬取指定 ASIN 的全量 Review（可配置页数）
- LLM 提炼：用户痛点、高频好评点、改进建议
- 关键词词云 + 情感标签
- 自动生成 Listing 优化建议

### 竞品监控
- 添加任意 ASIN，定时追踪价格 / BSR 排名 / Review 数量 / 库存状态
- 可配置告警规则：降价幅度 %、BSR 变化 %、Review 突增
- Celery Beat 每小时自动快照
- 价格和 BSR 趋势折线图

### 广告优化
- 接入 Amazon Advertising API 拉取广告数据
- AI 分析每个关键词的 ACoS / ROAS / CTR
- 给出关键词出价建议（涨 / 降 / 暂停 / 新增 / 否定）
- 预算重新分配建议 + 预估月节省金额

## 快速启动

### 前提条件
- Docker + Docker Compose
- LLM API Key（OpenAI / Anthropic / Gemini）或本地 Ollama

### 1. 克隆并配置

```bash
git clone https://github.com/yoligehude14753/ecom-agent
cd ecom-agent
cp .env.example .env
```

编辑 `.env`，至少填写：

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

### 2. 一键启动

```bash
docker compose up -d
```

启动后访问：
- `http://localhost:3000` — 前端界面
- `http://localhost:8000/docs` — API 文档

### 3. 开始使用

访问 `http://localhost:3000`，从 Product Research 开始选品。

## 配置说明

所有配置均在 `.env` 文件中，详见 [`.env.example`](.env.example)。

### LLM 配置

```env
LLM_PROVIDER=openai          # openai | anthropic | gemini | ollama
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
```

支持 Ollama（本地离线模式）：

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1
```

### Amazon SP-API（可选，用于 Listing 上架）

前往 [Amazon 开发者门户](https://developer-docs.amazon.com/sp-api/) 申请权限。

### Amazon 广告 API（可选，用于广告优化）

前往 [Amazon Advertising API](https://advertising.amazon.com/API/) 申请权限。

## 本地开发

```bash
# 后端
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

## 扩展新平台

1. 新建 `backend/app/adapters/my_platform/`
2. 继承并实现 `app/adapters/base.py` 中的 `BasePlatformAdapter`
3. 在 `app/adapters/__init__.py` 中注册

所有 5 个模块会自动识别并使用新平台。

## 路线图

- [ ] Shopify 适配器
- [ ] eBay 适配器
- [ ] TEMU 适配器
- [ ] 供应链对接（1688 / 阿里国际站，等待 API 开放）
- [ ] 多用户管理 + 每用户 API Key 隔离
- [ ] Webhook 告警（Slack / 邮件 / 企业微信）
- [ ] 全模块 CSV 导出

## 贡献

欢迎提 PR 和 Issue。

## 许可证

MIT
