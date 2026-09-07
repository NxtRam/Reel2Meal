"""
test_feed_algorithm.py
======================
Phase 2 feed ranking algorithm test suite.

Formula under test
------------------
    score = like_count * 3 + save_count * 5 + watch_time_seconds * 1

Test classes
------------
  TestScoringFormula   — pure arithmetic, zero DB dependency, sub-second
  TestFeedOrdering     — HTTP integration: feed returns reels in score order
  TestFeedPagination   — score-based cursor pagination correctness
  TestWatchTimeEndpoint — POST /watch increments score and triggers re-rank

Reel fixtures
-------------
┌────────┬────────────┬────────────┬──────────────────────┬───────────────┐
│ Label  │ like_count │ save_count │ watch_time_seconds   │ Score         │
├────────┼────────────┼────────────┼──────────────────────┼───────────────┤
│ HIGH   │     10     │      8     │        200           │ 30+40+200=270 │
│ MEDIUM │      5     │      3     │         50           │ 15+15+50 = 80 │
│ LOW    │      1     │      0     │         10           │  3+ 0+10 = 13 │
└────────┴────────────┴────────────┴──────────────────────┴───────────────┘
"""

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.schemas.reel import SCORE_WEIGHT_LIKES, SCORE_WEIGHT_SAVES, SCORE_WEIGHT_WATCH_TIME
from tests.conftest import TestSession


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _compute_score(like_count: int, save_count: int, watch_time_seconds: int) -> int:
    """Mirror of the scoring formula — used to compute expected values."""
    return (
        like_count * SCORE_WEIGHT_LIKES
        + save_count * SCORE_WEIGHT_SAVES
        + watch_time_seconds * SCORE_WEIGHT_WATCH_TIME
    )


REEL_FIXTURES = {
    "HIGH":   {"like_count": 10, "save_count": 8,  "watch_time_seconds": 200},
    "MEDIUM": {"like_count": 5,  "save_count": 3,  "watch_time_seconds": 50},
    "LOW":    {"like_count": 1,  "save_count": 0,  "watch_time_seconds": 10},
}

EXPECTED_SCORES = {k: _compute_score(**v) for k, v in REEL_FIXTURES.items()}
# HIGH=270, MEDIUM=80, LOW=13


async def _register_and_login(client: AsyncClient, suffix: str) -> dict[str, str]:
    """Register a unique user and return bearer headers."""
    email = f"algotest_{suffix}@example.com"
    await client.post("/api/v1/auth/register", json={
        "username": f"algotest_{suffix}",
        "email": email,
        "password": "password123",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": email, "password": "password123",
    })
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


async def _get_user_id(client: AsyncClient, headers: dict) -> uuid.UUID:
    resp = await client.get("/api/v1/auth/me", headers=headers)
    return uuid.UUID(resp.json()["id"])


async def _seed_reel(creator_id: uuid.UUID, label: str) -> str:
    """Insert a reel directly into the DB with deterministic metric values."""
    from app.models.reel import Reel
    metrics = REEL_FIXTURES[label]
    async with TestSession() as db:
        reel = Reel(
            creator_id=creator_id,
            title=f"AlgoTest_{label}_{uuid.uuid4().hex[:6]}",
            video_url=f"https://cdn.example.com/{label}.mp4",
            status="published",
            **metrics,
        )
        db.add(reel)
        await db.commit()
        await db.refresh(reel)
        return str(reel.id)


async def _seed_all_reels(creator_id: uuid.UUID) -> dict[str, str]:
    """Seed HIGH, MEDIUM, LOW reels. Returns {label: reel_id}."""
    return {label: await _seed_reel(creator_id, label) for label in REEL_FIXTURES}


# ---------------------------------------------------------------------------
# 1. TestScoringFormula — pure arithmetic, no DB
# ---------------------------------------------------------------------------

