import os
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field

# Constants for the Judge model
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "Qwen/Qwen2.5-72B-Instruct")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
HF_TOKEN = os.getenv("HF_TOKEN")

class JudgeVerdict(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="The semantic similarity score between the agent verdict and ground truth.")
    reasoning: str = Field(..., description="Short explanation for the assigned score.")

class SemanticJudge:
    def __init__(self):
        self.client = instructor.patch(OpenAI(
            base_url=API_BASE_URL,
            api_key=HF_TOKEN
        ))

    async def evaluate(self, task: str, code: str, agent_verdict: str, ground_truth: str) -> JudgeVerdict:
        if not HF_TOKEN:
            # Fallback if no token is provided for the judge
            return JudgeVerdict(score=0.5, reasoning="Judge disabled (No HF_TOKEN).")

        prompt = f"""You are an expert Code Review Judge. 
Evaluate the 'Agent Verdict' against the 'Ground Truth' for the following Python task.

Task Category: {task}
Code Snippet:
{code}

Ground Truth Explanation:
{ground_truth}

Agent Verdict:
{agent_verdict}

Rate the Agent Verdict from 0.0 to 1.0 based on:
1. Accuracy: Did they find the right issue?
2. Precision: Did they identify the correct line/location?
3. Reasoning: Is their technical explanation sound?

Return a JSON with 'score' and 'reasoning'."""

        try:
            return self.client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_model=JudgeVerdict,
                max_retries=2
            )
        except Exception as e:
            return JudgeVerdict(score=0.1, reasoning=f"Judge error: {str(e)}")
