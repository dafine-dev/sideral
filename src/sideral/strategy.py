from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum
from .utils import UNLOADED
from .session import transaction, SessionFactory

if TYPE_CHECKING:
    from .proxy import Proxy
    from .mapper import Property


def eager(prop: Property, proxy: Proxy) -> any:
    return getattr(proxy.__element__, prop.attribute_name)


@transaction
def lazy(prop: Property, proxy: Proxy) -> any:
    attribute_value = prop.get_attribute(proxy.__element__)

    if attribute_value is UNLOADED:
        model = proxy.__model__
        sql = prop.build_select(id = getattr(proxy, model.identifier.attribute_name))

        session = SessionFactory.get()
        session.clear_result()
        session.transaction.execute_query(sql)
        result = session.get_result()

        if result.is_empty():
            prop.set_null(proxy)
        else:
            for value in prop._post_execute_action(result): 
                prop.set_attribute(proxy, value, mirror = True)
        
        return getattr(proxy.__element__, prop.attribute_name)
    else:
        return attribute_value


def no(prop: Property, proxy: Proxy) -> any: 
    attribute_value = getattr(proxy.__element__, prop.attribute_name)
    if attribute_value is UNLOADED:
        return prop._null_value
    else:
        return attribute_value


class  load(Enum):

    EAGER = eager
    LAZY = lazy
    NO = no


