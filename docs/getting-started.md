# Getting started

The idea in three steps: **show** the arm what to do, **train** a policy from the recordings, **let it drive**.

## 0. Try it without an arm

You can run every command against the built-in practice arm by using the port `sim` (for example `--robot.port=sim`). Nothing moves in real life. It is the quickest way to check your install.

## 1. Show the arm (Mode 2)

1. Switch the arm on, pair your phone, and open the SixEyes Drive page. Press **Home**.
2. Plug the arm's Base board into this computer with a USB data cable and find its port: `sixeyes-bringup ports`.
3. Start `lerobot-record` as in the [README](../README.md#mode-2-record-while-a-phone-drives).
4. Drive the arm with the phone to do the task. Each episode is saved as camera pictures plus joint positions plus what you commanded.

Tips: do the task the same way each time; 20 to 50 good episodes is a normal starting point.

## 2. Train

Train with LeRobot as usual on the recorded dataset (`lerobot-train`). The arm's values are in joint space (angles in radians, gripper 0 to 100), the same space a policy outputs later.

## 3. Let the policy drive (Mode 3)

1. Disconnect the phone from driving (or switch Bluetooth off on it). Only one device is in control at a time.
2. Run your policy with `--robot.type=sixeyes --robot.port=COM5`. The computer homes the arm first: **keep clear of it**.
3. **Stop** by closing the program, pressing the BOOT button on any board, or pressing Stop on the phone page. The arm also stops by itself if the computer goes quiet for a fraction of a second.

## If something goes wrong

| Message | What to do |
|---|---|
| "The arm is not homed yet" | Home it (the phone in Mode 2; this program does it in Mode 3) |
| "Another source is in control" | Disconnect the phone, or switch the arm off and on |
| "No recent data from the arm" | Check the USB cable and that the arm is powered |
| "cannot echo the phone's targets" | The arm's firmware is too old for Mode 2; update it |

More depth: [how it works](appendix/appendix-how-it-works.md).
