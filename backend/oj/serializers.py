from django.contrib.auth import authenticate, get_user_model, password_validation
from rest_framework import serializers

from judge.enums import Language, SubmissionStatus

from .models import Problem, ProblemSampleCase, Submission, SubmissionCaseResult


class ProblemSampleCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemSampleCase
        fields = [
            "id",
            "sort_order",
            "input_text",
            "output_text",
        ]


class ProblemListSerializer(serializers.ModelSerializer):
    is_solved = serializers.BooleanField(read_only=True)

    class Meta:
        model = Problem
        fields = [
            "id",
            "display_number",
            "title",
            "difficulty",
            "time_limit_ms",
            "memory_limit_mb",
            "judge_mode",
            "is_public",
            "is_solved",
        ]


class ProblemDetailSerializer(serializers.ModelSerializer):
    sample_cases = ProblemSampleCaseSerializer(many=True, read_only=True)
    is_solved = serializers.BooleanField(read_only=True)

    class Meta:
        model = Problem
        fields = [
            "id",
            "display_number",
            "title",
            "description",
            "difficulty",
            "sample_input",
            "sample_output",
            "time_limit_ms",
            "memory_limit_mb",
            "judge_mode",
            "is_public",
            "is_solved",
            "sample_cases",
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
            raise serializers.ValidationError("Stage 1 currently supports only cpp17.")
        return value

    def validate_problem(self, value: Problem) -> Problem:
        if not value.is_public:
            raise serializers.ValidationError("This problem is not open for submissions.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is required.")

        return Submission.objects.create(
            user=user,
            status=SubmissionStatus.QUEUED.value,
            **validated_data,
        )


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, trim_whitespace=False, style={"input_type": "password"})

    def validate_username(self, value: str) -> str:
        user_model = get_user_model()
        if user_model.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        user_model = get_user_model()
        user = user_model(username=attrs["username"])
        password_validation.validate_password(attrs["password"], user)
        return attrs

    def create(self, validated_data):
        user_model = get_user_model()
        return user_model.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False, style={"input_type": "password"})

    def validate(self, attrs):
        request = self.context.get("request")
        user = authenticate(request=request, username=attrs["username"], password=attrs["password"])
        if user is None:
            raise serializers.ValidationError({"non_field_errors": ["Invalid username or password."]})
        attrs["user"] = user
        return attrs
