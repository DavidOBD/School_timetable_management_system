import os
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_timetable.settings")

import django
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, connection

django.setup()

from timetable.models import Grade, Schedule, SchoolClass, Student, Subject, Teacher


def prepare_database():
    call_command("migrate", interactive=False, verbosity=0)


def read_required_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Поле не може бути порожнім.")


def read_optional_text(prompt):
    return input(prompt).strip()


def read_int(prompt, min_value=None, max_value=None):
    while True:
        raw_value = input(prompt).strip()
        try:
            value = int(raw_value)
        except ValueError:
            print("Введіть ціле число.")
            continue

        if min_value is not None and value < min_value:
            print(f"Значення має бути не менше {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Значення має бути не більше {max_value}.")
            continue
        return value


def read_date(prompt):
    while True:
        raw_value = input(prompt).strip()
        if not raw_value:
            return datetime.today().date()
        try:
            return datetime.strptime(raw_value, "%Y-%m-%d").date()
        except ValueError:
            print("Введіть дату у форматі YYYY-MM-DD або залиште поле порожнім.")


def read_required_date(prompt):
    while True:
        raw_value = input(prompt).strip()
        if not raw_value:
            print("Дата є обов'язковою.")
            continue
        try:
            return datetime.strptime(raw_value, "%Y-%m-%d").date()
        except ValueError:
            print("Введіть дату у форматі YYYY-MM-DD.")


def read_time(prompt):
    while True:
        raw_value = input(prompt).strip()
        if not raw_value:
            return None
        try:
            return datetime.strptime(raw_value, "%H:%M").time()
        except ValueError:
            print("Введіть час у форматі HH:MM або залиште поле порожнім.")


def read_required_time(prompt):
    while True:
        value = read_time(prompt)
        if value is not None:
            return value
        print("Час початку є обов'язковим.")


def choose_object(queryset, title):
    items = list(queryset)
    if not items:
        print(f"Немає записів для вибору: {title}.")
        return None

    print(f"\n{title}:")
    for item in items:
        print(f"{item.id}. {item}")

    valid_ids = {item.id: item for item in items}
    while True:
        object_id = read_int("Введіть ID: ", min_value=1)
        if object_id in valid_ids:
            return valid_ids[object_id]
        print("Запис з таким ID не знайдено.")


def save_instance(instance):
    try:
        instance.full_clean()
        instance.save()
    except ValidationError as error:
        print(f"Помилка перевірки даних: {error}")
        return False
    except IntegrityError as error:
        print(f"Помилка збереження. Можливо, такий запис уже існує: {error}")
        return False
    return True


def add_subject():
    print("\nДодавання предмету")
    name = read_required_text("Назва: ")
    description = read_optional_text("Опис: ")

    if Subject.objects.filter(name__iexact=name).exists():
        print("Предмет з такою назвою вже існує.")
        return

    subject = Subject(name=name, description=description)
    if save_instance(subject):
        print(f"Предмет додано: {subject}")


def add_teacher():
    print("\nДодавання вчителя")
    subject = choose_object(Subject.objects.all(), "Доступні предмети")
    if subject is None:
        print("Спочатку додайте предмет.")
        return

    first_name = read_required_text("Ім'я: ")
    last_name = read_required_text("Прізвище: ")
    teacher = Teacher(first_name=first_name, last_name=last_name, subject=subject)

    if save_instance(teacher):
        print(f"Вчителя додано: {teacher}")


def add_school_class():
    print("\nДодавання класу")
    name = read_required_text("Назва класу, наприклад 7-А: ")
    study_year = read_int("Рік навчання: ", min_value=1)

    exists = SchoolClass.objects.filter(name__iexact=name, study_year=study_year).exists()
    if exists:
        print("Клас з такою назвою та роком навчання вже існує.")
        return

    school_class = SchoolClass(name=name, study_year=study_year)
    if save_instance(school_class):
        print(f"Клас додано: {school_class}")


def add_student():
    print("\nДодавання учня")
    school_class = choose_object(SchoolClass.objects.all(), "Доступні класи")
    if school_class is None:
        print("Спочатку додайте клас.")
        return

    first_name = read_required_text("Ім'я: ")
    last_name = read_required_text("Прізвище: ")
    student = Student(first_name=first_name, last_name=last_name, school_class=school_class)

    if save_instance(student):
        print(f"Учня додано: {student}")


