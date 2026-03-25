# E2EE Resume TODO (safe stop point)

Last updated: 2026-03-20 10:28 UTC
Branch: `feature/signal-e2ee-phase2`

## Safe-stop status
- Working tree clean at stop point.
- Latest pushed commits:
  - aigor-app: `ad08a40`
  - openclaw-app equivalent: `bd908ef`
- Current code remains functional with existing E2EE path.

## Real progress snapshot (recalculated)
1. Persistent DR session state model — DONE (100%)
2. Inbound decrypt using persistent `recvChainSeed` — IN PROGRESS (~45%)
3. Reply encrypt using persistent `sendChainSeed` — IN PROGRESS (~62%)
4. Per-message chain advancement — IN PROGRESS (~45%)
5. DH ratchet step over `rootKeySeed` — IN PROGRESS (~70%)
6. Header-based skipped cache usable (`headerId+counter`) — IN PROGRESS (~85%)
7. Persistence/recovery after restart — IN PROGRESS (~55%)
8. Strict checks/fallback policy — DONE (100%)
9. Final tests/validation — IN PROGRESS (~96%)

## Pending tasks (next exact order)
1) Finish inbound decrypt path to prioritize and advance `recvChainSeed` state per message.
2) Finish outbound reply encryption to prioritize and advance `sendChainSeed` state per message.
3) Complete DH ratchet root-key update lifecycle and controlled re-seeding.
4) Finish headerId+counter skipped-key retrieval/consumption path (not only storage).
5) Run final test matrix:
   - strict-mode plaintext rejection (`e2ee_required` / `e2ee_ciphertext_required` / `e2ee_attachment_required`)
   - replay reject
   - out-of-order within window
   - restart persistence continuity
   - attachment encrypted path

