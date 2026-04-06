import asyncio
import os
import textwrap
from openai import OpenAI

from models import CodeReviewAction, CodeReviewObservation

API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
BENCHMARK = "code_review_env"

SYSTEM_PROMPT = textwrap.dedent("""
    You are an expert Python code reviewer.
    You will be shown a code snippet and a task.
    Respond concisely and directly to the instruction.
    Do not explain yourself — just give your verdict.
""").strip()

TASKS = ["bug_detection", "code_smell", "improvement"]

def run_episode(env, task_name: str):
    client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)

    obs = env.reset()
    done = False
    step = 0
    rewards = []
    total_score = 0.0

    print(f"[START] task={task_name} env={BENCHMARK} model={MODEL_NAME}")

    while not done:
        step += 1

        prompt = f"""Task: {obs.instruction}

Code:
{obs.code_snippet}

Give your verdict:"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.2
        )

        verdict = response.choices[0].message.content.strip()

        action = CodeReviewAction(
            task=obs.task,
            verdict=verdict,
            confidence=1.0
        )

        obs = env.step(action)
        reward = obs.last_reward
        done = obs.done
        rewards.append(reward)
        total_score = obs.score

        print(f"[STEP] step={step} action={repr(verdict[:80])} reward={reward:.2f} done={str(done).lower()} error=null")

    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    success = total_score > 0
    print(f"[END] success={str(success).lower()} steps={step} score={total_score:.2f} rewards={rewards_str}")
    return total_score


def main():
    # Import env locally to avoid circular imports
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from server.my_first_env_environment import MyFirstEnvironment

    env = MyFirstEnvironment()
    total = 0.0

    for task in TASKS:
        print(f"\n--- Running task: {task} ---")
        score = run_episode(env, task)
        total += score

    print(f"\n=== FINAL SCORE: {total:.2f} / {len(TASKS)}.0 ===")


if __name__ == "__main__":
    main()