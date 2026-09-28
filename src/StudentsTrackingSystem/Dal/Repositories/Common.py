from typing import Any

class _Unset:
    """
    Маркер «поле не передано» для update-методов.
    Позволяет отличить «не менять» (UNSET) от «очистить» (None):
        repo.update_lesson(5, topic=None)   -> тема очищается
        repo.update_lesson(5)               -> тема не меняется
    """

    def __bool__(self) -> bool:
        return False

UNSET = _Unset()

def apply_updates(obj: object, **fields: Any) -> None:
    for name, value in fields.items():
        if value is not UNSET:
            setattr(obj, name, value)
