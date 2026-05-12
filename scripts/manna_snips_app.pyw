from __future__ import annotations

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

PROFILE_ENV_VAR = "MANNA_SNIPS_PROFILE"


def split_profile_args(argv: list[str]) -> tuple[list[str], str | None]:
    forward: list[str] = []
    profile: str | None = None
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--profile" and index + 1 < len(argv):
            profile = argv[index + 1].strip()
            index += 2
            continue
        forward.append(arg)
        index += 1
    return forward, profile


forward_args, selected_profile = split_profile_args(sys.argv[1:])
if selected_profile:
    os.environ[PROFILE_ENV_VAR] = selected_profile

from manna_snips.app import main


if __name__ == "__main__":
    raise SystemExit(main(forward_args))
