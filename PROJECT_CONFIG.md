# 📋 Configurazione Progetto Quiz App

## 🎯 Descrizione del Progetto
**Quiz App** è un'applicazione web interattiva basata su Flask che offre due modalità di gioco:
- **Modalità Singola**: Quiz individuale con 12 domande
- **Modalità Squadra**: Quiz collaborativo con votazioni in tempo reale (1 admin + fino a 6 membri)

---

## 🛠️ Stack Tecnologico

### Backend
- **Framework**: Flask 3.1.2
- **Linguaggio**: Python 3.x
- **Template Engine**: Jinja2 3.1.6
- **Session Management**: Flask built-in sessions

### Frontend
- **HTML5** con CSS3
- **JavaScript Vanilla** (ES6+)
- **Design**: Responsive mobile-first
- **Animazioni**: CSS keyframes

### Dipendenze Python
```
flask==3.1.2
werkzeug==3.1.3
jinja2==3.1.6
click==8.3.1
itsdangerous==2.2.0
markupsafe==3.0.3
blinker==1.9.0
colorama==0.4.6
```

---

## 📁 Struttura del Progetto

```
Quiz/
│
├── app.py                      # File principale Flask
├── questions.json              # Database domande (12 domande)
├── data.json                   # Storage risultati quiz
├── requirements.txt            # Dipendenze Python
├── render.yaml                 # Config per deployment Render
├── README.md                   # Documentazione
├── PROJECT_CONFIG.md          # Questo file
│
├── templates/                  # Template HTML Jinja2
│   ├── mode_select.html       # Selezione modalità gioco
│   ├── index.html             # Home page (modalità singola)
│   ├── quiz.html              # Quiz modalità singola
│   ├── final.html             # Risultati modalità singola
│   ├── team_create.html       # Form creazione squadra
│   ├── team_join.html         # Form join squadra
│   ├── team_lobby.html        # Lobby pre-quiz squadra
│   ├── team_quiz.html         # Quiz modalità squadra
│   ├── team_final.html        # Risultati squadra
│   ├── team_error.html        # Pagina errori squadra
│   ├── password_error.html    # Errore password modalità singola
│   ├── admin_login.html       # Login pannello admin
│   └── admin.html             # Pannello amministrazione
│
└── Environment/                # Virtual environment (non committato)
```

---

## 🔧 Configurazione Iniziale

### 1. Prerequisiti
- **Python 3.8+** installato
- **Git** per clonare il repository
- **Editor di codice** (VS Code consigliato)

### 2. Setup Ambiente

#### Clonare il Repository
```bash
git clone https://github.com/DannyKrueger94/quiz-app.git
cd quiz-app
```

#### Creare Virtual Environment
```bash
# Windows
python -m venv Environment
Environment\Scripts\activate

# Linux/Mac
python3 -m venv Environment
source Environment/bin/activate
```

#### Installare Dipendenze
```bash
pip install -r requirements.txt
```

### 3. Configurazione File

#### app.py - Variabili di Configurazione
```python
app.secret_key = "supersecretkey"     # ⚠️ Cambiare in produzione!
ADMIN_PASSWORD = "admin123"           # ⚠️ Password pannello admin
PASSWORD_QUIZ_SINGOLA = "quizdanny2025"  # Password modalità singola
```

#### questions.json - Struttura Domande
```json
[
  {
    "id": 1,
    "question": "Testo della domanda?",
    "answers": {
      "A": "Risposta A",
      "B": "Risposta B",
      "C": "Risposta C",
      "D": "Risposta D",
      "E": "Risposta E"
    },
    "correct": "A",
    "image": "URL_immagine_opzionale"
  }
]
```

#### data.json - Storage Risultati
```json
[
  {
    "name": "Nome Giocatore/Squadra",
    "answers": {"1": "A", "2": "B", ...},
    "score": 8
  }
]
```

---

## 🚀 Esecuzione

### Modalità Sviluppo
```bash
# Attiva virtual environment
Environment\Scripts\activate  # Windows
source Environment/bin/activate  # Linux/Mac

# Avvia server
python app.py
```

L'app sarà disponibile su: `http://localhost:5000`

