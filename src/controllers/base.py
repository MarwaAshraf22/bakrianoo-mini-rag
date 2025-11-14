from pathlib import Path

from helpers.config import Settings, get_settings


class BaseController:
    def __init__(self):
        self.settings: Settings = get_settings()
        self.dir_base = Path(__file__).parent.resolve()
        self.dir_files = self.dir_base.parent / "assets/files"
