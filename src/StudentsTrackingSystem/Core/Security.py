import bcrypt

# bcrypt учитывает только первые 72 байта пароля, а bcrypt 5.x на более длинный пароль
# выбрасывает ValueError. В UTF-8 кириллица занимает 2 байта, то есть это 36 русских букв.
MAX_PASSWORD_BYTES = 72

def hash_password(password: str) -> str:
    """
    Возвращает хеш для колонки users.password_hash, например '$2b$12$...' (60 символов).
    Соль генерируется и хранится внутри хеша, отдельно её хранить не нужно.
    """
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > MAX_PASSWORD_BYTES:
        raise ValueError(f"Пароль слишком длинный: максимум {MAX_PASSWORD_BYTES} байт")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    """Проверяет пароль при входе: verify_password(введённый_пароль, user.password_hash)."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # Пароль длиннее 72 байт или в базе лежит не bcrypt-хеш.
        return False
