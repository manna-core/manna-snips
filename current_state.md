# Manna Snips Current State

## Summary

`Manna Snips` is now in a solid local release state with an installer-first shipping path. The main app stays copy-first, the installer is the preferred public lane, and the old direct PyInstaller portable build remains secondary after the earlier shutdown scare.

## Current Capabilities

- global `Ctrl+Shift+S` hotkey while the app is running
- custom drag-to-select overlay
- built-in lightweight annotation editor
- copy-first workflow with explicit download flow
- local-only state and disposable scratch files
- in-app downloads-folder control
- in-app `Start with Windows` control
- startup launches minimized when Windows auto-start is enabled

## Latest Batch Outcome

- kept the main surface simple and release-friendly while adding one practical final control:
  - `Start with Windows` can now be turned on or off from inside the app, not only during install
- tightened startup behavior:
  - Windows auto-start now launches minimized to the taskbar instead of throwing the main window open at sign-in
- tightened release engineering:
  - installer staging is now rebuilt cleanly each run instead of risking stale files
  - release artifacts now include SHA-256 sidecar files
- tightened public docs:
  - `README.md` now speaks installer-first
  - portable PyInstaller output is now clearly treated as an advanced secondary lane

## Shipping Truth

- preferred public path:
  - `D:\Manna-core\projects\manna-snips\dist\installer\MannaSnips-0.1.0-Setup.exe`
- installer hash:
  - `D:\Manna-core\projects\manna-snips\dist\installer\MannaSnips-0.1.0-Setup.sha256.txt`
- secondary portable path:
  - `D:\Manna-core\projects\manna-snips\dist\MannaSnips`
- portable zip hash:
  - `D:\Manna-core\projects\manna-snips\dist\MannaSnips-0.1.0-windows-x64.sha256.txt`
- the installer still uses the source app plus bundled Python runtime as the main launch path
- the old direct PyInstaller portable app is still the less-trusted lane and should not be treated as the default public recommendation

## Verification So Far

- source verification:
  - `py -3 -m py_compile D:\Manna-core\projects\manna-snips\src\manna_snips\app.py D:\Manna-core\projects\manna-snips\scripts\manna_snips_app.pyw D:\Manna-core\scripts\manna_snips_app.pyw`
  - `py -3 D:\Manna-core\projects\manna-snips\scripts\manna_snips_app.pyw --smoke`
  - `py -3 D:\Manna-core\projects\manna-snips\scripts\manna_snips_app.pyw --version`
  - direct startup-toggle registry round-trip under `--profile public-test`
  - direct Tk startup smoke of the main window after the final polish pass
- packaged verification:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File D:\Manna-core\projects\manna-snips\scripts\build-release.ps1`
  - `D:\Manna-core\projects\manna-snips\dist\MannaSnips\MannaSnips.exe --smoke`
  - verified release zip SHA-256 sidecar output
- installer verification:
  - `powershell -NoProfile -ExecutionPolicy Bypass -File D:\Manna-core\projects\manna-snips\scripts\build-installer.ps1`
  - silent installer smoke into `D:\Manna-core\projects\manna-snips\runtime\install-smoke-3`
  - installed-app smoke from that install root
  - installed `--version` check from that install root
  - installed `pythonw.exe` launch smoke with `--minimized`
  - verified installer SHA-256 sidecar output

## Remaining Work

- capture README screenshots or a short GIF from the installer-backed app surface
- do one real human click-through of the refreshed installer if possible, now paying attention to:
  - welcome-screen startup choice
  - install-location page
  - app startup after install
  - minimized behavior when `Start with Windows` is enabled
- open the standalone repo on GitHub and publish the first release assets when Grayson is ready for machine-external steps

## Latest Batch Outcome

- captured real README screenshots into:
  - `D:\Manna-core\projects\manna-snips\docs\screenshots\main-window.png`
  - `D:\Manna-core\projects\manna-snips\docs\screenshots\editor-window.png`
- added reusable preview/capture helpers:
  - `D:\Manna-core\projects\manna-snips\scripts\launch_readme_preview.py`
  - `D:\Manna-core\projects\manna-snips\scripts\capture-readme-assets.ps1`
- updated `README.md` to show the real app surface and document screenshot regeneration
- initialized a real local git repository under `projects\manna-snips`
- installed local publish prerequisites:
  - Git for Windows
  - GitHub CLI
- current GitHub-side blocker is now specific and honest:
  - `gh` is installed, but `gh auth status` says no GitHub host is logged in yet
  - actual repo creation and push can continue immediately after GitHub CLI authentication is completed
