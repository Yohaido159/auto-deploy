from pathlib import Path
import os
import subprocess
from subprocess import PIPE, check_output, STDOUT
from dataclasses import dataclass, field


@dataclass
class OsConfig:
    docker_path: Path


class OSExecutable:
    def __init__(self, django_path):
        self.django_path = django_path

    def execute(self) -> None:
        excludes = [
            'boto3',
            'botocore',
            'django-tenants',
        ]
