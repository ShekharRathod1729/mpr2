from django.urls import path
from . import views
from .views import register, login_view, home, start_quiz, quiz_question, quiz_results, user_dashboard, logout_view

urlpatterns = [
        path("register/", register, name="register"),
        path("login/", login_view, name="login"),
        path("", home, name="home"),    
        path("quiz/<int:quiz_id>/start/", start_quiz, name="start_quiz"),
        path("quiz/<int:quiz_id>/question/<int:question_id>/", quiz_question, name="quiz_question"),
        path("quiz/<int:quiz_id>/results/", quiz_results, name="quiz_results"),
        path("profile/", user_dashboard, name="user_dashboard"),
        path("logout/", logout_view, name="logout")
]


