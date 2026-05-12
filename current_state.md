# Manna Snips Current State

## Summary

`Manna Snips` is now publicly shipped on GitHub with a real `v0.1.0` release. The bundled-runtime Windows installer is the preferred public path, the portable PyInstaller zip is available as a secondary lane, and the repo now includes real README screenshots plus reusable asset-capture helpers.

## Public Release

- repository:
  - `https://github.com/manna-core/manna-snips`
- first release:
  - `https://github.com/manna-core/manna-snips/releases/tag/v0.1.0`
- preferred public download:
  - installer `MannaSnips-0.1.0-Setup.exe`
- secondary public download:
  - portable zip `MannaSnips-0.1.0-windows-x64.zip`
- checksum files are published for both downloads

## Current Capabilities

- global `Ctrl+Shift+S` hotkey while the app is running
- custom drag-to-select overlay
- built-in lightweight annotation editor
- copy-first workflow with explicit download flow
- local-only state and disposable scratch files
- in-app downloads-folder control
- in-app `Start with Windows` control
- minimized startup when Windows auto-start is enabled

## Latest Batch Outcome

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
- release handoff verification:
  - GitHub repo creation succeeded
  - initial push to `main` succeeded
  - GitHub release `v0.1.0` succeeded

## Remaining Work

- do one last real human installer click-through from the public release page if desired
- if real users hit hotkey conflicts, add configurable rebinding as the first post-release usability hardening pass
- keep the bundled-runtime installer as the recommended public path unless the older portable-build trust question is explicitly revisited and cleared
