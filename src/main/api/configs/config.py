from pathlib import Path
from typing import Any


class Config:

    _instance = None
    _dictionary: dict[str, str] = {}

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super().__new__(cls)

            config_path = (
                Path(__file__).resolve().parents[4]
                / "resources"
                / "urls.properties"
            )

            if not config_path.exists():
                raise FileNotFoundError(
                    f"Config file was not found: {config_path}"
                )

            with config_path.open(
                mode="r",
                encoding="utf-8"
            ) as file:

                for line in file:
                    line = line.strip()

                    if not line or line.startswith("#"):
                        continue

                    if "=" not in line:
                        continue

                    key, value = line.split("=", maxsplit=1)

                    cls._dictionary[key.strip()] = value.strip()

        return cls._instance

    @classmethod
    def fetch(
        cls,
        key: str,
        default_value: Any = None
    ) -> Any:

        # Ensure that the configuration file is loaded
        cls()

        return cls._dictionary.get(
            key,
            default_value
        )