from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework.authentication import BasicAuthentication
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Problem, Submission
from .serializers import (
    ProblemDetailSerializer,
    ProblemListSerializer,
    SubmissionCreateSerializer,
    SubmissionDetailSerializer,
    SubmissionListSerializer,
)


def get_effective_user(request):
    if request.user.is_authenticated:
        return request.user

    user_model = get_user_model()
    user, _ = user_model.objects.get_or_create(username="demo")
    return user


class ProblemListView(generics.ListAPIView):
    serializer_class = ProblemListSerializer

    def get_queryset(self) -> QuerySet[Problem]:
        queryset = Problem.objects.filter(is_public=True)
        query = self.request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset.order_by("id")


class ProblemDetailView(generics.RetrieveAPIView):
    serializer_class = ProblemDetailSerializer
    queryset = Problem.objects.filter(is_public=True)


class SubmissionListCreateView(generics.ListCreateAPIView):
    authentication_classes = [BasicAuthentication]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SubmissionCreateSerializer
        return SubmissionListSerializer

    def get_queryset(self) -> QuerySet[Submission]:
        user = get_effective_user(self.request)
        queryset = Submission.objects.select_related("problem", "user").filter(user=user)

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
    authentication_classes = [BasicAuthentication]
    serializer_class = SubmissionDetailSerializer

    def get_queryset(self) -> QuerySet[Submission]:
        user = get_effective_user(self.request)
        return Submission.objects.select_related("problem", "user").filter(user=user)


class UserMeView(APIView):
    def get(self, request):
        user = get_effective_user(request)
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "is_authenticated": request.user.is_authenticated,
                "is_demo": not request.user.is_authenticated,
            }
        )
