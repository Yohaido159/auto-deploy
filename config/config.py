import json
from pathlib import Path
from typing import Protocol
from dataclasses import dataclass


@dataclass
class Config:
    config_location: str
    lambda_zip_path: str
    django_project_path: str
    lambda_layer_zip_path: str
    react_path: str
    project_name: str
    bucket_name: str
    generated_files: str
    utils_path: str


class ConfigLoader(Protocol):
    def load_config(self) -> Config:
        ...


class ConfigLoaderJson:
    def __init__(self, path) -> None:
        self.path = path

    def load_config(self) -> Config:
        file = Path(self.path).read_text()
        config = json.loads(file)
        return Config(**config)
