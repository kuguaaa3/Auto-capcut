# Matt Pocock two-axis code review

Date: 2026-10-27. Independent Standards and Spec subagents ran in parallel.
Fixed point: `18d5baf0ec7324118a36b6e1b199b07eb2700dd0`.
Command: `git diff 18d5baf0ec7324118a36b6e1b199b07eb2700dd0...HEAD`.
Initial reviewed integration: `d844df6`; status/docs subsequently updated.

## Standards

1. P1: `media.py` used container duration when the video stream omitted duration.
   A real technical MKV with 1-second video and 2-second audio was incorrectly
   reported as 2.023-second video despite its stream DURATION tag. This violated
   DEVELOPMENT_AUDIT and DATA_CONTRACTS source bounds.
2. P1: `cli.py` retained an old plan after selecting a different style, and
   operation preflight did not compare the selected style/version. A local
   handoff for the old style could still receive execute. This violated AGENTS
   explicit-choice priority.
3. P1: `styles.py` validated a proposal before converting its source to learned.
   Builtin metadata with a relative license path could be persisted, then fail
   loading and poison the catalogue. This violated failure recovery guarantees.
4. P2: the untrusted-style screen rejected legitimate 9:16/16:9 visual rules as
   source timestamps, contrary to transferable visual configuration governance.

No separately actionable Fowler baseline smell justified broadening the refactor.

## Spec

1. P1: stale-style plan execution violated INTERACTION_ROUTES user-choice lock
   and versioned style-switch behavior. This independently confirmed Standards #2.
2. P1: native-edit preflight relied on cached source exists/hash metadata. Deleting
   a genuinely inspected temporary technical video still allowed execute, contrary
   to US02 and resume-time source verification requirements.
3. P2: plan-first/direct preference was only a route hint. It was neither persisted
   nor enforced across sessions, contrary to US23.

Known external gap: the adapter currently prepares native tool handoffs. Real
creation, edits, export and readback have not been verified because authorization
timed out and no approved user media was supplied. The user subsequently requested
deferring real acceptance; this gap remains explicitly unverified, not passed.
No extra UI or alternate editing engine was found.

## Resolution

All six distinct local findings are fixed with public regression tests; the
primary agent took over when the fix subagent hit an account usage limit before
editing. The duplicate stale-style finding stays recorded in both axes without
changing their priorities. See review-fixes.md: 65 tests passed, no skips.

Initial totals: Standards 4 findings (worst P1 source-bound/stale-style errors);
Spec 3 local findings (worst P1 stale-style/missing-source execution), plus the
separately disclosed official-connection and real-acceptance gap.
