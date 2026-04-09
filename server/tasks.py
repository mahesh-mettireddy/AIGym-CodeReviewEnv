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
