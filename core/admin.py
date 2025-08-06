from django.contrib import admin

from .models import AnswerOption, Question, UserProfile


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("identifier", "text")
    search_fields = ("identifier", "text")


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ("question", "text", "value")
    search_fields = ("text", "value")
    list_filter = ("question",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at")
    readonly_fields = ("answers",)
    ordering = ("-created_at",)
