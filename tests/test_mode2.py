"""Mode 2 end to end: a phone drives the arm, this computer records. Both plugins share one USB connection."""
import time
import unittest

import bootstrap  # noqa: F401
from helpers import PORT, Phone, release_everything, wait_for
from lerobot_robot_sixeyes import SixEyesRobot, SixEyesRobotConfig
from lerobot_teleoperator_sixeyes import SixEyesPassthrough, SixEyesPassthroughConfig
from sixeyes_host import JOINTS, pool


class Mode2Tests(unittest.TestCase):
    def tearDown(self):
        release_everything()

    def test_record_while_the_phone_drives(self):
        robot = SixEyesRobot(SixEyesRobotConfig(port=PORT, listen_only=True))
        teleop = SixEyesPassthrough(SixEyesPassthroughConfig(port=PORT))
        phone = Phone()

        # LeRobot connects the robot and the teleoperator separately, to the same port.
        robot.connect()
        teleop.connect()
        self.assertIs(robot._arm, teleop._arm)
        self.assertEqual(pool.users(PORT), 3)  # robot, teleoperator and the phone's side of the test

        # The arm starts unhomed, and the laptop leaves homing to the phone.
        self.assertFalse(robot.is_calibrated)
        self.assertEqual(robot._arm.state.control_source, 0)  # still under the phone's (Bluetooth) control
        phone.home()
        wait_for(lambda: robot.is_calibrated, what="the phone to home the arm")

        # Record a short episode: every step is (observation, action), like lerobot-record does.
        episode = []
        goals = [[0.3, 0.2, 0.1, 0.0, 0.0, 20.0], [0.6, 0.3, -0.2, 0.1, 0.4, 70.0]]
        for goal in goals:
            phone.move_to(goal)
            for _ in range(12):  # keep the phone "alive" and sample at roughly 30 Hz
                phone.move_to(goal)
                action = teleop.get_action()
                obs = robot.get_observation()
                sent = robot.send_action(action)  # lerobot-record sends the teleop action to the robot
                self.assertEqual(sent, action)  # listen_only: returned as is, and not sent
                episode.append((obs, action))
                time.sleep(1 / 30)

        # The action is what the phone commanded; the observation follows it.
        keys = [f"{j}.pos" for j in JOINTS]
        self.assertTrue(all(list(o) == keys and list(a) == keys for o, a in episode))
        last_action = episode[-1][1]
        for j, want in zip(JOINTS, goals[-1]):
            self.assertAlmostEqual(last_action[f"{j}.pos"], want, places=4)
        self.assertGreater(episode[-1][0]["base.pos"], 0.5)  # the arm really moved
        self.assertNotEqual(episode[0][1], episode[-1][1])  # and the action changed over the episode
        self.assertEqual(robot._arm.state.control_source, 0)  # we never took control

        robot.disconnect()
        teleop.disconnect()
        phone.close()
        self.assertEqual(pool.users(PORT), 0)

    def test_the_laptop_cannot_move_the_arm_in_listen_only_mode(self):
        robot = SixEyesRobot(SixEyesRobotConfig(port=PORT, listen_only=True))
        phone = Phone()
        phone.home()
        robot.connect()
        wait_for(lambda: robot.is_calibrated, what="homing")
        before = list(robot._arm.state.target)
        robot.send_action({f"{j}.pos": 1.0 for j in JOINTS})
        time.sleep(0.1)
        self.assertEqual(list(robot._arm.state.target), before)
        robot.disconnect()
        phone.close()


if __name__ == "__main__":
    unittest.main()
