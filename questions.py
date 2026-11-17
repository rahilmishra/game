"""Question bank for Smart Quiz Challenge.

Questions are stored in a dictionary of lists. Each question is itself a
dictionary with the question text, four options, and exactly one answer.
The answer string must match one option exactly.
"""

import random

# How many questions a player sees in one game.
QUESTIONS_PER_QUIZ = 10

# Display order of the category cards.
CATEGORY_ORDER = [
    "Python Programming",
    "Science",
    "Sports",
    "General Knowledge",
]

# Short text shown on each category card.
CATEGORY_DETAILS = {
    "Python Programming": {
        "tag": "PY",
        "blurb": "Syntax, data types, and programming basics",
    },
    "Science": {
        "tag": "SC",
        "blurb": "Physics, chemistry, biology, and space",
    },
    "Sports": {
        "tag": "SP",
        "blurb": "Rules, events, and famous sporting facts",
    },
    "General Knowledge": {
        "tag": "GK",
        "blurb": "India, the world, and everyday facts",
    },
}

QUESTIONS = {
    "Python Programming": [
        {
            "question": "Which keyword is used to define a function in Python?",
            "options": ["define", "func", "def", "function"],
            "answer": "def",
        },
        {
            "question": "Which of these data types is immutable?",
            "options": ["list", "dictionary", "set", "tuple"],
            "answer": "tuple",
        },
        {
            "question": 'What is the result of len("quiz")?',
            "options": ["3", "4", "5", "0"],
            "answer": "4",
        },
        {
            "question": "Which symbol starts a single-line comment in Python?",
            "options": ["//", "#", "<!--", "%"],
            "answer": "#",
        },
        {
            "question": "Which data type stores unique items and has no fixed order?",
            "options": ["list", "tuple", "set", "string"],
            "answer": "set",
        },
        {
            "question": "What sequence does range(3) produce?",
            "options": ["0, 1, 2", "1, 2, 3", "0, 1, 2, 3", "3, 2, 1"],
            "answer": "0, 1, 2",
        },
        {
            "question": "Which list method adds one item at the end of a list?",
            "options": ["add()", "push()", "append()", "insert_end()"],
            "answer": "append()",
        },
        {
            "question": "What is the value of the expression 2 ** 3?",
            "options": ["5", "6", "8", "9"],
            "answer": "8",
        },
        {
            "question": "Which statements are used to handle runtime errors in Python?",
            "options": ["try and except", "catch and throw", "error and fix", "guard and rescue"],
            "answer": "try and except",
        },
        {
            "question": "What does OOP stand for?",
            "options": [
                "Object-Oriented Programming",
                "Only One Program",
                "Open Option Process",
                "Ordered Output Program",
            ],
            "answer": "Object-Oriented Programming",
        },
    ],
    "Science": [
        {
            "question": "What is the chemical formula of water?",
            "options": ["CO2", "H2O", "NaCl", "O2"],
            "answer": "H2O",
        },
        {
            "question": "Which planet is closest to the Sun?",
            "options": ["Venus", "Earth", "Mercury", "Mars"],
            "answer": "Mercury",
        },
        {
            "question": "Which gas do plants absorb during photosynthesis?",
            "options": ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"],
            "answer": "Carbon dioxide",
        },
        {
            "question": "Which organelle is known as the powerhouse of the cell?",
            "options": ["Nucleus", "Ribosome", "Mitochondria", "Chloroplast"],
            "answer": "Mitochondria",
        },
        {
            "question": "What is the approximate speed of light in a vacuum?",
            "options": ["3 x 10^8 m/s", "3 x 10^5 m/s", "340 m/s", "1,500 m/s"],
            "answer": "3 x 10^8 m/s",
        },
        {
            "question": "What is the boiling point of pure water at sea level?",
            "options": [
                "0 degrees Celsius",
                "50 degrees Celsius",
                "100 degrees Celsius",
                "212 degrees Celsius",
            ],
            "answer": "100 degrees Celsius",
        },
        {
            "question": "Which is the largest organ of the human body?",
            "options": ["Liver", "Skin", "Heart", "Brain"],
            "answer": "Skin",
        },
        {
            "question": "Which equation states Newton's second law of motion?",
            "options": ["F = ma", "V = IR", "E = mc^2", "P = IV"],
            "answer": "F = ma",
        },
        {
            "question": "What is the pH value of a neutral solution?",
            "options": ["0", "5", "7", "14"],
            "answer": "7",
        },
        {
            "question": "Which is the natural satellite of Earth?",
            "options": ["Titan", "Moon", "Phobos", "Europa"],
            "answer": "Moon",
        },
    ],
    "Sports": [
        {
            "question": "How many players from one team are on the field in a standard football (soccer) match?",
            "options": ["9", "10", "11", "12"],
            "answer": "11",
        },
        {
            "question": "How often are the Summer Olympic Games normally held?",
            "options": ["Every year", "Every 2 years", "Every 4 years", "Every 5 years"],
            "answer": "Every 4 years",
        },
        {
            "question": "In cricket, how many runs are scored when the ball crosses the boundary along the ground?",
            "options": ["1", "3", "4", "6"],
            "answer": "4",
        },
        {
            "question": "What is the standard height of a basketball hoop?",
            "options": ["8 feet", "9 feet", "10 feet", "12 feet"],
            "answer": "10 feet",
        },
        {
            "question": "Which Grand Slam tennis tournament is played on grass?",
            "options": ["Australian Open", "French Open", "Wimbledon", "US Open"],
            "answer": "Wimbledon",
        },
        {
            "question": "Which country won the FIFA World Cup in 2022?",
            "options": ["France", "Brazil", "Argentina", "Germany"],
            "answer": "Argentina",
        },
        {
            "question": "How many rings appear on the Olympic flag?",
            "options": ["4", "5", "6", "7"],
            "answer": "5",
        },
        {
            "question": "What do players hit across the net in badminton?",
            "options": ["A ball", "A puck", "A shuttlecock", "A disc"],
            "answer": "A shuttlecock",
        },
        {
            "question": "How many players from one team are on the field in a standard field hockey match?",
            "options": ["6", "9", "11", "15"],
            "answer": "11",
        },
        {
            "question": "How many pieces does each player start with in chess?",
            "options": ["12", "14", "16", "18"],
            "answer": "16",
        },
    ],
    "General Knowledge": [
        {
            "question": "What is the capital of India?",
            "options": ["Mumbai", "New Delhi", "Kolkata", "Bengaluru"],
            "answer": "New Delhi",
        },
        {
            "question": "Which is the largest ocean on Earth?",
            "options": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
            "answer": "Pacific Ocean",
        },
        {
            "question": "What is the currency of Japan?",
            "options": ["Yuan", "Won", "Yen", "Ringgit"],
            "answer": "Yen",
        },
        {
            "question": "Which animal is the national animal of India?",
            "options": ["Lion", "Elephant", "Tiger", "Peacock"],
            "answer": "Tiger",
        },
        {
            "question": "How many continents are there?",
            "options": ["5", "6", "7", "8"],
            "answer": "7",
        },
        {
            "question": "Who is credited with inventing the telephone?",
            "options": [
                "Thomas Edison",
                "Alexander Graham Bell",
                "Isaac Newton",
                "Nikola Tesla",
            ],
            "answer": "Alexander Graham Bell",
        },
        {
            "question": "In which city is the Taj Mahal located?",
            "options": ["Delhi", "Jaipur", "Agra", "Lucknow"],
            "answer": "Agra",
        },
        {
            "question": "Which is the largest planet in our solar system?",
            "options": ["Earth", "Saturn", "Jupiter", "Neptune"],
            "answer": "Jupiter",
        },
        {
            "question": "In which year was the United Nations founded?",
            "options": ["1919", "1945", "1950", "1965"],
            "answer": "1945",
        },
        {
            "question": "Which river is traditionally taught as the longest river in the world?",
            "options": ["Amazon", "Nile", "Ganga", "Yangtze"],
            "answer": "Nile",
        },
    ],
}