### Modalità Produzione
```bash
# Usando Gunicorn (Linux/Mac)
gunicorn app:app --bind 0.0.0.0:5000

# Usando Waitress (Windows)
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

---

## 🎮 Funzionalità Principali

### Modalità Singola
- **Route**: `/mode` → `/quiz`
- **Password**: Configurata in `app.py`
- **Flusso**: Home → Inserimento nome → Quiz → Risultati
- **Storage**: Salva risultati in `data.json`

### Modalità Squadra

#### Sistema di Creazione Squadra
- **Admin crea squadra** con:
  - Nome squadra
  - Password (case insensitive)
  - Nome admin
- **Team ID generato**: `{nome_squadra}_{numero_random_1-100}`

#### Join Squadra
- **Ricerca case insensitive** del Team ID
- **Password case insensitive**
- **Limite**: Max 6 membri + 1 admin
- **Tracciamento nomi**: Ogni membro ha nome visibile

#### Lobby e Sincronizzazione
- **Polling real-time**: 1 secondo
- **Aggiornamento automatico**: Lista membri si aggiorna quando qualcuno si unisce
- **Avvio quiz**: Solo admin può avviare

#### Sistema Votazioni
- **Membri votano**: Ogni membro seleziona una risposta
- **Admin vede voti**: Badge numerici accanto a ogni opzione
- **Aggiornamento live**: Voti si aggiornano in tempo reale
- **Admin conferma**: Sceglie risposta finale per la squadra

#### Storage In-Memory
```python
active_teams = {
    "team_id": {
        "name": str,                    # Nome squadra
        "password": str,                # Password (lowercase)
        "admin_session": str,           # Session ID admin
        "admin_name": str,              # Nome admin visibile
        "members": [session_ids],       # Lista session ID membri
        "member_names": {               # Dizionario session_id: nome
            session_id: name
        },
        "current_question": int,        # -1 = lobby, 0+ = quiz attivo
        "votes": {                      # Voti membri per domanda corrente
            member_session: answer
        },
        "answers": {},                  # Risposte confermate dall'admin
        "final_answer": None            # Risposta finale selezionata
    }
}
```

---

## 🎨 Design e UX

### Responsive Design
- **Mobile-first approach**
- **Breakpoint**: 480px
- **Touch-friendly**: Pulsanti grandi, no hover effects
- **Viewport settings**: `user-scalable=no`, tap highlight disabilitato

### Colori Principali
```css
/* Modalità Singola */
--primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Modalità Squadra */
--team-primary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);

/* Voti e Badge */
--vote-badge: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);

/* Success */
--success: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
```

### Animazioni
- **Confetti**: Per punteggi ≥80% nella pagina finale
- **Bounce**: Trofeo pagina risultati
- **Scale**: Feedback touch sui pulsanti
- **Pulse**: Animazione voti real-time

---

## 🔐 Sicurezza

### Password
- ✅ **Case insensitive**: Nome squadra e password
- ⚠️ **Non criptate**: Stored in plaintext (ambiente sviluppo)
- 🔄 **Consiglio**: Implementare hashing (bcrypt) in produzione

### Session Management
- **Flask sessions**: Cookie-based
- **Secret key**: Da cambiare in produzione
- **Session ID**: Utilizzato per tracciare membri squadra

### Admin Panel
- **Password protection**: `ADMIN_PASSWORD` in app.py
- **Funzioni**: Visualizza risultati, elimina singoli/tutti

---

## 📊 API Endpoints

### Pubblici
```
GET  /                      → Redirect a /mode
GET  /mode                  → Selezione modalità
POST /quiz                  → Avvia quiz singolo (con password)
GET  /quiz                  → Schermata quiz singolo
POST /quiz/answer           → Invia risposta quiz singolo
GET  /submit                → Risultati quiz singolo
```

### Squadra
```
GET  /team/create           → Form creazione squadra
POST /team/create           → Crea squadra (ritorna team_id)
GET  /team/join             → Form join squadra
POST /team/join             → Join a squadra esistente
GET  /team/lobby            → Lobby pre-quiz
POST /team/start            → Avvia quiz (solo admin)
GET  /team/quiz             → Schermata quiz squadra
POST /team/vote             → Invia voto membro (JSON)
POST /team/answer           → Conferma risposta admin
GET  /team/submit           → Risultati squadra
GET  /team/data             → API polling real-time (JSON)
```

### Admin
```
GET  /admin                 → Login admin
POST /admin                 → Autentica admin
GET  /admin/panel           → Pannello amministrazione
POST /admin/delete/<index>  → Elimina risultato singolo
POST /admin/delete-all      → Elimina tutti i risultati
```

---

## 🔄 Workflow Modalità Squadra

```
1. Admin crea squadra
   ↓
