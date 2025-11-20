from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Cambia la chiave!
# Configurazione session più robusta per persistenza
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 ora
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
#     "admin_name": str,
#     "members": [session_ids],
#     "member_names": {session_id: name},
#     "current_question": int,
#     "votes": {member_session: answer},
#     "answers": {},
#     "final_answer": None
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
    return redirect(url_for("create_team"))

@app.route("/mode")
def select_mode():
    """Redirect a creazione squadra (modalità singola rimossa)"""
    return redirect(url_for("create_team"))

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
    
    # Generate unique admin ID per supportare multi-squadra
    admin_id = str(uuid.uuid4())
    
    # Create team (password case insensitive)
    active_teams[team_id] = {
        "name": team_name,
        "password": team_password.lower(),
        "admin_id": admin_id,  # UUID univoco per admin
        "admin_name": admin_name,
        "members": [],
        "member_names": {},
        "current_question": -1,  # -1 = lobby, 0+ = quiz started
        "votes": {},
        "answers": {},
        "final_answer": None,
        "admin_selected_answer": None  # Traccia cosa seleziona admin in tempo reale
    }
    
    # Set session data con UUID univoco
    session.permanent = True  # Rende la session persistente
    session["team_id"] = team_id
    session["admin_id"] = admin_id  # Salva admin ID univoco
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
    
    # Check if team exists (case insensitive)
    team_id_lower = team_id.lower()
    found_team_id = None
    for tid in active_teams.keys():
        if tid.lower() == team_id_lower:
            found_team_id = tid
            break
    
    if not found_team_id:
        return render_template("team_error.html", message="Squadra non trovata")
    
    team = active_teams[found_team_id]
    
    # Check password (case insensitive)
    if team["password"] != team_password.lower():
        return render_template("team_error.html", message="Password errata")
    
    # Check if team is full (max 6 members + 1 admin)
    if len(team["members"]) >= 6:
        return render_template("team_error.html", message="Squadra piena (massimo 6 membri)")
    
    # Generate unique member ID
    member_id = str(uuid.uuid4())
    
    print(f"[JOIN] Nuovo membro: {member_name} | ID: {member_id} | Team: {found_team_id}")
    
    # Add member
    team["members"].append(member_id)
    team["member_names"][member_id] = member_name
    
    # Set session data
    session.permanent = True  # Rende la session persistente
    session["team_id"] = found_team_id
    session["is_team_admin"] = False
    session["player_name"] = member_name
    session["member_id"] = member_id  # Salva l'ID univoco in session
    
    print(f"[JOIN] Session salvata: team_id={session.get('team_id')}, member_id={session.get('member_id')}")
    print(f"[JOIN] Membri totali in team: {len(team['members'])}")
    
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
        return redirect(url_for("create_team"))
    
    # Verifica che sia l'admin della PROPRIA squadra
    team = active_teams[team_id]
    admin_id = session.get("admin_id")
    if not admin_id or team["admin_id"] != admin_id:
        return "Solo l'admin di questa squadra può avviare il quiz", 403
    
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
    
    # Store vote usando member_id dalla session
    member_id = session.get("member_id")
    if not member_id:
        print(f"[ERROR] Member ID non trovato in session per team {team_id}")
        print(f"[DEBUG] Session data: {dict(session)}")
        return jsonify({"error": "Member ID not found"}), 400
    
    # Debug logging
    print(f"[VOTE] Team: {team_id}, Member: {member_id}, Answer: {answer}")
    print(f"[VOTE] Votes PRIMA: {team['votes']}")
    
    team["votes"][member_id] = answer
    
    print(f"[VOTE] Votes DOPO: {team['votes']}")
    print(f"[VOTE] Numero totale voti: {len(team['votes'])}")
    
    # Calculate votes summary
    votes_summary = {}
    for ans in ["A", "B", "C", "D", "E"]:
        votes_summary[ans] = sum(1 for v in team["votes"].values() if v == ans)
    
    return jsonify({"success": True, "votes": votes_summary})

@app.route("/team/admin/select", methods=["POST"])
def admin_select():
    """L'admin seleziona una risposta (non conferma ancora) - i membri vedono la selezione"""
    team_id = session.get("team_id")
    if not team_id or team_id not in active_teams:
        return jsonify({"error": "Team not found"}), 404
    
    # Verifica admin_id per multi-squadra
    team = active_teams[team_id]
    admin_id = session.get("admin_id")
    if not admin_id or team["admin_id"] != admin_id:
        return jsonify({"error": "Solo l'admin di questa squadra può selezionare"}), 403
    
    team = active_teams[team_id]
    answer = request.json.get("answer")
    
    # Salva la selezione temporanea dell'admin
    team["admin_selected_answer"] = answer
    
    return jsonify({"success": True, "selected": answer})

@app.route("/team/answer", methods=["POST"])
def team_answer():
    """L'admin conferma la risposta finale"""
    team_id = session.get("team_id")
    if not team_id or team_id not in active_teams:
        return redirect(url_for("create_team"))
    
    # Verifica admin_id per multi-squadra
    team = active_teams[team_id]
    admin_id = session.get("admin_id")
    if not admin_id or team["admin_id"] != admin_id:
        return "Solo l'admin di questa squadra può confermare la risposta", 403
    
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
        team["admin_selected_answer"] = None  # Reset selezione admin
    
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
        "member_names": list(team.get("member_names", {}).values()),
        "final_answer": team.get("final_answer"),
        "admin_selected": team.get("admin_selected_answer")  # Aggiunto per mostrare selezione admin
    })

# Modalità singola rimossa - solo modalità squadra disponibile

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
