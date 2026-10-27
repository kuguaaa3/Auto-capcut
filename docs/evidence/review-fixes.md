# Review fixes and regression evidence

2026-10-27, Windows, Python 3.11. Real acceptance is deferred by user instruction.
The intended single fix implementer was interrupted by an account usage limit
before making changes. The primary agent completed the fixes directly, preserving
the independent two-axis reports and using the same agreed public test seams.

All six distinct local findings are addressed:

- Style switch: current plan pointer is invalidated on ID/version changes,
  historical plans remain, saved plans pin style_version, and editor handoff
  rechecks the current selected pair.
- Source integrity: referenced local files are reopened and SHA-256 checked
  before editing; missing, unreadable or changed bytes block before journaling.
  Resume rechecks sources as well.
- Execution preference: direct/plan-first persists across processes, confirm-plan
  records explicit consent for the current plan, and changed plans/materials/
  styles clear prior confirmation. Direct mode adds no plan approval.
- Video bounds: missing stream duration now reads stream ticks/time base or the
  stream DURATION tag. An unknown stream duration blocks; longer container audio
  is not a fallback video bound. A real MKV regression covers this case.
- Portable configuration: 9:16/16:9 display ratios pass screening while an actual
  00:12 source timestamp is still rejected.
- Style recovery: final converted learned metadata is validated before any write,
  and persistence revalidates its final version. Rejected proposals cannot poison
  active.json or make the existing catalogue unreadable.

Each new regression was observed red before the corresponding implementation.
The installer also now preserves the actual safe filesystem failure and retries
only Windows permission/sharing errors briefly; existing installations remain
untouched. Fresh temporary installation and execution succeeded, and reinstallation
to an occupied target was correctly rejected.

Verification: **65 tests passed, no skips** with existing native ffprobe and full
video FFmpeg configured. compileall and git diff --check passed. Tests use isolated
technical media; no user footage, uploads or CapCut editor calls were performed.

Original review totals remain Standards 4 / Spec 3 (one duplicate). All local
findings have a regression/fix. Official account-backed execution, full editing,
MP4/project export and real content/editor QA remain unverified and deferred.
