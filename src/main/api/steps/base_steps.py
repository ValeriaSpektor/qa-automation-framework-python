from typing import Any


class BaseSteps:

    def __init__(
        self,
        created_obj: list[Any] | None = None
    ):
        self.created_obj = (
            created_obj
            if created_obj is not None
            else []
        )