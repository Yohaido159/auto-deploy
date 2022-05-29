from typing import Protocol
from pathlib import Path

from config.config import ConfigLoader


class Executable(Protocol):
    def execute(self) -> None:
        ...


class Executor:
    def __init__(self, config_loader: ConfigLoader) -> None:
        self.config = config_loader.load_config()

    def execute(self, executable: Executable) -> None:
        executable.execute()
