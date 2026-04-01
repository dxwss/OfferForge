# shared_schema

`shared_schema` 是 OfferForge 的协议层模块，对齐设计文档中的“模块 0：Shared Schema / Contract Layer”。

## 模块职责

- 定义跨模块共享的数据契约
- 提供统一的序列化 / 反序列化能力
- 提供基础字段校验，防止模块间随意传递不稳定结构

## 输入输出

- 输入：Python 字典或模块内 dataclass 对象
- 输出：经过校验的共享协议对象，或可持久化/传输的字典

## 当前包含

- `schema.py`：核心协议对象
- `service.py`：统一序列化、反序列化与注册表服务
- `interfaces.py`：协议层接口定义
- `config/`：默认配置与校验范围
- `tests/`：模块级单元测试

## 核心对象

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

## 设计说明

- 当前实现只依赖 Python 标准库，方便在项目早期快速迭代
- 协议对象使用 dataclass，便于测试与阅读
- 分数、时长、字符区间等字段内置基本校验
- `SharedSchemaService` 负责统一管理协议对象注册和字典转换

## 使用示例

```python
from datetime import datetime, timezone

from packages.shared_schema.service import SharedSchemaService
from packages.shared_schema.schema import RawPost, SourceType

service = SharedSchemaService()

raw_post = RawPost(
    post_id="post_001",
    source_type=SourceType.MANUAL_IMPORT,
    source_url=None,
    author_id_masked="user_xxx",
    title="字节后端一面",
    content_raw="问了 TCP 三次握手和 Redis 持久化。",
    created_at=None,
    ingested_at=datetime.now(timezone.utc),
)

payload = service.serialize(raw_post)
reloaded = service.deserialize("RawPost", payload)
```
