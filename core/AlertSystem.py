# ---------- core/AlertSystem.py ----------
"""
Sends real-time alerts and notifications.
"""
import logging


class AlertSystem:
    def __init__(self) -> None:
        self.logger = logging.getLogger("AlertSystem")

    def send(self, message: str) -> None:
        self.logger.info("ALERT: %s", message)
