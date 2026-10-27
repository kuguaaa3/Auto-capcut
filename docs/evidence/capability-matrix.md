# Target-machine capability evidence

2026-10-27, Asia/Shanghai. This is actual setup evidence, not media acceptance.
Machine/software versions and the safe authorization result are in environment.json.

| Capability | Status | Actual observation |
|---|---|---|
| Official plugin installation | supported | Native `plugin list` shows CapCut@CapCut 0.2.6 installed/enabled at the managed local source; native `mcp get` shows the official endpoint. |
| Account connection | blocked | Vendor read-only helper returned login_required. In-app browser visibly showed the CapCut sign-in page. OAuth helper later returned success=false, timed out waiting for OAuth callback, exit 1. |
| Native editing tool availability in this chat | unknown | No native protected CapCut tool was found. Installation alone is not authorization or usable tool evidence. |
| New editable project and three-clip import | blocked | No account authorization; no user-provided clips or upload approval. No draft created. |
| Trim/reorder and actual readback | blocked | Requires the authorized official tools and actual source clips. |
| Third-shot shortening preserving other clips | blocked | Requires actual separate editable source segments; no test performed. |
| Captions and music/volume adjustment | blocked | Vendor workflows read; actual account tools not exercised. |
| Real MP4 export and independent playback | blocked | No official edit/export has occurred. No plan JSON or technical fixture is counted as exported video. |
| CapCut project reopen/edit | blocked | No project has been created or reopened. |
| Domestic Jianying draft compatibility | unknown | Installed application observed. No official or compatibility draft generated/opened/modified/saved/reopened. |

The expired browser authorization tab was closed after the helper exited; its
callback is no longer listening. The vendor runbook prohibits automatic retries
for this definitive failure in the same installation attempt. The plugin remains
installed; a later recovery should check and finish only its authorization.

No private media was scanned outside the selected workspace, uploaded, or pushed.
Local technical test media is isolated and never counted toward B01–B10 or D01–D04.
