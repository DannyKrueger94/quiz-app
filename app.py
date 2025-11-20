from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Cambia la chiave!
ADMIN_PASSWORD = "admin123"        # Cambiala!

QUESTIONS_FILE = "questions.json"
DATA_FILE = "data.json"

def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_submission(name, answers, score):
    # Try to read existing data
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                else:
                    data = []
        else:
            data = []
    except (json.JSONDecodeError, ValueError, OSError):
        # If file is corrupted or can't be read, start fresh
        data = []

    data.append({
        "name": name,
        "answers": answers,
        "score": score
    })

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except OSError:
        # If we can't write to file, continue without saving (for read-only filesystems)
        pass

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/quiz", methods=["POST"])
def start_quiz():
    name = request.form.get("name")
    if not name:
        return redirect(url_for("index"))

    session["player_name"] = name
    session["current_question"] = 0
    session["user_answers"] = {}
    return redirect(url_for("quiz"))

@app.route("/quiz")
def quiz():
    if "player_name" not in session:
        return redirect(url_for("index"))
    
    questions = load_questions()
    current_idx = session.get("current_question", 0)
    
    # Fix: Check if we've reached the end of questions
    if current_idx >= len(questions):
        return redirect(url_for("submit"))
    
    current_question = questions[current_idx]
    total_questions = len(questions)
    
    return render_template("quiz.html", 
                         question=current_question, 
                         current=current_idx + 1, 
                         total=total_questions)

@app.route("/quiz/answer", methods=["POST"])
def answer_question():
    if "player_name" not in session:
        return redirect(url_for("index"))
    
    questions = load_questions()
    current_idx = session.get("current_question", 0)
    
    # Fix: Check bounds before accessing questions
    if current_idx >= len(questions):
        return redirect(url_for("submit"))
    
    answer = request.form.get("answer")
    if answer:
        user_answers = session.get("user_answers", {})
        user_answers[str(questions[current_idx]["id"])] = answer
        session["user_answers"] = user_answers
    
    session["current_question"] = current_idx + 1
    return redirect(url_for("quiz"))

@app.route("/submit")
def submit():
    if "player_name" not in session:
        return redirect(url_for("index"))
    
    name = session.get("player_name")
    user_answers = session.get("user_answers", {})
    questions = load_questions()

    score = 0
    for q in questions:
        q_id = str(q["id"])
        ans = user_answers.get(q_id)
        if ans == q["correct"]:
            score += 1

    save_submission(name, user_answers, score)
    
    # Clear session data
    session.pop("current_question", None)
    session.pop("user_answers", None)
    
    return render_template("final.html", score=score, total=len(questions), name=name)

@app.route("/admin")
def admin_login():
    return render_template("admin_login.html")

@app.route("/admin", methods=["POST"])
def admin_login_post():
    pwd = request.form.get("password")
    if pwd == ADMIN_PASSWORD:
        session["admin"] = True
        return redirect(url_for("admin_panel"))
    return "Password errata"

@app.route("/admin/panel")
def admin_panel():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    # Load questions
    questions = load_questions()

    # Load submissions
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                else:
                    data = []
        except (json.JSONDecodeError, ValueError):
            data = []
    else:
        data = []

    return render_template("admin.html", data=data, questions=questions)

@app.route("/admin/delete/<int:index>", methods=["POST"])
def delete_result(index):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                else:
                    data = []
        except (json.JSONDecodeError, ValueError):
            data = []
    else:
        data = []
    
    # Delete the result at the specified index
    if 0 <= index < len(data):
        data.pop(index)
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    
    return redirect(url_for("admin_panel"))

@app.route("/admin/delete-all", methods=["POST"])
def delete_all_results():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    # Clear all results
    with open(DATA_FILE, "w") as f:
        json.dump([], f, indent=4)
    
    return redirect(url_for("admin_panel"))

if __name__ == "__main__":
    # Development mode
    app.run(debug=True, host='0.0.0.0', port=5000)
# Production mode: use gunicorn app:app
