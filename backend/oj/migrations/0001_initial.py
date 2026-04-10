# Generated for the first-stage OJ schema.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Problem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("sample_input", models.TextField(blank=True)),
                ("sample_output", models.TextField(blank=True)),
                ("time_limit_ms", models.PositiveIntegerField(default=1000)),
                ("memory_limit_mb", models.PositiveIntegerField(default=128)),
                ("judge_mode", models.CharField(choices=[("standard", "standard")], default="standard", max_length=32)),
                ("is_public", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="TestCase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("input_path", models.CharField(max_length=500)),
                ("output_path", models.CharField(max_length=500)),
                ("sort_order", models.PositiveIntegerField(default=1)),
                ("score", models.PositiveIntegerField(default=0)),
                ("is_hidden", models.BooleanField(default=True)),
                (
                    "problem",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="test_cases", to="oj.problem"),
                ),
            ],
            options={
                "ordering": ["problem_id", "sort_order", "id"],
            },
        ),
        migrations.CreateModel(
            name="Submission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language", models.CharField(choices=[("cpp17", "cpp17")], default="cpp17", max_length=32)),
                ("source_code", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[("QUEUED", "QUEUED"), ("JUDGING", "JUDGING"), ("FINISHED", "FINISHED")],
                        db_index=True,
                        default="QUEUED",
                        max_length=20,
                    ),
                ),
                (
                    "final_verdict",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("AC", "AC"),
                            ("WA", "WA"),
                            ("CE", "CE"),
                            ("RE", "RE"),
                            ("TLE", "TLE"),
                            ("MLE", "MLE"),
                            ("OLE", "OLE"),
                            ("SE", "SE"),
                        ],
                        db_index=True,
                        max_length=20,
                        null=True,
                    ),
                ),
                ("total_time_ms", models.PositiveIntegerField(default=0)),
                ("max_memory_kb", models.PositiveIntegerField(default=0)),
                ("compile_log", models.TextField(blank=True)),
                ("submitted_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("judged_at", models.DateTimeField(blank=True, null=True)),
                (
                    "problem",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submissions", to="oj.problem"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-submitted_at"],
            },
        ),
        migrations.CreateModel(
            name="SubmissionCaseResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "verdict",
                    models.CharField(
                        choices=[
                            ("AC", "AC"),
                            ("WA", "WA"),
                            ("CE", "CE"),
                            ("RE", "RE"),
                            ("TLE", "TLE"),
                            ("MLE", "MLE"),
                            ("OLE", "OLE"),
                            ("SE", "SE"),
                        ],
                        max_length=20,
                    ),
                ),
                ("time_used_ms", models.PositiveIntegerField(default=0)),
                ("memory_used_kb", models.PositiveIntegerField(default=0)),
                ("message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "submission",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="case_results", to="oj.submission"),
                ),
                (
                    "test_case",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submission_results", to="oj.testcase"),
                ),
            ],
            options={
                "ordering": ["submission_id", "test_case_id", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="submission",
            index=models.Index(fields=["status", "submitted_at"], name="idx_submission_queue"),
        ),
        migrations.AddIndex(
            model_name="submission",
            index=models.Index(fields=["problem", "submitted_at"], name="idx_submission_problem"),
        ),
        migrations.AddIndex(
            model_name="submission",
            index=models.Index(fields=["user", "submitted_at"], name="idx_submission_user"),
        ),
        migrations.AddConstraint(
            model_name="testcase",
            constraint=models.UniqueConstraint(fields=("problem", "sort_order"), name="uniq_testcase_problem_order"),
        ),
        migrations.AddConstraint(
            model_name="submissioncaseresult",
            constraint=models.UniqueConstraint(fields=("submission", "test_case"), name="uniq_submission_case_result"),
        ),
    ]
