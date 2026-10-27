import abc


class Teleoperator(abc.ABC):
    config_class = None
    name = None

    def __init__(self, config):
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
    def action_features(self) -> dict: ...

    @property
    @abc.abstractmethod
    def feedback_features(self) -> dict: ...

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
    def get_action(self) -> dict: ...

    @abc.abstractmethod
    def send_feedback(self, feedback: dict) -> None: ...

    @abc.abstractmethod
    def disconnect(self) -> None: ...
