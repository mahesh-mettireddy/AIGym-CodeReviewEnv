import os
import sys
import textwrap

# Ensure tasks can be imported
sys.path.append(os.getcwd())
from server.tasks import TASKS

def clean_code(code):
    if not code: return ""
    
    # Split into lines
    lines = code.split('\n')
    
    # Aggressively clean each line's indentation if it's a "hanging" indent
    # We find the first line that defines the "base" (usually indent 0 or 4)
    # and we normalize everything relative to it.
    
    # Step 1: Strip leading/trailing empty lines
    while lines and not lines[0].strip(): lines.pop(0)
    while lines and not lines[-1].strip(): lines.pop(-1)
    
    if not lines: return ""
    
    # Step 2: If the first line is indented, it's a global indent. Remove it.
    first_line_indent = len(lines[0]) - len(lines[0].lstrip())
    if first_line_indent > 0:
        lines = [l[first_line_indent:] if len(l) >= first_line_indent else l.lstrip() for l in lines]
        
    # Step 3: Now check if any subsequent line that should be at 0 (like def, import) has 1 space
    # This specifically fixes the copy-paste artifacts found in security snippets.
    cleaned_lines = []
    for l in lines:
        # If it's a line like " def " or " import " or " @", and it's not inside a block (heuristic)
        if len(l) > 0 and l.startswith(" ") and not l.startswith("    "):
            temp = l.lstrip()
            if any(temp.startswith(kw) for kw in ["def ", "import ", "from ", "@", "class ", "app ="]):
                cleaned_lines.append(temp)
                continue
        cleaned_lines.append(l)
            
    return '\n'.join(cleaned_lines).strip()

def clean_tasks():
    import pprint
    
    cleaned_tasks = {}
    for task_id, task_data in TASKS.items():
        cleaned_tasks[task_id] = {
            "instruction": task_data["instruction"],
            "difficulty": task_data["difficulty"],
            "snippets": []
        }
        for s in task_data["snippets"]:
            s["code"] = clean_code(s["code"])
            cleaned_tasks[task_id]["snippets"].append(s)
            
    with open("server/tasks.py", "w", encoding='utf-8') as f:
        f.write("TASKS = ")
        pp = pprint.PrettyPrinter(indent=4, width=120, sort_dicts=False)
        f.write(pp.pformat(cleaned_tasks))
        f.write("\n")

if __name__ == "__main__":
    clean_tasks()
    print("Tasks cleaned successfully (v3 - aggressive).")
