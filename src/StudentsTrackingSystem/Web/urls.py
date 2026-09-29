from django.urls import path
from Web.views.Login import login_view, logout_view
from Web.views.Home import home
from Web.views.Users import users_list, user_create, user_created, user_edit, user_reset_password, user_deactivate, user_archive, user_restore
from Web.views.SchoolYears import school_years_list, school_year_create, school_year_edit, school_year_make_current
from Web.views.SchoolClasses import school_classes_list, school_class_create, school_class_edit, classes_root, school_class_students, school_class_set_student, school_class_remove_student
from Web.views.Subjects import subject_list, subject_create, subject_edit
from Web.views.SchoolCalendar import calendar_root, school_calendar_list, quarter_add, quarter_edit, dayoff_add, dayoff_edit
from Web.views.Schedule import schedule_list, schedule_by_class, schedule_by_teacher, schedule_create, schedule_edit
from Web.views.Teacher import teacher_shedule, lessons_list, teacher_lesson, teacher_journals, class_journal
from Web.views.Student import student_schedule, student_diary 

urlpatterns = [
    #URL LoginPage
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    #URL HomePage
    path("", home, name="home"),
    #URL UserPage
    path("users/", users_list, name="users"),
    path("users/create/", user_create, name="user_create"),
    path("users/created/", user_created, name="user_created"),
    path("users/<int:user_id>/edit/", user_edit, name="user_edit"),
    path("users/<int:user_id>/reset-password/", user_reset_password, name="user_reset_password"),
    path("users/<int:user_id>/deactivate/", user_deactivate, name="user_deactivate"),
    path("users/archive/", user_archive, name="user_archive"),
    path("users/archive/<int:user_id>/restore/", user_restore, name="user_restore"),
    #URL SchoolYearPage
    path("school-years/", school_years_list, name="school_years"),
    path("school-years/create/", school_year_create, name="school_year_create"),
    path("school-years/<int:year_id>/edit/", school_year_edit, name="school_year_edit"),
    path("school-years/<int:year_id>/make-current/", school_year_make_current, name="school_year_make_current"),
    #URL SchoolClassPage
    path("classes/", classes_root, name="classes_root"),
    path("school-years/<int:year_id>/classes/", school_classes_list, name="school_classes"),
    path("school-years/<int:year_id>/classes/create/", school_class_create, name="school_class_create"),
    path("school-years/<int:year_id>/classes/<int:class_id>/edit/", school_class_edit, name="school_class_edit"),
    path("school-years/<year_id>/classes/<int:class_id>/", school_class_students, name="school_class_students"),
    path("school-years/<year_id>/classes/<int:class_id>/students/<int:user_id>/add/", school_class_set_student, name="school_class_set_student"),
    path("school-years/<year_id>/classes/<int:class_id>/students/<int:user_id>/remove/", school_class_remove_student, name="school_class_remove_student"),
    #URL SubjectsPage
    path("subjects/", subject_list, name="subjects"),
    path("subjects/create/", subject_create, name="subject_create"),
    path("subjects/<int:subject_id>/edit/", subject_edit, name="subject_edit"),
    #URL SchoolCalendarPage
    path("calendar/", calendar_root, name="calendar_root"),
    path("school-years/<int:year_id>/calendar/", school_calendar_list, name="school_calendar"),
    path("school-years/<int:year_id>/calendar/quarter/add/", quarter_add, name="quarter_add"),
    path("school-years/<int:year_id>/calendar/quarter/<int:quarter_id>/edit/", quarter_edit, name="quarter_edit"),
    path("school-years/<int:year_id>/calendar/dayoff/add/", dayoff_add, name="dayoff_add"),
    path("school-years/<int:year_id>/calendar/dayoff/<int:day_id>/edit/", dayoff_edit, name="dayoff_edit"),
    #URL ShedulePage
    path("schedule/", schedule_list, name="schedule_list"),
    path("schedule/class/<int:class_id>/", schedule_by_class, name="schedule_by_class"),
    path("schedule/teacher/<int:teacher_id>/", schedule_by_teacher, name="schedule_by_teacher"),
    path("schedule/class/<int:class_id>/create/", schedule_create, name="schedule_create"),
    path("schedule/<int:schedule_id>/edit/", schedule_edit, name="schedule_edit"),
    #URL TeacherPage
    path("teacher/shedule/", teacher_shedule, name="teacher_shedule"),
    path("teacher/lessons/", lessons_list, name="lessons_by_day"),
    path("teacher/lessons/<int:lesson_id>/", teacher_lesson, name="teacher_lesson"),
    path("teacher/journals/", teacher_journals, name="teacher_journals"),
    path("teacher/journals/<int:class_id>/<int:subject_id>/:", class_journal, name="class_journal"),
    #URL StudentPage
    path("student/schedule/", student_schedule, name="student_schedule"),
    path("student/diary/", student_diary, name="student_diary"),
]