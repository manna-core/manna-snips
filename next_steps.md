# Manna Snips Next Steps

1. Finish the first public release handoff.
   Status: the installer-first local release lane is healthy, rebuilt, verified, and now has real README screenshots.
   Next step: complete GitHub CLI authentication, then create the public repository and push the first release-ready tree.

2. Do one last real human installer pass.
   Status: silent install smoke, installed-app smoke, installed `--version`, and installed minimized-launch smoke all passed.
   Next step: click through the visual installer once more and confirm the welcome-screen startup choice plus install-location page feel clean on the desktop.

3. Keep the safer shipping recommendation honest.
   Status: the bundled-runtime installer is the preferred lane, and the portable PyInstaller build still exists as secondary.
   Next step: keep recommending the installer publicly unless the old portable-build trust question is explicitly revisited and cleared.

4. Keep the public surface simple.
   Status: the app is already in the subtractive `Crystal Utility` lane.
   Next step: if any more UI polish happens, prefer smaller copy and clearer defaults over added panels or extra explanation.

5. Plan the first post-release hardening lane.
   Next step: configurable hotkeys, tray/startup refinement, clean-machine validation, and deeper packaged-launch trust work are the highest-value follow-ups after the first release is out.
