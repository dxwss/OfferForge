# OfferForge：基于真实面经知识库与用户长期记忆的 Agent 面试训练系统设计文档

## 1. 项目概述

### 1.1 项目目的
OfferForge 是一个面向计算机求职者的智能面试训练系统。它的核心目标不是做一个普通的聊天机器人，而是构建一个**基于真实面经证据的个性化面试训练 Agent**，帮助用户完成以下任务：

- 从公开面经/社交帖子中沉淀真实的面试题、公司、岗位、轮次、流程与答案要点
- 构建面向求职场景的全局知识库（Global Interview KB）
- 在训练过程中持续记录用户表现，构建用户长期学习记忆（User Learning Memory）
- 基于用户目标公司、岗位、薄弱点与历史表现，动态生成学习计划、随机出题、模拟面试与复盘反馈
- 为每一道题提供“证据强度 / 出现置信度 / 目标相关度”的解释，避免黑盒出题

该项目面向两类价值：

1. **个人价值**：帮助项目作者系统化准备计算机面试，提升找工作效率
2. **项目价值**：作为一个可开源、可展示、可持续扩展的 AI Agent 项目，用于求职展示和工程能力证明

---

### 1.2 项目方法
OfferForge 的核心方法是：

1. **数据接入**：从公开来源或人工导入面经文本
2. **数据清洗**：去噪、去重、筛选面试相关内容
3. **信息抽取**：从帖子中抽取结构化的 Interview Event（公司、岗位、轮次、题目、流程、答案要点、证据）
4. **知识构建**：构建全局面试知识库，支持结构化检索、关键词检索、向量检索
5. **用户建模**：记录用户答题日志、技能状态、长期记忆
6. **智能体调度**：根据训练目标进行知识点规划、随机出题、模拟面试、评分和复盘
7. **闭环优化**：根据用户表现持续更新用户画像，动态调整下一轮出题与规划

---

### 1.3 项目最终效果
项目完成后，应达到以下效果：

- 用户输入目标（如：字节后端实习 / 算法岗 / 7 天冲刺）
- 系统自动生成学习计划
- 系统可按公司 / 岗位 / 轮次 / 知识点随机出题
- 系统可进行多轮模拟面试并追问
- 系统能对每道题展示：
  - 该题出现在哪些公司/轮次
  - 证据数量与证据来源
  - 出现置信度与目标相关度
- 系统可记录用户表现，识别薄弱点，持续调整题目分布
- 用户下次回来时，系统能基于历史表现继续训练，而不是重新开始

---

### 1.4 项目定位
本项目定位为：

> 一个“证据驱动的、支持用户长期记忆的、适合 AI coding 迭代开发”的模块化 Agent 项目。

因此在工程设计上，必须优先满足：

- 模块独立
- 输入输出稳定
- 适合 AI coding 逐模块生成代码
- 先跑通闭环，再逐步增强
- 全局知识与用户知识严格隔离

---

## 2. 非目标与边界

### 2.1 非目标
当前版本不以以下目标为优先：

- 不追求大规模商业化爬取平台数据
- 不追求首版就做复杂多 Agent 系统
- 不追求全岗位、全公司、全语言覆盖
- 不追求一次性完成前后端完整商业产品

### 2.2 合规边界
数据源必须作为“可替换接入层”处理。优先考虑：

- 合法 API
- 人工整理导入
- 用户自己上传的面经文本
- 明确允许抓取和使用的公开数据

本项目的核心竞争力应放在：

- 结构化抽取能力
- 检索与证据组织能力
- 用户长期记忆与训练闭环

而不是“全网抓取能力”。

---

## 3. 总体设计原则

### 3.1 模块单一职责
每个模块只解决一个明确问题，避免模块之间职责混乱。

### 3.2 协议先行
所有模块之间通过共享数据协议通信，禁止随意传字典和临时字段。

### 3.3 全局知识与用户知识隔离
- 全局知识库：记录客观面试知识
- 用户知识库：记录用户个人表现与长期记忆

两者分库存储，避免污染检索结果。

