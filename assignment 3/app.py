import json
import random
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify, session, make_response

app = Flask(__name__)
app.secret_key = "quiz-secret-key"


# Helper functions

def load_questions():
    """Load questions from questions.json."""
    with open("questions.json", "r") as f:
        return json.load(f)


def load_users():
    """Load users from users.json. Returns empty dict if file doesn't exist yet."""
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_users(users):
    """Save users dict to users.json."""
    with open("users.json", "w") as f:
        json.dump(users, f)


def save_score_to_file(username, score, total):
    """Append score to scores.txt with a timestamp."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with open("scores.txt", "a") as f:
        f.write(f"{timestamp} - {username} - Score: {score}/{total}\n")


def fifty_fifty(choices, correct_answer):
    """Remove 2 wrong answers."""
    wrong_letters = [letter for letter in choices if letter != correct_answer]
    removed = random.sample(wrong_letters, 2)
    return {letter: text for letter, text in choices.items() if letter not in removed}


# Page routes

@app.route("/")
def index():
    """Home page — checks for username cookie to greet returning users."""
    username = request.cookies.get("username")
    return render_template("index.html", username=username)


@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


@app.route("/results")
def results():
    return render_template("results.html")


# API routes

@app.route("/api/set_user", methods=["POST"])
def set_user():
    """
    Save username in a cookie and look them up in users.json.
    New users get high_score: 0. Returning users get their stored high score.
    """
    data = request.get_json()
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"error": "Name cannot be empty"}), 400
    if len(name) > 50:
        return jsonify({"error": "Name must be 50 characters or fewer"}), 400

    users = load_users()
    is_new = name not in users
    if is_new:
        users[name] = {"high_score": 0}
        save_users(users)

    response = make_response(jsonify({
        "success":    True,
        "name":       name,
        "is_new":     is_new,
        "high_score": users[name]["high_score"]
    }))
    response.set_cookie("username", name, max_age=30 * 24 * 60 * 60, samesite="Lax")
    return response


@app.route("/api/user_history", methods=["GET"])
def user_history():
    """Return the username and their high score — used on the welcome screen."""
    username = request.cookies.get("username")
    high_score = 0
    if username:
        users = load_users()
        high_score = users.get(username, {}).get("high_score", 0)
    return jsonify({"username": username, "high_score": high_score})


@app.route("/api/questions", methods=["GET"])
def get_questions():
    """
    Return randomised questions to the client.
    The correct answer is stored in the session (server-side only) so the
    browser can't cheat by inspecting the response.
    """
    all_questions = load_questions()
    count = min(int(request.args.get("count", 10)), len(all_questions))
    selected = random.sample(all_questions, count)

    # Store answers in session, send questions without answers to browser
    session["quiz_questions"] = [
        {"id": q["id"], "answer": q["answer"], "choices": q["choices"], "explanation": q["explanation"]}
        for q in selected
    ]
    session["quiz_start_time"] = datetime.now(timezone.utc).isoformat()
    session["lifeline_used"] = False

    client_questions = [
        {"id": q["id"], "question": q["question"], "choices": q["choices"]}
        for q in selected
    ]
    return jsonify({"questions": client_questions})


@app.route("/api/fifty_fifty", methods=["POST"])
def use_fifty_fifty():
    """
    Removes 2 wrong answers.
    Can only be used once per quiz.
    """
    if session.get("lifeline_used"):
        return jsonify({"error": "You have already used your 50/50 lifeline."}), 400

    question_id = request.get_json().get("question_id")
    quiz_questions = session.get("quiz_questions", [])
    question = next((q for q in quiz_questions if q["id"] == question_id), None)

    if not question:
        return jsonify({"error": "Question not found"}), 404

    trimmed = fifty_fifty(question["choices"], question["answer"])
    question["choices"] = trimmed
    session["quiz_questions"] = quiz_questions
    session["lifeline_used"] = True
    session.modified = True

    return jsonify({"choices": trimmed})


@app.route("/api/submit_answer", methods=["POST"])
def submit_answer():
    """Check the player's answer against the session."""
    data = request.get_json()
    question_id = data.get("question_id")
    selected = data.get("selected_option", "").strip().lower()

    quiz_questions = session.get("quiz_questions", [])
    question = next((q for q in quiz_questions if q["id"] == question_id), None)

    if not question:
        return jsonify({"error": "Question not found"}), 404

    correct_letter = question["answer"]
    is_correct = selected == correct_letter

    return jsonify({
        "correct":        is_correct,
        "correct_letter": correct_letter,
        "correct_answer": question["choices"][correct_letter],
        "explanation":    question["explanation"]
    })


@app.route("/api/save_score", methods=["POST"])
def save_score():
    """
    Save the final score — updates high score in users.json and appends to scores.txt
    """
    data     = request.get_json()
    correct  = data.get("correct", 0)
    total    = data.get("total", 0)
    username = request.cookies.get("username", "Anonymous")

    # Update high score in users.json
    users = load_users()
    if username not in users:
        users[username] = {"high_score": 0}

    new_high_score = correct > users[username]["high_score"]
    if new_high_score:
        users[username]["high_score"] = correct
    save_users(users)

    # Append to scores.txt
    save_score_to_file(username, correct, total)

    return jsonify({
        "success":        True,
        "new_high_score": new_high_score,
        "high_score":     users[username]["high_score"]
    })


if __name__ == "__main__":
    app.run(debug=True)