def validate_question_bank():
    """Check the bank once at startup so a bad question cannot crash a game."""
    if list(CATEGORY_DETAILS) != CATEGORY_ORDER:
        raise ValueError("Category details are not in the same order as CATEGORY_ORDER.")

    for name in CATEGORY_ORDER:
        items = QUESTIONS.get(name)
        if not items or len(items) < QUESTIONS_PER_QUIZ:
            raise ValueError(f"{name} needs at least {QUESTIONS_PER_QUIZ} questions.")

        seen_questions = set()
        for item in items:
            question_text = item.get("question", "")
            options = item.get("options", [])
            answer = item.get("answer", "")
            if question_text in seen_questions:
                raise ValueError(f"Duplicate question in {name}: {question_text}")
            seen_questions.add(question_text)
            if len(options) != 4 or len(set(options)) != 4:
                raise ValueError(f"Each question needs 4 unique options: {question_text}")
            # Exactly one option is correct, and it must be one of the four strings.
            if options.count(answer) != 1:
                raise ValueError(f"Answer must match one option: {question_text}")


def prepare_quiz(category_name):
    """Copy and shuffle questions so every new game has a new order.

    random.sample chooses each question once and shuffles the selection.
    Copies are returned so a game cannot change the original bank.
    """
    bank = QUESTIONS[category_name]
    chosen = random.sample(bank, QUESTIONS_PER_QUIZ)
    quiz = []
    for item in chosen:
        quiz.append(
            {
                "question": item["question"],
                "options": list(item["options"]),
                "answer": item["answer"],
            }
        )
    return quiz


validate_question_bank()
