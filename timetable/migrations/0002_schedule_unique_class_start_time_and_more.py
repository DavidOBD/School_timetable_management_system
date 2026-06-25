

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='schedule',
            constraint=models.UniqueConstraint(fields=('school_class', 'weekday', 'start_time'), name='unique_class_start_time'),
        ),
        migrations.AddConstraint(
            model_name='schedule',
            constraint=models.UniqueConstraint(fields=('teacher', 'weekday', 'start_time'), name='unique_teacher_start_time'),
        ),
    ]
