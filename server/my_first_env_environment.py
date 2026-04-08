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
        "instruction": "Does this code have a critical runtime bug or logical flaw? Reply with 'yes' or 'no' and explain briefly.",
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
                "keywords": ["sql injection", "sqli", "injection", "parameterized", "f-string"],
                "explanation": "Critical vulnerability: SQL Injection via f-strings in query."
            },
            {
                "code": """
def append_to_log(message, log=[]):
    log.append(message)
    return log
""",
                "has_bug": True,
                "keywords": ["mutable default", "default argument", "list", "persists", "memory"],
                "explanation": "Logical bug: default argument 'log=[]' is mutable and persists globally across calls."
            },
            {
                "code": """
def divide_chunks(files):
    return [files[i:i + 10] for i in range(0, len(files), 10)]
""",
                "has_bug": False,
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
                "keywords": ["race condition", "lock", "thread safe", "gil", "atomic"],
                "explanation": "Concurrency Bug: Race condition when modifying global counter without a lock."
            }
        ]
    },

    "code_smell": {
        "instruction": "Identify the code smell or bad practice in this code. Be specific.",
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
                "smells": ["bare except", "empty except", "silent", "swallow", "exception", "error handling", "pass"],
                "explanation": "Bare except with pass — silently swallows all exceptions obscuring runtime crashes."
            },
            {
                "code": """
result = []
for item in range(10):
    result.append(item * item)
""",
                "smells": ["list comprehension", "comprehension", "pythonic", "append", "loop"],
                "explanation": "Should use list comprehension: [item*item for item in range(10)]"
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
                "smells": ["god object", "single responsibility", "srp", "god class", "too many", "cohesion"],
                "explanation": "God Object / Violation of Single Responsibility Principle — handles UI, DB, parsing, and networking."
            }
        ]
    },

    "improvement": {
        "instruction": "Suggest one specific algorithmic or runtime improvement to this code with a brief reason.",
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
                "improvements": ["hash map", "set", "o(n)", "complexity", "counter", "collections"],
                "explanation": "O(N^2) complexity. Use a set or collections.Counter to reduce to O(N)."
            },
            {
                "code": """
def read_config(path):
    f = open(path)
    data = f.read()
    f.close()
    return data
""",
                "improvements": ["with", "context manager", "with open", "close", "resource", "leak"],
                "explanation": "Use 'with open()' context manager to ensure the file descriptor doesn't leak if an exception is raised."
            }
        ]
    },
    
    "security_vulnerability": {
         "instruction": "Identify the critical security vulnerability and recommend the exact fix.",
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
                "flaws": ["path traversal", "directory traversal", "lfi", "sanitize", "dot dot slash"],
                "explanation": "Path Traversal vulnerability. User can pass '../../etc/passwd' to expose internal files."
             },
             {
                 "code": """
import hashlib

def hash_password(password_string):
    return hashlib.md5(password_string.encode()).hexdigest()
""",
                 "flaws": ["md5", "collision", "weak hash", "bcrypt", "argon2", "salt"],
                 "explanation": "Weak/Broken hashing algorithm (MD5) without a salt. Should use bcrypt or Argon2."
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
        self._total_score = 0.0
        self._task_index = 0
        # Auto-load first task so env is valid even without explicit reset

    def reset(self) -> CodeReviewObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task_index = 0
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
        self._task_index += 1
        done = self._task_index >= len(self.TASKS)

        feedback = self._get_feedback(action, reward)

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
        """
        The grader — scores agent's verdict against known answers.
        This is the core of the environment.
        """
        verdict = self._normalize(action.verdict)
        task = self._current_task
        snippet = self._current_snippet

        if task == "bug_detection":
            has_bug = snippet["has_bug"]
            said_yes = "yes" in verdict
            said_no = "no" in verdict

            if has_bug and said_yes:
                # Check if they explained it correctly
                for kw in snippet["keywords"]:
                    if kw in verdict:
                        return 0.99      # correct + good explanation
                return 0.6              # correct verdict, weak explanation

            elif not has_bug and said_no:
                return 0.99             # correctly identified no bug

            elif has_bug and said_no:
                return 0.01             # missed the bug

            elif not has_bug and said_yes:
                return 0.01             # false positive

            return 0.1                  # didn't say yes or no clearly

        elif task == "code_smell":
            for smell in snippet["smells"]:
                if smell in verdict:
                    return 0.99         # identified the smell correctly
            # Partial credit if answer is long and relevant
            if len(verdict) > 20:
                return 0.3
            return 0.01

        elif task == "improvement":
            for imp in snippet["improvements"]:
                if imp in verdict:
                    return 0.99         # suggested the right improvement
            if len(verdict) > 30:
                return 0.4              # suggested something, just not ideal
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