### 3.4 先模块化单体，后服务化
初期采用 monorepo + modular monolith，后续如果需要，再演化成微服务。

### 3.5 先闭环后增强
优先实现最小训练闭环：

导入数据 → 抽取面试事件 → 建知识库 → 出题 → 用户回答 → 评分 → 更新用户画像 → 继续出题

---

## 4. 系统总架构

```text
[Shared Schema]
      ↓
[Source Ingestion]
      ↓
[Cleaning & Canonicalization]
      ↓
[Interview IE Extraction]
      ↓
[Taxonomy & Entity Resolution]
      ↓
[Global Knowledge Builder]
      ↓
[Global Retrieval Service]

[User Modeling Service] ← [Assessment Engine] ← [Session Orchestrator] → [Global Retrieval Service]
                               ↑                        ↓
                          用户回答 / 日志           [Planning Engine]
                                                        ↓
                                                [API / Frontend]
```

说明：

- 左侧为离线知识构建流
- 右侧为在线训练会话流
- User Modeling 独立维护用户状态
- Planning Engine 负责决策，不直接做检索和评分
- Orchestrator 负责调度，不直接实现底层能力

---

## 5. 核心模块拆分

---

## 模块 0：Shared Schema / Contract Layer

### 5.0.1 作用
定义全项目通用数据结构，是所有模块的协议层。

### 5.0.2 目标
- 统一字段命名
- 降低模块耦合
- 为 AI coding 提供稳定输入输出定义

### 5.0.3 核心数据对象
建议至少定义以下对象：

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

### 5.0.4 示例字段建议

#### RawPost
- `post_id`
- `source_type`
- `source_url`
- `author_id_masked`
- `title`
- `content_raw`
- `created_at`
- `ingested_at`
- `metadata`

#### CleanedPost
- `post_id`
- `content_cleaned`
- `segments`
- `language`
- `is_relevant`
- `dedup_group_id`

#### InterviewEvent
- `event_id`
- `post_id`
- `company`
- `company_canonical`
- `role`
- `role_canonical`
- `round`
- `round_canonical`
- `question_text`
- `answer_hint`
- `topic_tags`
- `difficulty_level`
- `interview_stage_type`
- `event_time`
- `evidence_spans`
- `source_reliability_score`

#### UserAttempt
- `attempt_id`
- `user_id`
- `question_id`
- `session_id`
- `user_answer`
- `answer_duration_sec`
- `hint_used`
- `submitted_at`

#### UserSkillState
- `user_id`
- `topic`
- `correct_rate`
- `completeness_score`
- `depth_score`
- `communication_score`
- `followup_robustness_score`
- `forgetting_risk`
- `attempt_count`
- `last_practiced_at`

---

## 模块 1：Source Ingestion（数据接入模块）

### 5.1.1 作用
从不同来源获取原始帖子/面经文本，并统一转成 `RawPost`。

### 5.1.2 子模块建议
- `manual_import_connector`
- `reddit_connector`
- `zhihu_connector`
- `xiaohongshu_connector`
- `csv_json_importer`

### 5.1.3 输入
- 数据源配置
- 关键词
- 时间范围
- 导入文件路径

### 5.1.4 输出
- `RawPost[]`

### 5.1.5 只负责什么
- 获取原始文本
- 保存原始数据
- 记录来源和元信息

### 5.1.6 不负责什么
- 不做清洗
- 不做抽取
- 不做检索
- 不做向量化

### 5.1.7 与其他模块的依赖
- 输出给 Cleaning 模块
- 不依赖下游业务模块

---

## 模块 2：Cleaning & Canonicalization（清洗与初步标准化模块）

### 5.2.1 作用
将 `RawPost` 转化为适合抽取的 `CleanedPost`。

### 5.2.2 核心任务
- 去除噪声和广告
- 去除明显无关段落
- 格式标准化
- 分段
- 语言检测
- 相似内容去重
- 面试相关性初筛

### 5.2.3 输入
- `RawPost[]`

### 5.2.4 输出
- `CleanedPost[]`

### 5.2.5 建议子组件
- `text_normalizer`
- `relevance_filter`
- `segmenter`
- `deduplicator`

