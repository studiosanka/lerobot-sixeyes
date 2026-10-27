import time

from sixeyes_host import pool
from sixeyes_host import _protocol as p
from sixeyes_host.codec import encode_frame

PORT = "sim:20"  # the pretend arm, running its motion 20 times faster than real life


def wait_for(condition, timeout=5.0, what="the condition"):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if condition():
            return
        time.sleep(0.005)
    raise AssertionError(f"timed out waiting for {what}")


class Phone:
    """Plays the phone: writes to the pretend arm's Bluetooth side, which is where a phone connects."""

    def __init__(self, port=PORT):
        self.link = pool.acquire(port).link
        self.port = port
        self.seq = 0

    def send(self, msg):
        self.seq += 1
        self.link.ble_write(encode_frame(msg.TYPE, self.seq, msg.encode()))

    def home(self):
        self.send(p.Home())

    def move_to(self, joints):
        self.send(p.Targets(joints=tuple(float(v) for v in joints)))

    def close(self):
        pool.release(self.port)


def release_everything(port=PORT):
    while pool.users(port):
        pool.release(port)
