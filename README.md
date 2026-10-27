# lerobot-sixeyes

Use a [SixEyes](https://github.com/studiosanka/sixeyes) robot arm with [LeRobot](https://github.com/huggingface/lerobot): record training data, train a policy, and let the policy drive the arm.

> **Work in progress.** Everything works against the built-in practice arm, using a stand-in for LeRobot. It has **not** been run with the real LeRobot or a real arm yet.

Two small plugins, because LeRobot wants one package per device:

| Package | LeRobot name | Mode |
|---|---|---|
| `lerobot_robot_sixeyes` | `--robot.type=sixeyes` | **3:** a policy drives the arm. Also **2:** listen only |
| `lerobot_teleoperator_sixeyes` | `--teleop.type=sixeyes_passthrough` | **2:** record what the phone commands |

## Install

LeRobot needs Python 3.12 or newer.

```
pip install lerobot
pip install "sixeyes-host @ git+https://github.com/studiosanka/sixeyes-host.git#subdirectory=python"
pip install -e lerobot_robot_sixeyes -e lerobot_teleoperator_sixeyes
```

Find the arm's port with `sixeyes-bringup ports` (for example `COM5`).

## Mode 2: record while a phone drives

The phone drives the arm over Bluetooth. This computer only listens (USB) and records, with the wrist camera.

```
lerobot-record --robot.type=sixeyes --robot.port=COM5 --robot.listen_only=true \
  --teleop.type=sixeyes_passthrough --teleop.port=COM5 \
  --dataset.repo_id=YOUR_NAME/sixeyes-demo --dataset.single_task="Pick up the block"
```

Add your wrist camera with `--robot.cameras=...` as for any LeRobot robot. Home the arm from the phone first.

## Mode 3: a trained policy drives the arm

This computer takes control over USB, homes the arm, and sends joint targets. Run your policy the usual LeRobot way, with `--robot.type=sixeyes --robot.port=COM5`. Each step is limited to a small move for safety (`--robot.max_step_rad`, `--robot.max_step_gripper`).

## Status

| Part | State |
|---|---|
| Robot and teleoperator plugins | ✅ written, 23 tests against the practice arm |
| Real LeRobot (Python 3.12+) | ⬜ not run yet; CI will do it ([why](docs/appendix/appendix-lerobot-contract.md)) |
| A real arm | ⬜ the firmware is written but not run on hardware |
| Windows, macOS, Linux | 🚧 CI matrix written, not run yet |

## More

[Getting started](docs/getting-started.md) · [How it works](docs/appendix/appendix-how-it-works.md) · [What was checked against LeRobot](docs/appendix/appendix-lerobot-contract.md) · [Testing](docs/appendix/appendix-testing.md) · [Contributing](CONTRIBUTING.md) · Licence: Apache-2.0

Built by [Studio Sanka](https://github.com/studiosanka). Developed with AI assistance from [Claude](https://www.anthropic.com/claude) (Anthropic); the designs, decisions and review are by the Studio Sanka team.
