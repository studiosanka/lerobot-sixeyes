"""The SixEyes arm as a LeRobot robot.

Joint values are the same ones the arm and the phone page use: five angles in radians at the output shaft
(base, shoulder, elbow, wrist_pitch, wrist_roll) and the gripper as 0..100. Observation keys and action keys
are the same names with ".pos" added, for example "base.pos".

Mode 3 (a policy drives the arm): this computer takes control over USB, homes the arm, and sends targets.
Mode 2 (recording while a phone drives): set listen_only; see lerobot_teleoperator_sixeyes.
"""
import logging
from typing import Any

from lerobot.cameras import make_cameras_from_configs
from lerobot.robots import Robot
from sixeyes_host import JOINTS, Capability, HomingState, pool

from .config_sixeyes import SixEyesRobotConfig

log = logging.getLogger(__name__)

# How old the newest state from the arm may be before we stop trusting it, in seconds.
MAX_STATE_AGE_S = 0.5


class SixEyesRobot(Robot):
    config_class = SixEyesRobotConfig
    name = "sixeyes"

    def __init__(self, config: SixEyesRobotConfig):
        super().__init__(config)
        self.config = config
        self.cameras = make_cameras_from_configs(config.cameras)
        self._arm = None

    # ------------------------------------------------------------ what the robot offers
    @property
    def _joints_ft(self) -> dict[str, type]:
        return {f"{j}.pos": float for j in JOINTS}

    @property
    def _cameras_ft(self) -> dict[str, tuple]:
        return {cam: (self.cameras[cam].height, self.cameras[cam].width, 3) for cam in self.cameras}

    @property
    def observation_features(self) -> dict:
        return {**self._joints_ft, **self._cameras_ft}

    @property
    def action_features(self) -> dict:
        return self._joints_ft

    # ------------------------------------------------------------ connection
    @property
    def is_connected(self) -> bool:
        return self._arm is not None and all(cam.is_connected for cam in self.cameras.values())

    def connect(self, calibrate: bool = True) -> None:
        if self._arm is not None:
            raise ConnectionError(f"{self} is already connected.")
        arm = pool.acquire(self.config.port)
        try:
            if not (arm.info.capabilities & Capability.homing):
                raise ConnectionError("This arm's firmware cannot home yet, so it cannot be driven from a computer.")
            if not self.config.listen_only:
                arm.set_control("usb")  # this computer is now in charge; refused while the arm is moving
            self._arm = arm
            if calibrate and not self.is_calibrated:
                self.calibrate()
            for cam in self.cameras.values():
                cam.connect()
        except Exception:
            self._arm = None
            pool.release(self.config.port)
            raise
        self.configure()

    def disconnect(self) -> None:
        if self._arm is None:
            return
        for cam in self.cameras.values():
            if cam.is_connected:
                cam.disconnect()
        self._arm = None
        pool.release(self.config.port)

    # ------------------------------------------------------------ calibration: for this arm that means homing
    @property
    def is_calibrated(self) -> bool:
        return self._arm is not None and self._arm.state is not None and self._arm.state.homing_state == HomingState.ready

    def calibrate(self) -> None:
        if self.config.listen_only:
            log.info("listen_only: the phone homes the arm, not this computer.")
            return
        log.info("Homing the arm. Keep clear of it.")
        self._arm.home()

    def configure(self) -> None:
        pass  # nothing to set up: the arm's limits and speeds live in its firmware

    # ------------------------------------------------------------ the control loop
    def get_observation(self) -> dict[str, Any]:
        if self._arm is None:
            raise ConnectionError(f"{self} is not connected.")
        if self._arm.state_age > MAX_STATE_AGE_S:
            raise ConnectionError("No recent data from the arm. Check the USB cable and that the arm is powered.")
        obs = {f"{j}.pos": float(v) for j, v in zip(JOINTS, self._arm.state.measured)}
        for name, cam in self.cameras.items():
            obs[name] = cam.async_read()
        return obs

    def send_action(self, action: dict[str, Any]) -> dict[str, Any]:
        """Send joint targets. Returns what was really sent, after the per-step safety limit."""
        if self._arm is None:
            raise ConnectionError(f"{self} is not connected.")
        if self.config.listen_only:
            return action  # Mode 2: the phone is driving; a computer must not send anything
        measured = self._arm.state.measured
        goal = []
        for i, joint in enumerate(JOINTS):
            value = float(action[f"{joint}.pos"])
            limit = self.config.max_step_gripper if joint == "gripper" else self.config.max_step_rad
            if limit is not None:
                value = min(max(value, measured[i] - limit), measured[i] + limit)
            goal.append(value)
        self._arm.send_targets(goal)  # raises ArmError, in plain words, if the arm refuses
        return {f"{j}.pos": v for j, v in zip(JOINTS, goal)}