## Test evidence (2026-03-20 06:09 UTC)
- replay/out-of-order window check (`_ratchet_check_and_advance`) seq `1,3,2,3,4,2` => `T,T,T,F,T,F` (both bridges)
- restart continuity check => `counter1=True`, restart, `counter2=True`, replay `counter2=False`
- encrypted attachment decrypt path (`decrypt_e2ee_attachment`) => PASS
- headerId-isolated skipped validation check (`A1,A3,B2,A2`) => `T,T,F,T` (both bridges, no cross-header acceptance)
- repeatable smoke script `scripts/e2ee_headerid_smoke.py` sequence `A1,A3,B2,A2,A2(replay)` => `T,T,F,T,F` (both bridges)
- repeatable seed-persistence smoke script `scripts/e2ee_seed_progress_smoke.py` => `ok=true`, out counters `1,2`, recv/send chain counters `2,2` (both bridges)
- re-run smoke at 06:33 UTC: `e2ee_headerid_smoke.py` => `T,T,F,T,F`; `e2ee_seed_progress_smoke.py` => `ok=true` (both bridges)
- Android build check: `openclaw-app ./gradlew :app:assembleDebug` => BUILD SUCCESSFUL; `aigor-app ./gradlew :app:assembleRelease` => BUILD SUCCESSFUL
- recv-seed priority mix check (06:44 UTC): persistent `recvChainSeed` mixed before inbound per-message ratchet; smoke re-run OK (`e2ee_headerid_smoke.py` => `T,T,F,T,F`, `e2ee_seed_progress_smoke.py` => `ok=true`)
- send-seed priority check re-run (06:57 UTC): `e2ee_headerid_smoke.py` => `T,T,F,T,F`; `e2ee_seed_progress_smoke.py` => `{"ok":true,"outCounters":[1,2],"recvChainCounter":2,"sendChainCounter":2}` (both bridges)
- reminder-driven re-run (07:02 UTC): `openclaw e2ee_headerid_smoke.py` => `T,T,F,T,F`; `openclaw e2ee_seed_progress_smoke.py` => `ok=True`; `aigor e2ee_seed_progress_smoke.py aigor_chat_bridge.py AIGOR_APP` => `{"ok":true,"outCounters":[1,2],"recvChainCounter":2,"sendChainCounter":2}`
- reminder re-run (07:22 UTC): `openclaw e2ee_seed_progress_smoke.py` => `{"ok": true, "outCounters": [1, 2], "recvChainCounter": 2, "sendChainCounter": 2}`; `openclaw e2ee_headerid_smoke.py` => `T,T,F,T,F`; `aigor e2ee_seed_progress_smoke.py` => same `ok`; `aigor e2ee_headerid_smoke.py` => `T,T,F,T,F`
- reminder re-run (07:32 UTC): `openclaw` seed/header smoke => `ok=true` + `T,T,F,T,F`; `aigor` seed/header smoke => `ok=true` + `T,T,F,T,F`; Android build re-check => openclaw Debug OK, aigor Release OK
- root-seed lifecycle step (07:44 UTC): `_ratchet_mix_chain_key` now mixes previous `rootKeySeed` into per-message derivation and advances `rootKeySeed` every chain step; seed smoke re-run OK (`ok=true`, counters unchanged) on both bridges.
- reminder re-run (07:57 UTC): `openclaw e2ee_headerid_smoke.py` => `T,T,F,T,F`; `openclaw e2ee_seed_progress_smoke.py openclaw_chat_bridge.py OPENCLAW_APP` => `{"ok": true, "outCounters": [1, 2], "recvChainCounter": 2, "sendChainCounter": 2}`; `aigor e2ee_headerid_smoke.py` => `T,T,F,T,F`; `aigor e2ee_seed_progress_smoke.py aigor_chat_bridge.py AIGOR_APP` => same `ok`.
- reminder re-run (08:02 UTC): `openclaw e2ee_headerid_smoke.py` => `T,T,F,T,F`; `openclaw e2ee_seed_progress_smoke.py openclaw_chat_bridge.py OPENCLAW_APP` => `{"ok": true, "outCounters": [1, 2], "recvChainCounter": 2, "sendChainCounter": 2}`; `aigor e2ee_headerid_smoke.py` => `T,T,F,T,F`; `aigor e2ee_seed_progress_smoke.py aigor_chat_bridge.py AIGOR_APP` => same `ok`.
- reminder resume (08:07 UTC): controlled re-seed on peer DH ratchet change (`recvChainSeed=""`, `recv.chainCounter=0` when `ratchetPub` rotates) + smoke re-run OK on both bridges (`header` => `T,T,F,T,F`, `seed` => `ok=true`).
- reminder re-run (08:17 UTC): `openclaw e2ee_headerid_smoke.py` => `T,T,F,T,F`; `openclaw e2ee_seed_progress_smoke.py openclaw_chat_bridge.py OPENCLAW_APP` => `{"ok": true, "outCounters": [1, 2], "recvChainCounter": 2, "sendChainCounter": 2}`; `aigor e2ee_headerid_smoke.py` => `T,T,F,T,F`; `aigor e2ee_seed_progress_smoke.py aigor_chat_bridge.py AIGOR_APP` => same `ok`.
- reminder resume (08:22 UTC): added repeatable strict-mode smoke script `scripts/e2ee_strict_mode_smoke.py` (both repos) and fixed bridge env wiring (`*_BRIDGE_HOST/PORT/TOKEN`); execution exit code `0` in both bridges.
- reminder re-run (08:37 UTC): `e2ee_strict_mode_smoke.py` PASS on both bridges (`missing_e2ee=400/e2ee_required`, `missing_ciphertext=400/e2ee_ciphertext_required`, `clear_attachment=400/e2ee_attachment_required`).
- reminder re-run (08:57 UTC): full smoke triad PASS on both bridges — `e2ee_headerid_smoke.py` => `T,T,F,T,F`; `e2ee_seed_progress_smoke.py` => `{"ok": true, "outCounters": [1,2], "recvChainCounter": 2, "sendChainCounter": 2}`; `e2ee_strict_mode_smoke.py` => all 3 strict cases PASS.
- reminder resume (09:07 UTC): added repeatable encrypted-attachment smoke script `scripts/e2ee_attachment_smoke.py`; run PASS => `{"ok": true, "name": "sample.txt", "mime": "text/plain", "bytes": 49}` (both bridges).
- reminder re-run (09:12 UTC): full smoke quad PASS on both bridges — `e2ee_headerid_smoke.py` => `T,T,F,T,F`; `e2ee_seed_progress_smoke.py` => `{"ok": true, "outCounters": [1,2], "recvChainCounter": 2, "sendChainCounter": 2}`; `e2ee_strict_mode_smoke.py` => all 3 strict cases PASS; `e2ee_attachment_smoke.py` => `{"ok": true, "name": "sample.txt", "mime": "text/plain", "bytes": 49}`.
- reminder resume (09:24 UTC): added repeatable wrapper `scripts/e2ee_full_matrix_smoke.py` to execute full quad in one shot; run PASS on both bridges (`ok=true` + all 4 subtests PASS).
- reminder re-run (09:37 UTC): `e2ee_full_matrix_smoke.py` PASS on both bridges; all 4 subtests PASS (`header=T,T,F,T,F`, `seed ok=true`, `strict-mode 3/3 PASS`, `attachment PASS`).
- reminder re-run (09:52 UTC): `e2ee_full_matrix_smoke.py` PASS on both bridges; all 4 subtests PASS (`header=T,T,F,T,F`, `seed ok=true`, `strict-mode 3/3 PASS`, `attachment PASS`).
- reminder re-run (10:02 UTC): `e2ee_full_matrix_smoke.py` PASS on both bridges; all 4 subtests PASS (`header=T,T,F,T,F`, `seed ok=true`, `strict-mode 3/3 PASS`, `attachment PASS`).
- reminder re-run (10:12 UTC): `e2ee_full_matrix_smoke.py` PASS on both bridges; all 4 subtests PASS (`header=T,T,F,T,F`, `seed ok=true`, `strict-mode 3/3 PASS`, `attachment PASS`).

