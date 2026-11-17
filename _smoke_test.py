"""Temporary checks for scoring, screens, timer locks, and results. Deleted after the run."""

import copy
import tkinter as tk

import quiz_app
from questions import CATEGORY_ORDER, QUESTIONS, prepare_quiz
from quiz_app import QuizApp, calculate_percentage, performance_message
from styles import COLORS

assert calculate_percentage(0, 10) == 0
assert calculate_percentage(5, 10) == 50
assert calculate_percentage(9, 10) == 90
assert calculate_percentage(10, 10) == 100
assert calculate_percentage(1, 3) == 33
assert calculate_percentage(0, 0) == 0

assert performance_message(100) == "Excellent!"
assert performance_message(90) == "Excellent!"
assert performance_message(89) == "Very Good!"
assert performance_message(75) == "Very Good!"
assert performance_message(74) == "Good Job!"
assert performance_message(50) == "Good Job!"
assert performance_message(49) == "Keep Practicing!"
assert performance_message(0) == "Keep Practicing!"

app = QuizApp()
app.sound_enabled = False
app.withdraw()


def button_texts(widget):
    found = []
    if widget.winfo_class() == "Button":
        found.append(widget.cget("text"))
    for child in widget.winfo_children():
        found.extend(button_texts(child))
    return found


def same_color(widget_color, expected):
    return app.winfo_rgb(widget_color) == app.winfo_rgb(expected)


assert app.screen_name == "welcome"
assert app.welcome_title.cget("text") == "SMART QUIZ CHALLENGE"
assert app.welcome_subtitle.cget("text") == "Test Your Knowledge, Challenge Yourself!"
assert "Start Quiz" in button_texts(app.container)

app.name_var.set("   ")
app.on_start_welcome()
assert app.screen_name == "welcome"
assert app.player_name == ""
assert app.name_error.cget("text") == "Please enter your name."

app.name_var.set("Asha")
app.on_start_welcome()
assert app.screen_name == "category"
assert app.player_name == "Asha"
assert app.greeting.cget("text") == "Hello, Asha"
assert "Back" in button_texts(app.container)

app.on_start_quiz()
assert app.screen_name == "category"
assert app.category_error.cget("text") == "Please choose a category."

for category in CATEGORY_ORDER:
    app.select_category(category)
    assert app.selected_category == category
    assert app.selected_label.cget("text") == f"Selected: {category}"
    frame = app.category_cards[category]["frame"]
    assert same_color(frame.cget("highlightbackground"), COLORS["accent"])
    app.on_start_quiz()
    assert app.screen_name == "quiz"
    assert app.category == category
    assert len(app.quiz_questions) == 10
    bank = {item["question"] for item in QUESTIONS[category]}
    for item in app.quiz_questions:
        assert item["question"] in bank
        assert item["answer"] in item["options"]
        assert len(item["options"]) == 4
    app.show_categories()

app.select_category("Science")
app.on_start_quiz()
assert app.displayed_time == 20
assert app.time_left == 19
assert app.timer_job is not None
assert "Exit" in button_texts(app.container)
assert "Next Question" in button_texts(app.container)

quiz_app.messagebox.askyesno = lambda *args, **kwargs: False
shown = app.displayed_time
app.confirm_exit()
assert app.winfo_exists()
assert app.screen_name == "quiz"
assert app.timer_job is not None
assert app.time_left == shown

plan = [True, False, True, False, "timeout", True, False, True, False, True]
for index, step in enumerate(plan):
    assert app.question_index == index
    assert app.question_counter.cget("text") == f"Question {index + 1} of 10"
    question = app.quiz_questions[index]
    assert question["question"] in {item["question"] for item in QUESTIONS["Science"]}
    if step == "timeout":
        score_before = app.score
        app.handle_timeout()
        app.handle_timeout()
        assert app.score == score_before
        assert len(app.answer_log) == index + 1
        assert app.timer_job is None
        assert "Time's up" in app.feedback.cget("text")
        assert question["answer"] in app.feedback.cget("text")
        assert app.progress.percent == (index + 1) * 10
        app.goto_next()
    else:
        if step:
            choice = question["options"].index(question["answer"])
        else:
            choice = next(
                number
                for number, option in enumerate(question["options"])
                if option != question["answer"]
            )
        score_before = app.score
        app.select_answer(choice)
        app.select_answer(choice)
        app.select_answer(0)
        assert len(app.answer_log) == index + 1
        assert app.timer_job is None
        assert app.progress.percent == (index + 1) * 10
        feedback = app.feedback.cget("text")
        if step:
            assert app.score == score_before + 1
            assert feedback == "Correct Answer!"
        else:
            assert app.score == score_before
            assert feedback.startswith("Incorrect Answer!")
            assert question["answer"] in feedback
        app.on_next()

