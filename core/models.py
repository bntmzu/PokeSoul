from django.db import models


class Question(models.Model):
    identifier = models.CharField(max_length=64, unique=True)  # e.g., "favorite_color"
    text = models.CharField(max_length=255)  # e.g., "What is your favorite color?"

    class Meta:
        ordering = ["identifier"]
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        indexes = [
            models.Index(fields=["identifier"]),
        ]

    def __str__(self):
        return self.text


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question, related_name="options", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    value = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.question.identifier}: {self.text}"


class UserProfile(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # (keys = question.identifier)
    answers = models.JSONField()

    def __str__(self):
        return f"UserProfile #{self.id} – {self.created_at.strftime('%Y-%m-%d %H:%M')}"
