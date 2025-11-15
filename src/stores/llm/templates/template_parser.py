from pathlib import Path


class TemplateParser:
    def __init__(self, language: str | None = None, default_language: str = "en"):
        self._language = language or default_language
        self.default_language = default_language
        self.cwd = Path(__file__).parent

    @property
    def language(self) -> str:
        return self._language

    @language.setter
    def language(self, value: str):
        dir_language = self.cwd / "locales" / value
        if dir_language.exists() and dir_language.is_dir():
            self._language = value
        else:
            self._language = self.default_language

    def get(self, group: str, key: str, _vars: dict = {}):
        if not (group and key):
            return ""

        group_path = self.cwd / "locales" / self.language / f"{group}.py"
        target = self.language
        if not group_path.exists():
            group_path = self.cwd / "locales" / self.default_language / f"{group}.py"
            target = self.default_language

        if not group_path.exists():
            return ""

        module = __import__(
            f"stores.llm.templates.locales.{target}.{group}", fromlist=[group]
        )

        if not module or not hasattr(module, key):
            return ""

        key_attr = getattr(module, key)
        if not key_attr:
            return ""

        # if _vars:
        #     try:
        #         key_attr = key_attr.substitute(**_vars)
        #     except Exception:
        #         pass

        return key_attr.substitute(**_vars)
