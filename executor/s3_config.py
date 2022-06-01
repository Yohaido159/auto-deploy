from dataclasses import dataclass
from pathlib import Path


@dataclass
class S3Config:
    bucket_name: str
    from_path: Path
    key: str
    file_or_folder: str
    acl: str
