from __future__ import annotations
from .utils import UNLOADED
from typing import Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from .result import Row
    from .proxy import Proxy
    from .mapper import Model
    from .schema import Column
    from .session import Session

    
class Loader:
    _model: Model
    _session: Session

    def __init__(self, model: Model) -> None:
        self._model = model
        self._session = SessionFactory.get()
    
    def _select(self, id: any = ...) -> None:
        query = self._model.build_select()

        self._session.clear_result()

        self._session.transaction.execute_query(query)
    
        for relationship in self._model.relationships():
            if not relationship.is_lazy:
                sub_query = relationship.build_select()
                self._session.transaction.execute_query(sub_query)
    

    def _select_by_id(self, id: any) -> None:
        primary_key = self._model.identifier.column
        query = self._model.build_select().where(primary_key == id)

        self._session.clear_result()

        self._session.transaction.execute_query(query)

        for relationship in self._model.relationships():
            if not relationship.is_lazy:
                sub_query = relationship.build_select(id = id)
                self._session.transaction.execute_query(sub_query)
        
        
    def _load(self) -> list[Proxy]:
        response = []
        elements = self.load_on_pk(self._session.get_result().main(), self._model)

        for proxy in elements:
            relationships = proxy.__model__.relationships()

            for index, relationship in enumerate(relationships):
                if relationship.is_lazy:
                    setattr(proxy, relationship.attribute_name, UNLOADED)
                else:
                    associated_elements = self.load_on(
                        rows = self._session.get_result().get(index), 
                        model = relationship.reference, 
                        key = relationship.join_column.column
                    )
                    
                    try:
                        relationship.set_attribute(proxy, next(associated_elements), mirror = True)
                    except StopIteration:
                        relationship.set_null(proxy)
                    finally:
                        for associated_element in associated_elements: 
                            relationship.set_attribute(proxy, associated_element, mirror = True)
            
            response.append(proxy)

        return response

    def load(self) -> list[Proxy]:
        self._select()
        return self._load()

    def load_by_id(self, id: any) -> Proxy:
        self._select_by_id(id)
        try:
            return self._load()[0]
        except IndexError:
            raise SideralException(f"Can't find {self._model._class.__name__} register with id {id} in database.")
    
    @classmethod
    def load_on(self, rows: Generator[Row], model: Model, key: Column) -> Generator[Proxy]:
        row = ...
        key_value = ...
        try:
            row = next(rows)
            key_value = row.get_by(key)
        except StopIteration:
            return []
            
        yield self.load_element(row, model)
        for row in rows:
            if row.get_by(key) == key_value:
                yield self.load_element(row, model)
            else:
                break
    
    @classmethod
    def load_on_pk(self, rows: Generator[Row], model: Model) -> Generator[Proxy]:
        key = model.table.primary_key.column
        last_pk_value = ...

        for row in rows:
            key_value = row.get_by(key)
        
            if key_value != last_pk_value:
                yield self.load_element(row, model)
                last_pk_value = key_value
    
    @classmethod
    def load_element(self, row: Row, model: Model) -> Proxy:
        element_model = model.get_model(row)
        element = element_model.new()
        for column_prop in element_model.columns():
            setattr(
                element, 
                column_prop.attribute_name, 
                UNLOADED if column_prop.is_lazy else row.get_by(column_prop.column)
            )
        
        return element_model.proxy(element)



from .session import SessionFactory
from .errors import SideralException