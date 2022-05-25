from __future__ import annotations
from sideral.utils import interface
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .builder import Select

@interface
class Selectable:
    
    def build_select(self) -> Select: ...


@interface
class Modifiable:
    
    def save(self) -> Select: ...
