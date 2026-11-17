"""Smart Quiz Challenge — start the desktop app from this file."""

import tkinter as tk

from quiz_app import QuizApp


def main():
    """Create the window and keep it open until the player exits."""
    try:
        app = QuizApp()
    except tk.TclError as error:
        print("Could not open the quiz window. Tkinter may not be installed.")
        print(error)
        return
    app.mainloop()


if __name__ == "__main__":
    main()
