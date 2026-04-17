from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from src.scanner import Scanner


def _make_scanner() -> Scanner:
    signal_queue = MagicMock()
    signal_queue.put = AsyncMock(return_value=True)
    router_mock = MagicMock(active_signals={})
    router_mock.cleanup_expired.return_value = 0
    return Scanner(
        pair_mgr=MagicMock(),
        data_store=MagicMock(),
        channels=[],
        smc_detector=MagicMock(),
        regime_detector=MagicMock(),
        predictive=MagicMock(),
        exchange_mgr=MagicMock(),
        spot_client=None,
        telemetry=MagicMock(),
        signal_queue=signal_queue,
        router=router_mock,
    )


def test_pr7c_target_setup_filter_is_explicit_and_narrow():
    assert Scanner._is_pr7c_target_setup("SR_FLIP_RETEST") is True
    assert Scanner._is_pr7c_target_setup("TREND_PULLBACK_EMA") is True
    assert Scanner._is_pr7c_target_setup("BREAKOUT_RETEST") is False


def test_tier_compression_helper_is_doctrine_aligned():
    assert Scanner._is_tier_compressed("B", "WATCHLIST") is True
    assert Scanner._is_tier_compressed("A+", "B") is False
    assert Scanner._is_tier_compressed("WATCHLIST", "WATCHLIST") is False


def test_target_path_tier_migration_summary_tracks_compression_signal():
    scanner = _make_scanner()
    scanner._record_target_path_tier_migration(
        setup_family="reclaim_retest",
        setup_class="SR_FLIP_RETEST",
        pre_tier="B",
        post_tier="WATCHLIST",
    )
    scanner._record_target_path_tier_migration(
        setup_family="reclaim_retest",
        setup_class="SR_FLIP_RETEST",
        pre_tier="B",
        post_tier="WATCHLIST",
    )
    scanner._record_target_path_tier_migration(
        setup_family="other",
        setup_class="BREAKOUT_RETEST",
        pre_tier="B",
        post_tier="WATCHLIST",
    )

    summary = scanner._build_target_path_tier_migration_summary()
    token = "SR_FLIP_RETEST[reclaim_retest]"
    assert summary[token]["B->WATCHLIST"] == 2
    assert summary[token]["pre_B_or_A+_compressed"] == 2
    assert all("BREAKOUT_RETEST" not in key for key in summary)


def test_target_path_penalty_summary_aggregates_gate_hits():
    scanner = _make_scanner()
    scanner._modulate_penalty_base(
        base=15.0,
        penalty_key="vwap",
        chan_name="360_SCALP",
        setup_family="reclaim_retest",
        setup_class="SR_FLIP_RETEST",
    )
    scanner._modulate_penalty_base(
        base=12.0,
        penalty_key="volume_div",
        chan_name="360_SCALP",
        setup_family="continuation",
        setup_class="POST_DISPLACEMENT_CONTINUATION",
    )
    scanner._modulate_penalty_base(
        base=15.0,
        penalty_key="vwap",
        chan_name="360_SCALP",
        setup_family="other",
        setup_class="BREAKOUT_RETEST",
    )

    summary = scanner._build_target_path_penalty_summary()
    assert summary["SR_FLIP_RETEST[reclaim_retest]"]["vwap"] == 1
    assert summary["POST_DISPLACEMENT_CONTINUATION[continuation]"]["volume_div"] == 1
    assert all("BREAKOUT_RETEST" not in key for key in summary)


def test_target_path_funnel_summary_links_stage_and_outcome_counts():
    scanner = _make_scanner()
    scanner._path_funnel_counters[
        "generated:360_SCALP:reclaim_retest:SR_FLIP_RETEST"
    ] += 2
    scanner._path_funnel_counters[
        "filtered:360_SCALP:reclaim_retest:SR_FLIP_RETEST"
    ] += 1
    scanner._path_funnel_counters[
        "lifecycle:TP1_HIT:360_SCALP:reclaim_retest:SR_FLIP_RETEST"
    ] += 3
    scanner._path_funnel_counters[
        "generated:360_SCALP:other:BREAKOUT_RETEST"
    ] += 10

    funnel, outcomes = scanner._build_target_path_funnel_summary()
    token = "SR_FLIP_RETEST[reclaim_retest]"
    assert funnel[token]["generated"] == 2
    assert funnel[token]["filtered"] == 1
    assert outcomes[token]["TP1_HIT"] == 3
    assert all("BREAKOUT_RETEST" not in key for key in funnel)
