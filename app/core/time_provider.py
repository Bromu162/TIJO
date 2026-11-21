from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone


class TimeProvider(ABC):
    @abstractmethod
    def now(self) -> datetime:
        """Return the current UTC datetime."""


class SystemTimeProvider(TimeProvider):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FrozenTimeProvider(TimeProvider):
    def __init__(self, initial_time: datetime | None = None) -> None:
        if initial_time is not None:
            self._current_time = (
                initial_time
                if initial_time.tzinfo is not None
                else initial_time.replace(tzinfo=timezone.utc)
            )
        else:
            self._current_time = datetime.now(timezone.utc)

    def now(self) -> datetime:
        return self._current_time

    def set_time(self, new_time: datetime) -> None:
        self._current_time = (
            new_time
            if new_time.tzinfo is not None
            else new_time.replace(tzinfo=timezone.utc)
        )

    def advance(self, duration: timedelta) -> None:
        self._current_time += duration

