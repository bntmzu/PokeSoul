import json
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from core.models import Question, AnswerOption

class Command(BaseCommand):
    help = "Seeds the database with questions and answer options."

    def handle(self, *args, **kwargs):
        json_path = Path(settings.BASE_DIR) / "data" / "question_set.json"

        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f"File not found: {json_path}"))
            return

        with open(json_path, "r", encoding="utf-8") as file:
            questions = json.load(file)

        created_questions = 0
        created_options = 0

        for q in questions:
            question, q_created = Question.objects.get_or_create(
                identifier=q["identifier"],
                defaults={"text": q["text"]}
            )
            if q_created:
                created_questions += 1

            for opt in q.get("options", []):
                option, o_created = AnswerOption.objects.get_or_create(
                    question=question,
                    text=opt["text"],
                    defaults={"value": opt["value"]}
                )
                if o_created:
                    created_options += 1

        self.stdout.write(self.style.SUCCESS(
            f"{created_questions} questions and {created_options} answer options seeded."
        ))
