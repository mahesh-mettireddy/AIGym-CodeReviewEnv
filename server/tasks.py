TASKS = {
    "bug_detection": {
        "instruction": "Does this code have a critical runtime bug or logical flaw? Reply with 'yes' or 'no' and specify the line number (e.g., 'Line 3').",
        "difficulty": "easy",
        "snippets": [
            {
                "code": """def get_user_session(db, user_id):
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM sessions WHERE id = '{user_id}'")
    return cursor.fetchone()""",
                "has_bug": True,
                "target_line": 3,
                "keywords": ["sql injection", "sqli", "injection", "parameterized", "f-string"],
                "explanation": "Critical vulnerability: SQL Injection via f-strings on Line 3."
            },
            {
                "code": """def append_to_log(message, log=[]):
    log.append(message)
    return log""",
                "has_bug": True,
                "target_line": 1,
                "keywords": ["mutable default", "default argument", "list", "persists", "memory"],
                "explanation": "Logical bug: default argument 'log=[]' on Line 1 is mutable and persists globally."
            },
            {
                "code": """def divide_chunks(files):
    return [files[i:i + 10] for i in range(0, len(files), 10)]""",
                "has_bug": False,
                "target_line": None,
                "keywords": ["no bug", "correct", "works", "chunking", "fine"],
                "explanation": "No bug: Standard and correct list chunking in Python."
            },
            {
                "code": """import threading
counter = 0

def increment():
    global counter
    for _ in range(1000):
        counter += 1""",
                "has_bug": True,
                "target_line": 6,
                "keywords": ["race condition", "lock", "thread safe", "gil", "atomic"],
                "explanation": "Concurrency Bug: Race condition on Line 6 when modifying global counter without a lock."
            },
            {
                "code": """def calculate_avg(nums):
    total = sum(nums)
    return total / len(nums)

print(calculate_avg([]))""",
                "has_bug": True, 
                "target_line": 3,
                "keywords": ["zerodivisionerror", "empty list", "divide by zero", "empty"],
                "explanation": "ZeroDivisionError on Line 3 when calling with an empty list."
            },
            {
                "code": """def find_match(items, target):
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1""",
                "has_bug": False,
                "target_line": None,
                "keywords": ["no bug", "correct", "works"],
                "explanation": "No bug: Standard search loop returning index or -1."
            },
            {
                "code": """import time
def get_now(t=time.time()):
    return t

print(get_now())
time.sleep(1)
print(get_now())""",
                "has_bug": True,
                "target_line": 2,
                "keywords": ["static", "default", "time", "binding", "instantiated once"],
                "explanation": "Logic bug: default argument time.time() is evaluated once at definition time, not call time."
            }
        ]
    },

    "code_smell": {
        "instruction": "Identify the code smell or bad practice in this code and specify the line number.",
        "difficulty": "medium",
        "snippets": [
            {
                "code": """def process(data):
    try:
        result = transform_pipeline(data)
        return result
    except Exception:
        pass""",
                "target_line": 5,
                "smells": ["bare except", "empty except", "silent", "swallow", "exception", "error handling", "pass"],
                "explanation": "Bare except with pass on Line 5 — silently swallows all exceptions."
            },
            {
                "code": """result = []
for item in range(10):
    result.append(item * item)""",
                "target_line": 2,
                "smells": ["list comprehension", "comprehension", "pythonic", "append", "loop"],
                "explanation": "Should use list comprehension on Line 2 instead of manual append loop."
            },
            {
                "code": """class DataProcessor:
    def process_csv(self): pass
    def validate_xml(self): pass
    def generate_html_report(self): pass
    def connect_to_db(self): pass
    def send_email_alert(self): pass""",
                "target_line": 1,
                "smells": ["god object", "single responsibility", "srp", "god class", "too many", "cohesion"],
                "explanation": "God Object (Line 1) — Violation of Single Responsibility Principle."
            },
            {
                "code": """def check_status(s):
    if s == 1:
        return "Active"
    elif s == 2:
        return "Inactive"
    else:
        return "Unknown\"""",
                "target_line": 1,
                "smells": ["magic number", "enum", "constants", "readability"],
                "explanation": "Magic numbers used on Line 1. Should use an Enum or named constants for status values."
            },
            {
                "code": """def get_user_data(user):
    id = user.id
    name = user.profile.name
    email = user.profile.contact.email
    return email""",
                "target_line": 3,
                "smells": ["law of demeter", "chaining", "coupling", "nested access"],
                "explanation": "Violation of Law of Demeter on Line 3 — excessive chaining through deep object structure."
            }
        ]
    },

    "improvement": {
        "instruction": "Suggest one specific algorithmic or runtime improvement to this code (including the line) with reasoning.",
        "difficulty": "hard",
        "snippets": [
            {
                "code": """def find_duplicates(data_list):
    duplicates = []
    for i in range(len(data_list)):
        for j in range(i+1, len(data_list)):
            if data_list[i] == data_list[j]:
                duplicates.append(data_list[i])
    return list(set(duplicates))""",
                "target_line": 3,
                "improvements": ["hash map", "set", "o(n)", "complexity", "counter", "collections"],
                "explanation": "O(N^2) complexity on Line 3. Use a set or collections.Counter to reduce to O(N)."
            },
            {
                "code": """def read_config(path):
    f = open(path)
    data = f.read()
    f.close()
    return data""",
                "target_line": 2,
                "improvements": ["with", "context manager", "with open", "close", "resource", "leak"],
                "explanation": "Use 'with open()' on Line 2 context manager to ensure the file descriptor doesn't leak."
            },
            {
                "code": """def get_unique(items):
    res = []
    for x in items:
        if x not in res:
            res.append(x)
    return res""",
                "target_line": 4,
                "improvements": ["set", "hashable", "o(n)", "complexity"],
                "explanation": "O(N^2) complexity due to 'x not in res' list search. Use set() for O(N) performance."
            },
            {
                "code": """def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)""",
                "target_line": 3,
                "improvements": ["lru_cache", "memoization", "dynamic programming", "recursion"],
                "explanation": "Exponential complexity. Use @functools.lru_cache(None) for O(N) memoized performance."
            }
        ]
    },
    
    "security_vulnerability": {
         "instruction": "Identify the critical security vulnerability (specify line) and recommend the exact fix.",
         "difficulty": "expert",
         "snippets": [
             {
                "code": """import os
from flask import request, send_file

def download_file():
    filename = request.args.get('file')
    filepath = os.path.join('/var/www/uploads/', filename)
    return send_file(filepath)""",
                "target_line": 6,
                "flaws": ["path traversal", "directory traversal", "lfi", "sanitize", "dot dot slash"],
                "explanation": "Path Traversal vulnerability on Line 6. User can pass '../../etc/passwd'."
             },
             {
                 "code": """import hashlib

def hash_password(password_string):
    return hashlib.md5(password_string.encode()).hexdigest()""",
                 "target_line": 4,
                 "flaws": ["md5", "collision", "weak hash", "bcrypt", "argon2", "salt"],
                 "explanation": "Weak/Broken hashing algorithm (MD5) on Line 4 without a salt."
             },
             {
                 "code": """import pickle
import base64

def load_session(cookie_data):
    return pickle.loads(base64.b64decode(cookie_data))""",
                 "target_line": 5,
                 "flaws": ["pickle", "insecure deserialization", "rce", "security vulnerability"],
                 "explanation": "Insecure Deserialization (Line 5) — pickle.loads() can execute arbitrary code."
             },
             {
                 "code": """import subprocess

def run_cmd(user_path):
    subprocess.call("ls -l " + user_path, shell=True)""",
                 "target_line": 4,
                 "flaws": ["shell injection", "command injection", "subprocess", "shell=true"],
                 "explanation": "Command Injection vulnerability on Line 4 via shell=True and unsanitized input."
             }
         ]
    }
}

