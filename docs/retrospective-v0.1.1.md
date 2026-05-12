# Manna Snips Retrospective

Scope: work completed between the first local utility pass and the public `v0.1.1` maintenance release on `2026-05-12`.

## What Went Well

- The core product truth was strong early.
  - `copy first`
  - `download explicitly`
  - `stay local`
  - `stay simple`
- User feedback was fast and concrete.
  - real desktop testing surfaced the hotkey conflict immediately
  - real usage exposed that `copy` still felt like a hidden save-to-disk action
  - real install behavior exposed the difference between source launchers, test installs, and the public path
- The app improved most when the work stayed close to the real job.
  - replacing the Windows snip handoff with a Manna-owned overlay made the tool feel more like a real instrument
  - keeping the editor lightweight preserved speed instead of turning the tool into a heavy graphics app
  - subtracting UI copy made the main window better than adding more teaching chrome
- The standalone-repo move was the right call.
  - it created one real source of truth
  - it made packaging, docs, screenshots, and release notes cleaner
  - it let the root workspace delegate into the project instead of keeping a shadow copy alive
- Verification discipline paid off.
  - source smoke
  - packaged smoke
  - installer smoke
  - isolated-profile testing
  - installed-app testing
  - GitHub release asset confirmation

## What Went Wrong

- The first native Windows handoff was wrong for the product.
  - using the Windows snip UI pulled control away from the real job: quick copy into Manna
  - that path created confusion around whether copy really belonged to Manna Snips or the OS tool
- Packaging trust broke before release confidence was truly earned.
  - the packaged public-test launcher was correlated with a real machine power-off event
  - even without a proven code-level cause, that had to be treated as a release blocker
  - the correct response was quarantine, not rationalization
- Source, packaged, installed, and test copies became too easy to mix up.
  - source launchers
  - packaged EXE builds
  - installer smoke installs
  - GitHub test installs
  - Start Menu shortcuts
  - local state
  - all of those were valid during development, but the machine drift became messy
- Product truth drifted a few times.
  - copy briefly behaved too much like save
  - last-download state carried a legacy repo path that no longer matched the live downloads root
  - those were fixable, but they show how fast small utility UX can become misleading
- Public-state claims need strict proof.
  - when shipping work touches GitHub, install state, or release assets, the state should only move forward after command output proves it
  - machine-external truth should never be inferred from intent

## Best Decisions

- Owning the capture overlay instead of delegating the core flow to Snipping Tool
- Keeping the app in the `Crystal Utility` lane instead of letting it become noisy
- Splitting `copy` from `download` explicitly in both language and behavior
- Preferring the bundled-runtime installer over the less-trusted portable EXE lane
- Adding preset-based hotkey rebinding instead of building a more complex freeform shortcut editor
- Using `--profile public-test` to isolate release-style validation from the daily-driver profile

## Disturbance Minimizers

These are the habits that reduced chaos and should be repeated:

- Keep one source of truth for the app code.
- Label test surfaces clearly:
  - `public-test`
  - `install-smoke`
  - `release`
  - `source`
- Treat installer smoke installs as disposable and remove them after validation.
- Prefer one recommended public lane.
  - for `Manna Snips`, that is the bundled-runtime installer
- Verify installed behavior, not just built artifacts.
- Keep cleanup part of the release workflow, not an afterthought.

## Rules To Carry Forward

- For small utilities, validate the real user loop before borrowing native OS UI just because it is convenient.
- If the app promise is simple, make the implementation complexity invisible.
- If system-level behavior looks scary, stop and quarantine first.
- Keep source, packaged, installed, and test copies clearly separated in naming, paths, and shortcuts.
- Only claim push, release, or install success after direct tool confirmation.
- When the UI starts getting wordy, subtract first.

## Next Smart Uses Of These Lessons

- Turn the release/testing separation into a reusable checklist for future Manna utilities.
- Keep the root decision memory updated with shipping-truth rules, not just project-specific implementation notes.
- Use `Manna Snips` as the model for:
  - small public utility packaging
  - installer-first Windows releases
  - post-release maintenance releases driven by real friction instead of feature creep
