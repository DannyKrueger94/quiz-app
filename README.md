# Quiz App 🎯

Applicazione Quiz interattiva realizzata con Flask.

## 🚀 Deployment su Render.com

### Passaggi per pubblicare l'app online:

1. **Crea un account su Render.com**
   - Vai su https://render.com
   - Registrati gratuitamente

2. **Carica il progetto su GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/TUO_USERNAME/quiz-app.git
   git push -u origin main
   ```

3. **Connetti Render a GitHub**
   - Nel dashboard di Render, clicca "New +"
   - Seleziona "Web Service"
   - Connetti il tuo repository GitHub
   - Render rileverà automaticamente `render.yaml`
   - Clicca "Create Web Service"

4. **Attendi il deployment**
   - Render installerà le dipendenze e avvierà l'app
   - Riceverai un URL tipo: `https://quiz-app-xxxx.onrender.com`

5. **L'app è online! 🎉**
   - Condividi l'URL con chiunque
   - Accessibile da PC, smartphone, tablet

### ⚙️ Configurazione Locale

```bash
# Installa dipendenze
pip install -r requirements.txt

# Avvia l'applicazione
python app.py

# Accedi a: http://localhost:5000
```

### 📱 Funzionalità

- ✅ Quiz interattivo con paginazione
- ✅ Supporto immagini nelle domande
- ✅ Barra di progresso
- ✅ Pannello admin per visualizzare risultati
- ✅ Design responsive moderno
- ✅ Statistiche dettagliate per squadra

### 🔐 Accesso Admin

URL: `/admin`
Password predefinita: `admin123` (modificabile in `app.py`)

### 📝 Note

- Il piano gratuito di Render può avere qualche secondo di ritardo al primo accesso (cold start)
- I dati delle squadre sono salvati in `data.json`
- Le domande sono configurabili in `questions.json`

---

Creato con ❤️ usando Flask