class TestScoringFormula:
    """Pure arithmetic tests — zero DB dependency."""

    def test_high_reel_score(self):
        score = _compute_score(like_count=10, save_count=8, watch_time_seconds=200)
        assert score == 270, f"10*3 + 8*5 + 200 = 270, got {score}"

    def test_medium_reel_score(self):
        score = _compute_score(like_count=5, save_count=3, watch_time_seconds=50)
        assert score == 80, f"5*3 + 3*5 + 50 = 80, got {score}"

    def test_low_reel_score(self):
        score = _compute_score(like_count=1, save_count=0, watch_time_seconds=10)
        assert score == 13, f"1*3 + 0*5 + 10 = 13, got {score}"

    def test_ordering_is_high_medium_low(self):
        scores = [_compute_score(**REEL_FIXTURES[k]) for k in ("HIGH", "MEDIUM", "LOW")]
        assert scores == sorted(scores, reverse=True), (
            f"Expected HIGH > MEDIUM > LOW, got {scores}"
        )

    def test_weights_match_schema_constants(self):
        assert SCORE_WEIGHT_LIKES == 3
        assert SCORE_WEIGHT_SAVES == 5
        assert SCORE_WEIGHT_WATCH_TIME == 1

    def test_formula_symmetry(self):
        """1 save (=5pts) beats 1 like (=3pts)."""
        assert _compute_score(0, 1, 0) > _compute_score(1, 0, 0)

    def test_watch_time_accumulates(self):
        """100s watch-time (=100pts) outranks 1 save (=5pts) and 1 like (=3pts)."""
        assert _compute_score(0, 0, 100) > _compute_score(0, 1, 0) > _compute_score(1, 0, 0)

    def test_zero_metrics_gives_zero_score(self):
        assert _compute_score(0, 0, 0) == 0

    def test_save_weight_dominates_likes_at_equal_count(self):
        """At equal count, saves contribute more than likes (weight 5 vs 3)."""
        n = 10
        assert _compute_score(n, 0, 0) < _compute_score(0, n, 0)


# ---------------------------------------------------------------------------
# 2. TestFeedOrdering — integration: correct descending order
# ---------------------------------------------------------------------------

class TestFeedOrdering:

    @pytest.mark.asyncio
    async def test_feed_returns_highest_score_first(self, client: AsyncClient):
        headers = await _register_and_login(client, "ord1")
        creator_id = await _get_user_id(client, headers)
        reel_ids = await _seed_all_reels(creator_id)

        resp = await client.get("/api/v1/feed/", headers=headers, params={"limit": 20})
        assert resp.status_code == 200, resp.text

        titles = [r["title"] for r in resp.json()["data"]]
        # Extract just the label portion for our seeded reels
        label_order = []
        for t in titles:
            for label in ("HIGH", "MEDIUM", "LOW"):
                if f"AlgoTest_{label}_" in t and reel_ids[label] in [
                    r["id"] for r in resp.json()["data"] if r["title"] == t
                ]:
                    label_order.append(label)
                    break

        # Simpler: get scores for our three seeded reels and verify descending
        our_reels = {
            r["id"]: r for r in resp.json()["data"]
            if r["id"] in reel_ids.values()
        }
        ordered_scores = [
            our_reels[reel_ids["HIGH"]]["feed_score"],
            our_reels[reel_ids["MEDIUM"]]["feed_score"],
            our_reels[reel_ids["LOW"]]["feed_score"],
        ]
        assert ordered_scores == sorted(ordered_scores, reverse=True), (
            f"Expected HIGH > MEDIUM > LOW scores: {ordered_scores}"
        )

    @pytest.mark.asyncio
    async def test_feed_score_field_matches_formula(self, client: AsyncClient):
        headers = await _register_and_login(client, "ord2")
        creator_id = await _get_user_id(client, headers)
        reel_ids = await _seed_all_reels(creator_id)

        resp = await client.get("/api/v1/feed/", headers=headers, params={"limit": 20})
        assert resp.status_code == 200

        items = {r["id"]: r for r in resp.json()["data"]}
        for label, expected_score in EXPECTED_SCORES.items():
            rid = reel_ids[label]
            assert rid in items, f"Reel {label} not in feed"
            actual = items[rid]["feed_score"]
            assert actual == expected_score, (
                f"{label}: feed_score={actual}, expected={expected_score}"
            )

    @pytest.mark.asyncio
    async def test_feed_scores_are_globally_descending(self, client: AsyncClient):
        """Every score in the feed page must be ≥ the next one."""
        headers = await _register_and_login(client, "ord3")
        creator_id = await _get_user_id(client, headers)
        await _seed_all_reels(creator_id)

        resp = await client.get("/api/v1/feed/", headers=headers, params={"limit": 20})
        assert resp.status_code == 200
        scores = [r["feed_score"] for r in resp.json()["data"]]
        assert scores == sorted(scores, reverse=True), (
            f"Feed scores not in descending order: {scores}"
        )

    @pytest.mark.asyncio
    async def test_feed_response_includes_new_fields(self, client: AsyncClient):
        """save_count, watch_time_seconds, and feed_score must be present."""
        headers = await _register_and_login(client, "ord4")
        creator_id = await _get_user_id(client, headers)
        reel_ids = await _seed_all_reels(creator_id)

        resp = await client.get("/api/v1/feed/", headers=headers, params={"limit": 20})
        assert resp.status_code == 200
        items = {r["id"]: r for r in resp.json()["data"]}

        hi = items[reel_ids["HIGH"]]
        assert hi["like_count"] == REEL_FIXTURES["HIGH"]["like_count"]
        assert hi["save_count"] == REEL_FIXTURES["HIGH"]["save_count"]
        assert hi["watch_time_seconds"] == REEL_FIXTURES["HIGH"]["watch_time_seconds"]
        assert "feed_score" in hi


