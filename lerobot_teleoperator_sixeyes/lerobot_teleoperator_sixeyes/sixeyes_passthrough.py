"""A "teleoperator" that is really the phone, seen through the arm.

In Mode 2 a phone drives the arm over Bluetooth, and this computer only records. LeRobot needs the *action*
(what was commanded) as well as the observation (what the arm measured). The computer never sees the phone's
commands directly, but the arm echoes the last target it accepted in every state message over USB.
get_action() returns that echo, so the recorded action is in joint space, exactly like what a policy outputs
in Mode 3.

Use it together with the robot in listen-only mode (`--robot.listen_only=true`): the robot reads the measured
joints and the cameras, and sends nothing.
"""
from typing import Any

from lerobot.teleoperators.teleoperator import Teleoperator
from sixeyes_host import JOINTS, Capability, pool

from .config_sixeyes_passthrough import SixEyesPassthroughConfig

MAX_STATE_AGE_S = 0.5


class SixEyesPassthrough(Teleoperator):
    config_class = SixEyesPassthroughConfig
    name = "sixeyes_passthrough"

    def __init__(self, config: SixEyesPassthroughConfig):
        super().__init__(config)
        self.config = config
        self._arm = None

    @property
    def action_features(self) -> dict:
        # Same names as the robot's actions, so the recorded dataset lines up.
        return {f"{j}.pos": float for j in JOINTS}

    @property
    def feedback_features(self) -> dict:
        return {}

    @property
    def is_connected(self) -> bool:
        return self._arm is not None

    def connect(self, calibrate: bool = True) -> None:
        if self._arm is not None:
            raise ConnectionError(f"{self} is already connected.")
        arm = pool.acquire(self.config.port)
        if not (arm.info.capabilities & Capability.echo_targets):
            pool.release(self.config.port)
            raise ConnectionError(
                "This arm's firmware cannot echo the phone's targets over USB (capability echo_targets), "
                "so Mode 2 recording is not possible. Update the firmware."
            )
        self._arm = arm

    @property
    def is_calibrated(self) -> bool:
        return True  # nothing to calibrate: the phone and the arm do that

    def calibrate(self) -> None:
        pass

    def configure(self) -> None:
        pass

    def get_action(self) -> dict[str, Any]:
        if self._arm is None:
            raise ConnectionError(f"{self} is not connected.")
        if self._arm.state_age > MAX_STATE_AGE_S:
            raise ConnectionError("No recent data from the arm. Check the USB cable and that the arm is powered.")
        return {f"{j}.pos": float(v) for j, v in zip(JOINTS, self._arm.state.target)}

    def send_feedback(self, feedback: dict[str, Any]) -> None:
        pass  # the phone has no motors to give feedback on

    def disconnect(self) -> None:
        if self._arm is None:
            return
        self._arm = None
        pool.release(self.config.port)
