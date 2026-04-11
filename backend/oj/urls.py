from django.urls import path

from .views import (
    LoginView,
    ProblemDetailView,
    ProblemListView,
    RegisterView,
    LogoutView,
    SubmissionDetailView,
    SubmissionListCreateView,
    UserCheckinView,
    UserMeView,
    csrf_cookie_view,
)


urlpatterns = [
    path("auth/csrf/", csrf_cookie_view, name="auth-csrf"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("problems/", ProblemListView.as_view(), name="problem-list"),
    path("problems/<int:pk>/", ProblemDetailView.as_view(), name="problem-detail"),
    path("submissions/", SubmissionListCreateView.as_view(), name="submission-list-create"),
    path("submissions/<int:pk>/", SubmissionDetailView.as_view(), name="submission-detail"),
    path("users/me/", UserMeView.as_view(), name="user-me"),
    path("users/me/checkins/", UserCheckinView.as_view(), name="user-checkins"),
]
