from enum import Enum



class Join(Enum):

    INNER = ' INNER JOIN '
    LEFT = ' LEFT OUTER JOIN '
    RIGHT = ' RIGHT OUTER JOIN '


def format(value: any):
    if isinstance(value, str):
        return f"0x{value.encode('utf-8').hex()}"
    
    if value is None or value is ...:
        return 'null'
    
    return value