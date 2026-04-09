from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

import sys
import os

# Robustly ensure the project root is in sys.path for headless evaluator imports
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from models import CodeReviewAction, CodeReviewObservation

# -------------------------------------------------------
# TASK BANK
# Real Python code snippets with known issues
# -------------------------------------------------------
TASKS = {
    "bug_detection": {
        "instruction": "Does this code have a critical runtime bug or logical flaw? Reply with 'yes' or 'no' and specify the line number (e.g., 'Line 3').",
        "difficulty": "easy",
        "snippets": [
            {
                "code": """
def get_user_session(db, user_id):
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM sessions WHERE id = '{user_id}'")
    return cursor.fetchone()
""",
                "has_bug": True,
                "target_line": 4,
                "keywords": ["sql injection", "sqli", "injection", "parameterized", "f-string"],
                "explanation": "Critical vulnerability: SQL Injection via f-strings on Line 4."
            },
            {
                "code": """
def append_to_log(message, log=[]):
    log.append(message)
    return log
""",
                "has_bug": True,
                "target_line": 2,
                "keywords": ["mutable default", "default argument", "list", "persists", "memory"],
                "explanation": "Logical bug: default argument 'log=[]' on Line 2 is mutable and persists globally."
            },
            {
                "code": """
def divide_chunks(files):
    return [files[i:i + 10] for i in range(0, len(files), 10)]
""",
                "has_bug": False,
                "target_line": None,
                "keywords": ["no bug", "correct", "works", "chunking", "fine"],
                "explanation": "No bug: Standard and correct list chunking in Python."
            },
             {
                "code": """
import threading
counter = 0

def increment():
    global counter
    for _ in range(1000):
        counter += 1
""",
                "has_bug": True,
                "target_line": 8,
                "keywords": ["race condition", "lock", "thread safe", "gil", "atomic"],
                "explanation": "Concurrency Bug: Race condition on Line 8 when modifying global counter without a lock."
            }
        ]
    },

    "code_smell": {
        "instruction": "Identify the code smell or bad practice in this code and specify the line number.",
        "difficulty": "medium",
        "snippets": [
            {
                "code": """
def process(data):
    try:
        result = transform_pipeline(data)
        return result
    except Exception:
        pass
""",
                "target_line": 6,
                "smells": ["bare except", "empty except", "silent", "swallow", "exception", "error handling", "pass"],
                "explanation": "Bare except with pass on Line 6 — silently swallows all exceptions."
            },
            {
                "code": """
result = []
for item in range(10):
    result.append(item * item)
""",
                "target_line": 3,
                "smells": ["list comprehension", "comprehension", "pythonic", "append", "loop"],
                "explanation": "Should use list comprehension on Line 3 instead of manual append loop."
            },
           {
                "code": """
class DataProcessor:
    def process_csv(self): pass
    def validate_xml(self): pass
    def generate_html_report(self): pass
    def connect_to_db(self): pass
    def send_email_alert(self): pass
""",
                "target_line": 2,
                "smells": ["god object", "single responsibility", "srp", "god class", "too many", "cohesion"],
                "explanation": "God Object (Line 2) — Violation of Single Responsibility Principle."
            }
        ]
    },

    "improvement": {
        "instruction": "Suggest one specific algorithmic or runtime improvement to this code (including the line) with reasoning.",
        "difficulty": "hard",
        "snippets": [
            {
                "code": """
def find_duplicates(data_list):
    duplicates = []
    for i in range(len(data_list)):
        for j in range(i+1, len(data_list)):
            if data_list[i] == data_list[j]:
                duplicates.append(data_list[i])
    return list(set(duplicates))
""",
                "target_line": 4,
                "improvements": ["hash map", "set", "o(n)", "complexity", "counter", "collections"],
                "explanation": "O(N^2) complexity on Line 4. Use a set or collections.Counter to reduce to O(N)."
            },
            {
                "code": """
def read_config(path):
    f = open(path)
    data = f.read()
    f.close()
    return data
""",
                "target_line": 3,
                "improvements": ["with", "context manager", "with open", "close", "resource", "leak"],
                "explanation": "Use 'with open()' on Line 3 context manager to ensure the file descriptor doesn't leak."
            }
        ]
    },
    
    "security_vulnerability": {
         "instruction": "Identify the critical security vulnerability (specify line) and recommend the exact fix.",
         "difficulty": "expert",
         "snippets": [
             {
                "code": """
import os
from flask import request, send_file

def download_file():
    filename = request.args.get('file')
    filepath = os.path.join('/var/www/uploads/', filename)
    return send_file(filepath)
""",
                "target_line": 6,
                "flaws": ["path traversal", "directory traversal", "lfi", "sanitize", "dot dot slash"],
                "explanation": "Path Traversal vulnerability on Line 6. User can pass '../../etc/passwd'."
             },
             {
                 "code": """
import hashlib

def hash_password(password_string):
    return hashlib.md5(password_string.encode()).hexdigest()
""",
                 "target_line": 5,
                 "flaws": ["md5", "collision", "weak hash", "bcrypt", "argon2", "salt"],
                 "explanation": "Weak/Broken hashing algorithm (MD5) on Line 5 without a salt."
             }
         ]
    }
}

