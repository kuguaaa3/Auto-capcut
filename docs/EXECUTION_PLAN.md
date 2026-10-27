# Auto-capcut execution plan

Date: 2026-10-27 (Asia/Shanghai). Base: `18d5baf0ec7324118a36b6e1b199b07eb2700dd0`.
Integration branch: `implement/auto-capcut`.

## Confirmed scope

Implement the locked PRODUCT_SPEC, INTERACTION_ROUTES and CAPCUT_ADAPTER contracts.
No additional UI, server, database or alternate editing engine. Actual editing and
acceptance must use the official CapCut connection; automated local tests cannot
prove B/C/D media acceptance. Private media stays out of Git.

## Engineering workflow

Matt Pocock plugin 1.3.1 installed using its official Codex marketplace commands.
Use setup-matt-pocock-skills, to-spec, to-tickets, implement-spec, tdd and
code-review. Reuse the existing approved product decisions and T01–T13 graph.
Tracker: GitHub Issues. Domain: GLOSSARY.md and docs/adr/. Docs: docs/.
Default triage roles retain their upstream names.

Public test seams, already specified by AGENTS.md and ENGINEERING_WORKFLOW:
conversation/CLI routes, persistent project artifacts, editor adapter boundary,
and style discovery/versioning. Red → green one behavior at a time. Local
contract tests are labeled local; no mock result counts as CapCut acceptance.

## Implementation sequence

1. T01: configure tracker, packaging, stdlib Python test runner and CI.
2. T02: install verified official CapCut bundle, check connection, authorize,
   discover actual tool schemas, and record each capability with evidence.
3. Independent local frontier: T03 project store and routing; T04 style registry;
   T05 media inspection and plan validation. Use isolated implementation branches
   and merge onto this integration branch under implement-spec.
4. T06–T09: connect discovered official tools, build/read back a real draft,
   preserve versions during changes, verify subtitles/audio and actual exports.
5. T10: separately measure domestic Jianying compatibility. Unknown stays unknown.
6. T11–T12: approved style learning, recovery, multi-project and failure checks.
7. T13: installable Skill, standards and spec reviews, regression checks and
   real acceptance evidence. Keep unresolved tickets open and PR draft.

## Current evidence and constraints

- Local Windows desktop, Codex CLI 0.164.0-alpha.11.1.
- Official page links to a vendor-hosted installation Skill, advertising 0.2.6.
- CapCut 0.2.6 installed and enabled under the managed marketplace; configured
  account endpoint is https://www.capcut.com/api/external_mcp.
- Read-only connection helper returned login_required. The in-app browser visibly
  showed the CapCut sign-in page; the OAuth helper subsequently exited 1 with
  success=false, timed out waiting for OAuth callback. Authorization is incomplete.
  The stale page was closed. No editing capability has been marked supported.
- No user-approved local media folder has yet been supplied. Requested at least
  three clips and explicit approval before uploading to CapCut.

## Completion gate

Update a per-ticket evidence/status ledger, review both standards and spec against
the pinned base, and report verified/unverified separately. Never close a ticket
whose DoD still depends on unavailable authorization, media or real application QA.
