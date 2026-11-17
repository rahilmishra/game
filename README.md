# Smart Quiz Challenge

Smart Quiz Challenge is a desktop quiz for a B.Tech CSE mini project. The player types a name, picks a category, and answers 10 multiple-choice questions. Each question has a 20 second timer. At the end, the app shows the score, the percentage, and a short performance message.

The program uses Python and Tkinter. It does not need any third-party packages, so it can run on a Windows lab PC after Python is installed.

## Features

- Welcome screen with a dark navy and purple card layout
- Player name check (blank names are not accepted)
- Four categories: Python Programming, Science, Sports, and General Knowledge
- 10 multiple-choice questions in each category, with four options and one correct answer
- One question on screen at a time, shown as "Question 1 of 10"
- Correct and incorrect feedback, including the right answer after a miss
- One point for a correct answer and zero points for a wrong answer or a timeout
- A player can select only one option for each question
- Visual progress bar that moves after every question
- 20 second countdown that stops when an answer is submitted
- Automatic move to the next question when time runs out
- Questions are shuffled at the start of every new game
- Windows sound cues for a correct answer, a wrong answer, and a timeout
- Result screen with name, category, totals, score, percentage, and a performance message
- Play Again and Exit, with a confirmation message before the window closes

### Performance messages

| Percentage | Message |
| --- | --- |
| 90–100% | Excellent! |
| 75–89% | Very Good! |
| 50–74% | Good Job! |
| Below 50% | Keep Practicing! |

Percentage is calculated as:

```text
Percentage = (Correct Answers / Total Questions) × 100
```

The result is rounded to the nearest whole number. With 10 questions, every score lands on a whole ten (0%, 10%, 20%, and so on).

## Project architecture

```text
jiya project/
├── main.py         # Starts the application
├── quiz_app.py     # Screens, scoring, timer, and events
├── questions.py    # Category list and question bank
├── styles.py       # Colors and fonts
└── README.md       # This file
```

The window is one object, `QuizApp`. It shows one screen at a time:

1. **Welcome** collects the player name.
2. **Category** stores the chosen subject.
3. **Quiz** shows one question, checks the answer, and updates the score.
4. **Result** reads the answer log and displays the final figures.

`main.py` only creates that object and calls `mainloop()`. The question text lives in `questions.py`, away from the buttons and colors. `styles.py` keeps the navy and purple theme in one place so the screens match.

A new game calls `prepare_quiz()`. That function copies 10 questions and shuffles their order. The original lists in `QUESTIONS` stay unchanged.

## Purpose of each file

| File | Purpose |
| --- | --- |
| `main.py` | Entry point. Run this file to open the quiz. |
| `quiz_app.py` | The `QuizApp` class, the progress bar, score maths, timer, and all four screens. |
| `questions.py` | The question dictionary, category names, and the shuffle helper. |
| `styles.py` | Shared colors and fonts. |
| `README.md` | How the project is built, how to run it, and how to explain it in a viva. |

## Python concepts used

The project is a small example of the concepts from a first programming course.

- **Variables.** `player_name`, `score`, `time_left`, and `question_index` hold the current game. They are reset when the player starts again.
- **Data types.** Names and messages are strings. The score, timer, and question number are integers. The percentage uses division, then `round`. `answered` is a Boolean that locks a question after the first choice.
- **Lists.** Every category stores questions in a list. Each question has an `options` list of four strings. `answer_log` is a list of the player's results, one item per question. `random.sample` builds a new shuffled list for the game.
- **Dictionaries.** `QUESTIONS` maps a category name to its list. One question looks like `{"question": "...", "options": [...], "answer": "..."}`. `COLORS` and `CATEGORY_DETAILS` are dictionaries too.
- **Functions.** `prepare_quiz()` builds a game. `calculate_percentage()` applies the percentage formula. `performance_message()` chooses Excellent, Very Good, Good Job, or Keep Practicing. `validate_question_bank()` checks that every question has four options and one matching answer.
- **Classes.** `QuizApp` is the window. `ProgressBar` is a small class that draws the bar. Both use attributes (`self.score`) and methods (`self.show_question()`).
- **Loops.** The category screen loops over `CATEGORY_ORDER` to build four cards. The quiz loops over the four options. The result adds up correct answers with `sum(...)` over `answer_log`.
- **Conditional statements.** The welcome screen rejects an empty name with `if not name`. Answer checking uses `if is_correct`. The timer uses `if self.time_left <= 0`. The performance message uses a chain of `if` / comparisons (`>= 90`, `>= 75`, `>= 50`).
- **Event handling.** Tkinter calls a function when something happens. The Start button calls `on_start_welcome`. Option cards use `bind("<Button-1>", ...)`. The name box uses the Return key. `after(1000, self._tick)` is the timer event. The window close button is handled with `WM_DELETE_WINDOW`, which opens the exit confirmation.

