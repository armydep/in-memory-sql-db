from contextlib import contextmanager
from threading import Condition, Lock
from typing import Iterator


class RWLock:
    def __init__(self) -> None:
        self._condition = Condition(Lock())
        self._readers = 0
        self._writer_active = False
        self._waiting_writers = 0

    @contextmanager
    def read_locked(self) -> Iterator[None]:
        with self._condition:
            while self._writer_active or self._waiting_writers:
                self._condition.wait()
            self._readers += 1
        try:
            yield
        finally:
            with self._condition:
                self._readers -= 1
                if self._readers == 0:
                    self._condition.notify_all()

    @contextmanager
    def write_locked(self) -> Iterator[None]:
        with self._condition:
            self._waiting_writers += 1
            try:
                while self._writer_active or self._readers:
                    self._condition.wait()
                self._writer_active = True
            finally:
                self._waiting_writers -= 1
        try:
            yield
        finally:
            with self._condition:
                self._writer_active = False
                self._condition.notify_all()
