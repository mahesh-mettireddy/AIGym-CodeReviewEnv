# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""CodeReviewEnv Environment Client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import CodeReviewAction, CodeReviewObservation


class CodeReviewEnv(
    EnvClient[CodeReviewAction, CodeReviewObservation, State]
):
    """
    Client for the CodeReviewEnv Environment.

    This client maintains a persistent WebSocket connection to the environment server,
    enabling efficient multi-step interactions with lower latency.
    Each client instance has its own dedicated environment session on the server.

    Example:
        >>> with CodeReviewEnv(base_url="http://localhost:8000") as client:
        ...     result = client.reset()
        ...     print(result.observation.code_snippet)
        ...
        ...     result = client.step(CodeReviewAction(
        ...         task="bug_detection",
        ...         verdict="yes, division by zero",
        ...         confidence=1.0
        ...     ))
        ...     print(result.observation.feedback)
    """

    def _step_payload(self, action: CodeReviewAction) -> Dict:
        """
        Convert CodeReviewAction to JSON payload for step message.

        Args:
            action: CodeReviewAction instance

        Returns:
            Dictionary representation suitable for JSON encoding
        """
        return {
            "task": action.task,
            "verdict": action.verdict,
            "confidence": action.confidence,
        }

    def _parse_result(self, payload: Dict) -> StepResult[CodeReviewObservation]:
        """
        Parse server response into StepResult[CodeReviewObservation].

        Args:
            payload: JSON response data from server

        Returns:
            StepResult with CodeReviewObservation
        """
        obs_data = payload.get("observation", {})
        observation = CodeReviewObservation(
            task=obs_data.get("task", ""),
            code_snippet=obs_data.get("code_snippet", ""),
            instruction=obs_data.get("instruction", ""),
            last_verdict=obs_data.get("last_verdict", ""),
            last_reward=obs_data.get("last_reward", 0.0),
            done=obs_data.get("done", False),
            score=obs_data.get("score", 0.0),
            feedback=obs_data.get("feedback", ""),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        """
        Parse server response into State object.

        Args:
            payload: JSON response from state request

        Returns:
            State object with episode_id and step_count
        """
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
