# Assignment 3 — Requirements Satisfaction

## How to Run

```bash
pip install flask pytest
python app.py
# Open http://127.0.0.1:5000
```

## How to Run Tests

```bash
pytest tests/test_app.py -v
```

All 20 tests pass.

---

## Core Functional Requirements

### Clean and Intuitive UI
**Satisfied by:** `templates/`, `static/css/style.css`

The app has three pages (home, quiz, results) built with HTML, CSS, and Jinja templates. Answer buttons highlight green/red after each answer, a progress bar fills as the quiz advances, and a score counter updates live. Error messages appear inline without page reloads.

### Questions Loaded Dynamically from JSON
**Satisfied by:** `questions.json`, `load_questions()` in `app.py`, `GET /api/questions`

All questions are stored in `questions.json` using the same format as Assignment 1 (choices dict with a/b/c/d keys). The `/api/questions` route loads the file, randomly picks 10 questions using `random.sample()`, and returns them to the browser. No questions are hard-coded in any template or Python file.

### Randomized Question Order
**Satisfied by:** `random.sample()` in `GET /api/questions`

`random.sample()` returns questions in a different random order every session.

### Answer Submission and Real-Time Feedback
**Satisfied by:** `POST /api/submit_answer`, `templates/quiz.html`

When the player clicks an answer button, the browser sends the question ID and chosen letter to `/api/submit_answer`. The server checks it against the answer stored in the session and returns whether it was correct, the correct answer text, and an explanation. The page updates button colours and shows the explanation immediately — no page reload.

### Score Tracking
**Satisfied by:** `templates/quiz.html` (JavaScript), `POST /api/save_score`

The score is tracked in JavaScript as the quiz runs and displayed live. When the quiz ends, the final score is sent to `/api/save_score`, which updates the high score in `users.json` and appends a line to `scores.txt` — the same files used in Assignment 1.

### Data Stored in JSON / Data Files
**Satisfied by:** `questions.json`, `users.json`, `scores.txt`

| File | What it stores |
|---|---|
| `questions.json` | All quiz questions, choices, answers, explanations |
| `users.json` | Each player's username and all-time high score |
| `scores.txt` | Timestamped log of every completed quiz |

### Flask Backend with RESTful API Routes
**Satisfied by:** `app.py`

| Route | Method | What it does |
|---|---|---|
| `/` | GET | Home / welcome page |
| `/quiz` | GET | Quiz page |
| `/results` | GET | Results page |
| `/api/set_user` | POST | Save username in a cookie, look up high score in users.json |
| `/api/user_history` | GET | Return username and high score for the welcome screen |
| `/api/questions` | GET | Return 10 randomised questions (answer key stored server-side only) |
| `/api/fifty_fifty` | POST | Remove 2 wrong answers (50/50 lifeline, once per quiz) |
| `/api/submit_answer` | POST | Check the player's answer against the session |
| `/api/save_score` | POST | Update high score in users.json and append to scores.txt |

### Score and Feedback on Results Page
**Satisfied by:** `templates/results.html`

The results page shows: correct count, incorrect count, accuracy %, a grade badge (Outstanding / Great Work / Good Effort / Keep Practising), personal best from `users.json`, and a "New Personal Best!" banner if the current run beats the stored high score.

### Error Handling and Input Validation
**Satisfied by:** `app.py`, `templates/index.html`

- Submitting an empty name returns HTTP 400 and shows an inline error message.
- Names over 50 characters are rejected with HTTP 400.
- Submitting an answer for an unknown question ID returns HTTP 404.
- If questions fail to load in the browser, an error card is shown instead of a blank page.

---

## Individual Requirements

### 1 — Persistent User Identification and History
**Satisfied by:** `app.py`, `templates/index.html`, `templates/results.html`, `users.json`

