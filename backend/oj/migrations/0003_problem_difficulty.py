from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("oj", "0002_problemsamplecase_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="problem",
            name="difficulty",
            field=models.CharField(
                blank=True,
                choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
                default="",
                max_length=16,
            ),
        ),
    ]
