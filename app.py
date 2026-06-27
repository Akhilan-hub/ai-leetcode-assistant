"""
app.py - AI LeetCode Helper Agent (Flask backend)
"""
from flask import Flask, render_template, request, jsonify
import db
import ai_engine

app = Flask(__name__)

# Initialize DB on startup
db.init_db()
DEFAULT_USER_ID = db.get_default_user_id()


@app.route("/")
def index():
    return render_template("index.html")


# ---------- 1. Question Understanding ----------
@app.route("/api/explain", methods=["POST"])
def api_explain():
    data = request.get_json()
    question_text = data.get("question_text", "").strip()
    question_name = data.get("question_name", "").strip() or "Untitled Question"
    tamil = bool(data.get("tamil", False))

    if not question_text:
        return jsonify({"error": "Please paste a question."}), 400

    try:
        explanation = ai_engine.explain_question(question_text, tamil=tamil)
        qid = db.save_question(DEFAULT_USER_ID, question_name, question_text, explanation)
        return jsonify({"result": explanation, "question_id": qid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- 2. Approach Section ----------
@app.route("/api/approach", methods=["POST"])
def api_approach():
    data = request.get_json()
    question_text = data.get("question_text", "").strip()
    if not question_text:
        return jsonify({"error": "Please paste a question."}), 400
    try:
        result = ai_engine.get_approaches(question_text)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- 3. Complexity Analysis ----------
@app.route("/api/complexity", methods=["POST"])
def api_complexity():
    data = request.get_json()
    question_text = data.get("question_text", "").strip()
    code = data.get("code", "")
    if not question_text:
        return jsonify({"error": "Please paste a question."}), 400
    try:
        result = ai_engine.analyze_complexity(question_text, code)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- 4. Hint Mode ----------
@app.route("/api/hints", methods=["POST"])
def api_hints():
    data = request.get_json()
    question_text = data.get("question_text", "").strip()
    if not question_text:
        return jsonify({"error": "Please paste a question."}), 400
    try:
        result = ai_engine.get_hints(question_text)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- 5. Code Review ----------
@app.route("/api/review", methods=["POST"])
def api_review():
    data = request.get_json()
    question_text = data.get("question_text", "").strip()
    user_code = data.get("user_code", "").strip()
    language = data.get("language", "python")
    question_id = data.get("question_id")

    if not question_text or not user_code:
        return jsonify({"error": "Question and code are both required."}), 400

    try:
        feedback = ai_engine.review_code(question_text, user_code, language)

        # If no question_id passed, create a question entry first
        if not question_id:
            question_id = db.save_question(DEFAULT_USER_ID, "Code Review Submission", question_text, "")

        db.save_code_review(question_id, user_code, feedback)
        return jsonify({"result": feedback, "question_id": question_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- 6. Dry Run ----------
@app.route("/api/dryrun", methods=["POST"])
def api_dryrun():
    data = request.get_json()
    question_text = data.get("question_text", "").strip()
    user_code = data.get("user_code", "").strip()
    sample_input = data.get("sample_input", "")
    language = data.get("language", "python")

    if not question_text or not user_code:
        return jsonify({"error": "Question and code are both required."}), 400

    try:
        result = ai_engine.dry_run(question_text, user_code, sample_input, language)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- History & Favorites (SQL features) ----------
@app.route("/api/history", methods=["GET"])
def api_history():
    history = db.get_history(DEFAULT_USER_ID)
    return jsonify({"history": history})


@app.route("/api/favorites", methods=["GET"])
def api_favorites():
    favs = db.get_favorites(DEFAULT_USER_ID)
    return jsonify({"favorites": favs})


@app.route("/api/favorite/<int:question_id>", methods=["POST"])
def api_toggle_favorite(question_id):
    new_val = db.toggle_favorite(question_id)
    if new_val is None:
        return jsonify({"error": "Question not found"}), 404
    return jsonify({"is_favorite": bool(new_val)})


@app.route("/api/question/<int:question_id>", methods=["GET"])
def api_get_question(question_id):
    q = db.get_question(question_id)
    if not q:
        return jsonify({"error": "Not found"}), 404
    reviews = db.get_reviews_for_question(question_id)
    q["reviews"] = reviews
    return jsonify(q)


@app.route("/api/question/<int:question_id>", methods=["DELETE"])
def api_delete_question(question_id):
    db.delete_question(question_id)
    return jsonify({"deleted": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
