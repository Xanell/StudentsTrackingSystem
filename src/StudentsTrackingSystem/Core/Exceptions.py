class BllError(Exception):
    pass

class NotFoundError(BllError):
    #Запись не найдена
    pass

class ConflictError(BllError):
    #Дубликат либо значение занято
    pass

class BusinessValidationError(BllError):
    #Ошибка валидации
    pass

class PermissionDeniedError(BllError):
    #Ограничение прав доступа
    pass
