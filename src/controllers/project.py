from pathlib import Path

from controllers.base import BaseController


class ProjectController(BaseController):
    def __init__(self):
        super().__init__()

    def get_dir_project(self, projectid: str) -> Path:
        dir_project = self.dir_files / str(projectid)
        dir_project.mkdir(parents=True, exist_ok=True)
        return dir_project
