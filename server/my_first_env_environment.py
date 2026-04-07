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
        "instruction": "Does this code have a bug? Reply with 'yes' or 'no' and explain briefly.",
        "difficulty": "easy",
        "snippets": [
            {
                "code": """
def divide(a, b):
    return a / b

result = divide(10, 0)
print(result)
""",
                "has_bug": True,
                "keywords": ["zero", "division", "zerodivision", "divide by zero", "zero error"],
                "explanation": "ZeroDivisionError — dividing by 0 with no error handling"
            },
            {
                "code": """
def get_first(lst):
    return lst[0]

items = []
print(get_first(items))
""",
                "has_bug": True,
                "keywords": ["index", "empty", "indexerror", "list", "out of range"],
                "explanation": "IndexError — accessing index 0 of an empty list"
            },
            {
                "code": """
def add(a, b):
    return a + b

print(add(3, 4))
""",
                "has_bug": False,
                "keywords": ["no bug", "correct", "no error", "works", "fine", "no issue"],
                "explanation": "No bug — simple addition works fine"
            },
            {
                "code": """
def get_value(d, key):
    return d[key]

data = {"name": "Alice"}
print(get_value(data, "age"))
""",
                "has_bug": True,
                "keywords": ["key", "keyerror", "missing", "not found", "dict"],
                "explanation": "KeyError — 'age' key doesn't exist in the dict"
            },
            {
                "code": """
numbers = [1, 2, 3, 4, 5]
total = 0
for i in range(1, len(numbers) + 1):
    total += numbers[i]
print(total)
""",
                "has_bug": True,
                "keywords": ["index", "off by one", "range", "indexerror", "out of range"],
                "explanation": "Off-by-one error — range goes to len(numbers) but max valid index is len-1"
            },
        ]
    },

    "code_smell": {
        "instruction": "Identify the code smell or bad practice in this code. Be specific.",
        "difficulty": "medium",
        "snippets": [
            {
                "code": """
def calculate(x):
    return x * 3.14159 * 2
""",
                "smells": ["magic number", "hardcoded", "constant", "pi", "named constant"],
                "explanation": "Magic number — 3.14159 should be a named constant like PI"
            },
            {
                "code": """
def process(data):
    try:
        result = int(data)
        return result
    except:
        pass
""",
                "smells": ["bare except", "empty except", "silent", "swallow", "exception", "error handling"],
                "explanation": "Bare except with pass — silently swallows all exceptions"
            },
            {
                "code": """
def get_user_data(id, name, email, age, address, phone, country):
    return {"id": id, "name": name, "email": email,
            "age": age, "address": address, "phone": phone,
            "country": country}
""",
                "smells": ["too many", "parameters", "arguments", "long parameter", "data class", "object"],
                "explanation": "Too many parameters — should use a data class or object"
            },
            {
                "code": """
def check_user(u):
    if u == 1:
        return True
    return False
""",
                "smells": ["single letter", "variable name", "naming", "unclear", "descriptive"],
                "explanation": "Poor variable naming — 'u' is not descriptive, should be 'user_id'"
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
        ]
    },

    "improvement": {
        "instruction": "Suggest one specific improvement to this code with a brief reason.",
        "difficulty": "hard",
        "snippets": [
            {
                "code": """
def find_user(users, name):
    for i in range(len(users)):
        if users[i]["name"] == name:
            return users[i]
    return None
""",
                "improvements": ["enumerate", "next", "list comprehension", "pythonic", "range(len"],
                "explanation": "Use enumerate() or next() instead of range(len()) — more Pythonic"
            },
            {
                "code": """
import os
db_password = "admin123"
api_key = "sk-abc123xyz"
""",
                "improvements": ["environment variable", "env var", "os.getenv", "secret", "hardcoded", "config"],
                "explanation": "Hardcoded secrets — use environment variables or a config file"
            },
            {
                "code": """
def celsius_to_fahrenheit(c):
    f = c * 9 / 5 + 32
    return f
""",
                "improvements": ["docstring", "type hint", "annotation", "return type", "documentation"],
                "explanation": "Missing type hints and docstring — add them for clarity"
            },
            {
                "code": """
def read_file(path):
    f = open(path)
    data = f.read()
    f.close()
    return data
""",
                "improvements": ["with", "context manager", "with open", "close", "resource"],
                "explanation": "Use 'with open()' context manager to ensure file is always closed"
            },
            {
                "code": """
import time
def retry(func):
    for i in range(3):
        try:
            return func()
        except:
            time.sleep(1)
""",
                "improvements": ["bare except", "exception type", "specific exception", "logging", "backoff"],
                "explanation": "Bare except hides errors — catch specific exceptions and add logging"
            },
        ]
    }
}

import random

class CodeReviewEnvironment(Environment):
    """
    CodeReviewEnv — teaches AI agents to review Python code.
    3 tasks: bug detection (easy), code smell (medium), improvement suggestion (hard).
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True
    TASKS = ["bug_detection", "code_smell", "improvement"]

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