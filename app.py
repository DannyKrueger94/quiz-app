from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Cambia la chiave!
ADMIN_PASSWORD = "admin123"        # Cambiala!

QUESTIONS_FILE = "questions.json"
DATA_FILE = "data.json"
TEAMS_FILE = "teams.json"

# In-memory storage for active teams (for real-time features)
active_teams = {}
# Structure: {team_id: {
#     "name": str,
#     "password": str,
#     "admin_session": str,
#     "members": [session_ids],
#     "current_question": int,
#     "votes": {member_session: answer},
#     "answers": {}
# }}

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
    return redirect(url_for("select_mode"))

@app.route("/mode")
def select_mode():
    """Scegli tra modalità singola o squadra"""
    return render_template("mode_select.html")

@app.route("/team/create")
def create_team():
    """Form per creare una nuova squadra"""
    return render_template("team_create.html")

@app.route("/team/create", methods=["POST"])
def create_team_post():
    """Crea una nuova squadra e diventa admin"""
    import random
    team_name = request.form.get("team_name")
    team_password = request.form.get("team_password")
    admin_name = request.form.get("admin_name")
    
    if not team_name or not team_password or not admin_name:
        return "Tutti i campi sono obbligatori", 400
    
    # Generate unique team ID: team_name + random number 1-100
    random_num = random.randint(1, 100)
    team_name_clean = team_name.replace(" ", "_").lower()[:15]  # Max 15 chars
    team_id = f"{team_name_clean}_{random_num}"
    
    # Create team
    active_teams[team_id] = {
        "name": team_name,
        "password": team_password,
        "admin_session": session.sid if hasattr(session, 'sid') else id(session),
        "admin_name": admin_name,
        "members": [],
        "current_question": -1,  # -1 = lobby, 0+ = quiz started
        "votes": {},
        "answers": {},
        "final_answer": None
    }
    
    # Set session data
    session["team_id"] = team_id
    session["is_team_admin"] = True
    session["player_name"] = admin_name
    
    return redirect(url_for("team_lobby"))

@app.route("/team/join")
def join_team():
    """Form per unirsi a una squadra"""
    return render_template("team_join.html")

@app.route("/team/join", methods=["POST"])
def join_team_post():
    """Unisciti a una squadra esistente"""
    team_id = request.form.get("team_id")
    team_password = request.form.get("team_password")
    member_name = request.form.get("member_name")
    
    if not team_id or not team_password or not member_name:
        return "Tutti i campi sono obbligatori", 400
    
    # Check if team exists
    if team_id not in active_teams:
        return render_template("team_error.html", message="Squadra non trovata")
    
    team = active_teams[team_id]
    
    # Check password
    if team["password"] != team_password:
        return render_template("team_error.html", message="Password errata")
    
    # Check if team is full (max 6 members + 1 admin)
    if len(team["members"]) >= 6:
        return render_template("team_error.html", message="Squadra piena (massimo 6 membri)")
    
    # Add member
    member_session_id = session.sid if hasattr(session, 'sid') else id(session)
    if member_session_id not in team["members"]:
        team["members"].append(member_session_id)
    
    # Set session data
    session["team_id"] = team_id
    session["is_team_admin"] = False
    session["player_name"] = member_name
    
    return redirect(url_for("team_lobby"))

@app.route("/team/lobby")
def team_lobby():
    """Lobby della squadra - mostra membri connessi"""
    team_id = session.get("team_id")
    if not team_id or team_id not in active_teams:
        return redirect(url_for("select_mode"))
    
    team = active_teams[team_id]
    is_admin = session.get("is_team_admin", False)
    
    return render_template("team_lobby.html", 
                         team=team, 
                         team_id=team_id,
                         is_admin=is_admin,
                         member_count=len(team["members"]))

@app.route("/team/start", methods=["POST"])
def start_team_quiz():
    """L'admin avvia il quiz per tutta la squadra"""
    team_id = session.get("team_id")
    if not team_id or team_id not in active_teams:
        return redirect(url_for("select_mode"))
    
    if not session.get("is_team_admin"):
        return "Solo l'admin può avviare il quiz", 403
    
    team = active_teams[team_id]
    team["current_question"] = 0
    team["votes"] = {}
    team["answers"] = {}
    team["final_answer"] = None
    
    return redirect(url_for("team_quiz"))

