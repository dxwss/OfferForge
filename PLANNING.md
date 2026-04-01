# OfferForge Planning

## 当前状态

基于 [`OfferForge_Design.md`](/g:/OfferForge/OfferForge_Design.md) 的需求梳理，当前仓库处于“设计已完成、实现刚起步”的阶段。

### 已完成

- [x] 读通整体设计文档，确认产品目标、系统边界、MVP 范围与推荐开发顺序
- [x] 确认项目以“协议先行、模块化单体、先跑闭环再增强”为核心工程原则
- [x] 完成模块 0 `Shared Schema / Contract Layer` 的首版实现
- [x] 为模块 0 补齐基础交付件：`README`、`schema.py`、`service.py`、`interfaces.py`、`config/`、`tests/`

### 进行中

- [ ] 暂无

### 未开始

- [ ] 模块 1 `Source Ingestion`
- [ ] 模块 2 `Cleaning & Canonicalization`
- [ ] 模块 3 `Interview IE Extraction`
- [ ] 模块 4 `Taxonomy & Entity Resolution`
- [ ] 模块 5 `Global Knowledge Builder`
- [ ] 模块 6 `Global Retrieval Service`
- [ ] 模块 7 `User Modeling Service`
- [ ] 模块 8 `Assessment & Grading Engine`
- [ ] 模块 9 `Question Selection & Planning Engine`
- [ ] 模块 10 `Session Orchestrator`
- [ ] 模块 11 `API / Frontend Layer`

## 已完成内容说明

### 模块 0 交付范围

模块 0 目前已经提供以下能力：

- 统一定义全局知识流和用户训练流共享的数据契约
- 覆盖设计文档中要求的核心对象：
  - `RawPost`
  - `CleanedPost`
  - `InterviewEvent`
  - `QuestionAtom`
  - `EvidenceSpan`
  - `InterviewRound`
  - `KnowledgeDocument`
  - `UserAttempt`
  - `UserProfile`
  - `UserSkillState`
  - `EvaluationResult`
  - `QuestionRecommendation`
  - `PracticePlan`
  - `PracticeSession`
- 提供统一的序列化、反序列化与基础校验服务
- 为后续模块保留稳定输入输出接口，避免模块间直接传递随意字典

### 当前实现假设

- 首版选择 Python 标准库实现协议层，优先保证零额外依赖、易测试、易迭代
- 当前只实现共享契约和通用校验，不提前耦合数据库、向量库、LLM SDK 或 Web 框架
- 各模块后续可以继续沿用 `packages/<module_name>/` 的组织方式扩展

## 推荐下一步

### Phase 1：最小训练闭环

按照设计文档建议，优先推进以下模块：

1. `模块 2 Cleaning`
2. `模块 3 Extraction`
3. `模块 5 Knowledge Builder`
4. `模块 7 User Modeling`
5. `模块 8 Assessment`
6. `模块 9 Planning`
7. `模块 10 Orchestrator`

目标是先跑通：

`导入样本 -> 清洗 -> 抽取 -> 建 question-level 知识 -> 出题 -> 回答 -> 评分 -> 更新画像 -> 继续出题`

### 最值得立刻实现的内容

1. 模块 2：把 `RawPost -> CleanedPost` 跑通，先用规则清洗与分段。
2. 模块 3：把 `CleanedPost -> InterviewEvent` 跑通，哪怕先做弱抽取版本。
3. 模块 5 + 9：先做基于规则和频次的 question-level 出题。
4. 模块 8 + 7：完成评分回写和用户技能状态更新，形成最小闭环。

## 风险与注意事项

- 不要在模块尚未稳定前引入复杂多 Agent 编排
- 不要把用户历史和全局知识混在同一存储或同一检索索引里
- 不要绕开 shared schema 直接在模块间传临时字段
- 抽取、评分、编排类模块都应补独立测试，避免后续协议漂移
