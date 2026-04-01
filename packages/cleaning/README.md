# cleaning

`cleaning` 对应设计文档中的“模块 2：Cleaning & Canonicalization”。

## 模块职责

- 将 `RawPost` 转化为适合后续抽取的 `CleanedPost`
- 做第一版规则化文本清洗与初步标准化
- 在不引入数据库、向量库、LLM 的前提下，提供稳定可测试的输入输出

## 输入

- `CleaningRequest`
  - `raw_posts: list[RawPost]`
  - `deduplicate: bool`
  - `drop_irrelevant: bool`
  - `min_relevance_score: float`

## 输出

- `CleaningResult`
  - `cleaned_posts: list[CleanedPost]`
  - `dropped_post_ids: list[str]`
  - `dedup_primary_by_post_id: dict[str, str]`
  - `warnings: list[str]`
  - `stats: CleaningStats`

## 当前实现范围

- 文本标准化
- 噪声/广告行过滤
- 面试相关性初筛
- 规则式语言检测
- 段落切分
- 基于规范化指纹的精确去重

## 当前不做

- embedding 去重
- LLM relevance classification
- 存储层接入
- 下游抽取逻辑