### 5.2.6 关键实现建议
- 第一版优先规则 + 轻量分类器
- 后续再引入 embedding 去重和 LLM relevance classification

---

## 模块 3：Interview IE Extraction（面试信息抽取模块）

### 5.3.1 作用
从 `CleanedPost` 中抽取结构化 `InterviewEvent`。

### 5.3.2 为什么重要
这是项目的核心技术模块之一。它决定后续是否能做：

- 公司/轮次统计
- 高频题挖掘
- 轮次模拟
- 基于证据的出题

### 5.3.3 子步骤建议

#### Step 1：面试帖识别
判断该文本是否为面试经验/题目相关文本

#### Step 2：实体抽取
抽取：
- 公司
- 岗位
- 轮次
- 时间
- 结果
- 题型

#### Step 3：题目抽取
识别每一个独立题目，形成 question-level event

#### Step 4：答案要点抽取
抽取作者提到的回答思路或要点，而非生成标准答案

#### Step 5：证据对齐
每个字段尽量绑定原文 span，便于后续解释与置信度计算

### 5.3.4 输入
- `CleanedPost[]`

### 5.3.5 输出
- `InterviewEvent[]`

### 5.3.6 关键设计要求
- 同一帖子可对应多个 InterviewEvent
- 每个 event 尽量是“最小可复用面试事实单元”
- 证据字段必须可追溯

---

## 模块 4：Taxonomy & Entity Resolution（知识标准化与实体归一模块）

### 5.4.1 作用
将抽取结果做实体统一与知识分类统一。

### 5.4.2 主要解决的问题
- “字节 / 字节跳动 / Bytedance”归一
- “后端 / 服务端 / Backend”归一
- “一面 / 技术一面 / phone screen”归一
- “OS / 操作系统 / 进程线程 / 虚拟内存”映射到统一知识树

### 5.4.3 输入
- `InterviewEvent[]`

### 5.4.4 输出
- 归一化后的 `InterviewEvent[]`
- 统一 taxonomy 标签

### 5.4.5 建议维护的字典
- 公司字典
- 岗位字典
- 轮次字典
- 知识点树
- 难度等级体系
- 题型体系

### 5.4.6 设计要求
- 支持人工纠错与增量更新
- 保留原始值和 canonical 值

---

## 模块 5：Global Knowledge Builder（全局知识构建模块）

### 5.5.1 作用
将标准化后的 InterviewEvent 构造成全局面试知识库。

### 5.5.2 核心目标
构建三层知识表示：

1. 结构化数据库
2. 关键词检索索引
3. 向量检索索引

### 5.5.3 建议产物

#### 结构化表
- 公司表
- 岗位表
- 题目表
- 轮次表
- 题目出现记录表
- 证据表
- 流程事件表

#### 检索文档
- question-level 文档
- company-round-topic 聚合文档
- 流程类文档
- 高频题总结文档

#### 检索索引
- 倒排索引
- 向量索引
- metadata filter 索引

### 5.5.4 输入
- 归一化后的 `InterviewEvent[]`

### 5.5.5 输出
- 全局知识库索引
- 可检索文档
- 结构化统计信息

### 5.5.6 重要说明
全局知识库不保存用户个人答题记录。

---

## 模块 6：Global Retrieval Service（全局知识检索模块）

### 5.6.1 作用
为上层 agent 提供“按目标、轮次、知识点、证据”检索全局面试知识的能力。

### 5.6.2 核心能力
- hybrid retrieval（关键词 + 向量）
- metadata filter（公司、岗位、轮次、topic、时间）
- rerank
- 证据组织与上下文打包

### 5.6.3 输入
- 目标公司
- 目标岗位
- 轮次
- topic
- 难度
- 用户当前模式（学习规划 / 刷题 / 模拟面试）

### 5.6.4 输出
- 候选题目列表
- 候选流程列表
- 每条结果的证据
- 相关统计信息
- 出现置信度特征

### 5.6.5 说明
该模块只负责检索与组织证据，不负责最终决策下一题。

---

## 模块 7：User Modeling Service（用户建模模块）

