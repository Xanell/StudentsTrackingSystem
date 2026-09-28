from datetime import time
from enum import Enum

class StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value

class RoleName(StrEnum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

ROLE_LABELS = {
    RoleName.STUDENT: "Ученик",
    RoleName.TEACHER: "Учитель",
    RoleName.ADMIN: "Администратор",
}

class DayType(StrEnum):
    SCHOOL_DAY = "school_day"
    WEEKEND = "weekend"
    HOLIDAY = "holiday"   
    VACATION = "vacation"  
    OTHER = "other"       

DAY_TYPE_LABELS = {
    DayType.SCHOOL_DAY: "Учебный день",
    DayType.WEEKEND: "Выходной",
    DayType.HOLIDAY: "Праздник",
    DayType.VACATION: "Каникулы",
    DayType.OTHER: "Неучебный день",
}

DAY_OFF_TYPES = (DayType.SCHOOL_DAY, DayType.HOLIDAY, DayType.VACATION, DayType.OTHER)
SCHOOL_DAYS_PER_WEEK = 6
WEEKDAY_LABELS = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье",
}

LESSON_TIMES: dict[int, tuple[time, time]] = {
    1: (time(8, 30), time(9, 15)),
    2: (time(9, 25), time(10, 10)),
    3: (time(10, 30), time(11, 15)),
    4: (time(11, 35), time(12, 20)),
    5: (time(12, 30), time(13, 15)),
    6: (time(13, 25), time(14, 10)),
    7: (time(14, 20), time(15, 5)),
    8: (time(15, 15), time(16, 0)),
}

MAX_LESSONS_PER_DAY = len(LESSON_TIMES)

class GradeType(StrEnum):
    CLASSWORK = "class_work"
    HOMEWORK = "home_work"
    TEST = "test"

GRADE_TYPE_LABELS = {
    GradeType.CLASSWORK: "Работа на уроке",
    GradeType.HOMEWORK: "Домашняя работа",
    GradeType.TEST: "Контрольная работа",
}
