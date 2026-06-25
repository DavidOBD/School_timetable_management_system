from django.contrib import admin

from .models import Grade, Schedule, SchoolClass, Student, Subject, Teacher


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "subject")
    list_filter = ("subject",)
    search_fields = ("first_name", "last_name")


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("name", "study_year")
    search_fields = ("name",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "school_class")
    list_filter = ("school_class",)
    search_fields = ("first_name", "last_name")


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("weekday", "lesson_number", "school_class", "subject", "teacher", "room")
    list_filter = ("weekday", "school_class", "subject", "teacher")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("date", "student", "subject", "value")
    list_filter = ("date", "subject", "value")
    search_fields = ("student__first_name", "student__last_name", "subject__name")