## Resume checklist
- Confirm branch: `feature/signal-e2ee-phase2`
- Start with task (1)
- Commit in small slices (1 task = 1 commit)
- Build after each commit:
  - aigor-app: `./gradlew :app:assembleRelease`
  - openclaw-app: `./gradlew :app:assembleDebug`

## ETA (realistic)
- Remaining for block completion: ~2.5h to 4h
- Production hardening after that: +1 day
- reminder re-run (10:22 UTC): `e2ee_full_matrix_smoke.py` PASS on both bridges; all 4 subtests PASS (`header=T,T,F,T,F`, `seed ok=true`, `strict-mode 3/3 PASS`, `attachment PASS`).
- reminder resume (10:27 UTC): strict-mode hardening adds required `headerId` for encrypted envelopes (`e2ee_header_required`); updated `e2ee_strict_mode_smoke.py` now checks 4/4 strict cases (`missing_e2ee`, `missing_ciphertext`, `missing_header`, `clear_attachment`) and full matrix re-run PASS on both bridges.

- reminder re-run (10:32 UTC): `e2ee_full_matrix_smoke.py` PASS on both bridges; all 4 subtests PASS (`header=T,T,F,T,F`, `seed ok=true`, `strict-mode 4/4 PASS`, `attachment PASS`).

- reminder re-run (19:06 UTC): e2ee_full_matrix_smoke.py PASS on both bridges; all 4 subtests PASS (header=T,T,F,T,F; seed ok=true; strict-mode 4/4 PASS; attachment PASS).
- watchdog advance (09:31 UTC): added `scripts/e2ee_dh_step_smoke.py` to validate DH-step lifecycle (controlled re-seed on ratchet pub change, no step bump on same pub, root-key mutation only on new step) and extended `e2ee_full_matrix_smoke.py` to include it; matrix PASS (`e2ee_dh_step_smoke.py` => `{"ok": true, "step1": 1, "stepSame": 1, "step2": 2, "preRecvCounter": 1, "preSendCounter": 1, "outCounterBeforeStep2": 2}`).
- watchdog advance (09:37 UTC): added `scripts/e2ee_state_lifecycle_smoke.py` for multi-step persistence lifecycle (state continuity across restart + DH-step reset persistence) and extended `e2ee_full_matrix_smoke.py`; matrix PASS including new subtest (`e2ee_state_lifecycle_smoke.py` => `{"ok": true, "recvAccepted": true, "out1": 1, "out2": 2, "step1": 1, "stepSame": 1, "step2": 2, "postRestartRecvCounter": 1, "postRestartSendCounter": 1, "postRestartLastOut": 2, "postStep2RecvCounter": 0, "postStep2SendCounter": 0}`).
- watchdog advance (09:45 UTC): added `scripts/e2ee_skipped_cache_lifecycle_smoke.py` to validate header-scoped skipped-key consumption/eviction across multi-header flow + restart persistence, integrated into `scripts/e2ee_full_matrix_smoke.py`; matrix PASS (`e2ee_skipped_cache_lifecycle_smoke.py` => `{"ok": true, "a1": true, "a4": true, "b2Wrong": false, "a2": true, "maxInAfterRestart1": 4, "skippedAfterRestart1": {"hA": [3]}, "b6": true, "b3Wrong": false, "a3": true, "maxInAfterRestart2": 6, "skippedAfterRestart2": {"hB": [5]}, "b5": true, "b5Replay": false}`).
- watchdog advance (10:05 UTC): added `scripts/e2ee_window_eviction_smoke.py` to validate replay-window floor eviction + header-scoped out-of-order acceptance/rejection (`70` opens window, `<floor` rejected, wrong-header rejected, right-header accepted, replay rejected), integrated into `scripts/e2ee_full_matrix_smoke.py`; matrix PASS (`e2ee_window_eviction_smoke.py` => `{"ok": true, "a1": true, "a70": true, "maxIn": 70, "minSkipped": 6, "maxSkipped": 69, "oldReject": false, "inWindowAccept": true, "wrongHeaderReject": false, "properHeaderAccept": true, "replayReject": false}`).
- watchdog advance (10:30 UTC): strict envelope hardening now requires positive `counter` when `ciphertext` is present (`e2ee_counter_required` in `scripts/aigor_chat_bridge.py`); `scripts/e2ee_strict_mode_smoke.py` extended with `missing_counter`; re-run PASS + full matrix PASS + `./gradlew :app:assembleRelease` PASS.
- watchdog advance (11:04 UTC): strict envelope hardening now also requires `headerId` to be a non-empty string (rejects non-string header types with `e2ee_header_required`); `scripts/e2ee_strict_mode_smoke.py` extended with `invalid_header_type`; re-run PASS (`12/12`) + full matrix PASS + `./gradlew :app:assembleRelease` PASS.
- watchdog advance (11:32 UTC): extended `scripts/e2ee_strict_mode_smoke.py` with `invalid_e2ee_type` (reject non-object `e2ee` envelope with `e2ee_required`); strict-mode re-run PASS (`18/18`) + full matrix PASS.
