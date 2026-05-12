# Privacy

`Manna Snips` is intended to be a local-first screenshot tool.

## Current Privacy Model

- Screenshots are captured locally on the machine.
- Clipboard operations happen locally.
- The app does not upload images anywhere.
- The app does not require sign-in.
- The app does not include analytics or telemetry.

## Local Files

The app may write:

- local settings under the current Windows user's local app-data folder
- temporary scratch files used during copy/edit flow
- explicit downloads only when the user chooses to save a PNG

Scratch files are disposable implementation detail and are cleaned automatically.

## Scope

This project currently targets Windows desktop use and does not claim hardened enterprise privacy guarantees.
