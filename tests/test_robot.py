"""Mode 3: this computer drives the arm (here, the pretend arm)."""
import time
import unittest
from unittest import mock

import bootstrap  # noqa: F401  (sets up the import paths)
from helpers import PORT, release_everything, wait_for
from lerobot_robot_sixeyes import SixEyesRobot, SixEyesRobotConfig
from sixeyes_host import ArmError, JOINTS, Capability, pool
from sixeyes_host.link import SimLink
from sixeyes_host.session import Arm
from sixeyes_host.sim import SimArm


def make(**kw):
    return SixEyesRobot(SixEyesRobotConfig(port=PORT, **kw))


class FeaturesTests(unittest.TestCase):
    def test_observation_and_action_features_use_the_joint_names(self):
        robot = make()
        keys = [f"{j}.pos" for j in JOINTS]
        self.assertEqual(list(robot.action_features), keys)
        self.assertEqual(list(robot.observation_features), keys)
        self.assertTrue(all(t is float for t in robot.action_features.values()))
        self.assertEqual(JOINTS, ("base", "shoulder", "elbow", "wrist_pitch", "wrist_roll", "gripper"))

    def test_features_work_before_connecting(self):
        self.assertFalse(make().is_connected)

    def test_the_config_is_registered_under_the_type_name(self):
        from lerobot.robots import RobotConfig

        self.assertIs(RobotConfig.get_known_choices()["sixeyes"], SixEyesRobotConfig)
        self.assertIs(SixEyesRobot.config_class, SixEyesRobotConfig)
        self.assertEqual(SixEyesRobot.name, "sixeyes")


class DriveTests(unittest.TestCase):
    def tearDown(self):
        release_everything()

    def test_connect_homes_the_arm_and_disconnect_lets_go(self):
        robot = make()
        robot.connect()
        self.assertTrue(robot.is_connected)
        self.assertTrue(robot.is_calibrated)  # for this arm, calibrated means homed
        self.assertEqual(pool.users(PORT), 1)
        robot.disconnect()
        self.assertFalse(robot.is_connected)
        self.assertEqual(pool.users(PORT), 0)

    def test_observation_has_every_joint_as_a_float(self):
        with make() as robot:
            obs = robot.get_observation()
            self.assertEqual(sorted(obs), sorted(robot.observation_features))
            self.assertTrue(all(isinstance(v, float) for v in obs.values()))

    def test_send_action_moves_the_arm(self):
        with make() as robot:
            action = {f"{j}.pos": v for j, v in zip(JOINTS, [0.2, 0.1, 0.0, 0.0, 0.0, 30.0])}
            sent = robot.send_action(action)
            self.assertEqual(sent, action)  # within the step limit, so unchanged
            wait_for(lambda: abs(robot.get_observation()["base.pos"] - 0.2) < 0.01, what="the base to arrive")
            self.assertAlmostEqual(robot.get_observation()["gripper.pos"], 30.0, delta=0.5)

    def test_a_big_jump_is_cut_down_to_the_step_limit(self):
        with make() as robot:
            wanted = {f"{j}.pos": 0.0 for j in JOINTS}
            wanted["base.pos"] = 2.0
            wanted["gripper.pos"] = 100.0
            sent = robot.send_action(wanted)
            self.assertAlmostEqual(sent["base.pos"], 0.35)  # max_step_rad
            self.assertAlmostEqual(sent["gripper.pos"], 35.0)  # max_step_gripper
            time.sleep(0.05)
            self.assertAlmostEqual(robot._arm.state.target[0], 0.35, places=3)

    def test_the_step_limit_can_be_switched_off(self):
        with make(max_step_rad=None, max_step_gripper=None) as robot:
            wanted = {f"{j}.pos": 0.0 for j in JOINTS}
            wanted["base.pos"] = 2.0
            self.assertAlmostEqual(robot.send_action(wanted)["base.pos"], 2.0)

    def test_a_policy_loop_streams_actions_without_tripping_the_watchdog(self):
        with make() as robot:
            for i in range(40):  # 40 steps at about 30 Hz
                robot.send_action({**{f"{j}.pos": 0.0 for j in JOINTS}, "base.pos": 0.01 * i})
                time.sleep(1 / 30)
            self.assertFalse(robot._arm.state.faults)
            wait_for(lambda: robot._arm.state.homing_state == 2, what="still ready")

    def test_not_homed_gives_a_plain_message(self):
        robot = make()
        robot.connect(calibrate=False)
        self.assertFalse(robot.is_calibrated)
        with self.assertRaises(ArmError) as cm:
            robot.send_action({f"{j}.pos": 0.0 for j in JOINTS})
        self.assertIn("not homed", str(cm.exception))

    def test_connecting_twice_is_refused(self):
        robot = make()
        robot.connect()
        with self.assertRaises(ConnectionError):
            robot.connect()

    def test_stale_data_from_the_arm_is_an_error_not_silence(self):
        with make() as robot:
            robot._arm._state_time = time.monotonic() - 5  # pretend the arm went quiet
            with self.assertRaises(ConnectionError) as cm:
                robot.get_observation()
            self.assertIn("USB cable", str(cm.exception))

    def test_not_connected_errors(self):
        robot = make()
        with self.assertRaises(ConnectionError):
            robot.get_observation()
        with self.assertRaises(ConnectionError):
            robot.send_action({})

    def test_firmware_that_cannot_home_is_refused_and_nothing_stays_open(self):
        weak = Arm(SimLink(SimArm(capabilities=Capability.ble)))
        with mock.patch("lerobot_robot_sixeyes.sixeyes.pool.acquire", return_value=weak):
            robot = make()
            with self.assertRaises(ConnectionError) as cm:
                robot.connect()
        self.assertIn("cannot home", str(cm.exception))
        self.assertFalse(robot.is_connected)
        weak.close()


class CameraTests(unittest.TestCase):
    """Cameras need the stand-in's simple camera config; the real LeRobot builds its own (see appendix)."""

    def tearDown(self):
        release_everything()

    @unittest.skipUnless(bootstrap.USING_STUB, "uses a fake camera config that only the stand-in understands")
    def test_cameras_appear_in_the_features_and_the_observation(self):
        class FakeCamera:
            height, width, is_connected = 480, 640, False

            def connect(self):
                self.is_connected = True

            def disconnect(self):
                self.is_connected = False

            def async_read(self):
                return "frame"

        class FakeCameraConfig:
            def make(self):
                return FakeCamera()

        robot = SixEyesRobot(SixEyesRobotConfig(port=PORT, cameras={"wrist": FakeCameraConfig()}))
        self.assertEqual(robot.observation_features["wrist"], (480, 640, 3))
        robot.connect()
        self.assertEqual(robot.get_observation()["wrist"], "frame")
        robot.disconnect()
        self.assertFalse(robot.cameras["wrist"].is_connected)


if __name__ == "__main__":
    unittest.main()