### 5.7.1 作用
维护用户长期学习状态，是项目个性化能力的核心。

### 5.7.2 子层设计

#### A. Attempt Log
记录每次练习行为

包含：
- 题目 ID
- 用户回答
- 提交时间
- 用时
- 是否用了提示
- 是否追问
- 分数
- 反馈摘要

#### B. Skill State
按 topic / round / company 聚合用户能力状态

包含：
- 正确率
- 完整性得分
- 深度得分
- 表达得分
- 追问鲁棒性得分
- 遗忘风险
- 最近趋势
- 最近练习时间

#### C. Personal Memory
作为用户个人 RAG，保存高价值文本记忆

包含：
- 代表性错误答案
- 高质量答案
- 容易混淆的知识点
- 历史追问记录
- 项目深挖表现片段

### 5.7.3 输入
- 用户练习记录
- 评分结果
- 会话历史

### 5.7.4 输出
- `UserProfile`
- `UserSkillState[]`
- `PersonalMemorySearchResult[]`

### 5.7.5 设计要求
- 结构化状态与向量记忆分开存
- 可解释地更新用户状态
- 保持增量更新能力

---

## 模块 8：Assessment & Grading Engine（评分与反馈模块）

### 5.8.1 作用
对用户回答进行多维评估，并生成可执行反馈。

### 5.8.2 评分维度建议
- Correctness（正确性）
- Completeness（完整性）
- Depth（深度）
- Communication（表达结构）
- Follow-up Robustness（追问鲁棒性）

### 5.8.3 输入
- 题目文本
- 推荐答案要点
- 证据上下文
- 用户回答
- 当前训练模式

### 5.8.4 输出
`EvaluationResult`：
- 总分
- 各维度评分
- 错误点
- 漏答点
- 改进建议
- 推荐复习知识点
- 用户画像更新建议

### 5.8.5 说明
评分模块可以多次迭代，不应与检索、出题强耦合。

---

## 模块 9：Question Selection & Planning Engine（出题与学习规划模块）

### 5.9.1 作用
根据目标与用户状态决定：
- 练什么
- 出什么题
- 是否追问
- 下一轮练什么
- 学习计划如何生成

### 5.9.2 子模块

#### A. Question Selector
负责“下一题是什么”

输入：
- 目标公司/岗位
- 当前 topic
- 检索候选题目
- 用户薄弱点
- 历史练习记录
- 难度控制参数

输出：
- `QuestionRecommendation`

#### B. Study Planner
负责生成未来训练计划

输出：
- `PracticePlan`

### 5.9.3 推荐打分逻辑
可设计为可解释公式：

`question_score = target_relevance × frequency_weight × weakness_weight × forgetting_risk × freshness_weight`

### 5.9.4 设计要求
- 决策必须可解释
- 支持规则优先，后续再加模型策略

---

## 模块 10：Session Orchestrator（会话智能体编排模块）

### 5.10.1 作用
调度整个在线训练流程，是系统的上层控制器。

### 5.10.2 负责的流程
- 识别用户当前意图
- 获取检索结果
- 获取用户状态
- 调用出题模块
- 发起模拟面试
- 调用评分模块
- 更新用户画像
- 决定是否继续追问
- 决定是否切换 topic / 难度 / 模式

### 5.10.3 支持的模式
- 知识点规划模式
- 随机刷题模式
- 模拟面试模式
- 复盘模式

### 5.10.4 设计要求
- 初版采用单 Orchestrator + 多工具调用
- 不建议一开始做多 Agent
- 保持流程图明确、状态流清晰

---

## 模块 11：API / Frontend Layer（接口与前端模块）

### 5.11.1 作用
为用户提供可交互入口，为开发者提供可调用接口。

### 5.11.2 API 能力建议
- 导入原始面经
- 触发知识构建
- 发起训练会话
- 获取下一题
- 提交回答
- 获取评分
- 获取学习计划
- 获取用户画像
- 查看题目证据

### 5.11.3 前端页面建议
- 首页 / 目标设置页
- 刷题页
- 模拟面试页
- 学习计划页
- 用户画像页
- 题目证据详情页

