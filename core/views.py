from django.shortcuts import redirect, render

from core.models import AnswerOption, Question, UserProfile
from matcher.matching_engine import MatchingEngine


def home(request):
    """Home page view"""
    return render(request, "core/home.html")


def take_quiz(request):
    # Load all questions ordered by 'order'
    questions = list(Question.objects.all().order_by("id"))
    total = len(questions)

    # Get the current question index from session (defaults to 0)
    current_index = request.session.get("quiz_index", 0)

    # Only clear session data on the very first GET request (fresh start)
    # Don't clear on redirects or POST requests
    if (
        request.method == "GET"
        and current_index == 0
        and not request.session.get("quiz_answers")
    ):
        session_keys_to_clear = ["quiz_answers", "quiz_index"]
        for key in session_keys_to_clear:
            if key in request.session:
                del request.session[key]
        request.session.save()
        print("DEBUG: Cleared session for fresh quiz start")
        current_index = 0

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

        # Store the selected answer in session
        user_answers = request.session.get("quiz_answers", {})
        user_answers[str(question.id)] = selected_option_id
        request.session["quiz_answers"] = user_answers

        # Advance to the next question
        request.session["quiz_index"] = current_index + 1
        print(
            f"DEBUG: Saved answer for question {question.id}, advancing to question {current_index + 1}"
        )
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

    print(f"DEBUG: Session data: {dict(request.session)}")
    print(f"DEBUG: Quiz answers from session: {quiz_answers}")

    if not quiz_answers:
        print("DEBUG: No quiz answers in session, redirecting to quiz")
        return redirect("take_quiz")

    # Debug: print current answers
    print(f"DEBUG: Processing quiz answers: {quiz_answers}")

    # Check if we have all required answers (16 questions)
    if len(quiz_answers) < 16:
        print(
            f"DEBUG: Incomplete answers ({len(quiz_answers)}/16), redirecting to quiz"
        )
        return redirect("take_quiz")

    # Create user profile with answers
    user_profile = UserProfile.objects.create(answers=quiz_answers)
    print(f"DEBUG: Created UserProfile with ID: {user_profile.id}")

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
        print(f"DEBUG: No match found, using fallback: {pokemon.name}")
    else:
        pokemon = match_result.pokemon
        print(
            f"DEBUG: Matched Pokemon: {pokemon.name} with score: {match_result.total_score}"
        )
        print(
            f"DEBUG: Pokemon types: {pokemon.types}, color: {pokemon.color}, habitat: {pokemon.habitat}"
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

    print("DEBUG: Quiz session cleared")
    return redirect("take_quiz")
