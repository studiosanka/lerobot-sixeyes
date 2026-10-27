from dataclasses import dataclass


@dataclass(kw_only=True)
class CameraConfig:
    fps: int | None = None
    width: int | None = None
    height: int | None = None


def make_cameras_from_configs(camera_configs: dict) -> dict:
    """The real one builds OpenCV and RealSense cameras. The stand-in builds whatever a test config's make() gives."""
    return {name: cfg.make() for name, cfg in camera_configs.items()}