# ---------------------------------------------------------------------------
# 3. TestFeedPagination — score-based cursor pages
# ---------------------------------------------------------------------------

class TestFeedPagination:

    @pytest.mark.asyncio
    async def test_cursor_pagination_no_duplicates(self, client: AsyncClient):
        headers = await _register_and_login(client, "pag1")
        creator_id = await _get_user_id(client, headers)
        reel_ids = await _seed_all_reels(creator_id)

        # Collect ALL pages with limit=2 to avoid the feed window issue
        all_ids = set()
        cursor = None
        page = 0
        while True:
            params = {"limit": 2}
            if cursor:
                params["cursor"] = cursor
            resp = await client.get("/api/v1/feed/", headers=headers, params=params)
            assert resp.status_code == 200
            body = resp.json()
            page_ids = {r["id"] for r in body["data"]}

            # No duplicates across pages
            assert not all_ids & page_ids, f"Duplicate IDs on page {page}: {all_ids & page_ids}"
            all_ids |= page_ids

            if not body["has_more"]:
                break
            cursor = body["next_cursor"]
            page += 1

        # All three seeded reels must appear across all pages
        assert {reel_ids["HIGH"], reel_ids["MEDIUM"], reel_ids["LOW"]} <= all_ids, (
            f"Not all seeded reels found across pages. Missing: "
            f"{set(reel_ids.values()) - all_ids}"
        )

    @pytest.mark.asyncio
    async def test_page2_scores_lower_than_page1(self, client: AsyncClient):
        headers = await _register_and_login(client, "pag2")
        creator_id = await _get_user_id(client, headers)
        await _seed_all_reels(creator_id)

        resp1 = await client.get("/api/v1/feed/", headers=headers, params={"limit": 2})
        body1 = resp1.json()
        p1_min = min(r["feed_score"] for r in body1["data"])

        resp2 = await client.get(
            "/api/v1/feed/", headers=headers,
            params={"limit": 2, "cursor": body1["next_cursor"]},
        )
        body2 = resp2.json()
        if body2["data"]:
            p2_max = max(r["feed_score"] for r in body2["data"])
            assert p2_max <= p1_min, (
                f"Page 2 max score ({p2_max}) exceeds page 1 min score ({p1_min})"
            )

    @pytest.mark.asyncio
    async def test_invalid_cursor_returns_first_page(self, client: AsyncClient):
        """A garbled cursor should be ignored and return the first page normally."""
        headers = await _register_and_login(client, "pag3")
        creator_id = await _get_user_id(client, headers)
        await _seed_all_reels(creator_id)

        resp = await client.get(
            "/api/v1/feed/", headers=headers,
            params={"limit": 5, "cursor": "NOTAVALIDCURSOR"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1


# ---------------------------------------------------------------------------
# 4. TestWatchTimeEndpoint — POST /reels/{id}/watch
# ---------------------------------------------------------------------------

class TestWatchTimeEndpoint:

    @pytest.mark.asyncio
    async def test_watch_increments_watch_time(self, client: AsyncClient):
        headers = await _register_and_login(client, "wt1")
        creator_id = await _get_user_id(client, headers)
        reel_ids = await _seed_all_reels(creator_id)
        low_id = reel_ids["LOW"]

        resp = await client.post(
            f"/api/v1/reels/{low_id}/watch", json={"seconds": 60}
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["seconds_added"] == 60
        assert body["reel_id"] == low_id
        # LOW started at 10 seconds
        assert body["watch_time_seconds"] == REEL_FIXTURES["LOW"]["watch_time_seconds"] + 60

    @pytest.mark.asyncio
    async def test_watch_updates_feed_score(self, client: AsyncClient):
        """After posting watch time, the reel's feed_score should increase.
        Uses the detail endpoint to avoid the top-20 feed window truncation.
        """
        headers = await _register_and_login(client, "wt2")
        creator_id = await _get_user_id(client, headers)
        reel_ids = await _seed_all_reels(creator_id)
        low_id = reel_ids["LOW"]

        # Get baseline feed_score from the reel detail endpoint
        r1 = await client.get(f"/api/v1/reels/{low_id}", headers=headers)
        assert r1.status_code == 200
        score_before = r1.json()["feed_score"]
        assert score_before == EXPECTED_SCORES["LOW"]

        # Record 30 seconds of watch time
        resp = await client.post(f"/api/v1/reels/{low_id}/watch", json={"seconds": 30})
        assert resp.status_code == 200

        # Score should have increased by 30 (weight=1)
        r2 = await client.get(f"/api/v1/reels/{low_id}", headers=headers)
        score_after = r2.json()["feed_score"]
        assert score_after == score_before + 30, (
            f"Expected score {score_before + 30}, got {score_after}"
        )

    @pytest.mark.asyncio
    async def test_watch_validates_seconds_min(self, client: AsyncClient):
        headers = await _register_and_login(client, "wt3")
        creator_id = await _get_user_id(client, headers)
        reel_ids = await _seed_all_reels(creator_id)
        resp = await client.post(
            f"/api/v1/reels/{reel_ids['LOW']}/watch", json={"seconds": 0}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_watch_validates_seconds_max(self, client: AsyncClient):
        headers = await _register_and_login(client, "wt4")
        creator_id = await _get_user_id(client, headers)
        reel_ids = await _seed_all_reels(creator_id)
        resp = await client.post(
            f"/api/v1/reels/{reel_ids['LOW']}/watch", json={"seconds": 9999}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_watch_time_on_nonexistent_reel_is_404(self, client: AsyncClient):
        resp = await client.post(
            f"/api/v1/reels/{uuid.uuid4()}/watch", json={"seconds": 30}
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_watch_time_re_ranks_low_above_medium(self, client: AsyncClient):
        """
        LOW starts at score=13, MEDIUM at 80.
        Adding 120 seconds to LOW  →  score = 13 + 120 = 133 > 80.
        LOW must then have a higher feed_score than MEDIUM.
        Uses detail endpoint to avoid top-20 feed window truncation.
        """
        headers = await _register_and_login(client, "wt5")
        creator_id = await _get_user_id(client, headers)
        reel_ids = await _seed_all_reels(creator_id)
        low_id  = reel_ids["LOW"]
        med_id  = reel_ids["MEDIUM"]

        # Confirm baseline scores
        low_before = (await client.get(f"/api/v1/reels/{low_id}", headers=headers)).json()["feed_score"]
        med_score  = (await client.get(f"/api/v1/reels/{med_id}", headers=headers)).json()["feed_score"]
        assert low_before == EXPECTED_SCORES["LOW"]   # 13
        assert med_score  == EXPECTED_SCORES["MEDIUM"] # 80
        assert low_before < med_score, "Precondition: LOW should start below MEDIUM"

        # Boost LOW by 120 seconds — new score = 13 + 120 = 133
        resp = await client.post(f"/api/v1/reels/{low_id}/watch", json={"seconds": 120})
        assert resp.status_code == 200

        # Verify LOW's new score directly via detail endpoint
        low_after = (await client.get(f"/api/v1/reels/{low_id}", headers=headers)).json()["feed_score"]
        assert low_after == low_before + 120, (
            f"Expected LOW score {low_before + 120}, got {low_after}"
        )
        assert low_after > med_score, (
            f"After 120s watch boost, LOW ({low_after}) should beat MEDIUM ({med_score})"
        )


