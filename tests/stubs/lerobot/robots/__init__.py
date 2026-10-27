import abc
from dataclasses import dataclass
from pathlib import Path


@dataclass(kw_only=True)
class RobotConfig:
    id: str | None = None
    calibration_dir: Path | None = None

    _choices = {}

    @classmethod
    def register_subclass(cls, name):
        def wrap(sub):
            RobotConfig._choices[name] = sub
            return sub

        return wrap

    @classmethod
    def get_known_choices(cls):
        return dict(RobotConfig._choices)


class Robot(abc.ABC):
    config_class = None
    name = None

    def __init__(self, config):
        self.robot_type = self.name
        self.id = config.id
        self.calibration = {}

    def __str__(self):
        return f"{self.id} {self.__class__.__name__}"

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *exc):
        self.disconnect()

    @property
    @abc.abstractmethod
    def observation_features(self) -> dict: ...

    @property
    @abc.abstractmethod
    def action_features(self) -> dict: ...

    @property
    @abc.abstractmethod
    def is_connected(self) -> bool: ...

    @abc.abstractmethod
    def connect(self, calibrate: bool = True) -> None: ...

    @property
    @abc.abstractmethod
    def is_calibrated(self) -> bool: ...

    @abc.abstractmethod
    def calibrate(self) -> None: ...

    @abc.abstractmethod
    def configure(self) -> None: ...

    @abc.abstractmethod
    def get_observation(self) -> dict: ...

    @abc.abstractmethod
    def send_action(self, action: dict) -> dict: ...

    @abc.abstractmethod
    def disconnect(self) -> None: ...
