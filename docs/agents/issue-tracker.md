# Issue tracker: GitHub

Specs and tickets live in kuguaaa3/Auto-capcut GitHub Issues. Use gh CLI with
--body-file for multiline content; read issues with gh issue view --json
number,title,body,labels,comments. List before creating to avoid duplicates.

Create one spec and one issue per approved T01–T13 vertical slice. Link sub-issues
and native blocking dependencies where available; include textual Blocked by
references as a readable fallback. Never close a parent automatically. Only close
a ticket after its DoD has actual evidence. PRs are the review surface; keep draft
while real acceptance is blocked. PRs as a request surface: no.
