from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("quiz/", views.take_quiz, name="take_quiz"),
    path("result/", views.quiz_result, name="quiz_result"),
    path("quiz/reset/", views.quiz_reset, name="quiz_reset"),
]