---

## 6. 数据库与存储设计建议

### 6.1 全局知识库相关表
建议使用关系型数据库保存结构化主数据：

- `raw_posts`
- `cleaned_posts`
- `interview_events`
- `question_atoms`
- `evidence_spans`
- `companies`
- `roles`
- `rounds`
- `topics`
- `question_occurrences`
- `knowledge_documents`

### 6.2 用户侧相关表
- `users`
- `practice_sessions`
- `user_attempts`
- `evaluation_results`
- `user_skill_states`
- `user_topic_mastery_snapshots`
- `user_memory_entries`

### 6.3 检索存储
- 倒排索引：用于关键词检索
- 向量索引：用于语义检索
- 结构化元数据索引：用于 filter

### 6.4 存储原则
- 原始数据、结构化数据、索引数据分层存放
- 用户数据与全局数据分库存储或逻辑隔离

---

## 7. 检索架构建议

### 7.1 必须采用 Hybrid Retrieval
不建议只做纯向量检索。

理由：
- 公司名、岗位名、轮次等适合关键词检索
- 题目变体、相近问法适合向量检索
- 两者结合更稳定

### 7.2 检索流程建议
1. metadata filter 预筛选
2. 关键词检索 top-k
3. 向量检索 top-k
4. 结果融合
5. rerank
6. 输出 evidence-packed context

### 7.3 检索结果必须返回的字段
- `question_id`
- `question_text`
- `company_distribution`
- `round_distribution`
- `evidence_count`
- `evidence_list`
- `occurrence_confidence`
- `target_relevance`
- `recommended_answer_hints`

---

## 8. 置信度与推荐分数设计

### 8.1 出现置信度（Occurrence Confidence）
表示一条题目“真实出现在某类面试中的证据强度”。

建议由以下因素构成：
- 独立来源数
- 来源一致性
- 是否明确提到公司/岗位/轮次
- 是否具有原文 evidence span
- 数据新鲜度
- 是否为第一手自述

### 8.2 目标相关度（Target Relevance）
表示该题对当前用户目标的重要程度。

建议由以下因素构成：
- 公司匹配度
- 岗位匹配度
- 轮次匹配度
- topic 匹配度
- 近年频率

### 8.3 最终推荐分数
可综合：
- 目标相关度
- 出现置信度
- 用户薄弱度
- 遗忘风险
- 题目新鲜度

---

## 9. 用户长期记忆设计

### 9.1 为什么不能只做用户 RAG
因为：
- 正确率、趋势、遗忘风险是结构化状态
- 历史优秀/错误回答才适合做向量记忆

### 9.2 最佳方案
用户侧采用三层记忆：

1. `Attempt Log`：时间序列行为记录
2. `Skill State`：结构化掌握度状态
3. `Personal Memory`：高价值文本向量记忆

### 9.3 用法
- 出题时：读取 Skill State
- 追问时：读取近期 Attempt Log
- 个性化反馈时：读取 Personal Memory

---

## 10. MVP 范围建议

### 10.1 MVP 目标
在最小范围内跑通训练闭环。

### 10.2 MVP 建议内容
- 支持手工导入 100~300 条面经文本
- 支持清洗与基本抽取
- 支持构建 question-level 知识库
- 支持按目标公司/岗位随机出题
- 支持用户提交回答
- 支持评分与用户画像更新
- 支持下次训练时基于用户画像继续出题

### 10.3 MVP 暂不做
- 不做全平台自动爬取
- 不做复杂多 Agent
- 不做完整移动端
- 不做复杂社交功能

---

## 11. 推荐开发顺序（适合 AI Coding）

### Phase 1：协议与最小闭环
优先实现：
- 模块 0 Shared Schema
- 模块 2 Cleaning
- 模块 3 Extraction
- 模块 5 Knowledge Builder
- 模块 7 User Modeling
- 模块 8 Assessment
- 模块 9 Planning
- 模块 10 Orchestrator

目标：
跑通“出题—答题—评分—更新画像—继续出题”闭环

