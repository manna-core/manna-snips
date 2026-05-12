# Release Plan

## Goal

Ship the first public GitHub-ready version of `Manna Snips` as a small Windows utility.

## Release Shape

- Windows-first
- Python source repo
- Inno Setup installer artifact as the preferred public lane
- bundled local Python runtime inside the installer
- PyInstaller `onedir` desktop build as a secondary advanced lane
- versioned zip artifact for GitHub releases
- local-first privacy posture
- preferred launch path: bundled-runtime installer

## Pre-Release Checklist

- app launches from the standalone project surface
- smoke mode works
- compile check works
- copy flow works
- explicit download flow works
- shortcut creation works
- packaged `onedir` release works
- packaged `--profile public-test` path works
- installer build works
- installer silent-install smoke works
- installed-app launch smoke works
- installed minimized-launch smoke works
- installer and release artifacts emit SHA-256 sidecar files
- installer welcome page and install-directory UX feel right in a real human pass
- startup can be managed again from inside the app after install
- README is enough for a stranger to run it
- privacy model is stated clearly

## First Maintenance Release Candidate

- configurable hotkey rebinding for busy Windows desktops
- keep installer-first release messaging simple
- preserve the copy-first model while hardening the real daily-use friction points

## Not Required For First Release

- onefile packaging
- updater
- tray mode
- cloud sync
