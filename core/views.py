import logging

from django.shortcuts import redirect, render

from core.models import AnswerOption, Question, UserProfile
from matcher.matching_engine import MatchingEngine

logger = logging.getLogger(__name__)


def home(request):
    """Home page view"""
    return render(request, "core/home.html")


def take_quiz(request):
    """Handle quiz questions with session-based state management"""
    # Load all questions ordered by ID
    questions = list(Question.objects.all().order_by("id"))
    total = len(questions)

    # Get the current question index from session (defaults to 0)
    current_index = request.session.get("quiz_index", 0)

    # Redirect to result view if quiz is finished
    if current_index >= total:
        return redirect("quiz_result")

    question = questions[current_index]
    options = AnswerOption.objects.filter(question=question)

    if request.method == "POST":
        selected_option_id = request.POST.get("answer")

        if not selected_option_id:
            return render(
                request,
                "core/question.html",
                {
                    "question": question,
                    "options": options,
                    "error": "Please select an option.",
                    "total_questions": total,
                    "progress_percent": int(current_index / total * 100),
                },
            )

        # Store the selected answer in session for persistence
        user_answers = request.session.get("quiz_answers", {})
        user_answers[str(question.id)] = selected_option_id
        request.session["quiz_answers"] = user_answers

        # Advance to the next question
        request.session["quiz_index"] = current_index + 1
        logger.debug(
            f"Saved answer for question {question.id}, advancing to question {current_index + 1}"
        )

        # Redirect to next question or results
        if current_index + 1 >= total:
            return redirect("quiz_result")
        else:
            return redirect("take_quiz")

    return render(
        request,
        "core/question.html",
        {
            "question": question,
            "options": options,
            "total_questions": total,
            "progress_percent": int(current_index / total * 100),
        },
    )


def quiz_result(request):
    """Show quiz results with matched Pokemon"""
    # Get answers from session
    quiz_answers = request.session.get("quiz_answers", {})
    logger.debug(f"Quiz answers from session: {len(quiz_answers)} answers")

    if not quiz_answers:
        return redirect("take_quiz")

    logger.debug(f"Processing {len(quiz_answers)} quiz answers")

    # Check if we have all required answers (16 questions total)
    if len(quiz_answers) < 16:
        logger.debug(
            f"Incomplete answers ({len(quiz_answers)}/16), redirecting to quiz"
        )
        return redirect("take_quiz")

    # Create user profile with answers
    user_profile = UserProfile.objects.create(answers=quiz_answers)
    logger.debug(f"Created UserProfile with ID: {user_profile.id}")

    # Find matching Pokemon
    engine = MatchingEngine(user_profile)
    match_result = engine.find_and_save_match()

    if not match_result:
        # Fallback - show a default Pokemon
        from pokemons.models import Pokemon

        pokemon = Pokemon.objects.first()
        if not pokemon:
            return render(
                request, "core/quiz_result.html", {"error": "No Pokemon found"}
            )
        logger.debug(f"No match found, using fallback: {pokemon.name}")
    else:
        pokemon = match_result.pokemon
        logger.debug(
            f"Matched Pokemon: {pokemon.name} with score: {match_result.total_score}"
        )
        logger.debug(
            f"Pokemon types: {pokemon.types}, color: {pokemon.color}, habitat: {pokemon.habitat}"
        )

    return render(request, "core/quiz_result.html", {"pokemon": pokemon})


def quiz_reset(request):
    """Reset quiz session and redirect to start"""
    # Clear all session data related to quiz
    session_keys_to_clear = ["quiz_answers", "quiz_index"]
    for key in session_keys_to_clear:
        if key in request.session:
            del request.session[key]

    # Force session save
    request.session.save()

    logger.debug("Quiz session cleared")
    return redirect("take_quiz")
