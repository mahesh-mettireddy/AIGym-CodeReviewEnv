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
            },
            {
                "code": """def process_items(items):
    for i in range(len(items)):
        if items[i] == 'remove':
            items.pop(i)
    return items""",
                "has_bug": True,
                "target_line": 4,
                "keywords": ["index error", "popping", "iteration", "list mutation", "indexoutofrange"],
                "explanation": "Runtime error: Modifying a list (pop) while iterating over its indices on Line 4 will cause IndexOutOfRange or skip items."
            },
            {
                "code": """count = 0
def increment():
    count += 1
increment()""",
                "has_bug": True,
                "target_line": 3,
                "keywords": ["unboundlocalerror", "global", "local scope", "shadowing"],
                "explanation": "UnboundLocalError on Line 3. 'count' is treated as a local variable because it's assigned to, but it hasn't been declared local or global."
            },
            {
                "code": """def recursive_sum(n):
    return n + recursive_sum(n-1)""",
                "has_bug": True,
                "target_line": 2,
                "keywords": ["recursionerror", "base case", "infinite recursion", "stack overflow"],
                "explanation": "Infinite recursion on Line 2. Missing base case will cause RecursionError."
            },
            {
                "code": """def check_auth(user):
    if user.is_admin is True:
        return "Admin"
    return "User\"""",
                "has_bug": False,
                "target_line": None,
                "keywords": ["no bug", "correct", "singleton comparison"],
                "explanation": "No bug: explicit comparison with 'is True' is correct for booleans in Python."
            },
            {
                "code": """def update_profile(user, data={}):
    user.profile.update(data)
    return user""",
                "has_bug": True,
                "target_line": 1,
                "keywords": ["mutable default", "dictionary", "shared state", "persists"],
                "explanation": "Logic bug on Line 1. Default argument 'data={}' is mutable and persists across calls."
            },
            {
                "code": """def get_age(birth_year):
    import datetime
    return datetime.date.today().year - birth_year""",
                "has_bug": False,
                "target_line": None,
                "keywords": ["no bug", "correct", "working"],
                "explanation": "No bug: Correct use of datetime to calculate age."
            },
            {
                "code": """def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None""",
                "has_bug": False,
                "target_line": None,
                "keywords": ["no bug", "correct", "error handling"],
                "explanation": "No bug: Correctly handles potential ZeroDivisionError."
            },
            {
                "code": """def calculate_total(prices):
    total = 0
    for p in prices:
        total += p
    return total""",
                "has_bug": False,
                "target_line": None,
                "keywords": ["no bug", "correct"],
                "explanation": "No bug: Standard and correct summation loop."
            },
            {
                "code": """def find_max(numbers):
    max_val = numbers[0]
    for n in numbers:
        if n > max_val:
            max_val = n
    return max_val""",
                "has_bug": True,
                "target_line": 2,
                "keywords": ["indexerror", "empty list", "empty sequence"],
                "explanation": "IndexError on Line 2 if the input 'numbers' list is empty."
            },
            {
                "code": """import json
def parse_config(s):
    return json.loads(s)""",
                "has_bug": False,
                "target_line": None,
                "keywords": ["no bug", "correct"],
                "explanation": "No bug: Standard JSON parsing."
            },
            {
                "code": """def binary_search(arr, x):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] < x:
            low = mid + 1
        elif arr[mid] > x:
            high = mid - 1
        else:
            return mid
    return -1""",
                "has_bug": False,
                "target_line": None,
                "keywords": ["no bug", "correct", "classic algo"],
                "explanation": "No bug: Standard and correct binary search implementation."
            },
            {
                "code": """def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True""",
                "has_bug": False,
                "target_line": None,
                "keywords": ["no bug", "correct", "is_prime"],
                "explanation": "No bug: Correct primality check using square root optimization."
            },
            {
                "code": """def get_first_character(s):
    return s[0]""",
                "has_bug": True,
                "target_line": 2,
                "keywords": ["indexerror", "empty string", "validation"],
                "explanation": "IndexError on Line 2 if called with an empty string."
            },
            {
                "code": """def validate_email(email):
    if "@" in email and "." in email:
        return True
    return False""",
                "has_bug": False,
                "target_line": None,
                "keywords": ["no bug", "basic validation"],
                "explanation": "No bug: Basic but functional logical check for email format placeholders."
            },
            {
                "code": """def factorial(n):
    res = 1
    for i in range(1, n + 1):
        res *= i
    return res""",
                "has_bug": False,
                "target_line": None,
                "keywords": ["no bug", "correct", "factorial"],
                "explanation": "No bug: Correct factorial implementation using range."
            },
            {
                "code": """def merge_dicts(a, b):
    return {**a, **b}""",
                "has_bug": False,
                "target_line": None,
                "keywords": ["no bug", "pythonic", "correct"],
                "explanation": "No bug: Correct and modern way to merge dictionaries in Python."
            },
            {
                "code": """def get_last_element(items):
    return items[-1]""",
                "has_bug": True,
                "target_line": 2,
                "keywords": ["indexerror", "empty list"],
                "explanation": "IndexError on Line 2 if passed an empty list."
            },
            {
                "code": """def compare_floats(a, b):
    return a == b

print(compare_floats(0.1 + 0.2, 0.3))""",
                "has_bug": True,
                "target_line": 2,
                "keywords": ["precision", "float equality", "rounding", "epsilon"],
                "explanation": "Logic bug on Line 2. Direct equality check for floats is unreliable due to precision issues (0.1 + 0.2 != 0.3)."
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
            },
            {
                "code": """def calculate(a, b, c, d, e, f, g, h):
    return (a + b) * (c - d) / (e + f) ** (g - h)""",
                "target_line": 1,
                "smells": ["long parameter list", "too many arguments", "readability", "complexity"],
                "explanation": "Long Parameter List on Line 1. Functions with too many arguments are hard to read and test."
            },
            {
                "code": """def process_data(data):
    if data:
        if 'id' in data:
            if data['id'] > 0:
                if 'status' in data:
                    if data['status'] == 'active':
                        return True
    return False""",
                "target_line": 2,
                "smells": ["arrow head", "nested if", "cyclomatic complexity", "guard clauses"],
                "explanation": "Arrow Head anti-pattern starting on Line 2. Excessive nesting makes code hard to follow; use guard clauses instead."
            },
            {
                "code": """def save_user(name, age, email, city, street, zip_code):
    db.save({'name': name, 'age': age, 'email': email, 'address': f'{city}, {street}, {zip_code}'})
""",
                "target_line": 1,
                "smells": ["data clump", "primitive obsession", "object parameter"],
                "explanation": "Data Clump on Line 1. Address components (city, street, zip) should be grouped into an Address object."
            },
            {
                "code": """# Increment i by 1
i += 1""",
                "target_line": 1,
                "smells": ["junk comment", "redundant comment", "noise"],
                "explanation": "Junk Comment on Line 1. The comment merely restates what the code obviously does."
            },
            {
                "code": """class Employee:
    def get_salary(self):
        return self.hours * self.rate

    def get_tax(self):
        return self.get_salary() * 0.2""",
                "target_line": 1,
                "smells": ["primitive obsession", "money type"],
                "explanation": "Primitive Obsession on Line 1. Using primitive types for money (salary, tax) instead of a dedicated Money class."
            },
            {
                "code": """def print_report(data):
    # Header
    print("Report")
    # Body
    for item in data:
        print(item)
    # Footer
    print("End")""",
                "target_line": 1,
                "smells": ["long method", "separation of concerns", "extract method"],
                "explanation": "Long Method / Lack of Abstraction on Line 1. Logic should be extracted into print_header, print_body, and print_footer."
            },
            {
                "code": """class Shape:
    def area(self): pass

class Circle(Shape):
    def area(self): return 3.14 * self.r**2

class Square(Shape):
    def area(self): return self.side**2""",
                "target_line": None,
                "smells": ["no smell", "correct polymorphism"],
                "explanation": "No smell: Correct use of inheritance and polymorphism."
            },
            {
                "code": """def get_config():
    # Fetching from DB
    url = "http://localhost"
    timeout = 30
    return url, timeout""",
                "target_line": 3,
                "smells": ["hardcoded", "magic string", "magic number"],
                "explanation": "Hardcoded values on Line 3 and 4. Configuration should be externalized."
            },
            {
                "code": """class User:
    def __init__(self, name):
        self.name = name
    def get_name(self):
        return self.name""",
                "target_line": 4,
                "smells": ["unnecessary getter", "not pythonic"],
                "explanation": "Unnecessary Getter on Line 4. In Python, direct attribute access is preferred unless logic is needed."
            },
            {
                "code": """def calculate_total(items):
    t = 0
    for i in items:
        t += i.price
    return t""",
                "target_line": 2,
                "smells": ["uninformative name", "naming convention"],
                "explanation": "Poor naming (t, i) on Line 2 and 3. Variables should have descriptive names like 'total' and 'item'."
            },
            {
                "code": """class Order:
    def process(self):
        # 100 lines of logic here
        pass""",
                "target_line": 2,
                "smells": ["large class", "long method", "god object"],
                "explanation": "Large Class/Method on Line 2. Should be broken down into smaller, manageable pieces."
            },
            {
                "code": """def fetch_user(id):
    pass
# def fetch_user_v2(id):
#     pass""",
                "target_line": 3,
                "smells": ["commented out code", "dead code", "clutter"],
                "explanation": "Commented-out code on Line 3. Clutters the repository; use version control instead."
            },
            {
                "code": """if status == 'active':
    pass
elif status == 'Active':
    pass""",
                "target_line": 3,
                "smells": ["duplicated logic", "case sensitivity", "normalization"],
                "explanation": "Duplicated logic with case variants on Line 1 and 3. Input should be normalized first."
            },
            {
                "code": """import os
import sys
import datetime
# Unused import below
import math
def get_date():
    return datetime.date.today()""",
                "target_line": 5,
                "smells": ["unused import", "dead code", "clutter"],
                "explanation": "Unused import (math) on Line 5."
            },
            {
                "code": """def solve():
    # Intentionally left blank for future use
    pass""",
                "target_line": 1,
                "smells": ["speculative generality", "lazy class", "placeholder"],
                "explanation": "Speculative Generality on Line 1. Placeholder code that serves no current purpose."
            },
            {
                "code": """def process(data):
    if not data: return
    # logic
    if not data: return
    # more logic""",
                "target_line": 4,
                "smells": ["redundant check", "dead code"],
                "explanation": "Redundant check on Line 4. 'data' was already checked on Line 2."
            },
            {
                "code": """class A:
    def do_x(self): pass
class B(A):
    def do_x(self):
        # B doesn't really need do_x, so it's empty
        pass""",
                "target_line": 3,
                "smells": ["refused bequest", "improper inheritance"],
                "explanation": "Refused Bequest on Line 3. Class B inherits a method it doesn't need or want to implement."
            },
            {
                "code": """def log(msg):
    print(f"LOG: {msg}")
def debug(msg):
    # exact same code
    print(f"LOG: {msg}")""",
                "target_line": 4,
                "smells": ["duplicated code", "dry violation"],
                "explanation": "Duplicated Code on Line 1 and 4. Both functions implement the exact same logic."
            },
            {
                "code": """val = data['user']['profile']['settings']['theme']""",
                "target_line": 1,
                "smells": ["message chain", "coupling", "fragile"],
                "explanation": "Message Chain on Line 1. Tight coupling to the structure of the data dictionary."
            },
            {
                "code": """def check(x):
    return x > 10 and x < 100""",
                "target_line": None,
                "smells": ["no smell", "clean"],
                "explanation": "No smell: Simple and clear boolean logic."
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
            },
            {
                "code": """def concatenate_strings(list_of_strings):
    result = ""
    for s in list_of_strings:
        result += s
    return result""",
                "target_line": 4,
                "improvements": ["join", "string concatenation", "efficiency", "o(n)"],
                "explanation": "Inefficient string concatenation (O(N^2)) on Line 4. Use ''.join(list_of_strings) for O(N) performance."
            },
            {
                "code": """def is_member(val, items):
    for i in items:
        if i == val:
            return True
    return False""",
                "target_line": 2,
                "improvements": ["set", "hash table", "o(1)", "membership"],
                "explanation": "O(N) search on Line 2. Convert 'items' to a set for O(1) constant time membership checks."
            },
            {
                "code": """def process_file(path):
    with open(path, 'r') as f:
        data = f.read()
        for line in data.split('\\n'):
            process(line)""",
                "target_line": 3,
                "improvements": ["generator", "iterator", "memory", "line by line"],
                "explanation": "Inefficient memory usage on Line 3. Large files should be iterated line-by-line using 'for line in f:' instead of loading everything into memory."
            },
            {
                "code": """import re
def find_all_emails(text_list):
    results = []
    for text in text_list:
        results.append(re.findall(r'[\\w\\.-]+@[\\w\\.-]+', text))
    return results""",
                "target_line": 5,
                "improvements": ["re.compile", "precompile", "performance", "regex"],
                "explanation": "Repeated regex compilation on Line 5. Pre-compile the pattern using re.compile() outside the loop for better performance."
            },
            {
                "code": """def get_top_k(nums, k):
    return sorted(nums, reverse=True)[:k]""",
                "target_line": 2,
                "improvements": ["heapq", "nlargest", "o(n log k)", "complexity"],
                "explanation": "O(N log N) sort on Line 2. Use heapq.nlargest for O(N log K) efficiency when getting the top K elements."
            },
            {
                "code": """class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y""",
                "target_line": 1,
                "improvements": ["slots", "memory optimization", "__slots__"],
                "explanation": "Memory inefficient for millions of instances. Use __slots__ = ('x', 'y') on Line 1/2 to reduce memory overhead per object."
            },
            {
                "code": """def check_status(codes):
    found = False
    for c in codes:
        if c == \"ERROR\":
            found = True
            break
    return found""",
                "target_line": 3,
                "improvements": ["any", "short-circuit", "pythonic", "built-in"],
                "explanation": "Manual loop on Line 3. Use the built-in any() function for more Pythonic and efficient early-exit logic."
            },
            {
                "code": """def get_vowels(s):
    res = []
    for char in s:
        if char in 'aeiou':
            res.append(char)
    return res""",
                "target_line": 3,
                "improvements": ["list comprehension", "pythonic", "comprehension", "append"],
                "explanation": "Should use list comprehension on Line 3 for more efficient and readable filtering."
            },
            {
                "code": """def update_inventory(inv, items):
    for item in items:
        if item in inv:
            inv[item] += 1
        else:
            inv[item] = 1""",
                "target_line": 2,
                "improvements": ["defaultdict", "counter", "collections", "efficiency"],
                "explanation": "Repetitive membership check on Line 2. Use collections.Counter or defaultdict(int) to simplify the update logic."
            },
            {
                "code": """import math
def get_distances(points):
    return [math.sqrt(p[0]**2 + p[1]**2) for p in points]""",
                "target_line": 3,
                "improvements": ["map", "math.hypot", "vectorization"],
                "explanation": "Use math.hypot(p[0], p[1]) on Line 3 for better numerical stability and performance."
            },
            {
                "code": """def remove_first(l):
    return l.pop(0)""",
                "target_line": 2,
                "improvements": ["deque", "collections", "popleft", "o(1)"],
                "explanation": "O(N) operation on Line 2. Popping from the start of a list is slow. Use collections.deque and popleft() for O(1) performance."
            },
            {
                "code": """def get_squares(n):
    return {x: x**2 for x in range(n)}""",
                "target_line": None,
                "improvements": ["no improvement", "pythonic", "correct"],
                "explanation": "No improvement: Modern and efficient use of dictionary comprehension."
            },
            {
                "code": """def count_matching(a, b):
    count = 0
    for x, y in zip(a, b):
        if x == y:
            count += 1
    return count""",
                "target_line": 3,
                "improvements": ["sum", "generator expression", "pythonic"],
                "explanation": "Manual counter on Line 3. Use sum(1 for x, y in zip(a, b) if x == y) for a more Pythonic implementation."
            },
            {
                "code": """def find_index(arr, x):
    for i in range(len(arr)):
        if arr[i] == x:
            return i
    return -1""",
                "target_line": 2,
                "improvements": ["enumerate", "index", "pythonic"],
                "explanation": "Non-Pythonic loop on Line 2. Use 'enumerate(arr)' for cleaner indexing or 'arr.index(x)' with error handling."
            },
            {
                "code": """def get_intersection(a, b):
    res = []
    for x in a:
        if x in b:
            res.append(x)
    return res""",
                "target_line": 4,
                "improvements": ["set intersection", "o(n+m)", "bitwise intersection"],
                "explanation": "O(N*M) loop on Line 4. Use set(a) & set(b) for efficient O(N+M) set intersection."
            },
            {
                "code": """def process_indices(data):
    i = 0
    for x in data:
        process(i, x)
        i += 1""",
                "target_line": 2,
                "improvements": ["enumerate", "pythonic"],
                "explanation": "Manual index management on Line 2. Use enumerate(data) instead."
            },
            {
                "code": """def load_lines(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    return lines""",
                "target_line": 2,
                "improvements": ["with statement", "context manager", "generator"],
                "explanation": "Potential resource leak on Line 2 if an error occurs. Always use the 'with' statement for file I/O."
            },
            {
                "code": """def check_existence(target, sorted_list):
    return target in sorted_list""",
                "target_line": 2,
                "improvements": ["bisect", "binary search", "o(log n)"],
                "explanation": "O(N) linear search on Line 2 for a sorted list. Use bisect_left for efficient O(log N) binary search."
            },
            {
                "code": """def get_unique_sorted(items):
    return sorted(list(set(items)))""",
                "target_line": None,
                "improvements": ["no improvement", "pythonic"],
                "explanation": "No improvement: Standard and correct way to get unique sorted elements."
            },
            {
                "code": """data = [1, 2, 3]
for i in range(len(data)):
    data[i] = data[i] * 2""",
                "target_line": 2,
                "improvements": ["list comprehension", "map", "pythonic"],
                "explanation": "In-place mutation while iterating on Line 2. Use a list comprehension 'data = [x * 2 for x in data]' for cleaner logic."
            },
            {
                "code": """# Large dataset sum
data = range(1000000)
total = 0
for x in data:
    total += x""",
                "target_line": 4,
                "improvements": ["sum built-in", "efficiency"],
                "explanation": "Manual summation loop on Line 4. Use the built-in sum() function which is implemented in C and much faster."
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
             },
             {
                 "code": """from flask import Flask, request
app = Flask(__name__)
 
 @app.route('/transfer')
 def transfer():
     amount = request.args.get('amount')
     to_user = request.args.get('to')
     # Missing CSRF protection
     db.transfer(session['user'], to_user, amount)""",
                 "target_line": 8,
                 "flaws": ["csrf", "cross-site request forgery", "session", "transfer"],
                 "explanation": "Cross-Site Request Forgery (CSRF) on Line 8. Sensitive state-changing operation lacks protection."
             },
             {
                 "code": """import requests
 
 def fetch_metadata(url):
     # Directly fetches from user-provided URL
     return requests.get(url).content""",
                 "target_line": 4,
                 "flaws": ["ssrf", "server-side request forgery", "internal", "network"],
                 "explanation": "Server-Side Request Forgery (SSRF) on Line 4. Agent can access internal cloud metadata or local services."
             },
             {
                 "code": """@app.route('/invoice/<int:id>')
 def get_invoice(id):
     invoice = db.query(f"SELECT * FROM invoices WHERE id = {id}")
     return jsonify(invoice)""",
                 "target_line": 3,
                 "flaws": ["idor", "insecure direct object reference", "authorization", "ownership"],
                 "explanation": "Insecure Direct Object Reference (IDOR) on Line 3. Missing ownership check: any user can view any invoice by ID."
             },
             {
                 "code": """import re
 
 def audit_text(text):
     pattern = re.compile(r'^(a+)+$')
     return pattern.match(text)""",
                 "target_line": 4,
                 "flaws": ["redos", "regular expression denial of service", "backtracking", "regex"],
                 "explanation": "Regular Expression Denial of Service (ReDoS) on Line 4. Catastrophic backtracking pattern used."
             },
             {
                 "code": """api_key = \"sk-12345abcdef67890\" # Production Key
 def call_api(): pass""",
                 "target_line": 1,
                 "flaws": ["hardcoded secret", "api key", "credentials", "security leak"],
                 "explanation": "Hardcoded API Key on Line 1. Secrets should be stored in environment variables or vault."
             },
             {
                 "code": """from flask import render_template_string
 
 @app.route('/hello')
 def hello():
     name = request.args.get('name')
     return render_template_string(f\"<h1>Hello {name}</h1>\")""",
                 "target_line": 6,
                 "flaws": ["ssti", "server-side template injection", "jinja2", "xss"],
                 "explanation": "Server-Side Template Injection (SSTI) on Line 6. Allows arbitrary code execution via template tags."
             },
             {
                 "code": """from flask import make_response
 
 def login():
     resp = make_response(\"Login Successful\")
     resp.set_cookie('session_id', '12345') # Missing secure flags
     return resp""",
                 "target_line": 5,
                 "flaws": ["insecure cookie", "httponly", "secure flag", "csrf"],
                 "explanation": "Insecure Cookie on Line 5. Missing HttpOnly and Secure flags, making it vulnerable to XSS and interception."
             },
             {
                 "code": """def admin_panel():
     if request.form.get('is_admin') == 'true':
         return \"Welcome Master\"
     return \"Access Denied\"""",
                 "target_line": 2,
                 "flaws": ["broken access control", "privilege escalation", "client-side trust"],
                 "explanation": "Broken Access Control on Line 2. Trusting client-side form values for authorization."
             },
             {
                 "code": """import os
 def get_file(user_input):
     return open(os.path.join('/tmp/', user_input)).read()""",
                 "target_line": 3,
                 "flaws": ["path traversal", "lfi", "directory traversal"],
                 "explanation": "Path Traversal vulnerability on Line 3. User can input '../../etc/passwd'."
             },
             {
                 "code": """import secret_service
 def authenticate(user, password):
     # Timing attack vulnerable comparison
     return password == secret_service.get_hash(user)""",
                 "target_line": 4,
                 "flaws": ["timing attack", "constant time comparison", "hmac.compare_digest"],
                 "explanation": "Timing Attack vulnerability on Line 4. Direct string comparison leaks password length/prefix info."
             },
             {
                 "code": """import random
 def generate_password():
     return \"\".join(random.choice(\"0123456789\") for _ in range(8))""",
                 "target_line": 3,
                 "flaws": ["insecure random", "predictable", "secrets", "cryptography"],
                 "explanation": "Insecure Randomness on Line 3. 'random' is not cryptographically secure; use 'secrets' instead."
             },
             {
                 "code": """from flask import redirect, request
 
 @app.route('/goto')
 def goto():
     return redirect(request.args.get('url'))""",
                 "target_line": 5,
                 "flaws": ["open redirect", "phishing", "unvalidated redirect"],
                 "explanation": "Open Redirect on Line 5. Allows attackers to use your domain to redirect users to malicious sites."
             },
             {
                 "code": """@app.after_request
 def add_headers(response):
     response.headers['Access-Control-Allow-Origin'] = '*'""",
                 "target_line": 3,
                 "flaws": ["insecure cors", "cross-origin resource sharing", "wildcard"],
                 "explanation": "Insecure CORS Policy (Line 3). Using wildcard '*' allows any site to read sensitive data."
             },
             {
                 "code": """def process_upload(file):
     # Missing size check
     save_to_disk(file.content)""",
                 "target_line": 3,
                 "flaws": ["denial of service", "unrestricted upload", "dos"],
                 "explanation": "Missing File Size Check on Line 3. Can lead to disk exhaustion and DoS."
             },
             {
                 "code": """from lxml import etree
 def parse_xml(xml_body):
     parser = etree.XMLParser(resolve_entities=True)
     return etree.fromstring(xml_body, parser)""",
                 "target_line": 3,
                 "flaws": ["xxe", "xml external entity", "lxml", "information leak"],
                 "explanation": "XML External Entity (XXE) vulnerability on Line 3. resolve_entities=True allows fetching external files."
             },
             {
                 "code": """import logging
 def login(user, password):
     logging.info(f\"Login attempt for {user} with password {password}\")""",
                 "target_line": 3,
                 "flaws": ["sensitive data in logs", "information leak", "credentials"],
                 "explanation": "Sensitive Data Logging on Line 3. Plaintext passwords should never be logged."
             },
             {
                 "code": """def validate_user(user):
     # Trusting the hidden admin field
     if user.form['is_admin']:
         return True""",
                 "target_line": 3,
                 "flaws": ["broken access control", "hidden field", "privilege escalation"],
                 "explanation": "Broken Access Control on Line 3 via untrusted hidden form field."
             },
             {
                 "code": """@app.route('/search')
 def search():
     q = request.args.get('q')
     return \"Results for: \" + q""",
                 "target_line": 4,
                 "flaws": ["xss", "cross-site scripting", "injection"],
                 "explanation": "Reflected XSS on Line 4. Unsanitized input is returned directly to the browser."
             },
             {
                 "code": """def create_app():
     app.run(host='0.0.0.0')""",
                 "target_line": 2,
                 "flaws": ["insecure bind", "network exposure", "listening"],
                 "explanation": "Insecure Bind on Line 2. Binding to 0.0.0.0 exposes the app to all network interfaces."
             },
             {
                 "code": """import os
 def safe_function(data):
     return data.strip().replace('<', '&lt;')""",
                 "target_line": None,
                 "flaws": ["no flaw", "basic sanitization"],
                 "explanation": "No flaw: Basic manual HTML escaping for XSS prevention."
             },
             {
                 "code": """import os
 def secure_it(path):
     os.chmod(path, 0o777)""",
                 "target_line": 3,
                 "flaws": ["insecure permissions", "world writable", "0777", "chmod"],
                 "explanation": "Insecure File Permissions on Line 3. Setting mode to 0o777 makes the file world-writable."
             }
         ]
     }
 }

