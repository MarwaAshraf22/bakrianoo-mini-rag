from pathlib import Path

from helpers.config import Settings, get_settings


class BaseController:
    def __init__(self):
        self.settings: Settings = get_settings()
        self.dir_base = Path(__file__).parent.resolve()
        self.dir_files = self.dir_base.parent / "assets/files"
        self.dir_db = self.dir_base.parent / "assets/database"

    def get_database_path(self, dbname: str) -> Path:
        db_path = self.dir_db / dbname
        db_path.mkdir(parents=True, exist_ok=True)
        return db_path
