

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Назва')),
                ('description', models.TextField(blank=True, verbose_name='Опис')),
            ],
            options={
                'verbose_name': 'Предмет',
                'verbose_name_plural': 'Предмети',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Назва класу')),
                ('study_year', models.PositiveSmallIntegerField(verbose_name='Рік навчання')),
            ],
            options={
                'verbose_name': 'Клас',
                'verbose_name_plural': 'Класи',
                'ordering': ['study_year', 'name'],
                'constraints': [models.UniqueConstraint(fields=('name', 'study_year'), name='unique_school_class_for_year')],
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=80, verbose_name="Ім'я")),
                ('last_name', models.CharField(max_length=80, verbose_name='Прізвище')),
                ('school_class', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='students', to='timetable.schoolclass', verbose_name='Клас')),
            ],
            options={
                'verbose_name': 'Учень',
                'verbose_name_plural': 'Учні',
                'ordering': ['school_class__study_year', 'school_class__name', 'last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)], verbose_name='Оцінка')),
                ('date', models.DateField(verbose_name='Дата')),
                ('comment', models.CharField(blank=True, max_length=255, verbose_name='Коментар')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='timetable.student', verbose_name='Учень')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='grades', to='timetable.subject', verbose_name='Предмет')),
            ],
            options={
                'verbose_name': 'Оцінка',
                'verbose_name_plural': 'Оцінки',
                'ordering': ['-date', 'student__last_name', 'subject__name'],
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=80, verbose_name="Ім'я")),
                ('last_name', models.CharField(max_length=80, verbose_name='Прізвище')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='teachers', to='timetable.subject', verbose_name='Предмет')),
            ],
            options={
                'verbose_name': 'Вчитель',
                'verbose_name_plural': 'Вчителі',
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.CharField(choices=[('monday', 'Понеділок'), ('tuesday', 'Вівторок'), ('wednesday', 'Середа'), ('thursday', 'Четвер'), ('friday', "П'ятниця")], max_length=20, verbose_name='День тижня')),
                ('lesson_number', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)], verbose_name='Номер уроку')),
                ('start_time', models.TimeField(blank=True, null=True, verbose_name='Початок')),
                ('end_time', models.TimeField(blank=True, null=True, verbose_name='Кінець')),
                ('room', models.CharField(blank=True, max_length=30, verbose_name='Кабінет')),
                ('school_class', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='schedule_items', to='timetable.schoolclass', verbose_name='Клас')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='schedule_items', to='timetable.subject', verbose_name='Предмет')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='schedule_items', to='timetable.teacher', verbose_name='Вчитель')),
            ],
            options={
                'verbose_name': 'Розклад',
                'verbose_name_plural': 'Розклад',
                'ordering': ['weekday', 'lesson_number', 'school_class__name'],
            },
        ),
        migrations.AddConstraint(
            model_name='student',
            constraint=models.UniqueConstraint(fields=('first_name', 'last_name', 'school_class'), name='unique_student_in_class'),
        ),
        migrations.AddConstraint(
            model_name='teacher',
            constraint=models.UniqueConstraint(fields=('first_name', 'last_name', 'subject'), name='unique_teacher_for_subject'),
        ),
        migrations.AddConstraint(
            model_name='schedule',
            constraint=models.UniqueConstraint(fields=('school_class', 'weekday', 'lesson_number'), name='unique_class_lesson_time'),
        ),
        migrations.AddConstraint(
            model_name='schedule',
            constraint=models.UniqueConstraint(fields=('teacher', 'weekday', 'lesson_number'), name='unique_teacher_lesson_time'),
        ),
    ]
