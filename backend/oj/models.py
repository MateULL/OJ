from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from judge.enums import JudgeMode, Language, SubmissionStatus, Verdict


def sample_input_upload_to(instance: "ProblemSampleCase", filename: str) -> str:
    ext = Path(filename).suffix.lower() or ".in"
    return f"problem_samples/problem_{instance.problem_id or 'unsaved'}/{instance.sort_order}_input{ext}"


def sample_output_upload_to(instance: "ProblemSampleCase", filename: str) -> str:
    ext = Path(filename).suffix.lower() or ".out"
    return f"problem_samples/problem_{instance.problem_id or 'unsaved'}/{instance.sort_order}_output{ext}"


class Problem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    sample_input = models.TextField(blank=True)
    sample_output = models.TextField(blank=True)
    time_limit_ms = models.PositiveIntegerField(default=1000)
    memory_limit_mb = models.PositiveIntegerField(default=128)
    judge_mode = models.CharField(
        max_length=32,
        choices=JudgeMode.choices(),
        default=JudgeMode.STANDARD.value,
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return self.title


class TestCase(models.Model):
    problem = models.ForeignKey(
        Problem,
        related_name="test_cases",
        on_delete=models.CASCADE,
    )
    input_path = models.CharField(max_length=500)
    output_path = models.CharField(max_length=500)
    sort_order = models.PositiveIntegerField(default=1)
    score = models.PositiveIntegerField(default=0)
    is_hidden = models.BooleanField(default=True)

    class Meta:
        ordering = ["problem_id", "sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["problem", "sort_order"],
                name="uniq_testcase_problem_order",
            )
        ]

    def __str__(self) -> str:
        return f"{self.problem_id}#{self.sort_order}"


class ProblemSampleCase(models.Model):
    problem = models.ForeignKey(
        Problem,
        related_name="sample_cases",
        on_delete=models.CASCADE,
    )
    sort_order = models.PositiveIntegerField(default=1)
    input_file = models.FileField(
        upload_to=sample_input_upload_to,
        validators=[FileExtensionValidator(allowed_extensions=["in"])],
    )
    output_file = models.FileField(
        upload_to=sample_output_upload_to,
        validators=[FileExtensionValidator(allowed_extensions=["out"])],
    )
    input_text = models.TextField(blank=True, editable=False)
    output_text = models.TextField(blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["problem_id", "sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["problem", "sort_order"],
                name="uniq_problem_sample_case_order",
            )
        ]

    def __str__(self) -> str:
        return f"Sample {self.problem_id}#{self.sort_order}"

    def clean(self) -> None:
        super().clean()
        errors = {}

        if not self.input_file:
            errors["input_file"] = "Please upload a .in sample input file."
        elif Path(self.input_file.name).suffix.lower() != ".in":
            errors["input_file"] = "Sample input file must use the .in extension."

        if not self.output_file:
            errors["output_file"] = "Please upload a .out sample output file."
        elif Path(self.output_file.name).suffix.lower() != ".out":
            errors["output_file"] = "Sample output file must use the .out extension."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        self.input_text = self._read_file_text(self.input_file)
        self.output_text = self._read_file_text(self.output_file)
        super().save(*args, **kwargs)

    def _read_file_text(self, field_file) -> str:
        if not field_file:
            return ""

        should_close = False
        file_obj = getattr(field_file, "file", None)
        if file_obj is None or getattr(file_obj, "closed", False):
            field_file.open("rb")
            file_obj = field_file.file
            should_close = True

        try:
            file_obj.seek(0)
            content = file_obj.read()
        finally:
            file_obj.seek(0)
            if should_close:
                field_file.close()

        if isinstance(content, str):
            return content
        return content.decode("utf-8", errors="replace")


class Submission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="submissions",
        on_delete=models.CASCADE,
    )
    problem = models.ForeignKey(
        Problem,
        related_name="submissions",
        on_delete=models.CASCADE,
    )
    language = models.CharField(
        max_length=32,
        choices=Language.choices(),
        default=Language.CPP17.value,
    )
    source_code = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=SubmissionStatus.choices(),
        default=SubmissionStatus.QUEUED.value,
        db_index=True,
    )
    final_verdict = models.CharField(
        max_length=20,
        choices=Verdict.choices(),
        null=True,
        blank=True,
        db_index=True,
    )
    total_time_ms = models.PositiveIntegerField(default=0)
    max_memory_kb = models.PositiveIntegerField(default=0)
    compile_log = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    judged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["status", "submitted_at"], name="idx_submission_queue"),
            models.Index(fields=["problem", "submitted_at"], name="idx_submission_problem"),
            models.Index(fields=["user", "submitted_at"], name="idx_submission_user"),
        ]

    def __str__(self) -> str:
        return f"Submission #{self.pk} {self.status}"


class SubmissionCaseResult(models.Model):
    submission = models.ForeignKey(
        Submission,
        related_name="case_results",
        on_delete=models.CASCADE,
    )
    test_case = models.ForeignKey(
        TestCase,
        related_name="submission_results",
        on_delete=models.CASCADE,
    )
    verdict = models.CharField(max_length=20, choices=Verdict.choices())
    time_used_ms = models.PositiveIntegerField(default=0)
    memory_used_kb = models.PositiveIntegerField(default=0)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["submission_id", "test_case_id", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "test_case"],
                name="uniq_submission_case_result",
            )
        ]

    def __str__(self) -> str:
        return f"Submission {self.submission_id} case {self.test_case_id}: {self.verdict}"
