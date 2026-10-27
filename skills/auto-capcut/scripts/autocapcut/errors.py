"""Structured errors at the public workflow boundary."""


class AutoCapcutError(Exception):
    def __init__(self, code: str, message: str, recovery: str = ""):
        super().__init__(message)
        self.code = code
        self.recovery = recovery

    def to_dict(self) -> dict:
        return {"code": self.code, "human_message": str(self), "recover_action": self.recovery}
