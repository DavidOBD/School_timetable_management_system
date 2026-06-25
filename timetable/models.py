from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Subject(models.Model):
    name = models.CharField("Назва", max_length=100, unique=True)
    description = models.TextField("Опис", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Предмет"
        verbose_name_plural = "Предмети"

    def __str__(self):
        return self.name


class Teacher(models.Model):
    first_name = models.CharField("Ім'я", max_length=80)
    last_name = models.CharField("Прізвище", max_length=80)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="teachers",
        verbose_name="Предмет",
    )

    class Meta:
        ordering = ["last_name", "first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name", "subject"],
                name="unique_teacher_for_subject",
            )
        ]
        verbose_name = "Вчитель"
        verbose_name_plural = "Вчителі"

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.subject.name})"


class SchoolClass(models.Model):
    name = models.CharField("Назва класу", max_length=20)
    study_year = models.PositiveSmallIntegerField("Рік навчання")

    class Meta:
        ordering = ["study_year", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "study_year"],
                name="unique_school_class_for_year",
            )
        ]
        verbose_name = "Клас"
        verbose_name_plural = "Класи"

    def __str__(self):
        return f"{self.name}, {self.study_year} рік"


class Student(models.Model):
    first_name = models.CharField("Ім'я", max_length=80)
    last_name = models.CharField("Прізвище", max_length=80)
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name="students",
        verbose_name="Клас",
    )

    class Meta:
        ordering = ["school_class__study_year", "school_class__name", "last_name", "first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name", "school_class"],
                name="unique_student_in_class",
            )
        ]
        verbose_name = "Учень"
        verbose_name_plural = "Учні"

    def __str__(self):
        return f"{self.last_name} {self.first_name} - {self.school_class.name}"


class Schedule(models.Model):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"

    WEEKDAY_CHOICES = [
        (MONDAY, "Понеділок"),
        (TUESDAY, "Вівторок"),
        (WEDNESDAY, "Середа"),
        (THURSDAY, "Четвер"),
        (FRIDAY, "П'ятниця"),
    ]

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="schedule_items",
        verbose_name="Предмет",
    )
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name="schedule_items",
        verbose_name="Клас",
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name="schedule_items",
        verbose_name="Вчитель",
    )
    weekday = models.CharField("День тижня", max_length=20, choices=WEEKDAY_CHOICES)
    lesson_number = models.PositiveSmallIntegerField(
        "Номер уроку",
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    start_time = models.TimeField("Початок", null=True, blank=True)
    end_time = models.TimeField("Кінець", null=True, blank=True)
    room = models.CharField("Кабінет", max_length=30, blank=True)

    class Meta:
        ordering = ["weekday", "lesson_number", "school_class__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school_class", "weekday", "lesson_number"],
                name="unique_class_lesson_time",
            ),
            models.UniqueConstraint(
                fields=["teacher", "weekday", "lesson_number"],
                name="unique_teacher_lesson_time",
            ),
            models.UniqueConstraint(
                fields=["school_class", "weekday", "start_time"],
                name="unique_class_start_time",
            ),
            models.UniqueConstraint(
                fields=["teacher", "weekday", "start_time"],
                name="unique_teacher_start_time",
            ),
        ]
        verbose_name = "Розклад"
        verbose_name_plural = "Розклад"

    def clean(self):
        if self.teacher_id and self.subject_id and self.teacher.subject_id != self.subject_id:
            raise ValidationError("Обраний вчитель викладає інший предмет.")
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("Час завершення уроку має бути пізніше часу початку.")

    def __str__(self):
        return f"{self.school_class.name}: {self.get_weekday_display()}, урок {self.lesson_number} - {self.subject.name}"


class Grade(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name="Учень",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="grades",
        verbose_name="Предмет",
    )
    value = models.PositiveSmallIntegerField(
        "Оцінка",
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    date = models.DateField("Дата")
    comment = models.CharField("Коментар", max_length=255, blank=True)

    class Meta:
        ordering = ["-date", "student__last_name", "subject__name"]
        verbose_name = "Оцінка"
        verbose_name_plural = "Оцінки"

    def __str__(self):
        return f"{self.student}: {self.subject.name} - {self.value}"