- **First visit:** The home page checks for a `username` cookie. If none exists, a name-entry form is shown.
- **Saving the name:** `POST /api/set_user` validates the name, adds the user to `users.json` with `high_score: 0`, and sets a `username` cookie with a 30-day expiry.
- **Return visit:** `GET /api/user_history` reads the cookie and looks up the high score in `users.json`. The welcome page greets the user by name and shows their personal best.
- **High score update:** After each quiz, `POST /api/save_score` compares the new score to the stored high score and updates `users.json` if it is beaten.
- **`test_app.py` verifies:** cookie is set on `/api/set_user`, new users start at 0, empty names are rejected, `/api/user_history` returns the stored username, and a new high score is correctly flagged.

### 2 — Responsive Design for Mobile
**Satisfied by:** `static/css/style.css`, `templates/base.html`

- CSS is written **mobile-first**: the base styles target small screens and three `min-width` breakpoints (560 px, 768 px, 1024 px) progressively enhance layout for larger screens.
- `<meta name="viewport" content="width=device-width, initial-scale=1.0">` is set in `base.html` so mobile browsers scale correctly.
- Font sizes use `clamp()` so they scale fluidly between screen sizes.
- The name input row uses `display: flex` with `min-width: 0` so it stays usable on narrow screens.
- A `prefers-reduced-motion` media query disables all animations for users who have that accessibility setting enabled.

---

## Non-Functional Requirements

### User-Friendliness
Progress bar, live score counter, colour-coded answer buttons, per-question explanations, and a grade badge on the results page all guide the player through the quiz without needing instructions.

### Performance
Questions load from a small local JSON file. JavaScript handles score tracking on the client side. Server responses are small JSON objects with no unnecessary data.

### Quality Assurance
`tests/test_app.py` has 20 automated tests in 7 classes. Run with `pytest tests/test_app.py -v`.

| Test class | What it checks |
|---|---|
| `TestPageRoutes` | `/`, `/quiz`, `/results` all return HTTP 200 |
| `TestQuestionsAPI` | 10 questions returned, required fields present, answer key not sent to browser, `?count=` param works |
| `TestAnswerSubmission` | Correct answer detected, wrong answer detected, invalid question ID returns 404 |
| `TestFiftyFifty` | Reduces choices to 2, correct answer survives, returns 400 on second use |
| `TestUserIdentification` | Cookie set on `/api/set_user`, new users start at 0, empty name rejected, `/api/user_history` returns username |
| `TestScoreSaving` | Returns success, flags new high score correctly |
| `TestFullQuizFlow` | End-to-end: set user → load questions → use lifeline → answer all → save score |

### Maintainability
- `app.py` is divided into clearly labelled sections: helper functions, page routes, API routes.
- All HTML is in separate template files that extend `base.html`, so the header only needs to be changed in one place.
- CSS uses variables (`--accent`, `--correct`, `--wrong`, etc.) so colours can be changed in one place.
- Questions are in `questions.json` — new questions can be added without touching any Python or HTML.

---

## AI Usage

Claude AI was used throughout this assignment in small focused steps:

1. **Flask session design** — asked how to store answer keys server-side so the browser can't see them. Reviewed the explanation and wrote the `/api/questions` and `/api/submit_answer` routes based on it.
2. **Cookie persistence** — asked how `make_response` and `set_cookie` work in Flask. Adapted the pattern into `/api/set_user` and `/api/user_history`.
3. **50/50 lifeline route** — the `fifty_fifty()` function is copied from Assignment 1. Asked Claude how to expose it as an API route and how to update the session afterward. The `session.modified = True` line was explained before keeping it.
4. **Responsive CSS** — asked Claude to explain mobile-first CSS and what breakpoints to use. Reviewed the suggestions and kept the three breakpoints (560/768/1024 px) because they match common device sizes.
5. **Test file** — asked Claude to help write one test class at a time and reviewed each test before including it. The `TestFullQuizFlow` integration test was written independently.
6. **Simplification** — the first generated version was too complex for a starter class (it had a score history cookie storing JSON arrays). Asked Claude to simplify it, reviewed the result, and confirmed the simpler version still met all requirements.

All generated code was read and understood before use. Code that was not understood was either removed or rewritten in a simpler way.
