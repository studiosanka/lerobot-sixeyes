from dataclasses import dataclass

from lerobot.teleoperators.config import TeleoperatorConfig


@TeleoperatorConfig.register_subclass("sixeyes_passthrough")
@dataclass(kw_only=True)
class SixEyesPassthroughConfig(TeleoperatorConfig):
    """Records what the phone is commanding. Use it with `--teleop.type=sixeyes_passthrough --teleop.port=COM5`."""

    # The same USB port as the robot (`--robot.port`). Both share one connection.
    port: str
