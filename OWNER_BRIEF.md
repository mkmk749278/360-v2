### Session — 2026-04-08 (ScanLat Root Cause + Signal Analysis Continued)

**What was discussed:**
- Owner requested analysis of signals from the VPS monitor workflow
- Copilot read monitor/latest.txt autonomously from monitor-logs branch
- Full ScanLat spike root cause investigation performed

**What was diagnosed:**
- ScanLat spikes (30-55s every ~5 minutes) root cause confirmed: `save_snapshot()` in `src/historical_data.py` calls `np.savez_compressed()` synchronously for 502 symbol-timeframe combos inside an async function with no `run_in_executor` wrapper — blocks the entire event loop
- Spike timing correlates exactly with `_snapshot_loop` firing every 300 seconds (`asyncio.sleep(300)`)
- Impact on signal quality: signals firing during snapshot window use candle data up to 45 seconds old; incoming WS kline messages queue up and process in burst after; REST calls also deferred during spike
- Fix identified: split `save_snapshot()` into async wrapper + sync `_save_snapshot_sync()`, wrap disk I/O in `loop.run_in_executor(None, self._save_snapshot_sync)` — ~20 line change, isolated to `src/historical_data.py`, zero risk to signal logic

**What was decided:**
- PR12 spec agreed: fix `save_snapshot()` blocking I/O — raise next session
- No other actions today — owner closing session, continuing tomorrow
- Brief to be updated with session history before close

**What was built:**
- OWNER_BRIEF.md updated: this session history entry appended

**Next actions (tomorrow):**
- Raise PR12 — `src/historical_data.py` snapshot I/O fix (run_in_executor wrapper)
- Check heartbeat hotfix PR status — merge if agent completed correctly
- Run monitor workflow after PR12 merges — confirm ScanLat spikes gone
- Continue watching for first new-engine signals as market normalises post tariff-shock


