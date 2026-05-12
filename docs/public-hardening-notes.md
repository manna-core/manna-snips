# Public Hardening Notes

## What Was Hardened For The Standalone Surface

- settings moved to local app-data
- temp scratch moved to local app-data
- default download root moved to the user's `Downloads\Manna Snips`
- copy and download behavior clearly separated
- frozen release now resolves helpers and icons through the bundled runtime root
- packaged fresh-profile testing is now supported through `--profile public-test`
- the main app now exposes the downloads folder, install location, and app-data location more explicitly
- the main app now also exposes `Start with Windows` directly so that installer-time startup is not a one-shot choice
- an Inno Setup installer build path now exists and supports install-directory choice
- the installer now uses the source app plus a bundled Python runtime instead of depending on the old direct portable EXE as the main launch path
- the installer now forces the welcome page and install-directory page and exposes `Start with Windows after install` on the welcome screen
- Windows auto-start now launches minimized instead of throwing the full app open at sign-in
- the app now exposes a compact preset-based hotkey picker so busy desktops can move off `Ctrl+Shift+S` without editing files or registry values
- release scripts now emit SHA-256 sidecar files for the public installer and release zip
- installer staging now rebuilds cleanly each run so stale files do not linger into new release artifacts

## What Still Needs Care

- packaging validation on a clean machine
- packaged-launch safety after the Explorer/User32 power-off incident
- README screenshots and friendlier first-run docs

## Public Messaging Truths

- Windows only
- local-first
- no telemetry
- no cloud sync
- no hidden auto-save on copy
