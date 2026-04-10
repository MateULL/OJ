from django.contrib import admin

from .models import Problem, Submission, SubmissionCaseResult, TestCase


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 0


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "time_limit_ms", "memory_limit_mb", "is_public")
    search_fields = ("title",)
    inlines = [TestCaseInline]


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
