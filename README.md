# Manna Snips

Copy-first Windows screenshots with lightweight markup.

`Manna Snips` is built for one fast path:

1. Take a snip.
2. Mark it up if needed.
3. Copy it.
4. Paste it where you need it.

Downloads are explicit. Copy stays temporary.

## Preview

![Manna Snips main window](docs/screenshots/main-window.png)

![Manna Snips editor](docs/screenshots/editor-window.png)

## Install

Use the Windows installer:

- `dist\installer\MannaSnips-0.1.0-Setup.exe`

The installer:

- lets you choose the install folder
- can enable `Start with Windows after install`
- installs the app with a bundled local Python runtime

Inside the app, you can also:

- change the downloads folder
- turn `Start with Windows` on or off later
- see the install folder
- see the settings and temp folder

If `Start with Windows` is enabled, `Manna Snips` launches minimized to the taskbar.

## Use

1. Open `Manna Snips`.
2. Leave it open or minimized.
3. Press `Ctrl+Shift+S`.
4. Drag a region.
5. Copy it back to the clipboard.
6. Paste with `Ctrl+V`.

Main behavior:

- `Copy` is temporary and clipboard-first.
- `Download` is the only path that creates a durable PNG on disk.
- Scratch files are disposable and cleaned automatically.

## What It Does

- Global `Ctrl+Shift+S` capture while the app is running
- Custom drag-to-select overlay
- Lightweight built-in editor
- Pen, highlight, rectangle, and arrow tools
- Clipboard-first export
- Explicit PNG download path
- Local-only state and scratch files

## Platform

- Windows
- Python `3.11+`

## Fresh Profile Testing

If you want to test the app like a new user on the same machine:

```powershell
py -3 scripts\manna_snips_app.pyw --profile public-test
```

That keeps settings, temp files, and default downloads separate from the default profile.

## Local Development

Run from source:

```powershell
py -3 scripts\manna_snips_app.pyw
```

Smoke:

```powershell
py -3 scripts\manna_snips_app.pyw --smoke
```

Fresh-profile smoke:

```powershell
py -3 scripts\manna_snips_app.pyw --profile public-test --smoke
```

Version:

```powershell
py -3 scripts\manna_snips_app.pyw --version
```

Compile check:

```powershell
py -3 -m py_compile src\manna_snips\app.py scripts\manna_snips_app.pyw
```

Refresh the README screenshots:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\capture-readme-assets.ps1
```

## Build The Installer

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-installer.ps1
```

That script builds:

- the installer under `dist\installer\`
- a SHA-256 file for the installer beside it

This is the preferred public release path.

## Advanced: Portable Build

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-release.ps1
```

That script builds:

- a PyInstaller `onedir` folder under `dist\MannaSnips`
- a versioned zip under `dist\`
- a SHA-256 file for the release zip beside it

The portable build is still a secondary lane. The installer is the preferred release shape.

## Privacy

`Manna Snips` is designed as a local-first tool:

- no telemetry
- no cloud sync
- no automatic uploads
- no account system

See [PRIVACY.md](PRIVACY.md).
