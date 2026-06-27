# 🧠🤖 AI LeetCode Assistant

An AI-powered coding interview assistant that helps users understand LeetCode problems, generate optimized approaches, review code, perform dry runs, analyze complexity, and track learning history.

## ✅ Features

1. **Question Understanding** — paste a problem, get summary, input/output, example walkthrough, key observation, real-world analogy, optional Tamil explanation.
2. **Approach Section** — Brute Force → Better → Optimal, each with steps + complexity.
3. **Complexity Analysis** — clean `Time Complexity / Space Complexity` output with reasoning.
4. **Hint Mode** — 3 progressive hints, no spoiler code.
5. **Code Review** — paste your code → syntax errors, logic mistakes, why it's wrong, corrected code, explanation.
6. **Dry Run** — step-by-step variable trace table for your code on a sample input.
7. **SQL Database (SQLite)** — `users`, `questions`, `code_reviews` tables. History + ⭐ Favorites drawer in the UI.

## 📁 Project Structure

leetcode_agent/
├── app.py              # Flask routes (all 6 features + history/favorites API)
├── ai_engine.py         # Gemini API calls + prompt templates
├── db.py                # SQLite helper functions
├── schema.sql           # users / questions / code_reviews tables
├── requirements.txt
├── .env.example         # rename to .env and add your GEMINI_API_KEY
├── templates/
│   └── index.html       # IDE-style two-panel UI
└── static/
    ├── css/style.css     # dark code-editor theme
    └── js/main.js        # tab logic, API calls, markdown renderer, history drawer


## 🛠️ Tech Stack

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- Database: SQLite
- AI Model: Google Gemini API
- Version Control: Git & GitHub

## 🚀 Setup

```bash
cd leetcode_agent
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Get a **free Gemini API key**: https://aistudio.google.com/app/apikey

```bash
cp .env.example .env
# then edit .env and paste your real key:
# GEMINI_API_KEY=AIza...
```

Run it:

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## 🗄️ Database

SQLite file `leetcode_agent.db` is created automatically on first run (`db.init_db()` runs `schema.sql`). A default `guest` user is created so you can start using it immediately without building login/signup — that's a natural next feature to add later (`users` table is already there for it).

## 🔧 Notes / Next steps you can add later

- Real login/signup (users table already supports it).
- Switch `MODEL_NAME` in `ai_engine.py` from `gemini-2.5-flash` to `gemini-2.5-pro` for higher quality, slower answers.
- Switch SQLite → MySQL: only `db.py`'s connection logic needs to change (swap `sqlite3` for `mysql-connector-python` / `PyMySQL`), the SQL itself is portable with minor tweaks.
- Add a "submit & auto-test" runner using `subprocess` to actually execute student code against sample inputs (currently dry run is AI-simulated, not real execution — safer for a hosted app).
