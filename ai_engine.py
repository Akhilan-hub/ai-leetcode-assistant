"""
ai_engine.py - Gemini API integration for AI LeetCode Helper Agent
Handles: Question Understanding, Approach, Complexity, Hints, Code Review, Dry Run
"""
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"  # change to "gemini-2.5-pro" for higher quality

_client = None


def _get_client():
    global _client
    if not API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY not set. Copy .env.example to .env and add your key."
        )
    if _client is None:
        _client = genai.Client(api_key=API_KEY)
    return _client


def _ask(prompt: str) -> str:
    client = _get_client()
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text


# ---------- Feature 1: Question Understanding ----------

def explain_question(question_text: str, tamil: bool = False) -> str:
    tamil_block = (
        "\n7. Tamil Explanation: This section is MANDATORY if requested. Re-explain the ENTIRE "
        "problem (summary, input, output, example, key observation) again from scratch in this "
        "section, but this time written COMPLETELY in Tamil script (தமிழ் எழுத்துக்களில்), not English. "
        "Do not just translate one line — write several full sentences in Tamil covering the whole problem. "
        "Write naturally the way a Tamil tutor would explain to a student in person.\n"
        if tamil else ""
    )
    language_instruction = (
        "IMPORTANT: Sections 1-6 must be written in English. Section 7 (Tamil Explanation) must be "
        "written entirely in actual Tamil script, not English, not Thanglish. This is a strict requirement.\n\n"
        if tamil else ""
    )
    prompt = f"""
You are a friendly DSA/LeetCode tutor. A student pasted this problem:

\"\"\"{question_text}\"\"\"

{language_instruction}Explain it clearly using EXACTLY these sections, with clear markdown headings:

1. Problem Summary: What is the problem actually asking, in one or two simple sentences.
2. Input: What is given, with type/format.
3. Output: What must be returned, with type/format.
4. Example Walkthrough: Take one example and explain it step by step in plain words.
5. Key Observation: The one insight that makes this problem easier once you see it.
6. Real-World Analogy: A simple everyday analogy a beginner can relate to.
{tamil_block}
Keep it beginner-friendly. Do not give the full optimal code here, just understanding.
"""
    return _ask(prompt)


# ---------- Feature 2: Approach Section ----------

def get_approaches(question_text: str) -> str:
    prompt = f"""
You are a DSA tutor. For this LeetCode-style problem:

\"\"\"{question_text}\"\"\"

Give THREE approaches, clearly separated with headings:

### Brute Force
- Idea in plain words
- Rough steps
- Time & Space complexity

### Better Approach
- Idea in plain words
- Rough steps
- Time & Space complexity

### Optimal Approach
- Idea in plain words
- Rough steps
- Time & Space complexity
- Why this is optimal

Do not write full code, just clear conceptual steps and pseudocode if helpful.
"""
    return _ask(prompt)


# ---------- Feature 3: Complexity Analysis ----------

def analyze_complexity(question_text: str, code: str = "") -> str:
    code_block = f"\n\nHere is the candidate code:\n```\n{code}\n```" if code.strip() else ""
    prompt = f"""
Analyze the time and space complexity for this problem's optimal solution:

\"\"\"{question_text}\"\"\"{code_block}

Respond in EXACTLY this format:

Time Complexity: O(...)
Space Complexity: O(...)

Reasoning:
- Explain briefly WHY the time complexity is what it is.
- Explain briefly WHY the space complexity is what it is.
"""
    return _ask(prompt)


# ---------- Feature 4: Hint Mode ----------

def get_hints(question_text: str) -> str:
    prompt = f"""
A student wants HINTS ONLY (no direct answer, no full code) for this problem:

\"\"\"{question_text}\"\"\"

Give exactly 3 progressive hints:

Hint 1: A gentle nudge about how to think about the problem (no algorithm name yet).
Hint 2: A bit more specific — mention the data structure or technique direction, but not the full algorithm.
Hint 3: Almost the approach, but still let the student write the code themselves. Do NOT provide code.

Keep each hint short (2-3 sentences max).
"""
    return _ask(prompt)


# ---------- Feature 5: Code Review ----------

def review_code(question_text: str, user_code: str, language: str = "python") -> str:
    prompt = f"""
You are reviewing a student's code submission for this problem:

\"\"\"{question_text}\"\"\"

Student's {language} code:
```{language}
{user_code}
```

Give feedback in EXACTLY these sections:

1. Syntax Errors: List any syntax errors found, or say "None found".
2. Logic Mistakes: Explain what is logically wrong (if anything), or say "Logic looks correct".
3. Why It's Wrong: Explain WHY the mistake causes wrong output/behaviour, with a concrete example if possible.
4. Corrected Code: Provide the corrected, working {language} code in a code block.
5. Explanation: Briefly explain what you changed and why it fixes the issue.

If the code is already fully correct and optimal, say so clearly and just confirm correctness with brief praise plus one small improvement suggestion (style/efficiency) if any.
"""
    return _ask(prompt)


# ---------- Feature 6: Dry Run ----------

def dry_run(question_text: str, user_code: str, sample_input: str = "", language: str = "python") -> str:
    sample_block = f"\nUse this sample input for the dry run: {sample_input}" if sample_input.strip() else \
        "\nPick a small, simple sample input yourself if none is given."
    prompt = f"""
Do a STEP-BY-STEP DRY RUN of this {language} code for the problem below.

Problem:
\"\"\"{question_text}\"\"\"

Code:
```{language}
{user_code}
```
{sample_block}

Respond as a markdown TABLE with columns: Step | Line/Action | Variable States | Notes
Walk through iteration by iteration / line by line showing how variables change.
After the table, give the Final Output and confirm whether it matches the expected output.
"""
    return _ask(prompt)
