from dataclasses import dataclass
from pathlib import Path


@dataclass(kw_only=True)
class TeleoperatorConfig:
    id: str | None = None
    calibration_dir: Path | None = None

    _choices = {}

    @classmethod
    def register_subclass(cls, name):
        def wrap(sub):
            TeleoperatorConfig._choices[name] = sub
            return sub

        return wrap

    @classmethod
    def get_known_choices(cls):
        return dict(TeleoperatorConfig._choices)
