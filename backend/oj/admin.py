from pathlib import Path

from django import forms
from django.contrib import admin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from .models import Problem, ProblemSampleCase, Submission, SubmissionCaseResult, TestCase


class ProblemAdminForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(attrs={"rows": 18}),
            "sample_input": forms.Textarea(attrs={"rows": 8}),
            "sample_output": forms.Textarea(attrs={"rows": 8}),
        }
        help_texts = {
            "description": "Supports Markdown. Store Markdown source only; do not paste rendered HTML.",
        }


class TestCaseInlineForm(forms.ModelForm):
    input_upload = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=["in"])],
        help_text="Upload a .in judge input file.",
    )
    output_upload = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=["out"])],
        help_text="Upload a .out expected output file.",
    )

    class Meta:
        model = TestCase
        fields = ("sort_order", "score", "is_hidden")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("DELETE"):
            return cleaned_data

        if not self.has_changed():
            return cleaned_data

        input_upload = cleaned_data.get("input_upload")
        output_upload = cleaned_data.get("output_upload")
        if self.instance.pk:
            if not input_upload and not self.instance.input_path:
                raise ValidationError({"input_upload": "Please upload a .in judge input file."})
            if not output_upload and not self.instance.output_path:
                raise ValidationError({"output_upload": "Please upload a .out judge output file."})
        else:
            if not input_upload:
                raise ValidationError({"input_upload": "Please upload a .in judge input file."})
            if not output_upload:
                raise ValidationError({"output_upload": "Please upload a .out judge output file."})
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        input_upload = self.cleaned_data.get("input_upload")
        output_upload = self.cleaned_data.get("output_upload")

        if input_upload:
            instance.input_path = self._write_testcase_file(instance, input_upload, ".in")
        if output_upload:
            instance.output_path = self._write_testcase_file(instance, output_upload, ".out")

        if commit:
            instance.save()
        return instance

    def _write_testcase_file(self, instance: TestCase, uploaded_file, extension: str) -> str:
        if not instance.problem_id:
            raise ValidationError("Problem must be saved before uploading testcase files.")

        relative_dir = Path(f"problem_{instance.problem_id}")
        relative_path = relative_dir / f"{instance.sort_order}{extension}"
        target = Path(settings.TESTCASE_ROOT) / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        return relative_path.as_posix()


class TestCaseInline(admin.StackedInline):
    model = TestCase
    form = TestCaseInlineForm
    extra = 0
    fields = (
        "sort_order",
        "score",
        "is_hidden",
        "input_upload",
        "output_upload",
        "current_input_path",
        "current_output_path",
    )
    readonly_fields = ("current_input_path", "current_output_path")
    ordering = ("sort_order", "id")

    @admin.display(description="Current Input Path")
    def current_input_path(self, obj: TestCase) -> str:
        return obj.input_path or "-"

    @admin.display(description="Current Output Path")
    def current_output_path(self, obj: TestCase) -> str:
        return obj.output_path or "-"


class ProblemSampleCaseInline(admin.StackedInline):
    model = ProblemSampleCase
    extra = 1
    fields = ("sort_order", "input_file", "output_file", "input_text", "output_text")
    readonly_fields = ("input_text", "output_text")
    ordering = ("sort_order", "id")


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    form = ProblemAdminForm
    list_display = ("id", "title", "time_limit_ms", "memory_limit_mb", "is_public")
    search_fields = ("title",)
    inlines = [ProblemSampleCaseInline, TestCaseInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "description",
                    "time_limit_ms",
                    "memory_limit_mb",
                    "judge_mode",
                    "is_public",
                )
            },
        ),
        (
            "Legacy Sample Fallback",
            {
                "fields": ("sample_input", "sample_output"),
                "classes": ("collapse",),
                "description": "Only used when no ProblemSampleCase is configured. Keep for old data compatibility.",
            },
        ),
    )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "problem", "user", "language", "status", "final_verdict", "submitted_at")
    list_filter = ("status", "final_verdict", "language")
    search_fields = ("problem__title", "user__username")
    readonly_fields = ("submitted_at", "judged_at")


@admin.register(SubmissionCaseResult)
class SubmissionCaseResultAdmin(admin.ModelAdmin):
    list_display = ("id", "submission", "test_case", "verdict", "time_used_ms", "memory_used_kb")
    list_filter = ("verdict",)
