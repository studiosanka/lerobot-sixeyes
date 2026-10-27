from dataclasses import dataclass, field

from lerobot.cameras import CameraConfig
from lerobot.robots import RobotConfig


@RobotConfig.register_subclass("sixeyes")
@dataclass(kw_only=True)
class SixEyesRobotConfig(RobotConfig):
    """Settings for a SixEyes arm. Use it with `--robot.type=sixeyes --robot.port=COM5`."""

    # The arm's USB port, for example COM5 (Windows) or /dev/ttyACM0 (Linux). Find it with `sixeyes-bringup ports`.
    port: str

    # Mode 2 (recording while a phone drives): only listen. The robot never moves the arm and never homes it;
    # the phone does that. Leave False for Mode 3 (a policy drives the arm from this computer).
    listen_only: bool = False

    # Safety for Mode 3: the most any joint may be asked to move in one step. The five angles are in
    # radians, the gripper in its 0..100 units. None switches the limit off.
    max_step_rad: float | None = 0.35
    max_step_gripper: float | None = 35.0

    # Cameras, for example the wrist camera. Same format as every other LeRobot robot.
    cameras: dict[str, CameraConfig] = field(default_factory=dict)