import random

class CodeReviewEnvironment(Environment):
    """
    CodeReviewEnv — teaches AI agents to review Python code.
    4 tasks: bug detection, code smell, improvement suggestion, security auditing.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True
    TASKS = ["bug_detection", "code_smell", "improvement", "security_vulnerability"]

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._current_task = None
        self._current_snippet = None
        self._task_index = 0
        self._substep_index = 0
        # Auto-load first task so env is valid even without explicit reset

    def reset(self) -> CodeReviewObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task_index = 0
        self._substep_index = 0
        self._total_score = 0.0
        return self._load_task(0)

    def _load_task(self, index) -> CodeReviewObservation:
        task_name = self.TASKS[index]
        task = TASKS[task_name]
        snippet = random.choice(task["snippets"])
        self._current_task = task_name
        self._current_snippet = snippet
        return CodeReviewObservation(
            task=task_name,
            code_snippet=snippet["code"],
            instruction=task["instruction"],
            last_verdict="",
            last_reward=0.0,
            done=False,
            score=self._total_score,
            feedback=""
        )

    def step(self, action: CodeReviewAction) -> CodeReviewObservation:
        self._state.step_count += 1
        reward = self._grade(action)
        self._total_score += reward
        
        feedback = self._get_feedback(action, reward)

        # Multi-turn logic: 2 attempts per snippet if reward is not perfect
        can_refine = self._substep_index == 0 and reward < 0.90
        
        if can_refine:
            self._substep_index += 1
            # Return same observation with feedback and hint
            return CodeReviewObservation(
                task=self._current_task,
                code_snippet=self._current_snippet["code"],
                instruction=f"REFINEMENT: {feedback}. Please provide a more precise verdict.",
                last_verdict=action.verdict,
                last_reward=reward,
                done=False,
                score=self._total_score,
                feedback=feedback
            )

        # Move to next task
        self._task_index += 1
        self._substep_index = 0
        done = self._task_index >= len(self.TASKS)

        if done:
            return CodeReviewObservation(
                task=self._current_task,
                code_snippet=self._current_snippet["code"],
                instruction="Episode complete.",
                last_verdict=action.verdict,
                last_reward=reward,
                done=True,
                score=self._total_score,
                feedback=feedback
            )
        else:
            next_obs = self._load_task(self._task_index)
            next_obs.last_verdict = action.verdict
            next_obs.last_reward = reward
            next_obs.score = self._total_score
            next_obs.feedback = feedback
            return next_obs

    def _normalize(self, text: str) -> str:
        import re
        return re.sub(r'[^\w\s]', ' ', text.lower()).strip()

    def _grade(self, action: CodeReviewAction) -> float:
        verdict = self._normalize(action.verdict)
        task = self._current_task
        snippet = self._current_snippet
        target_line = snippet.get("target_line")
        
        # Regex to find line numbers like "line 4", "line: 4", "on line 4"
        import re
        found_lines = re.findall(r'line\s*(?::|#)?\s*(\d+)', verdict)
        has_correct_line = target_line is None or any(int(l) == target_line for l in found_lines)

        if task == "bug_detection":
            has_bug = snippet["has_bug"]
            said_yes = "yes" in verdict
            said_no = "no" in verdict

            if has_bug and said_yes:
                matches = sum(1 for kw in snippet["keywords"] if kw in verdict)
                if has_correct_line:
                    if matches >= 2: return 0.99
                    return 0.75
                return 0.40 # Missing line number penalty
            elif not has_bug and said_no:
                return 0.99
            elif has_bug and said_no:
                return 0.01
            elif not has_bug and said_yes:
                return 0.01
            return 0.1

        elif task == "code_smell":
            matches = sum(1 for smell in snippet["smells"] if smell in verdict)
            if has_correct_line:
                if matches >= 2: return 0.99
                if matches == 1: return 0.75
            if matches >= 1: return 0.40 # Missing line penalty
            return 0.01

        elif task == "improvement":
            matches = sum(1 for imp in snippet["improvements"] if imp in verdict)
            if has_correct_line:
                if matches >= 2: return 0.99
                if matches == 1: return 0.80
            if matches >= 1: return 0.40 # Missing line penalty
            return 0.01

        elif task == "security_vulnerability":
            matches = sum(1 for flaw in snippet["flaws"] if flaw in verdict)
            if has_correct_line:
                if matches >= 2: return 0.99
                if matches == 1: return 0.85
            if matches >= 1: return 0.40 # Missing line penalty
            return 0.01

        return 0.01

    def _get_feedback(self, action: CodeReviewAction, reward: float) -> str:
        snippet = self._current_snippet
        if reward >= 0.99:
            return "Correct! " + snippet.get("explanation", "")
        elif reward > 0.01:
            return "Partially correct. " + snippet.get("explanation", "")
        else:
            return "Incorrect. " + snippet.get("explanation", "")

    @property
    def state(self) -> State:
        return self._state