2. Team ID generato → condiviso con membri
   ↓
3. Membri si uniscono (polling attivo)
   ↓
4. Lobby mostra membri connessi (auto-refresh)
   ↓
5. Admin avvia quiz
   ↓
6. Per ogni domanda:
   - Membri votano
   - Voti si aggiornano real-time
   - Admin vede voti e conferma risposta
   - Reset voti, next question
   ↓
7. Alla fine: Risultati con badge performance
```

---

## 🐛 Troubleshooting

### Problema: Voti non si aggiornano
**Soluzione**: Verificare che il polling JavaScript sia attivo (console browser)

### Problema: Password non funziona
**Soluzione**: Controllare che sia case insensitive e lowercase in storage

### Problema: Membri non compaiono in lobby
**Soluzione**: 
- Verificare `member_names` nel dizionario `active_teams`
- Controllare che il polling ricarichi la pagina quando cambia `member_count`

### Problema: Team non trovato
**Soluzione**: Il Team ID è case insensitive, verificare la ricerca nel codice

### Problema: Session persa
**Soluzione**: Verificare che `app.secret_key` sia configurata correttamente

---

## 🚀 Deployment

### Render.com (Consigliato)
File `render.yaml` già configurato:
```yaml
services:
  - type: web
    name: quiz-app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

### Variabili d'Ambiente da Configurare
```
FLASK_SECRET_KEY=your_production_secret_key_here
ADMIN_PASSWORD=your_admin_password_here
```

### Heroku
```bash
# Procfile
web: gunicorn app:app

# Deploy
heroku create quiz-app-unique-name
git push heroku main
```

---

## 📝 Manutenzione

### Aggiungere Nuove Domande
1. Editare `questions.json`
2. Seguire la struttura JSON esistente
3. Incrementare l'ID progressivo
4. URL immagini opzionali

### Modificare Colori/Stile
- Ogni template ha `<style>` inline
- Variabili CSS nei gradient
- Media query per mobile già configurate

### Backup Risultati
```bash
# Backup data.json
cp data.json data_backup_$(date +%Y%m%d).json
```

---

## 🤝 Contribuire

### Pull Request
1. Fork del repository
2. Crea branch feature (`git checkout -b feature/NuovaFeature`)
3. Commit modifiche (`git commit -m 'Add: Nuova feature'`)
4. Push al branch (`git push origin feature/NuovaFeature`)
5. Apri Pull Request

### Coding Style
- **Python**: PEP 8
- **JavaScript**: ES6+ con const/let
- **HTML/CSS**: Indentazione 4 spazi
- **Commenti**: In italiano per consistenza progetto

---

## 📄 Licenza
Progetto privato - Tutti i diritti riservati

---

## 👤 Autore
**DannyKrueger94**
- GitHub: [@DannyKrueger94](https://github.com/DannyKrueger94)
- Repository: [quiz-app](https://github.com/DannyKrueger94/quiz-app)

---

## 📅 Changelog

### v2.0.0 (Novembre 2025)
- ✨ Aggiunta modalità squadra collaborativa
- 🎨 Design responsive mobile-first
- 🗳️ Voti inline con le risposte
- 👥 Nomi membri visibili in lobby e quiz
- 🔐 Password e nome squadra case insensitive
- ⚡ Polling real-time per aggiornamenti live
- 🎊 Animazioni confetti per punteggi alti
- 📱 Ottimizzazione completa per smartphone

### v1.0.0
- 🚀 Release iniziale con modalità singola
- 📊 Pannello admin
- 💾 Storage risultati JSON

---

## 🔮 Roadmap Future

- [ ] Database PostgreSQL/MongoDB per storage persistente
- [ ] Autenticazione utenti con login/registrazione
- [ ] Multiplayer real-time con WebSocket
- [ ] Classifiche e leaderboard
- [ ] Statistiche dettagliate per squadra
- [ ] Export risultati CSV/PDF
- [ ] API REST per integrazioni esterne
- [ ] PWA (Progressive Web App)
- [ ] Dark mode
- [ ] Supporto multilingua

---

**Nota**: Questo file contiene tutte le informazioni necessarie per riprodurre, configurare e mantenere il progetto Quiz App. Per domande o supporto, aprire una issue su GitHub.
