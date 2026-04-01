import unittest
from datetime import datetime, timezone

from packages.cleaning import CleaningRequest, CleaningService
from packages.shared_schema import RawPost, SourceType


class CleaningServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.service = CleaningService()
        self.now = datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc)

    def test_clean_normalizes_noise_and_segments_text(self) -> None:
        raw_post = RawPost(
            post_id="post_001",
            source_type=SourceType.MANUAL_IMPORT,
            source_url=None,
            author_id_masked="user_xxx",
            title="字节后端一面面经",
            content_raw=(
                "问了 TCP 三次握手为什么不是两次。\n"
                "点赞收藏不迷路，私信领取资料。\n\n"
                "后面又问了 Redis 持久化和项目难点。"
            ),
            created_at=None,
            ingested_at=self.now,
        )

        result = self.service.clean(CleaningRequest(raw_posts=[raw_post]))

        self.assertEqual(len(result.cleaned_posts), 1)
        cleaned_post = result.cleaned_posts[0]
        self.assertTrue(cleaned_post.is_relevant)
        self.assertEqual(cleaned_post.language, "zh")
        self.assertEqual(len(cleaned_post.segments), 2)
        self.assertNotIn("私信领取资料", cleaned_post.content_cleaned)
        self.assertEqual(cleaned_post.metadata["removed_line_count"], 1)

    def test_clean_drops_irrelevant_posts(self) -> None:
        raw_post = RawPost(
            post_id="post_002",
            source_type=SourceType.MANUAL_IMPORT,
            source_url=None,
            author_id_masked=None,
            title="今天吃了什么",
            content_raw="午饭不错，顺便散步，和面试没有关系。",
            created_at=None,
            ingested_at=self.now,
        )

        result = self.service.clean(CleaningRequest(raw_posts=[raw_post]))

        self.assertEqual(result.cleaned_posts, [])
        self.assertIn("post_002", result.dropped_post_ids)
        self.assertEqual(result.stats.dropped_posts, 1)

    def test_clean_deduplicates_equivalent_posts(self) -> None:
        raw_posts = [
            RawPost(
                post_id="post_003",
                source_type=SourceType.MANUAL_IMPORT,
                source_url=None,
                author_id_masked=None,
                title="后端一面面经",
                content_raw="问了 MySQL 索引 和 Redis 持久化。",
                created_at=None,
                ingested_at=self.now,
            ),
            RawPost(
                post_id="post_004",
                source_type=SourceType.MANUAL_IMPORT,
                source_url=None,
                author_id_masked=None,
                title="后端一面面经",
                content_raw="问了MySQL索引和Redis持久化！",
                created_at=None,
                ingested_at=self.now,
            ),
        ]

        result = self.service.clean(CleaningRequest(raw_posts=raw_posts))

        self.assertEqual(len(result.cleaned_posts), 1)
        self.assertEqual(result.dedup_primary_by_post_id["post_004"], "post_003")
        self.assertEqual(result.stats.duplicate_posts, 1)

    def test_clean_detects_english_posts(self) -> None:
        raw_post = RawPost(
            post_id="post_005",
            source_type=SourceType.MANUAL_IMPORT,
            source_url=None,
            author_id_masked=None,
            title="Backend interview notes",
            content_raw="The interviewer asked about Redis persistence and HTTP caching.",
            created_at=None,
            ingested_at=self.now,
        )

        result = self.service.clean(CleaningRequest(raw_posts=[raw_post]))

        self.assertEqual(len(result.cleaned_posts), 1)
        self.assertEqual(result.cleaned_posts[0].language, "en")


if __name__ == "__main__":
    unittest.main()
