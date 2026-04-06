from openenv.core.env_server.types import Action, Observation
from pydantic import Field
from typing import Optional

class CodeReviewAction(Action):
    """What the agent sends — its review decision."""
    task: str = Field(..., description="Task name: bug_detection, code_smell, improvement")
    verdict: str = Field(..., description="Agent's verdict or suggestion as plain text")
    confidence: float = Field(default=1.0, description="Agent confidence 0.0 to 1.0")

class CodeReviewObservation(Observation):
    """What the agent sees each turn."""
    task: str = Field(default="", description="Current task name")
    code_snippet: str = Field(default="", description="Code snippet to review")
    instruction: str = Field(default="", description="What agent must do")
    last_verdict: str = Field(default="", description="Agent's last verdict")
    last_reward: float = Field(default=0.0, description="Reward from last step")
    done: bool = Field(default=False, description="Is episode over")
    score: float = Field(default=0.0, description="Total score so far")
    feedback: str = Field(default="", description="Feedback on last action")