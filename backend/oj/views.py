import calendar
from datetime import date, datetime, timedelta
from typing import List

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


def problem_queryset_for_request(request) -> QuerySet[Problem]:
    queryset = Problem.objects.filter(is_public=True)
    if request.user.is_authenticated:
        accepted_submissions = Submission.objects.filter(
            user=request.user,
            problem_id=OuterRef("pk"),
            final_verdict=Verdict.AC.value,
        )
        return queryset.annotate(is_solved=Exists(accepted_submissions))
    return queryset.annotate(is_solved=Value(False, output_field=BooleanField()))


@ensure_csrf_cookie
def csrf_cookie_view(request):
    return JsonResponse({"detail": "CSRF cookie set."})


class ProblemListView(generics.ListAPIView):
    serializer_class = ProblemListSerializer

    def get_queryset(self) -> QuerySet[Problem]:
        queryset = problem_queryset_for_request(self.request)
        query = self.request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(title__icontains=query)

        return queryset.order_by("id")


class ProblemDetailView(generics.RetrieveAPIView):
    serializer_class = ProblemDetailSerializer

    def get_queryset(self) -> QuerySet[Problem]:
        return problem_queryset_for_request(self.request).prefetch_related("sample_cases")


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
    permission_classes = [permissions.AllowAny]

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

    def _daily_counts(self, user):
        tz = timezone.get_current_timezone()
        daily_counts = (
            Submission.objects.filter(user=user, final_verdict=Verdict.AC.value)
            .annotate(activity_at=Coalesce("judged_at", "submitted_at"))
            .annotate(day=TruncDate("activity_at", tzinfo=tz))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        return list(daily_counts)

    def _available_years(self, active_dates: List[date]) -> List[int]:
        current_year = timezone.localdate().year
        if not active_dates:
            return [current_year]
        first_year = active_dates[0].year
        return list(range(first_year, current_year + 1))

    def _max_streak_days(self, active_dates: List[date]) -> int:
        if not active_dates:
            return 0

        streak = 1
        best = 1
        for index in range(1, len(active_dates)):
            if active_dates[index] - active_dates[index - 1] == timedelta(days=1):
                streak += 1
            else:
                streak = 1
            best = max(best, streak)
        return best

    def get(self, request):
        daily_counts = self._daily_counts(request.user)
        count_map = {row["day"].isoformat(): row["count"] for row in daily_counts if row["day"] is not None}
        active_dates = [row["day"] for row in daily_counts if row["day"] is not None]
        available_years = self._available_years(active_dates)

        year_str = request.query_params.get("year")
        if year_str:
            try:
                selected_year = int(year_str)
                start_date = date(selected_year, 1, 1)
                end_date = date(selected_year + 1, 1, 1)
            except ValueError:
                return Response({"detail": "year must use YYYY."}, status=status.HTTP_400_BAD_REQUEST)
            current_date = start_date
            values = []
            year_active_days = 0
            while current_date < end_date:
                key = current_date.isoformat()
                count = count_map.get(key, 0)
                if count > 0:
                    year_active_days += 1
                values.append({"date": key, "count": count})
                current_date += timedelta(days=1)

            today = timezone.localdate()
            last_30_days_start = today - timedelta(days=29)
            last_30_days_active = sum(1 for active_date in active_dates if last_30_days_start <= active_date <= today)

            return Response(
                {
                    "year": f"{selected_year}",
                    "available_years": available_years,
                    "values": values,
                    "stats": {
                        "total_active_days": len(active_dates),
                        "year_active_days": year_active_days,
                        "last_30_days_active_days": last_30_days_active,
                        "max_streak_days": self._max_streak_days(active_dates),
                    },
                }
            )

        month_str = request.query_params.get("month")
        if month_str:
            try:
                month_start = datetime.strptime(month_str, "%Y-%m").date().replace(day=1)
            except ValueError:
                return Response({"detail": "month must use YYYY-MM."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            today = timezone.localdate()
            month_start = today.replace(day=1)

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
