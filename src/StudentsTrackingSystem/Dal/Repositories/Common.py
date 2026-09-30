class _Unset:
    # Маркер поля не передан
    def __bool__(self) -> bool:
        return False

UNSET = _Unset()

def apply_updates(obj: object, **fields) -> None:
    for name, value in fields.items():
        if value is not UNSET:
            setattr(obj, name, value)
