"""Makes the tests runnable without installing anything.

- LeRobot: uses the real one if it is installed (Python 3.12+), otherwise the stand-in in tests/stubs.
- sixeyes_host: uses the installed one, otherwise the sibling repo's source.
- The two plugin packages are always taken from this repo.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

try:
    import lerobot  # noqa: F401

    USING_STUB = False
except ImportError:
    sys.path.insert(0, str(ROOT / "tests" / "stubs"))
    USING_STUB = True

try:
    import sixeyes_host  # noqa: F401
except ImportError:
    sys.path.insert(0, str(ROOT.parent / "sixeyes-host" / "python" / "src"))

for package in ("lerobot_robot_sixeyes", "lerobot_teleoperator_sixeyes"):
    sys.path.insert(0, str(ROOT / package))
