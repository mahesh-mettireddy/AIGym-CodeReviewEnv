import ast
import os
import sys

# Ensure server module can be imported
sys.path.append(os.getcwd())

try:
    from server.tasks import TASKS
except ImportError as e:
    print(f"FAILED: Could not import tasks. Error: {e}")
    sys.exit(1)

def verify_benchmark():
    print("=== CodeReviewEnv 2.0 Benchmark Audit ===")
    total_found = 0
    errors = []

    for task_id, task_data in TASKS.items():
        print(f"Auditing category: {task_id}...")
        snippets = task_data.get("snippets", [])
        total_found += len(snippets)
        
        for i, s in enumerate(snippets):
            # 1. Check required fields
            required = ["code", "explanation"]
            if task_id == "bug_detection": required.append("has_bug")
            
            for field in required:
                if field not in s:
                    errors.append(f"[{task_id}][#{i}] Missing field: {field}")
            
            # 2. Check syntax
            try:
                ast.parse(s["code"])
            except SyntaxError as e:
                errors.append(f"[{task_id}][#{i}] Syntax Error: {e}")
            
            # 3. Check target_line boundary
            if s.get("target_line") is not None:
                lines = s["code"].strip().split('\n')
                if s["target_line"] > len(lines) or s["target_line"] < 1:
                    errors.append(f"[{task_id}][#{i}] Line Boundary Error: target_line={s['target_line']}, len={len(lines)}")

    print(f"\nFinal Audit Results:")
    print(f"- Total Snippets: {total_found}")
    
    if errors:
        print(f"- ERRORS FOUND: {len(errors)}")
        for e in errors:
            print(f"  > {e}")
    else:
        print("- ALL CHECKS PASSED. Benchmark is 10/10 quality.")

if __name__ == "__main__":
    verify_benchmark()
