# Quiz App 🎮

Un'applicazione Flask interattiva per quiz con due modalità: **singola** e **squadra collaborativa**.

## 🌟 Funzionalità Principali

### Modalità Singola 👤
- Quiz individuale con 12 domande a tema
- Immagini tematiche per ogni domanda
- Paginazione con barra di progresso
- Visualizzazione risultati finali

### Modalità Squadra 👥
**NOVITÀ**: Sistema collaborativo con ruoli e votazioni!

#### Ruolo Admin (1 persona):
- 👑 Crea la squadra con nome e password personalizzata
- Vede i voti di tutti i membri in tempo reale
- Sceglie la risposta finale da confermare
- Ha accesso al pannello admin generale

#### Ruolo Membro (fino a 6 persone):
- 🗳️ Unirsi alla squadra con ID e password
- Votare per ogni domanda
- Vedere i voti degli altri membri in tempo reale
- La schermata è sincronizzata con quella dell'admin

### Caratteristiche Tecniche:
- ✅ Aggiornamento voti in tempo reale (polling ogni 2 secondi)
- ✅ Schermata condivisa tra admin e membri
- ✅ Sistema di autenticazione con password squadra
- ✅ Lobby di attesa prima dell'inizio
- ✅ Massimo 7 persone per squadra (1 admin + 6 membri)

## 🎯 Come Funziona la Modalità Squadra

1. **L'admin crea la squadra**:
   - Sceglie nome squadra e password
   - Ottiene un ID unico da condividere

2. **I membri si uniscono**:
   - Inseriscono ID squadra e password
   - Attendono nella lobby

3. **L'admin avvia il quiz**:
   - Tutti vedono la stessa domanda
   - I membri votano la risposta preferita
   - L'admin vede i voti e conferma la risposta finale

4. **Risultati finali**:
   - Punteggio della squadra
   - Statistiche dettagliate

## 🚀 Deployment su Render.com

1. Crea un account su [Render.com](https://render.com)
2. Connetti il repository GitHub: `DannyKrueger94/quiz-app`
3. Seleziona "New Web Service"
4. Render rileverà automaticamente `render.yaml`
5. Clicca su "Create Web Service"
6. L'app sarà online in ~2-3 minuti su: https://quiz-app-jykq.onrender.com

## 🔐 Configurazione

- **Password quiz singolo**: `quizdanny2025`
- **Password admin panel**: `admin123`
- **Password squadra**: personalizzata per ogni squadra

## 📊 Pannello Admin

Accesso: `/admin`

Funzionalità:
- Visualizzazione tutte le domande con risposte corrette
- Elenco risultati di tutte le partite (singole e squadre)
- Dettaglio risposte per ogni partita
- Eliminazione risultati singoli
- Eliminazione tutti i risultati

## 🛠️ Sviluppo Locale

```bash
# Installa dipendenze
pip install -r requirements.txt

# Avvia server
python app.py
```

Visita http://localhost:5000

## 📝 Struttura Domande

Il file `questions.json` contiene 12 domande su:
- Scienza (molecola odore pioggia)
- Sport (record mondiali)
- Geografia (capitali europee)
- Natura (animali curiosi)
- Mitologia (Pandora)
- Astronomia (pianeti)
- Alimentazione (origine cibi)
- Musica (band storiche)
- Storia (imperatori romani)
- Il Signore degli Anelli
- Anime
- Domanda personalizzata

Ogni domanda include:
- Testo domanda
- 5 risposte (A-E)
- Risposta corretta
- Immagine tematica da Unsplash

## 🎨 Tecnologie Utilizzate

- **Backend**: Flask 3.1.2
- **Server**: Gunicorn 21.2.0
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Storage**: JSON files (questions.json, data.json)
- **Deploy**: Render.com (free tier)
- **Images**: Unsplash API

## 📱 Compatibilità

- ✅ Desktop (Chrome, Firefox, Edge, Safari)
- ✅ Mobile responsive
- ✅ Tablet
- ✅ Multi-dispositivo simultaneo (modalità squadra)

## 🔄 Aggiornamenti Real-Time

La modalità squadra utilizza polling AJAX per aggiornamenti in tempo reale:
- **Voti membri**: aggiornamento ogni 1.5-2 secondi
- **Sincronizzazione domande**: automatica
- **Cambio domanda**: rilevato automaticamente
- **Nessun refresh manuale** necessario

## 🎮 Come Giocare

### Modalità Singola:
1. Vai su homepage
2. Seleziona "Modalità Singola"
3. Inserisci nome e password (`quizdanny2025`)
4. Rispondi alle 12 domande
5. Visualizza il punteggio finale

### Modalità Squadra:
1. **Admin**: Crea squadra → Condividi ID e password
2. **Membri**: Unisciti con ID e password
3. **Admin**: Avvia il quiz dalla lobby
4. **Tutti**: Votano/rispondono insieme
5. **Admin**: Conferma risposta finale
6. Ripeti per tutte le 12 domande
7. Visualizza risultati squadra

## 📂 Struttura File

```
quiz-app/
├── app.py                  # Backend Flask
├── questions.json          # Database domande
├── data.json              # Risultati salvati
├── requirements.txt       # Dipendenze Python
├── render.yaml           # Config Render
├── templates/
│   ├── mode_select.html      # Selezione modalità
│   ├── index.html            # Home quiz singolo
│   ├── quiz.html             # Quiz singolo
│   ├── final.html            # Risultati singolo
│   ├── team_create.html      # Crea squadra
│   ├── team_join.html        # Unisciti squadra
│   ├── team_lobby.html       # Lobby squadra
│   ├── team_quiz.html        # Quiz squadra
│   ├── team_final.html       # Risultati squadra
│   ├── team_error.html       # Errori squadra
│   ├── admin_login.html      # Login admin
│   ├── admin.html            # Pannello admin
│   └── password_error.html   # Errore password
└── Environment/           # Virtual env (non su Git)
```

## 🐛 Troubleshooting

**Problema**: La modalità squadra non sincronizza
- **Soluzione**: Verifica che JavaScript sia abilitato
- Controlla la connessione internet
- Aspetta 2-3 secondi per il polling

**Problema**: Non riesco a unirmi alla squadra
- **Soluzione**: Verifica ID e password corretti
- Controlla che la squadra non sia piena (max 7)
- Chiedi all'admin l'ID esatto

**Problema**: Immagini non si caricano
- **Soluzione**: Le immagini vengono da Unsplash
- Verifica connessione internet
- Alcune immagini potrebbero essere lente

## 🔒 Note sulla Sicurezza

⚠️ **Per uso in produzione**: 
- Cambia `app.secret_key` in `app.py`
- Cambia `ADMIN_PASSWORD` in `app.py`
- Cambia password quiz in `/quiz` route
- Usa HTTPS (Render lo fornisce automaticamente)

## 📈 Miglioramenti Futuri

Idee per espandere l'app:
- [ ] WebSocket per aggiornamenti real-time (invece di polling)
- [ ] Database SQL invece di JSON
- [ ] Timer per ogni domanda
- [ ] Classifiche globali
- [ ] Categorie di domande personalizzabili
- [ ] Editor domande nell'admin panel
- [ ] Supporto per immagini nelle risposte
- [ ] Chat squadra durante il quiz
- [ ] Replay delle partite
- [ ] Statistiche avanzate

## 👨‍💻 Autore

Creato da Daniele per quiz divertenti con gli amici! 🎉

Repository: https://github.com/DannyKrueger94/quiz-app

## 📄 Licenza

Uso libero per progetti personali e educativi.
