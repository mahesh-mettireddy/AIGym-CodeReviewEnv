from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

import sys
import os

# Robustly ensure the project root is in sys.path for headless evaluator imports
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from models import CodeReviewAction, CodeReviewObservation

# -------------------------------------------------------
# TASK BANK
# Real Python code snippets with known issues
# -------------------------------------------------------
from .tasks import TASKS
from .graders import (
    BugDetectionGrader, 
    CodeSmellGrader, 
    ImprovementGrader, 
    SecurityGrader
)

import random

class CodeReviewEnvironment(Environment):
    """
    CodeReviewEnv — teaches AI agents to review Python code.
    4 tasks: bug detection, code smell, improvement suggestion, security auditing.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True
    TASKS = ["bug_detection", "code_smell", "improvement", "security_vulnerability"]

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._current_task = None
        self._current_snippet = None
        self._task_index = 0
        self._substep_index = 0
        self._total_score = 0.0

    def reset(self) -> CodeReviewObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task_index = 0
        self._substep_index = 0
        self._total_score = 0.0
        return self._load_task(0)

    def _load_task(self, index) -> CodeReviewObservation:
        task_name = self.TASKS[index]
        task = TASKS[task_name]
        snippet = random.choice(task["snippets"])
        self._current_task = task_name
        self._current_snippet = snippet
        return CodeReviewObservation(
            task=task_name,
            code_snippet=snippet["code"],
            instruction=task["instruction"],
            last_verdict="",
            last_reward=0.0,
            done=False,
            score=self._total_score,
            feedback=""
        )

    def step(self, action: CodeReviewAction) -> CodeReviewObservation:
        self._state.step_count += 1
        reward = self._grade(action)
        self._total_score += reward
        
        feedback = self._get_feedback(action, reward)

        # Multi-turn logic: 2 attempts per snippet if reward is not perfect
        can_refine = self._substep_index == 0 and reward < 0.90
        
        if can_refine:
            self._substep_index += 1
            # Return same observation with feedback and hint
            return CodeReviewObservation(
                task=self._current_task,
                code_snippet=self._current_snippet["code"],
                instruction=f"REFINEMENT: {feedback}. Please provide a more precise verdict.",
                last_verdict=action.verdict,
                last_reward=reward,
                done=False,
                score=self._total_score,
                feedback=feedback
            )

        # Move to next task
        self._task_index += 1
        self._substep_index = 0
        done = self._task_index >= len(self.TASKS)

        if done:
            return CodeReviewObservation(
                task=self._current_task,
                code_snippet=self._current_snippet["code"],
                instruction="Episode complete.",
                last_verdict=action.verdict,
                last_reward=reward,
                done=True,
                score=self._total_score,
                feedback=feedback
            )
        else:
            next_obs = self._load_task(self._task_index)
            next_obs.last_verdict = action.verdict
            next_obs.last_reward = reward
            next_obs.score = self._total_score
            next_obs.feedback = feedback
            return next_obs

    def _grade(self, action: CodeReviewAction) -> float:
        """Delegate grading to the Source of Truth: The Grader Rubrics."""
        task = self._current_task
        observation = {
            "code_snippet": self._current_snippet["code"]
        }
        
        graders = {
            "bug_detection": BugDetectionGrader(),
            "code_smell": CodeSmellGrader(),
            "improvement": ImprovementGrader(),
            "security_vulnerability": SecurityGrader()
        }
        
        grader = graders.get(task)
        if not grader:
            return 0.01
            
        return grader.forward(action, observation)

    def _get_feedback(self, action: CodeReviewAction, reward: float) -> str:
        """Provide explanatory hints based on current performance."""
        if reward >= 0.90:
            return "Perfect! You correctly identified the issue and the line number."
        if reward >= 0.70:
            return "Correct issue, but please double check the line number."
        if reward >= 0.40:
            return f"Partially correct. {self._current_snippet['explanation']}"
        return "Incorrect. Please review the code carefully for logical or architectural flaws."

    @property
    def state(self) -> State:
        return self._state