There is no `while` loop waiting for the next question. After `mainloop()` starts, the program waits for events.

## How a point is awarded

1. The player clicks one option, or the timer reaches zero.
2. `answered` is set to `True` immediately. Later clicks on the same question return at once, so the score cannot rise twice.
3. A matching option adds 1 to `score` and appends one log entry with `is_correct` set to `True`.
4. A wrong option or a timeout appends one log entry with `is_correct` set to `False`. The score does not change.
5. The result screen counts the log again. That second count is what the result card shows, so the on-screen score and the final score stay the same.

## Timer behaviour

- The countdown starts at 20 seconds for every question.
- Choosing an answer cancels the timer. It does not keep running in the background.
- At zero, the question is marked incorrect, the correct option is shown, and the app moves on after a short pause (about 1.8 seconds). The player can also press Next Question or View Result during that pause.
- Starting another question, playing again, or closing the window cancels any previous `after()` callback.
- If the player opens the exit confirmation during a question, the countdown pauses and resumes only if they choose to stay.

## Install and run on Windows

Python 3.10 or newer is enough. Tkinter is included with the official Windows installer from [python.org](https://www.python.org/downloads/windows/). No `pip install` step is required.

1. Install Python and tick **Add python.exe to PATH**.
2. Open the project folder.
3. In PowerShell or Command Prompt, run:

```bat
python main.py
```

If that command is not recognized, use the Windows Python launcher:

```bat
py main.py
```

You can also run `quiz_app.py`. The supported entry point for the demonstration is `main.py`.

### If the window does not open

- Run `python --version` and confirm Python 3 is installed.
- Reinstall Python and include **tcl/tk and IDLE**.
- Sound uses the Windows system beep through `winsound`. If the PC is muted, the quiz still runs. A sound error is ignored on purpose.

## Demonstration script

Use this order in the viva so every feature is visible.

1. Run `python main.py`.
2. Press **Start Quiz** with an empty name and show the validation message.
3. Enter a name and open the category screen. Use **Back**, then come forward again.
4. Select a category. The card highlight and the "Selected" line should change. Repeat for another category if asked.
5. Start the quiz. Point out the question number, the four options, the progress bar, and the 20 second timer.
6. Answer one question correctly and one incorrectly. Show that a second click does not change the score.
7. Let one timer run out and show the automatic next question.
8. Finish the quiz and read the result: name, category, total, correct, incorrect, score, percentage, and message.
9. Press **Play Again** and show that the score starts over.
10. Press **Exit** (or the window close button) and show the confirmation. Choose No, then Yes.

## Future enhancements

- Save a local leaderboard in a text or CSV file
- Let a teacher add questions without editing code
- Add difficulty levels
- Review every answer on the result screen
- Add more categories, such as Mathematics or History

## Notes for the viva

- Only the Python standard library is used: `tkinter`, `random`, `winsound`, and `ctypes`.
- The question bank is checked when the program starts. A question with a missing or extra answer stops startup with a clear error instead of failing mid-demo.
- Timeout answers are incorrect. They are included in "Incorrect Answers" and they do not reduce the score below zero.
