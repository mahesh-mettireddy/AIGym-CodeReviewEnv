from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

import sys
import os
import inspect

# Robustly ensure the project root is in sys.path
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from models import CodeReviewAction, CodeReviewObservation
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
    CodeReviewEnv 2.0 — Production-grade RL environment for LLMs.
    Features: Semantic Judging, 40+ snippets, and Multi-turn refinement.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True
    TASKS = ["bug_detection", "code_smell", "improvement", "security_vulnerability"]

    def __init__(self):
        super().__init__()
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._current_task = None
        self._current_snippet = None
        self._task_index = 0
        self._substep_index = 0
        self._total_score = 0.0

    def reset(self, **kwargs) -> CodeReviewObservation:
        """Sync reset (fallback)."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task_index = 0
        self._substep_index = 0
        self._total_score = 0.0
        return self._load_task(0)

    async def reset_async(self, **kwargs) -> CodeReviewObservation:
        """Async reset used by modern clients."""
        return self.reset(**kwargs)

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

    async def step_async(self, action: CodeReviewAction, **kwargs) -> CodeReviewObservation:
        """Async step to support semantic LLM-as-a-judge calls."""
        self._state.step_count += 1
        
        # 1. Compute Semantic Reward
        reward = await self._grade_async(action)
        self._total_score += reward
        
        feedback = self._get_feedback(action, reward)

        # 2. Multi-turn logic: Allow 1 refinement per snippet if score is low
        can_refine = self._substep_index == 0 and reward < 0.85
        
        if can_refine:
            self._substep_index += 1
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

        # 3. Handle Transitions
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

    def step(self, action: CodeReviewAction, **kwargs) -> CodeReviewObservation:
        """Synchronous fallback (not recommended for Semantic Judging)."""
        import asyncio
        return asyncio.run(self.step_async(action))

    def _normalize(self, text: str) -> str:
        import re
        return re.sub(r'[^\w\s]', ' ', text.lower()).strip()

    async def _grade_async(self, action: CodeReviewAction) -> float:
        """Delegate to Async Semantic Graders."""
        task = self._current_task
        observation = {"code_snippet": self._current_snippet["code"]}
        
        graders = {
            "bug_detection": BugDetectionGrader(),
            "code_smell": CodeSmellGrader(),
            "improvement": ImprovementGrader(),
            "security_vulnerability": SecurityGrader()
        }
        
        grader = graders.get(task)
        if not grader: return 0.01
            
        result = grader.forward(action, observation)
        if inspect.iscoroutine(result):
            return await result
        return result

    def _get_feedback(self, action: CodeReviewAction, reward: float) -> str:
        """Provide explanatory hints based on current performance."""
        if reward >= 0.90:
            return "Excellent technical audit. High semantic match with ground truth."
        if reward >= 0.70:
            return "Good observation, but logic could be more precise."
        if reward >= 0.40:
            return f"Partially correct. Hint: {self._current_snippet['explanation']}"
        return "Incorrect. The agent failed to identify the core technical vulnerability or algorithmic flaw."

    @property
    def state(self) -> State:
        return self._state