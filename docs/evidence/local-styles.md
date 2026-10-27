# Local style implementation evidence

Date: 2026-10-27, Windows, Python 3.11. Scope: T04 local style routing and T11
local proposal/import/version lifecycle only. No media was uploaded or edited by
these checks. CapCut output quality and real style reuse remain unverified.

## Observed checks

`python -m unittest tests.test_styles -v`: 21 tests pass at the public
`StyleRegistry` seam. Initial red runs observed missing module/API, missing
approval/version lifecycle, unsafe-rule acceptance, invalid naming, data-only
import, corrupt pointer handling, metadata smuggling, standalone Markdown import,
lost source provenance and modified Skill text. The corresponding green runs
checked the implemented behaviors. Subsequent self-review factored shared
version persistence and tightened source screening.

The ten style-specific cases use recorded editorial observations and a negative
finding for each style's factual gates: causal payoff, observed pet behavior,
spatial continuity, hook payoff, actual time/place, original speech meaning,
musical variation, supported product claims, matched exposure and sourced facts.
These are local bookkeeping fixtures clearly labeled not actual footage.
They do not assess pixels, audio, aesthetics or a real CapCut timeline.

Other tests cover explicit selection over current/recommended style, no fallback
for an invalid explicit style, Chinese catalog search, approval-only storage,
version preservation and rollback in a fresh registry, unsafe/private rules,
case/path collisions, text-only imports, provenance retention and tamper checks.

All ten bundled styles pass the installed skill-creator `quick_validate.py`.
Use `python -X utf8` on this Windows host because its default encoding is GBK.
The validator caught unsupported top-level `version`; generated frontmatter now
stores it under `metadata.version`, with machine version in adjacent style.json.
`python -m compileall -q skills/auto-capcut/scripts` also passes.

## Sources and boundaries

Ten knowledge bundles preserve original source URLs, blob SHAs and individual
licenses. All ten LICENSE files are included in the installable Skill package.
Upstream renderers, downloads, model setup and execution instructions are excluded.

Local parsing and storage do not establish B10 or the per-style real-sample
requirements in STYLE_PRESETS. Those need authorized user media, actual CapCut
editing, export/reopen verification and content review. T11 must remain open until
the accepted style generates a real project in a subsequent user task.
