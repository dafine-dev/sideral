from __future__ import annotations
from sideral.errors import UnloadedIterator
from typing import Generic, TypeVar

def decorator(callable):
    return callable




class _Unloaded: 
    
    _instance: _Unloaded

    def __new__(cls) -> _Unloaded:
        try:
            return cls._instance
        except AttributeError:
            cls._instance = object.__new__(cls)
            return cls._instance

    def __iter__(self) -> None: 
        raise UnloadedIterator
    
    def __repr__(self) -> str:
        return f'<UNLOADED>'



T = TypeVar('T')
class ordered_set(Generic[T]):
    
    def __init__(self, *items) -> None:
        self._items = {}
        self._hashs = []

        for item in items:
            h = hash(item)
            self._items[h] = item
            self._hashs.append(h)
    
    def __str__(self) -> str:
        return str([self._items[h] for h in self._hashs])
    
    def __iter__(self) -> ordered_set:
        self._index = -1
        return self
    
    def __next__(self) -> T:
        self._index += 1

        if self._index > len(self._hashs) - 1:
            raise StopIteration
        
        return self._items[self._hashs[self._index]]
    
    def __len__(self) -> int:
        return len(self._hashs)
    
    def __contains__(self, item: any) -> bool:
        return (hash(item) in self._items)
    
    def __getitem__(self, index: int) -> any:
        return self._hashs[index]
    
    def add(self, item: any) -> None:
        h = hash(item)

        if h not in self._items:
            self._hashs.append(h)

        self._items[h] = item
    
    def remove(self, item: any) -> None:
        h = hash(item)
        self._hashs.remove(h)
        del self._items[h]
            


    

abstract = decorator
metaclass = decorator
interface = decorator
override = decorator
UNLOADED = _Unloaded()