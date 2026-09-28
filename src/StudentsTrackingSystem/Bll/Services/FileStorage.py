import os
import uuid
from Core.config import MEDIA_ROOT
from Core.Exceptions import BusinessValidationError, NotFoundError

ALLOWED_EXTENSIONS = (
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".txt", ".jpg", ".jpeg", ".png", ".zip",
)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ

def save_file(uploaded_file, folder: str) -> tuple[str, str]:
    """
    Сохраняет загруженный файл в MEDIA_ROOT/<folder>/ под случайным именем.
    uploaded_file — файл из request.FILES (у него есть .name, .size и .chunks()).
    Возвращает (file_path относительно MEDIA_ROOT, исходное имя файла).
    """
    original_name = os.path.basename(uploaded_file.name)
    extension = os.path.splitext(original_name)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise BusinessValidationError(f"Файлы {extension or 'без расширения'} загружать нельзя")
    if uploaded_file.size > MAX_FILE_SIZE:
        raise BusinessValidationError("Файл больше 10 МБ")

    file_path = f"{folder}/{uuid.uuid4().hex}{extension}"
    absolute_path = os.path.join(MEDIA_ROOT, file_path)
    os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

    with open(absolute_path, "wb") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    return file_path, original_name

def get_absolute_path(file_path: str) -> str:
    """Полный путь к сохранённому файлу — для FileResponse."""
    absolute_path = os.path.join(MEDIA_ROOT, file_path)
    if not os.path.isfile(absolute_path):
        raise NotFoundError("Файл не найден на диске")
    return absolute_path
