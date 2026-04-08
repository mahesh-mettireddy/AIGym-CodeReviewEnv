import os
import sys
import textwrap
from openai import OpenAI

sys.path.insert(0, os.path.dirname(__file__))

from models import CodeReviewAction, CodeReviewObservation

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
BENCHMARK = "code_review_env"

SYSTEM_PROMPT = textwrap.dedent("""
    You are an expert Python code reviewer.
    You will be shown a code snippet and a task.
    Respond concisely and directly to the instruction.
    Do not explain yourself — just give your verdict.
""").strip()


def main():
    from server.my_first_env_environment import CodeReviewEnvironment

    client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)
    env = CodeReviewEnvironment()

    obs = env.reset()
    done = False
    step = 0
    rewards = []

    print(f"[START] task=all_tasks env={BENCHMARK} model={MODEL_NAME}")

    while not done:
        step += 1

        prompt = f"""Task: {obs.instruction}

Code:
{obs.code_snippet}

Give your verdict:"""

        try:
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
            error_str = "null"
        except Exception as e:
            verdict = "no verdict"
            error_str = str(e)[:80]

        action = CodeReviewAction(
            task=obs.task,
            verdict=verdict,
            confidence=1.0
        )

        obs = env.step(action)
        reward = obs.last_reward
        done = obs.done
        rewards.append(reward)
        print(f"[STEP] step={step} task={obs.task} action={repr(verdict[:80])} reward={reward:.2f} done={str(done).lower()} error={error_str}")
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    total_raw = sum(rewards)
    total_normalized = total_raw / len(rewards) if rewards else 0.0
    success = total_raw > 0
    print(f"[END] success={str(success).lower()} steps={step} score={total_normalized:.2f} rewards={rewards_str}")


if __name__ == "__main__":
    main()
