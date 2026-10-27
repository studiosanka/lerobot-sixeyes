"""The passthrough teleoperator on its own."""
import unittest
from unittest import mock

import bootstrap  # noqa: F401
from helpers import PORT, Phone, release_everything, wait_for
from lerobot_robot_sixeyes import SixEyesRobot, SixEyesRobotConfig
from lerobot_teleoperator_sixeyes import SixEyesPassthrough, SixEyesPassthroughConfig
from sixeyes_host import JOINTS, Capability, pool
from sixeyes_host.link import SimLink
from sixeyes_host.session import Arm
from sixeyes_host.sim import SimArm


class TeleoperatorTests(unittest.TestCase):
    def tearDown(self):
        release_everything()

    def make(self):
        return SixEyesPassthrough(SixEyesPassthroughConfig(port=PORT))

    def test_registered_under_the_type_name(self):
        from lerobot.teleoperators.config import TeleoperatorConfig

        self.assertIs(TeleoperatorConfig.get_known_choices()["sixeyes_passthrough"], SixEyesPassthroughConfig)
        self.assertIs(SixEyesPassthrough.config_class, SixEyesPassthroughConfig)
        self.assertEqual(SixEyesPassthrough.name, "sixeyes_passthrough")

    def test_its_actions_line_up_with_the_robots_actions(self):
        teleop = self.make()
        robot = SixEyesRobot(SixEyesRobotConfig(port=PORT))
        self.assertEqual(list(teleop.action_features), list(robot.action_features))
        self.assertEqual(teleop.feedback_features, {})

    def test_connect_disconnect_and_nothing_to_calibrate(self):
        teleop = self.make()
        self.assertFalse(teleop.is_connected)
        teleop.connect()
        self.assertTrue(teleop.is_connected and teleop.is_calibrated)
        teleop.send_feedback({})  # harmless
        teleop.disconnect()
        self.assertFalse(teleop.is_connected)
        self.assertEqual(pool.users(PORT), 0)

    def test_it_reads_what_the_phone_commands(self):
        phone = Phone()
        phone.home()
        with self.make() as teleop:
            wait_for(lambda: teleop._arm.state.homing_state == 2, what="the phone to home the arm")
            phone.move_to([0.4, 0.2, -0.3, 0.1, 0.5, 60.0])
            wait_for(lambda: abs(teleop.get_action()["base.pos"] - 0.4) < 1e-6, what="the echoed target")
            action = teleop.get_action()
            self.assertEqual(list(action), [f"{j}.pos" for j in JOINTS])
            self.assertAlmostEqual(action["gripper.pos"], 60.0, places=3)
            self.assertAlmostEqual(action["elbow.pos"], -0.3, places=5)
        phone.close()

    def test_firmware_without_echo_is_refused_and_nothing_stays_open(self):
        weak = Arm(SimLink(SimArm(capabilities=Capability.homing | Capability.ble)))
        with mock.patch("lerobot_teleoperator_sixeyes.sixeyes_passthrough.pool.acquire", return_value=weak):
            with mock.patch("lerobot_teleoperator_sixeyes.sixeyes_passthrough.pool.release") as release:
                teleop = self.make()
                with self.assertRaises(ConnectionError) as cm:
                    teleop.connect()
                release.assert_called_once()
        self.assertIn("echo", str(cm.exception))
        self.assertFalse(teleop.is_connected)
        weak.close()

    def test_not_connected_errors(self):
        with self.assertRaises(ConnectionError):
            self.make().get_action()


if __name__ == "__main__":
    unittest.main()
