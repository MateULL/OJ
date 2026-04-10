from django.urls import path

from .views import (
    ProblemDetailView,
    ProblemListView,
    SubmissionDetailView,
    SubmissionListCreateView,
    UserMeView,
)


urlpatterns = [
    path("problems/", ProblemListView.as_view(), name="problem-list"),
    path("problems/<int:pk>/", ProblemDetailView.as_view(), name="problem-detail"),
    path("submissions/", SubmissionListCreateView.as_view(), name="submission-list-create"),
    path("submissions/<int:pk>/", SubmissionDetailView.as_view(), name="submission-detail"),
    path("users/me/", UserMeView.as_view(), name="user-me"),
]
