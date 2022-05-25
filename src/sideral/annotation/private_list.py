
    
    


class private_collection:

    def __init__(self, annotation, l: list) -> None:
        self._annotation = annotation
        self._l = l

    def __getattribute__(self, name: str) -> any:
        return getattr(self._l, name)
    
    def __setitem__(self, index, item) -> None:
        # self._annotation.update_row()
        self._l[index] = item

    def __delitem__(self, index) -> None:
        # self._annotation.delete_row()
        del self._l[index]

    def append(self, item) -> None:
        # self._annotation.insert_row()
        return self._l.append(item)
    
    def insert(self, position, item) -> None:
        # self._annotation.insert_row()
        return self._l.extend(position, item)
    
    def extend(self, l) -> None:
        # self._annotation.insert_rows()
        return self._l.extend(l)


class private_list:

    def __init__(self, annotation, l: list) -> None:
        self._annotation = annotation
        self._l = l