@app.route("/team/quiz")
def team_quiz():
    """Schermata quiz per la squadra"""
    team_id = session.get("team_id")
    if not team_id or team_id not in active_teams:
        return redirect(url_for("select_mode"))
    
    team = active_teams[team_id]
    questions = load_questions()
    current_idx = team["current_question"]
    
    if current_idx >= len(questions):
        return redirect(url_for("team_submit"))
    
    current_question = questions[current_idx]
    is_admin = session.get("is_team_admin", False)
    
    # Get current votes
    votes_summary = {}
    for answer in ["A", "B", "C", "D", "E"]:
        votes_summary[answer] = sum(1 for v in team["votes"].values() if v == answer)
    
    return render_template("team_quiz.html",
                         question=current_question,
                         current=current_idx + 1,
                         total=len(questions),
                         is_admin=is_admin,
                         team=team,
                         votes=votes_summary,
                         final_answer=team.get("final_answer"))

@app.route("/team/vote", methods=["POST"])
def team_vote():
    """Un membro vota per una risposta"""
    team_id = session.get("team_id")
    if not team_id or team_id not in active_teams:
        return jsonify({"error": "Team not found"}), 404
    
    if session.get("is_team_admin"):
        return jsonify({"error": "Admin non può votare"}), 403
    
    team = active_teams[team_id]
    answer = request.json.get("answer")
    
    if answer not in ["A", "B", "C", "D", "E"]:
        return jsonify({"error": "Risposta non valida"}), 400
    
    # Store vote
    member_session_id = session.sid if hasattr(session, 'sid') else id(session)
    team["votes"][member_session_id] = answer
    
    # Calculate votes summary
    votes_summary = {}
    for ans in ["A", "B", "C", "D", "E"]:
        votes_summary[ans] = sum(1 for v in team["votes"].values() if v == ans)
    
    return jsonify({"success": True, "votes": votes_summary})

@app.route("/team/answer", methods=["POST"])
def team_answer():
    """L'admin conferma la risposta finale"""
    team_id = session.get("team_id")
    if not team_id or team_id not in active_teams:
        return redirect(url_for("select_mode"))
    
    if not session.get("is_team_admin"):
        return "Solo l'admin può confermare la risposta", 403
    
    team = active_teams[team_id]
    questions = load_questions()
    current_idx = team["current_question"]
    
    if current_idx >= len(questions):
        return redirect(url_for("team_submit"))
    
    answer = request.form.get("answer")
    if answer:
        team["answers"][str(questions[current_idx]["id"])] = answer
        team["current_question"] = current_idx + 1
        team["votes"] = {}  # Reset votes for next question
        team["final_answer"] = None
    
    return redirect(url_for("team_quiz"))

@app.route("/team/submit")
def team_submit():
    """Invia i risultati della squadra"""
    team_id = session.get("team_id")
    if not team_id or team_id not in active_teams:
        return redirect(url_for("select_mode"))
    
    team = active_teams[team_id]
    questions = load_questions()
    
    score = 0
    for q in questions:
        q_id = str(q["id"])
        ans = team["answers"].get(q_id)
        if ans == q["correct"]:
            score += 1
    
    save_submission(team["name"], team["answers"], score)
    
    is_admin = session.get("is_team_admin", False)
    
    return render_template("team_final.html", 
                         score=score, 
                         total=len(questions), 
                         team_name=team["name"],
                         is_admin=is_admin)

@app.route("/team/data")
def team_data():
    """API endpoint per aggiornamenti real-time"""
    team_id = session.get("team_id")
    if not team_id or team_id not in active_teams:
        return jsonify({"error": "Team not found"}), 404
    
    team = active_teams[team_id]
    
    # Calculate votes summary
    votes_summary = {}
    for answer in ["A", "B", "C", "D", "E"]:
        votes_summary[answer] = sum(1 for v in team["votes"].values() if v == answer)
    
    return jsonify({
        "current_question": team["current_question"],
        "votes": votes_summary,
        "member_count": len(team["members"]),
        "final_answer": team.get("final_answer")
    })

@app.route("/quiz", methods=["POST"])
def start_quiz():
    name = request.form.get("name")
    password = request.form.get("password")
    
    if not name or not password:
        return redirect(url_for("index"))
    
    # Check password
    if password != "quizdanny2025":
        return render_template("password_error.html")

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

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        pwd = request.form.get("password")
        if pwd == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_panel"))
        return "Password errata"
    return render_template("admin_login.html")

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
