# Appendix: how it works

## Why two packages

LeRobot finds third-party devices by package name: `lerobot_robot_*` for robots, `lerobot_teleoperator_*` for teleoperators. One installable package can only have one of those prefixes, so this repo holds two small packages. Each has a `FooConfig` class registered with `register_subclass` (that gives the `--robot.type` / `--teleop.type` name) and a `Foo` class, both exposed in `__init__.py`, as LeRobot's guide requires.

## Values and units

Observation and action keys are the six joint names plus `.pos`: `base.pos`, `shoulder.pos`, `elbow.pos`, `wrist_pitch.pos`, `wrist_roll.pos`, `gripper.pos`. Angles are **radians at the output shaft**; the gripper is **0 to 100**. These are the units of the host protocol, so a recorded action and a policy's output are the same kind of number.

"Calibrated" means "homed": `is_calibrated` is true when the arm reports Ready, and `calibrate()` (Mode 3) sends Home. The arm has no calibration file because homing is done by the arm itself on every boot.

## One connection, two objects (the pool)

`lerobot-record` makes a robot object and a teleoperator object. A USB port can be opened only once, so both ask `sixeyes_host.pool` for the port: the first opens it, the last to disconnect closes it.

## Mode 2

- The phone is the source in control (Bluetooth). The robot is created with `listen_only`: it never calls `set_control_source`, never homes, and `send_action` returns the action unchanged without sending anything. (`lerobot-record` calls `send_action` with the teleoperator's action; here that must be harmless.)
- The arm puts the **last target it accepted** in every state message (`state.target`), and streams state to USB as well as Bluetooth. The teleoperator returns it as the action. The observation is `state.measured`.
- The teleoperator refuses to connect if the arm's firmware lacks the `echo_targets` capability.

## Mode 3

- The robot calls `set_control_source(usb)` (refused while the arm is moving), homes the arm if needed, and sends targets with each `send_action`.
- **Per-step limit:** each joint is moved at most `max_step_rad` (default 0.35 rad) or `max_step_gripper` (default 35 units) from where it is now, whatever the policy asks. The arm also clamps to its own joint limits and speeds. The returned action is what was really sent, so the dataset and the arm agree.
- The connection sends a heartbeat every 50 ms while ready, so the arm's 200 ms watchdog stays fed; if the program dies, the heartbeats stop and the arm stops.

## Errors

Anything that goes wrong raises `ConnectionError` or the host library's `ArmError`, with a message in plain words (see the table in [getting started](../getting-started.md)). Data older than 0.5 s counts as "no data".

## What is not done

- Reading the arm's own joint limits (the protocol does not publish them yet); only the step limit is applied here.
- Motion slots (motions stored on the arm) are not used by LeRobot.
- A `sixeyes_ros2` style hardware interface lives in a different repo.
