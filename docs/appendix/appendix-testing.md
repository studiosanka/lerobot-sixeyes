# Appendix: testing

## What the tests cover (23, all against the practice arm)

| File | What |
|---|---|
| `tests/test_robot.py` | features, connect and home, observation, `send_action`, the per-step limit, a 30 Hz loop, errors in plain words, stale data, firmware that cannot home, cameras (stand-in only) |
| `tests/test_teleoperator.py` | registration, lines up with the robot's actions, reads what a phone commands, firmware without echo is refused |
| `tests/test_mode2.py` | end to end: robot (listen only) and teleoperator share one connection while a pretend phone drives; the recorded actions match the phone and the observation follows; the laptop cannot move the arm |

Run: `python -m unittest discover -s tests` from the repo root. With Python 3.12 and LeRobot installed they run against the real LeRobot; otherwise the stand-in is used (the first line of output of a failing test says which).

## CI

- `stand-in`: Python 3.10 and 3.12 on Linux, Windows and macOS, no LeRobot.
- `real-lerobot`: Python 3.12 with `pip install lerobot`, then the same tests, plus a check that both plugins register under `sixeyes` and `sixeyes_passthrough`.

Neither has run yet (the repo is not on GitHub).

## Checklist for a first real run (needs the arm with the new firmware)

1. `sixeyes-bringup info COM5` shows capabilities `homing`, `ble`, `echo_targets`.
2. **Mode 3 with nothing attached to the gearbox:** `--robot.type=sixeyes`; the arm homes; send a small action; check each joint moves the right way and the step limit holds.
3. **Mode 2:** phone connected, `listen_only`; drive with the phone and watch the recorded action match; check the arm does not move when the laptop starts.
4. Camera frames are recorded in step with the joints (check timestamps in the dataset).
5. Unplug the USB cable during a Mode 3 episode: the arm must stop within a fraction of a second, and the program must report "No recent data".
6. Run on Windows, macOS and Linux; serial port names differ (`COM5`, `/dev/cu.usbmodem...`, `/dev/ttyACM0`).
