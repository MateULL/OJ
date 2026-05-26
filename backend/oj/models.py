from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from judge.enums import JudgeMode, Language, SubmissionStatus, Verdict


def sample_input_upload_to(instance: "ProblemSampleCase", filename: str) -> str:
    ext = Path(filename).suffix.lower() or ".in"
    return f"problem_samples/problem_{instance.problem_id or 'unsaved'}/{instance.sort_order}_input{ext}"


def sample_output_upload_to(instance: "ProblemSampleCase", filename: str) -> str:
    ext = Path(filename).suffix.lower() or ".out"
    return f"problem_samples/problem_{instance.problem_id or 'unsaved'}/{instance.sort_order}_output{ext}"


def _delete_storage_file(field_file) -> None:
    # 删除上传样例文件时只操作存储层，不影响数据库记录的删除流程。
    name = getattr(field_file, "name", "")
    if not name:
        return
    storage = getattr(field_file, "storage", None)
    if storage is None:
        return
    storage.delete(name)


def _delete_testcase_file(relative_path: str) -> None:
    if not relative_path:
        return

    # 测试点文件必须位于 TESTCASE_ROOT 下，避免误删项目目录外的文件。
    testcase_root = Path(settings.TESTCASE_ROOT).resolve()
    target = (testcase_root / relative_path).resolve()
    if target != testcase_root and testcase_root not in target.parents:
        return
    if not target.exists():
        return

    target.unlink()
    parent = target.parent
    while parent != testcase_root and parent.exists():
        try:
            parent.rmdir()
        except OSError:
            break
        parent = parent.parent


class Problem(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    title = models.CharField(max_length=200)
    # display_number 是前端展示的题号，和数据库主键分开，隐藏题或测试题不会让题号断档。
    display_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
    )
    description = models.TextField()
    difficulty = models.CharField(
        max_length=16,
        choices=Difficulty.choices,
        blank=True,
        default="",
    )
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

    def save(self, *args, **kwargs) -> None:
        previous_is_public = None
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).values("is_public").first()
            if previous is not None:
                previous_is_public = previous["is_public"]

        if not self.is_public:
            self.display_number = None

        super().save(*args, **kwargs)

        # 题目新增、删除、隐藏或公开后，公开题号需要重新排成连续序号。
        needs_sync = False
        if self.is_public and self.display_number is None:
            needs_sync = True
        if previous_is_public is not None and previous_is_public != self.is_public:
            needs_sync = True
        if previous_is_public is None and self.is_public:
            needs_sync = True

        if needs_sync:
            using = self._state.db or "default"
            transaction.on_commit(lambda: sync_public_problem_display_numbers(using), using=using)


def sync_public_problem_display_numbers(using: str = "default") -> None:
    # 只根据公开题重建可见题号，保证题库页显示为 1、2、3... 的连续序号。
    public_problems = list(Problem.objects.using(using).filter(is_public=True).order_by("id"))
    updated = []
    for index, problem in enumerate(public_problems, start=1):
        if problem.display_number != index:
            problem.display_number = index
            updated.append(problem)

    if updated:
        Problem.objects.using(using).bulk_update(updated, ["display_number"])


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

    def save(self, *args, **kwargs) -> None:
        old_input_path = ""
        old_output_path = ""
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).values("input_path", "output_path").first()
            if previous is not None:
                old_input_path = previous["input_path"] or ""
                old_output_path = previous["output_path"] or ""

        super().save(*args, **kwargs)

        if old_input_path and old_input_path != self.input_path:
            # 管理后台替换测试点文件后，及时清理旧文件，避免残留数据越积越多。
            _delete_testcase_file(old_input_path)
        if old_output_path and old_output_path != self.output_path:
            _delete_testcase_file(old_output_path)

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
        old_input_name = ""
        old_output_name = ""
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).values("input_file", "output_file").first()
            if previous is not None:
                old_input_name = previous["input_file"] or ""
                old_output_name = previous["output_file"] or ""

        self.full_clean()
        # 上传的样例文件保留在磁盘；同时把文本提取到数据库，前端展示时无需再读文件。
        self.input_text = self._read_file_text(self.input_file)
        self.output_text = self._read_file_text(self.output_file)
        super().save(*args, **kwargs)
        if old_input_name and old_input_name != self.input_file.name:
            self.input_file.storage.delete(old_input_name)
        if old_output_name and old_output_name != self.output_file.name:
            self.output_file.storage.delete(old_output_name)
        self.input_file.close()
        self.output_file.close()

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


@receiver(post_delete, sender=ProblemSampleCase)
def cleanup_problem_sample_case_files(sender, instance: ProblemSampleCase, **kwargs) -> None:
    _delete_storage_file(instance.input_file)
    _delete_storage_file(instance.output_file)


@receiver(post_delete, sender=Problem)
def sync_problem_display_numbers_after_delete(sender, instance: Problem, **kwargs) -> None:
    if not instance.is_public and instance.display_number is None:
        return

    using = instance._state.db or "default"
    transaction.on_commit(lambda: sync_public_problem_display_numbers(using), using=using)


@receiver(post_delete, sender=TestCase)
def cleanup_testcase_files(sender, instance: TestCase, **kwargs) -> None:
    _delete_testcase_file(instance.input_path)
    _delete_testcase_file(instance.output_path)
