# Appendix: what was checked against LeRobot

LeRobot's API moves quickly, so this records exactly what the plugins were written against and what has **not** been verified.

## Read on 2026-10-27 (LeRobot `main`, version 0.6.2)

- Hugging Face guide "Bring Your Own Hardware" (`docs/lerobot/integrate_hardware`): the four plugin conventions (package prefix, `Config` / device naming, file placement, expose both in `__init__.py`), the `register_subclass` decorator, and a full robot example.
- `src/lerobot/robots/robot.py`: abstract members `observation_features`, `action_features`, `is_connected`, `connect(calibrate=True)`, `is_calibrated`, `calibrate`, `configure`, `get_observation`, `send_action`, `disconnect`.
- `src/lerobot/teleoperators/teleoperator.py`: abstract members `action_features`, `feedback_features`, `is_connected`, `connect(calibrate=True)`, `is_calibrated`, `calibrate`, `configure`, `get_action`, `send_feedback`, `disconnect`.
- `pyproject.toml`: version 0.6.2, **Python 3.12 or newer**, console scripts including `lerobot-record`, `lerobot-teleoperate`, `lerobot-calibrate`.

## The stand-in

The machine this was written on has Python 3.10, so the real LeRobot could not be installed. `tests/stubs/lerobot/` is a small stand-in with the same abstract members and the same `register_subclass` registry. The tests use the real LeRobot if it is importable and the stand-in otherwise, so **the same tests run both ways**. If the stand-in and LeRobot disagree, the real-LeRobot CI job fails.

## Not verified

- Importing against the real LeRobot: the exact import paths (`lerobot.robots.Robot`, `lerobot.teleoperators.teleoperator.Teleoperator`, `lerobot.cameras.make_cameras_from_configs`) come from the guide and sources above, not from running them.
- That `lerobot-record` accepts `--robot.listen_only` and the other plugin fields (it should: the config is a dataclass registered with draccus, like the built-in robots).
- Exact flags of `lerobot-record` and of running a policy on a robot in 0.6.x: check `lerobot-record --help` for your version.
- Real cameras: the camera test only runs with the stand-in. A first real run should include the wrist camera.
- Behaviour of LeRobot's calibration prompt: this arm reports `is_calibrated` from its homing state and never writes a calibration file.

## Pinned version

`lerobot>=0.6.2,<0.7` in both `pyproject.toml` files. Widen only after CI passes on the newer version.