### Phase 2：补齐标准化与接入
- 模块 1 Ingestion
- 模块 4 Taxonomy
- 模块 6 Retrieval 增强

### Phase 3：增强模拟面试与证据展示
- 追问策略
- 证据解释
- 出现置信度
- 更丰富的学习计划

### Phase 4：产品化外层
- API
- Web 前端
- 可视化画像页

---

## 12. 推荐仓库结构

```text
project/
  apps/
    api/
    web/
    worker/

  packages/
    shared_schema/
    source_ingestion/
    cleaning/
    extraction/
    taxonomy/
    knowledge_builder/
    retrieval/
    user_modeling/
    assessment/
    planning/
    orchestrator/

  prompts/
    extraction/
    grading/
    interviewing/
    planning/

  data/
    raw/
    processed/
    eval/

  scripts/
    ingest/
    build_index/
    run_eval/

  tests/
    unit/
    integration/
    e2e/
```

---

## 13. 每个模块的交付要求（便于 AI Coding）

为了便于 AI coding，每个模块都应至少包含：

1. `README.md`：模块职责、输入输出、依赖说明
2. `schema.py / types.ts`：模块用到的数据结构
3. `service.py / service.ts`：模块主服务实现
4. `interfaces.py / interfaces.ts`：上游下游接口定义
5. `tests/`：单元测试与集成测试
6. `config/`：模块配置
7. `prompts/`：若使用 LLM，则单独存放 prompt 模板

---

## 14. 给 AI Coding 的实现规则

### 14.1 代码生成原则
- 优先生成小模块，不一次性生成整个项目
- 先写接口，再写实现
- 先写 schema，再写业务逻辑
- 每个模块必须可独立测试
- 所有外部依赖必须通过配置注入

### 14.2 Prompt 组织原则
- 抽取 Prompt、评分 Prompt、追问 Prompt、规划 Prompt 分开管理
- 每个 Prompt 版本化
- Prompt 输出强制结构化

### 14.3 测试原则
- 抽取模块：必须有标注样本测试
- 检索模块：必须有 top-k 相关性测试
- 评分模块：必须有 rubric consistency 测试
- 编排模块：必须有会话流程 e2e 测试

### 14.4 不允许的实现方式
- 不允许模块间直接访问彼此内部数据库表
- 不允许通过随意 dict 传递字段
- 不允许把 orchestrator 写成一个大函数
- 不允许把用户历史和全局知识直接混在同一向量库

---

## 15. 评测体系建议

### 15.1 抽取评测
- 公司抽取准确率
- 岗位抽取准确率
- 轮次抽取准确率
- 题目切分准确率
- 证据对齐准确率

### 15.2 检索评测
- Recall@k
- Precision@k
- MRR / NDCG
- metadata filter 命中率

### 15.3 训练效果评测
- 用户薄弱点命中率
- 复习后同类题提升率
- 高风险 topic 覆盖率
- 用户主观满意度

---

## 16. 最终项目故事（用于简历 / README / 面试讲解）

OfferForge 不是一个简单的“面试问答机器人”，而是一个：

- 从非结构化面经文本中抽取结构化 Interview Event
- 构建证据驱动的全局面试知识库
- 结合用户长期记忆与掌握状态
- 动态规划训练路径与模拟面试流程
- 形成“检索—出题—回答—评分—更新画像—继续训练”的闭环系统

它体现的核心能力包括：

- LLM 信息抽取
- RAG / Hybrid Retrieval
- 用户长期记忆设计
- 智能体会话编排
- 评测与可解释推荐

---

## 17. 下一步实现建议

建议立刻开始的三个具体动作：

1. 先实现 `Shared Schema` 与 `InterviewEvent` 数据协议
2. 用人工整理的小规模面经数据跑通 Extraction → Knowledge Builder → Question Selector → Assessment 的闭环
3. 再逐步增加数据源、证据展示和模拟面试追问能力

---

## 18. 一句话总结

> OfferForge 的本质，是一个以真实面试证据为基础、以用户长期记忆为核心、以模块化 AI coding 为实现路径的个性化面试训练 Agent 系统。
