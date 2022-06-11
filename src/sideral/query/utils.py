from enum import Enum



class Join(Enum):

    INNER = 'inner join'
    LEFT = 'left outer join'
    RIGHT = 'right outer join'


def format(value: any):
    if isinstance(value, str):
        return f"0x{value.encode('utf-8').hex()}" if value else "''"
    
    if value is None or value is ...:
        return 'null'
    
    return value