assert app.screen_name == "result"
assert app.score == 5
assert app.result_summary == {
    "name": "Asha",
    "category": "Science",
    "total": 10,
    "correct": 5,
    "incorrect": 5,
    "score": 5,
    "percentage": 50,
    "message": "Good Job!",
}
assert app.result_message.cget("text") == "Good Job!"
assert app.result_name.cget("text") == "Asha"
assert app.stat_values["Player"].cget("text") == "Asha"
assert app.stat_values["Category"].cget("text") == "Science"
assert app.stat_values["Total Questions"].cget("text") == "10"
assert app.stat_values["Correct Answers"].cget("text") == "5"
assert app.stat_values["Incorrect Answers"].cget("text") == "5"
assert app.stat_values["Final Score"].cget("text") == "5 / 10"
assert app.stat_values["Percentage"].cget("text") == "50%"
assert "Play Again" in button_texts(app.container)
assert "Exit" in button_texts(app.container)


def force_result(correct_count):
    app.player_name = "Asha"
    app.category = "Sports"
    app.quiz_questions = [
        {"question": f"Q{number}", "options": ["a", "b", "c", "d"], "answer": "a"}
        for number in range(10)
    ]
    app.answer_log = [
        {
            "selected": "a" if number < correct_count else "b",
            "answer": "a",
            "is_correct": number < correct_count,
        }
        for number in range(10)
    ]
    app.score = 999
    app.show_result()


expectations = {
    10: "Excellent!",
    9: "Excellent!",
    8: "Very Good!",
    7: "Good Job!",
    5: "Good Job!",
    4: "Keep Practicing!",
    0: "Keep Practicing!",
}
for correct_count, message in expectations.items():
    force_result(correct_count)
    summary = app.result_summary
    assert summary["correct"] == correct_count, summary
    assert summary["incorrect"] == 10 - correct_count, summary
    assert summary["score"] == correct_count, summary
    assert summary["percentage"] == correct_count * 10, summary
    assert summary["message"] == message, summary
    assert app.result_message.cget("text") == message
    assert app.stat_values["Final Score"].cget("text") == f"{correct_count} / 10"
    assert app.stat_values["Percentage"].cget("text") == f"{correct_count * 10}%"

# Last question timeout opens the result and scores zero for that question.
app.play_again()
app.name_var.set("Asha")
app.on_start_welcome()
app.select_category("Sports")
app.on_start_quiz()
app.question_index = 9
app.answer_log = [
    {"selected": None, "answer": "x", "is_correct": False} for _ in range(9)
]
app.score = 0
app.show_question()
assert app.next_button.cget("text") == "View Result"
assert app.question_counter.cget("text") == "Question 10 of 10"
app.handle_timeout()
assert app.score == 0
assert len(app.answer_log) == 10
assert app.answer_log[-1]["is_correct"] is False
app.goto_next()
assert app.screen_name == "result"
assert app.result_summary["correct"] == 0
assert app.result_summary["incorrect"] == 10
assert app.result_summary["message"] == "Keep Practicing!"

original = copy.deepcopy(QUESTIONS)
orders = []
for _ in range(25):
    quiz = prepare_quiz("Python Programming")
    order = tuple(item["question"] for item in quiz)
    orders.append(order)
    assert len(order) == 10
    assert len(set(order)) == 10
assert len(set(orders)) > 1
for category in CATEGORY_ORDER:
    prepare_quiz(category)
assert QUESTIONS == original

app.play_again()
assert app.screen_name == "welcome"
assert app.name_var.get() == "Asha"
assert app.score == 0
assert app.answer_log == []
assert app.quiz_questions == []
assert app.timer_job is None
assert app.advance_job is None

app.name_var.set("   ")
app.on_start_welcome()
assert app.screen_name == "welcome"
assert app.player_name == "Asha"
assert app.name_error.cget("text") == "Please enter your name."

app.show_welcome()
quiz_app.messagebox.askyesno = lambda *args, **kwargs: True
app.confirm_exit()
try:
    still_open = app.winfo_exists() == 1
except tk.TclError:
    still_open = False
assert not still_open

print("ALL TESTS PASSED")
