from yaml import load, CLoader

__all__ = ['ConfigurationFile']


class ConfigurationFile:
    def __init__(self, config_path: str) -> None:
        self.config_path: str = config_path
        self.config: dict = self.load_config()

    def load_config(self) -> dict:
        with open(self.config_path, "r") as file:
            return load(file, CLoader)

    def get_config(self) -> dict:
        return self.config
