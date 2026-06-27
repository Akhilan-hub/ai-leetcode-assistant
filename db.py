"""
db.py - SQLite helper layer for AI LeetCode Helper Agent
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "leetcode_agent.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables if they don't exist, and ensure a default user exists."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()

    # Ensure a default guest user exists (simple version, no auth/login yet)
    cur = conn.execute("SELECT id FROM users WHERE username = ?", ("guest",))
    row = cur.fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            ("guest", "guest@example.com"),
        )
        conn.commit()
    conn.close()


def get_default_user_id():
    conn = get_connection()
    cur = conn.execute("SELECT id FROM users WHERE username = ?", ("guest",))
    row = cur.fetchone()
    conn.close()
    return row["id"] if row else None


# ---------- Questions ----------

def save_question(user_id, question_name, question_text, ai_response):
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO questions (user_id, question_name, question_text, ai_response)
           VALUES (?, ?, ?, ?)""",
        (user_id, question_name, question_text, ai_response),
    )
    conn.commit()
    qid = cur.lastrowid
    conn.close()
    return qid


def get_history(user_id, limit=50):
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, question_name, question_text, ai_response, is_favorite, date
           FROM questions WHERE user_id = ? ORDER BY date DESC LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_question(question_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def toggle_favorite(question_id):
    conn = get_connection()
    row = conn.execute("SELECT is_favorite FROM questions WHERE id = ?", (question_id,)).fetchone()
    if row is None:
        conn.close()
        return None
    new_val = 0 if row["is_favorite"] else 1
    conn.execute("UPDATE questions SET is_favorite = ? WHERE id = ?", (new_val, question_id))
    conn.commit()
    conn.close()
    return new_val


def get_favorites(user_id):
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, question_name, question_text, ai_response, date
           FROM questions WHERE user_id = ? AND is_favorite = 1 ORDER BY date DESC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_question(question_id):
    conn = get_connection()
    conn.execute("DELETE FROM code_reviews WHERE question_id = ?", (question_id,))
    conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()


# ---------- Code Reviews ----------

def save_code_review(question_id, user_code, ai_feedback):
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO code_reviews (question_id, user_code, ai_feedback)
           VALUES (?, ?, ?)""",
        (question_id, user_code, ai_feedback),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def get_reviews_for_question(question_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM code_reviews WHERE question_id = ? ORDER BY created_at DESC",
        (question_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
