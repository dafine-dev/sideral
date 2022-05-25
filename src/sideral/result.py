from __future__ import annotations
from typing import Generator
from typing import TYPE_CHECKING
from collections import deque

if TYPE_CHECKING: 
    from .schema import Column


class Row:

    def __init__(self, data: dict[str, any]) -> None:
        self._data = data
    
    def get_by(self, column: Column) -> any:
        return self._data[column.alias]


class ResultSet:

    _main: deque[dict[str, any]]
    _subs: list[deque[dict[str, any]]]

    def __init__(self) -> None:
        self._main = ...
        self._subs = []
    
    def main(self) -> Generator[Row]:
        return self._generator(self._main)
    
    def add_data(self, data: list[dict[str, any]]) -> None:
        data = deque(data)
        if self._main is ...:
            self._main = data
        else:
            self._subs.append(deque(data))
    
    def get(self, index: int) -> Generator[Row]:
        return self._generator(self._subs[index])
    
    def _generator(self, queue: deque[dict[str, any]]) -> Generator[Row]:
        while queue:
            yield Row(data = queue[0])
            queue.popleft()
    
    def is_empty(self) -> bool:
        if self._main is ... or (len(self._main) == 0):
            return True
        return False