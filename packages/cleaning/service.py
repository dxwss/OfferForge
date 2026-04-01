import re
import string
from collections import Counter
from typing import Iterable, List

from packages.shared_schema import CleanedPost, RawPost, TextSegment

from .schemas import CleaningRequest, CleaningResult, CleaningStats


class CleaningService:
    """Rule-based text cleaning and canonicalization for interview posts."""

    _NOISE_PATTERNS = tuple(
        re.compile(pattern, re.IGNORECASE)
        for pattern in [
            r"点赞|点个赞|收藏|转发",
            r"关注|私信|进群|加群|加v|加微|vx|vx[:：]?",
            r"公众号|小红书|二维码|扫码",
            r"内推|代投|简历修改|付费咨询",
            r"广告|推广|恰饭|合作",
        ]
    )
    _RELEVANT_PATTERNS = tuple(
        re.compile(pattern, re.IGNORECASE)
        for pattern in [
            r"面经|面试|一面|二面|三面|hr面|终面",
            r"笔试|机试|在线测评|online assessment|\boa\b",
            r"算法题|手撕|八股|反问|项目经历|系统设计",
            r"interview|backend|frontend|sde|intern",
        ]
    )

    def __init__(self) -> None:
        self._noise_patterns = tuple(self._NOISE_PATTERNS)
        self._relevant_patterns = tuple(self._RELEVANT_PATTERNS)

    def clean(self, request: CleaningRequest) -> CleaningResult:
        stats = CleaningStats(total_posts=len(request.raw_posts))
        result = CleaningResult(stats=stats)
        seen_fingerprints = {}

        for raw_post in request.raw_posts:
            cleaned_text, removed_lines = self._normalize_and_filter_text(raw_post)
            relevance_score = self._score_relevance(raw_post.title or "", cleaned_text)
            is_relevant = relevance_score >= request.min_relevance_score

            if request.drop_irrelevant and not is_relevant:
                result.dropped_post_ids.append(raw_post.post_id)
                result.warnings.append("Dropped irrelevant post: %s" % raw_post.post_id)
                stats.dropped_posts += 1
                continue

            if is_relevant:
                stats.relevant_posts += 1

            dedup_group_id = None
            if request.deduplicate:
                fingerprint = self._fingerprint(raw_post.title or "", cleaned_text)
                if fingerprint in seen_fingerprints:
                    primary_post_id = seen_fingerprints[fingerprint]
                    result.dedup_primary_by_post_id[raw_post.post_id] = primary_post_id
                    result.dropped_post_ids.append(raw_post.post_id)
                    result.warnings.append(
                        "Dropped duplicate post: %s -> %s" % (raw_post.post_id, primary_post_id)
                    )
                    stats.duplicate_posts += 1
                    stats.dropped_posts += 1
                    continue
                seen_fingerprints[fingerprint] = raw_post.post_id
                dedup_group_id = raw_post.post_id

            segments = self._segment_text(cleaned_text)
            language = self._detect_language(cleaned_text)
            cleaned_post = CleanedPost(
                post_id=raw_post.post_id,
                content_cleaned=cleaned_text,
                segments=segments,
                language=language,
                is_relevant=is_relevant,
                dedup_group_id=dedup_group_id,
                metadata={
                    "source_type": raw_post.source_type.value,
                    "source_url": raw_post.source_url,
                    "removed_line_count": removed_lines,
                    "relevance_score": round(relevance_score, 4),
                    "original_title": raw_post.title,
                },
            )
            result.cleaned_posts.append(cleaned_post)
            stats.cleaned_posts += 1

        return result

    def _normalize_and_filter_text(self, raw_post: RawPost) -> tuple[str, int]:
        raw_text = "\n".join(part for part in [raw_post.title or "", raw_post.content_raw] if part)
        text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t\f\v]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        filtered_lines: List[str] = []
        removed_lines = 0
        for raw_line in text.split("\n"):
            line = raw_line.strip()
            if not line:
                if filtered_lines and filtered_lines[-1] != "":
                    filtered_lines.append("")
                continue
            if self._is_noise_line(line):
                removed_lines += 1
                continue
            filtered_lines.append(line)

        cleaned = "\n".join(filtered_lines).strip()
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned or raw_post.content_raw.strip(), removed_lines

    def _is_noise_line(self, line: str) -> bool:
        lowered = line.lower()
        for pattern in self._noise_patterns:
            if pattern.search(lowered):
                return True
        return False

    def _score_relevance(self, title: str, cleaned_text: str) -> float:
        combined_text = " ".join(part for part in [title, cleaned_text] if part).strip()
        if not combined_text:
            return 0.0

        matches = sum(1 for pattern in self._relevant_patterns if pattern.search(combined_text))
        keyword_score = min(matches / 4.0, 1.0)
        topic_density = min(self._count_topic_tokens(combined_text) / 6.0, 1.0)
        length_score = 0.2 if len(combined_text) >= 40 else 0.0
        return min(keyword_score * 0.6 + topic_density * 0.2 + length_score, 1.0)

    def _count_topic_tokens(self, text: str) -> int:
        tokens = re.findall(
            r"面试|面经|算法|八股|项目|系统设计|redis|mysql|tcp|http|线程|进程|数据库|network|backend",
            text,
            flags=re.IGNORECASE,
        )
        return len(tokens)

    def _segment_text(self, cleaned_text: str) -> List[TextSegment]:
        segments: List[TextSegment] = []
        cursor = 0
        for block in self._iter_blocks(cleaned_text):
            start_char = cleaned_text.find(block, cursor)
            end_char = start_char + len(block)
            cursor = end_char
            segment_type = "bullet" if block.startswith(("-", "*", "1.", "2.", "3.")) else "paragraph"
            segments.append(
                TextSegment(
                    text=block,
                    start_char=start_char,
                    end_char=end_char,
                    segment_type=segment_type,
                )
            )
        if not segments:
            segments.append(
                TextSegment(
                    text=cleaned_text,
                    start_char=0,
                    end_char=len(cleaned_text),
                    segment_type="paragraph",
                )
            )
        return segments

    def _iter_blocks(self, cleaned_text: str) -> Iterable[str]:
        for block in re.split(r"\n\s*\n", cleaned_text):
            normalized = block.strip()
            if normalized:
                yield normalized

    def _detect_language(self, text: str) -> str:
        chinese_count = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
        latin_count = sum(1 for char in text if char.isascii() and char.isalpha())
        if chinese_count:
            if latin_count and latin_count > chinese_count * 1.5:
                return "mixed"
            return "zh"
        if latin_count:
            return "en"
        return "unknown"

    def _fingerprint(self, title: str, cleaned_text: str) -> str:
        combined = " ".join(part for part in [title, cleaned_text] if part).lower()
        combined = re.sub(r"\s+", "", combined)
        punctuation_table = str.maketrans("", "", string.punctuation + "，。！？；：、“”‘’（）《》【】")
        combined = combined.translate(punctuation_table)
        counter = Counter(combined)
        return "".join("%s%s" % (char, count) for char, count in sorted(counter.items()))
