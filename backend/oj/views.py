import calendar
from datetime import datetime

from django.contrib.auth import login, logout
from django.db.models import BooleanField, Count, Exists, OuterRef, QuerySet, Value
from django.db.models.functions import Coalesce, TruncDate
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.authentication import SessionAuthentication
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from judge.enums import Verdict

from .models import Problem, Submission
from .serializers import (
    LoginSerializer,
    ProblemDetailSerializer,
    ProblemListSerializer,
    RegisterSerializer,
    SubmissionCreateSerializer,
    SubmissionDetailSerializer,
    SubmissionListSerializer,
)


@ensure_csrf_cookie
def csrf_cookie_view(request):
    return JsonResponse({"detail": "CSRF cookie set."})


class ProblemListView(generics.ListAPIView):
    serializer_class = ProblemListSerializer

    def get_queryset(self) -> QuerySet[Problem]:
        queryset = Problem.objects.filter(is_public=True)
        query = self.request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(title__icontains=query)

        if self.request.user.is_authenticated:
            accepted_submissions = Submission.objects.filter(
                user=self.request.user,
                problem_id=OuterRef("pk"),
                final_verdict=Verdict.AC.value,
            )
            queryset = queryset.annotate(is_solved=Exists(accepted_submissions))
        else:
            queryset = queryset.annotate(is_solved=Value(False, output_field=BooleanField()))

        return queryset.order_by("id")


class ProblemDetailView(generics.RetrieveAPIView):
    serializer_class = ProblemDetailSerializer
    queryset = Problem.objects.filter(is_public=True).prefetch_related("sample_cases")


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if request.user.is_authenticated:
            return Response({"detail": "Already authenticated."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegisterSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "is_authenticated": True,
                "is_demo": False,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if request.user.is_authenticated:
            return Response({"detail": "Already authenticated."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "is_authenticated": True,
                "is_demo": False,
            }
        )


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubmissionListCreateView(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SubmissionCreateSerializer
        return SubmissionListSerializer

    def get_queryset(self) -> QuerySet[Submission]:
        queryset = Submission.objects.select_related("problem", "user").filter(user=self.request.user)

        problem_id = self.request.query_params.get("problem")
        if problem_id:
            queryset = queryset.filter(problem_id=problem_id)

        return queryset.order_by("-submitted_at")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        submission = Submission.objects.select_related("problem", "user").get(pk=response.data["id"])
        return Response(
            SubmissionDetailSerializer(submission, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )


class SubmissionDetailView(generics.RetrieveAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubmissionDetailSerializer

    def get_queryset(self) -> QuerySet[Submission]:
        return Submission.objects.select_related("problem", "user").filter(user=self.request.user)


class UserCheckinView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        month_str = request.query_params.get("month")
        if month_str:
            try:
                month_start = datetime.strptime(month_str, "%Y-%m").date().replace(day=1)
            except ValueError:
                return Response({"detail": "month must use YYYY-MM."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            today = timezone.localdate()
            month_start = today.replace(day=1)

        next_year = month_start.year + (1 if month_start.month == 12 else 0)
        next_month = 1 if month_start.month == 12 else month_start.month + 1
        month_end = datetime(next_year, next_month, 1).date()
        tz = timezone.get_current_timezone()
        range_start = timezone.make_aware(datetime(month_start.year, month_start.month, 1), tz)
        range_end = timezone.make_aware(datetime(month_end.year, month_end.month, 1), tz)

        daily_counts = (
            Submission.objects.filter(user=request.user, final_verdict=Verdict.AC.value)
            .annotate(activity_at=Coalesce("judged_at", "submitted_at"))
            .filter(activity_at__gte=range_start, activity_at__lt=range_end)
            .annotate(day=TruncDate("activity_at", tzinfo=tz))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        count_map = {row["day"].isoformat(): row["count"] for row in daily_counts if row["day"] is not None}
        last_day = calendar.monthrange(month_start.year, month_start.month)[1]
        values = []
        active_days = 0
        for day in range(1, last_day + 1):
            current_date = month_start.replace(day=day).isoformat()
            count = count_map.get(current_date, 0)
            if count > 0:
                active_days += 1
            values.append({"date": current_date, "count": count})

        return Response(
            {
                "month": month_start.strftime("%Y-%m"),
                "active_days": active_days,
                "values": values,
            }
        )


class UserMeView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {
                    "id": None,
                    "username": "",
                    "is_authenticated": False,
                    "is_demo": False,
                }
            )

        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "is_authenticated": True,
                "is_demo": False,
            }
        )
