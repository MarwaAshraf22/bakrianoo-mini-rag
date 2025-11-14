from pathlib import Path
from uuid import uuid4

import regex as re
from fastapi import UploadFile

from controllers.base import BaseController
from models import ResponseSignal


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024  # Bytes to Megabytes

    def validate_uploaded_file(self, file: UploadFile) -> bool:
        allowed_types = self.settings.FILE_ALLOWED_TYPES
        max_size_mb = self.settings.FILE_MAX_SIZE_MB

        if file.content_type not in allowed_types:
            raise ValueError(ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value)

        if file.size > (self.size_scale * max_size_mb):
            raise ValueError(ResponseSignal.FILE_SIZE_EXCEEDED.value)

        return True

    def generate_unique_filename(self, original_filename: str) -> str:
        unique_id = uuid4().hex
        extension = Path(original_filename).suffix
        normalised_filename = self.normalise_filename(Path(original_filename).stem)
        unique_filename = f"{normalised_filename}_{unique_id}{extension}"
        return unique_filename

    def normalise_filename(self, filename: str) -> str:
        pattern = r"[^\w.-]"
        return re.sub(pattern, "_", filename)