def add_schedule_item():
    print("\nДодавання заняття в розклад")
    print("Введіть день тижня, годину початку, предмет, клас та вчителя.")

    print("\nДні тижня:")
    for index, (_, label) in enumerate(Schedule.WEEKDAY_CHOICES, start=1):
        print(f"{index}. {label}")
    weekday_index = read_int("Оберіть день тижня: ", min_value=1, max_value=len(Schedule.WEEKDAY_CHOICES))
    weekday = Schedule.WEEKDAY_CHOICES[weekday_index - 1][0]

    start_time = read_required_time("Година початку заняття, HH:MM: ")

    subject = choose_object(Subject.objects.all(), "Доступні предмети")
    if subject is None:
        print("Спочатку додайте предмет.")
        return

    school_class = choose_object(SchoolClass.objects.all(), "Доступні класи")
    if school_class is None:
        print("Спочатку додайте клас.")
        return

    teacher = choose_object(Teacher.objects.filter(subject=subject), "Вчителі обраного предмету")
    if teacher is None:
        print("Спочатку додайте вчителя для цього предмету.")
        return

    class_busy = Schedule.objects.filter(
        school_class=school_class,
        weekday=weekday,
        start_time=start_time,
    ).exists()
    if class_busy:
        print("У цього класу вже є заняття в обраний день та час.")
        return

    teacher_busy = Schedule.objects.filter(
        teacher=teacher,
        weekday=weekday,
        start_time=start_time,
    ).exists()
    if teacher_busy:
        print("Цей вчитель уже має заняття в обраний день та час.")
        return

    lesson_number = read_int("Номер уроку: ", min_value=1, max_value=12)
    end_time = read_time("Кінець уроку, HH:MM або Enter: ")
    room = read_optional_text("Кабінет: ")

    schedule_item = Schedule(
        subject=subject,
        school_class=school_class,
        teacher=teacher,
        weekday=weekday,
        lesson_number=lesson_number,
        start_time=start_time,
        end_time=end_time,
        room=room,
    )

    if save_instance(schedule_item):
        print(f"Запис розкладу додано: {schedule_item}")


def add_grade():
    print("\nДодавання оцінки")
    student = choose_object(Student.objects.select_related("school_class"), "Доступні учні")
    if student is None:
        print("Спочатку додайте учня.")
        return

    subject = choose_object(Subject.objects.all(), "Доступні предмети")
    if subject is None:
        print("Спочатку додайте предмет.")
        return

    value = read_int("Оцінка від 1 до 12: ", min_value=1, max_value=12)
    date = read_required_date("Дата, YYYY-MM-DD: ")
    comment = read_optional_text("Коментар: ")

    grade = Grade(student=student, subject=subject, value=value, date=date, comment=comment)
    if save_instance(grade):
        print(f"Оцінку додано: {grade}")


def show_database_summary():
    print("\nПоточний стан бази даних")
    print(f"Предметів: {Subject.objects.count()}")
    print(f"Вчителів: {Teacher.objects.count()}")
    print(f"Класів: {SchoolClass.objects.count()}")
    print(f"Учнів: {Student.objects.count()}")
    print(f"Записів розкладу: {Schedule.objects.count()}")
    print(f"Оцінок: {Grade.objects.count()}")

    print("\nSQL-запит: кількість учнів у кожному класі")
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT c.name, c.study_year, COUNT(s.id) AS student_count
            FROM timetable_schoolclass AS c
            LEFT JOIN timetable_student AS s ON s.school_class_id = c.id
            GROUP BY c.id, c.name, c.study_year
            ORDER BY c.study_year, c.name
            """
        )
        rows = cursor.fetchall()

    if not rows:
        print("Класи ще не додані.")
        return

    for class_name, study_year, student_count in rows:
        print(f"{class_name}, {study_year} рік: {student_count} учнів")


def print_menu():
    print(
        """
Система керування шкільним розкладом
1. Додати предмет
2. Додати вчителя
3. Додати клас
4. Додати учня
5. Додати заняття в розклад
6. Додати оцінку
7. Показати стан бази даних
0. Вийти
"""
    )


def main():
    prepare_database()
    actions = {
        "1": add_subject,
        "2": add_teacher,
        "3": add_school_class,
        "4": add_student,
        "5": add_schedule_item,
        "6": add_grade,
        "7": show_database_summary,
    }

    while True:
        print_menu()
        choice = input("Ваш вибір: ").strip()
        if choice == "0":
            print("Роботу завершено.")
            break

        action = actions.get(choice)
        if action is None:
            print("Невірний пункт меню.")
            continue

        action()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nРоботу перервано користувачем.")
