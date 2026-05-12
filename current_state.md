# Manna Snips Current State

## Summary

`Manna Snips` is now publicly shipped on GitHub with a real `v0.1.1` maintenance release. The bundled-runtime Windows installer is the preferred public path, the portable PyInstaller zip is available as a secondary lane, the repo includes real README screenshots plus reusable asset-capture helpers, the first post-release hardening pass now adds configurable in-app hotkey presets, the project now has a written retrospective, and the public README plus repo metadata now explain the actual value proposition much more clearly for strangers landing on the page.

## Public Release

- repository:
  - `https://github.com/manna-core/manna-snips`
- latest release:
  - `https://github.com/manna-core/manna-snips/releases/tag/v0.1.1`
- preferred public download:
  - installer `MannaSnips-0.1.1-Setup.exe`
- secondary public download:
  - portable zip `MannaSnips-0.1.1-windows-x64.zip`
- checksum files are published for both downloads

## Current Capabilities

- global capture hotkey while the app is running
- in-app preset-based hotkey rebinding for busy Windows desktops
- custom drag-to-select overlay
- built-in lightweight annotation editor
- copy-first workflow with explicit download flow
- local-only state and disposable scratch files
- in-app downloads-folder control
- in-app `Start with Windows` control
- minimized startup when Windows auto-start is enabled

## Latest Batch Outcome

- expanded `README.md` so the public page now explains:
  - who the app is for
  - what problem it solves
  - why `copy first` vs `download explicitly` matters
  - why it is different from a save-heavy screenshot workflow
- fixed the public install instructions to point at the GitHub releases page instead of a repo-local `dist` path
- added `docs\launch-plan.md` with:
  - a lightweight traction plan
  - current Reddit channel recommendations
  - current subreddit-rule notes
  - ready-to-edit draft posts
  - follow-up discovery ideas like `winget` and AlternativeTo
- updated live GitHub repo metadata:
  - description
  - homepage URL pointing at `releases/latest`
  - discovery topics including `windows`, `screenshot`, `clipboard`, and `productivity`
- added configurable capture-hotkey presets directly in the main window
- the hotkey chip, help line, status text, and smoke output now all reflect the actual configured shortcut instead of a hardcoded `Ctrl+Shift+S`
- rebinding is preset-based and safe:
  - successful changes persist to settings
  - busy or failed combos revert to the previous configured shortcut
- verified isolated-profile behavior:
  - `Ctrl+Shift+S` was busy in the test profile
  - switching to `F10` succeeded
  - trying to reset back to the busy default correctly kept `F10`
- bumped the app and package version to `0.1.1`
- rebuilt the portable release zip and the preferred bundled-runtime installer for `v0.1.1`
- generated real README screenshots:
  - `D:\Manna-core\projects\manna-snips\docs\screenshots\main-window.png`
  - `D:\Manna-core\projects\manna-snips\docs\screenshots\editor-window.png`
- added reusable screenshot helpers:
  - `D:\Manna-core\projects\manna-snips\scripts\launch_readme_preview.py`
  - `D:\Manna-core\projects\manna-snips\scripts\capture-readme-assets.ps1`
- updated `README.md` to show the real app surface
- initialized a real local git repository
- installed local Git and GitHub CLI
- authenticated GitHub CLI
- created the public repository:
  - `https://github.com/manna-core/manna-snips`
- pushed `main`
- created the public `v0.1.0` release and attached:
  - installer
  - installer checksum
  - portable zip
  - portable zip checksum
- published the public `v0.1.1` maintenance release and attached:
  - installer
  - installer checksum
  - portable zip
  - portable zip checksum
- added a project retrospective at:
  - `D:\Manna-core\projects\manna-snips\docs\retrospective-v0.1.1.md`
- folded the highest-signal lessons back into project and root decision memory

## Verification So Far

- source verification:
  - `py -3 -m py_compile D:\Manna-core\projects\manna-snips\src\manna_snips\app.py D:\Manna-core\projects\manna-snips\scripts\manna_snips_app.pyw D:\Manna-core\scripts\manna_snips_app.pyw`
  - `py -3 D:\Manna-core\projects\manna-snips\scripts\manna_snips_app.pyw --smoke`
  - `py -3 D:\Manna-core\projects\manna-snips\scripts\manna_snips_app.pyw --version`
  - direct startup-toggle registry round-trip under `--profile public-test`
  - direct Tk startup smoke
- packaged verification:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File D:\Manna-core\projects\manna-snips\scripts\build-release.ps1`
  - `D:\Manna-core\projects\manna-snips\dist\MannaSnips\MannaSnips.exe --smoke`
  - verified release zip SHA-256 sidecar output
- installer verification:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File D:\Manna-core\projects\manna-snips\scripts\build-installer.ps1`
  - silent installer smoke into `D:\Manna-core\projects\manna-snips\runtime\install-smoke-3`
  - installed-app smoke
  - installed `--version`
  - installed minimized-launch smoke
  - verified installer SHA-256 sidecar output
- post-release hotkey verification:
  - `py -3 -m py_compile D:\Manna-core\projects\manna-snips\src\manna_snips\app.py D:\Manna-core\projects\manna-snips\scripts\manna_snips_app.pyw D:\Manna-core\scripts\manna_snips_app.pyw`
  - `py -3 D:\Manna-core\projects\manna-snips\scripts\manna_snips_app.pyw --smoke`
  - isolated-profile Tk startup smoke with in-app rebind from busy `Ctrl+Shift+S` to `F10`
  - isolated-profile smoke confirming persisted hotkey state after the rebind
  - `py -3 D:\Manna-core\projects\manna-snips\scripts\manna_snips_app.pyw --version`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File D:\Manna-core\projects\manna-snips\scripts\build-release.ps1`
  - `D:\Manna-core\projects\manna-snips\dist\MannaSnips\MannaSnips.exe --smoke`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File D:\Manna-core\projects\manna-snips\scripts\build-installer.ps1`
  - silent installer smoke into `D:\Manna-core\projects\manna-snips\runtime\install-smoke-0.1.1`
  - installed `--version` for the `0.1.1` installer lane
  - installed `--smoke` for the `0.1.1` installer lane
- release handoff verification:
  - GitHub repo creation succeeded
  - initial push to `main` succeeded
  - GitHub release `v0.1.0` succeeded
  - GitHub release `v0.1.1` succeeded
- public-page and launch-doc verification:
  - `gh api repos/manna-core/manna-snips` confirmed the updated public description
  - `gh api repos/manna-core/manna-snips` confirmed the homepage now points at `releases/latest`
  - `gh api repos/manna-core/manna-snips` confirmed public topics are now set
  - README install instructions now point at the real public release surface

## Remaining Work

- make the first low-noise public post, likely `r/sideprojects`, using the problem-first draft in `docs\launch-plan.md`
- consider a Wednesday `r/software` post after the first builder-community feedback pass
- submit `Manna Snips` to `winget`
- add the app to AlternativeTo
- decide whether a short README demo GIF is worth the extra upkeep after the current screenshot-based page
- collect real `v0.1.1` feedback on the new `SHORTCUT` picker
- keep clean-machine validation and deeper packaged-launch trust work on the follow-up list
- decide whether the next release should stay in hardening mode or pick up a small additional usability gain
- keep the bundled-runtime installer as the recommended public path unless the older portable-build trust question is explicitly revisited and cleared
- reuse the retrospective lessons as the default release/checklist shape for the next small Manna utility
