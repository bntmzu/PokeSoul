from django.shortcuts import render, redirect
from core.models import Question, AnswerOption


def take_quiz(request):
    # Load all questions ordered by 'order'
    questions = list(Question.objects.all().order_by('id'))
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
                    "progress_percent": int((current_index) / total * 100),
                },
            )

        # Store the selected answer in session
        user_answers = request.session.get("quiz_answers", {})
        user_answers[str(question.id)] = selected_option_id
        request.session["quiz_answers"] = user_answers

        # Advance to the next question
        request.session["quiz_index"] = current_index + 1
        return redirect("take_quiz")

    return render(
        request,
        "core/question.html",
        {
            "question": question,
            "options": options,
            "total_questions": total,
            "progress_percent": int((current_index) / total * 100),
        },
    )

def quiz_result(request):
    # Temporary placeholder
    return render(request, "core/quiz_result.html")

def quiz_reset(request):
    # Clear session state
    request.session.pop("quiz_answers", None)
    request.session.pop("quiz_index", None)
    return redirect("take_quiz")