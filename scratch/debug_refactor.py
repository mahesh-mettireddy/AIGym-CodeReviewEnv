import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from server.my_first_env_environment import CodeReviewEnvironment
from models import CodeReviewAction

env = CodeReviewEnvironment()
print("--- [VERIFY REFACTOR: INCORRECT -> REFINEMENT] ---")
obs = env.reset()
print(f"Task: {obs.task}")
action = CodeReviewAction(task=obs.task, verdict="vague guess", confidence=1.0)
obs = env.step(action)
print(f"Refinement Instruction: {obs.instruction[:80]}...")
print(f"Correct Delegation (Reward != 0): {obs.last_reward}")

print("\n--- [VERIFY REFACTOR: CORRECT + LINE -> SUCCESS] ---")
# Find the actual answer for the current snippet
from server.tasks import TASKS
snippet = next(s for s in TASKS[obs.task]["snippets"] if s["code"].strip() == obs.code_snippet.strip())
ans = "yes" if snippet.get("has_bug") else "no"
line = snippet.get("target_line")
verdict = f"{ans}, the issue is on line {line}" if line else f"{ans}, no bug"

action = CodeReviewAction(task=obs.task, verdict=verdict, confidence=1.0)
obs = env.step(action)
print(f"Moved to next task: {obs.task}")
print(f"Excellent Reward (>=0.90): {obs.last_reward}")
