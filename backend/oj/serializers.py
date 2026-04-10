from django.contrib.auth import get_user_model
from rest_framework import serializers

from judge.enums import Language, SubmissionStatus

from .models import Problem, Submission, SubmissionCaseResult


class ProblemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = [
            "id",
            "title",
            "time_limit_ms",
            "memory_limit_mb",
            "judge_mode",
            "is_public",
        ]


class ProblemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = [
            "id",
            "title",
            "description",
            "sample_input",
            "sample_output",
            "time_limit_ms",
            "memory_limit_mb",
            "judge_mode",
            "is_public",
        ]


class SubmissionCaseResultSerializer(serializers.ModelSerializer):
    test_case_order = serializers.IntegerField(source="test_case.sort_order", read_only=True)

    class Meta:
        model = SubmissionCaseResult
        fields = [
            "id",
            "test_case",
            "test_case_order",
            "verdict",
            "time_used_ms",
            "memory_used_kb",
            "message",
            "created_at",
        ]


class SubmissionListSerializer(serializers.ModelSerializer):
    problem_title = serializers.CharField(source="problem.title", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "problem",
            "problem_title",
            "username",
            "language",
            "status",
            "final_verdict",
            "total_time_ms",
            "max_memory_kb",
            "submitted_at",
            "judged_at",
        ]


class SubmissionDetailSerializer(serializers.ModelSerializer):
    problem_title = serializers.CharField(source="problem.title", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    case_results = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = [
            "id",
            "problem",
            "problem_title",
            "username",
            "language",
            "source_code",
            "status",
            "final_verdict",
            "total_time_ms",
            "max_memory_kb",
            "compile_log",
            "submitted_at",
            "judged_at",
            "case_results",
        ]

    def get_case_results(self, obj: Submission):
        results = obj.case_results.select_related("test_case").order_by("test_case__sort_order", "id")
        return SubmissionCaseResultSerializer(results, many=True).data


class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ["id", "problem", "language", "source_code"]
        read_only_fields = ["id"]

    def validate_language(self, value: str) -> str:
        if value != Language.CPP17.value:
            raise serializers.ValidationError("第一阶段仅支持 cpp17。")
        return value

    def validate_problem(self, value: Problem) -> Problem:
        if not value.is_public:
            raise serializers.ValidationError("题目不可提交。")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            user_model = get_user_model()
            user, _ = user_model.objects.get_or_create(username="demo")

        return Submission.objects.create(
            user=user,
            status=SubmissionStatus.QUEUED.value,
            **validated_data,
        )
