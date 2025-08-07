import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import AnswerOption, Question


class Command(BaseCommand):
    help = "Seeds the database with questions and answer options from JSON fixture."

    def handle(self, *args, **kwargs):
        """Load questions and answer options from JSON fixture file"""
        json_path = Path(settings.BASE_DIR) / "fixtures" / "question_set.json"

        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f"File not found: {json_path}"))
            return

        # Load questions from JSON fixture
        with open(json_path, "r", encoding="utf-8") as file:
            questions = json.load(file)

        created_questions = 0
        created_options = 0

        # Process each question and its answer options
        for q in questions:
            question, q_created = Question.objects.get_or_create(
                identifier=q["identifier"], defaults={"text": q["text"]}
            )
            if q_created:
                created_questions += 1

            # Create answer options for this question
            for opt in q.get("options", []):
                option, o_created = AnswerOption.objects.get_or_create(
                    question=question,
                    text=opt["text"],
                    defaults={"value": opt["value"]},
                )
                if o_created:
                    created_options += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{created_questions} questions and {created_options} answer options seeded."
            )
        )
