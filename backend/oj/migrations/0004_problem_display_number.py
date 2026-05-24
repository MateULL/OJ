from django.db import migrations, models


def populate_problem_display_numbers(apps, schema_editor):
    Problem = apps.get_model("oj", "Problem")
    public_problems = list(Problem.objects.filter(is_public=True).order_by("id"))
    for index, problem in enumerate(public_problems, start=1):
        problem.display_number = index
    if public_problems:
        Problem.objects.bulk_update(public_problems, ["display_number"])


def clear_problem_display_numbers(apps, schema_editor):
    Problem = apps.get_model("oj", "Problem")
    Problem.objects.update(display_number=None)


class Migration(migrations.Migration):

    dependencies = [
        ("oj", "0003_problem_difficulty"),
    ]

    operations = [
        migrations.AddField(
            model_name="problem",
            name="display_number",
            field=models.PositiveIntegerField(blank=True, null=True, unique=True),
        ),
        migrations.RunPython(populate_problem_display_numbers, clear_problem_display_numbers),
    ]
