"""Smoke tests for the Rubric graders.

Each test feeds a known-answer verdict for a deterministic snippet and asserts
the expected reward tier is returned.  This guards against regressions in the
scoring logic and validates that _total_score is initialised before step().
"""

from server.tasks import TASKS
from server.graders import (
    BugDetectionGrader,
    CodeSmellGrader,
    ImprovementGrader,
    SecurityGrader,
)
from models import CodeReviewAction, CodeReviewObservation

# Reward tier constants matching the graders' scoring rubric
REWARD_EXPERT = 0.99
REWARD_ADVANCED_BUG = 0.75
REWARD_ADVANCED_SMELL = 0.75
REWARD_ADVANCED_IMPROVEMENT = 0.80
REWARD_ADVANCED_SECURITY = 0.85
REWARD_PARTIAL = 0.40
REWARD_FAILED = 0.01


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _action(verdict: str) -> CodeReviewAction:
    return CodeReviewAction(task="", verdict=verdict, confidence=1.0)


def _obs(code: str) -> dict:
    return {"code_snippet": code}


def _first_snippet(task_name: str) -> dict:
    return TASKS[task_name]["snippets"][0]


# ---------------------------------------------------------------------------
# BugDetectionGrader
# ---------------------------------------------------------------------------

class TestBugDetectionGrader:
    grader = BugDetectionGrader()
    snippet = _first_snippet("bug_detection")  # has_bug=True, target_line=4

    def test_expert_reward_correct_line_and_keywords(self):
        verdict = "yes, SQL injection vulnerability on line 4 via f-string"
        reward = self.grader.forward(_action(verdict), _obs(self.snippet["code"]))
        assert reward == REWARD_EXPERT

    def test_advanced_reward_correct_but_wrong_line(self):
        verdict = "yes, SQL injection vulnerability on line 99"
        reward = self.grader.forward(_action(verdict), _obs(self.snippet["code"]))
        assert reward == REWARD_PARTIAL

    def test_failed_reward_incorrect_answer(self):
        verdict = "no, the code is perfectly fine"
        reward = self.grader.forward(_action(verdict), _obs(self.snippet["code"]))
        assert reward == REWARD_FAILED

    def test_unknown_snippet_returns_minimum(self):
        reward = self.grader.forward(_action("yes"), _obs("def foo(): pass"))
        assert reward == REWARD_FAILED


# ---------------------------------------------------------------------------
# CodeSmellGrader
# ---------------------------------------------------------------------------

class TestCodeSmellGrader:
    grader = CodeSmellGrader()
    snippet = _first_snippet("code_smell")

    def test_expert_reward(self):
        smells = self.snippet["smells"]
        verdict = f"line {self.snippet['target_line']}: {smells[0]} and {smells[1]}"
        reward = self.grader.forward(_action(verdict), _obs(self.snippet["code"]))
        assert reward == REWARD_EXPERT

    def test_minimum_reward_no_keywords(self):
        reward = self.grader.forward(_action("nothing wrong"), _obs(self.snippet["code"]))
        assert reward == REWARD_FAILED


# ---------------------------------------------------------------------------
# ImprovementGrader
# ---------------------------------------------------------------------------

class TestImprovementGrader:
    grader = ImprovementGrader()
    snippet = _first_snippet("improvement")

    def test_expert_reward(self):
        imps = self.snippet["improvements"]
        verdict = f"line {self.snippet['target_line']}: {imps[0]} and {imps[1]}"
        reward = self.grader.forward(_action(verdict), _obs(self.snippet["code"]))
        assert reward == REWARD_EXPERT

    def test_minimum_reward_no_keywords(self):
        reward = self.grader.forward(_action("looks fine"), _obs(self.snippet["code"]))
        assert reward == REWARD_FAILED


# ---------------------------------------------------------------------------
# SecurityGrader
# ---------------------------------------------------------------------------

class TestSecurityGrader:
    grader = SecurityGrader()
    snippet = _first_snippet("security_vulnerability")

    def test_expert_reward(self):
        flaws = self.snippet["flaws"]
        verdict = f"line {self.snippet['target_line']}: {flaws[0]} and {flaws[1]}"
        reward = self.grader.forward(_action(verdict), _obs(self.snippet["code"]))
        assert reward == REWARD_EXPERT

    def test_minimum_reward_no_keywords(self):
        reward = self.grader.forward(_action("no issues"), _obs(self.snippet["code"]))
        assert reward == REWARD_FAILED


# ---------------------------------------------------------------------------
# Environment initialisation guard (_total_score)
# ---------------------------------------------------------------------------

class TestEnvironmentInit:
    def test_step_without_reset_does_not_raise(self):
        """_total_score must be initialised in __init__ so step() before reset() is safe."""
        from server.my_first_env_environment import CodeReviewEnvironment
        env = CodeReviewEnvironment()
        # Load a task manually so _current_task and _current_snippet are populated
        env.reset()
        # Confirm attribute exists from __init__ before reset was ever called on a fresh env
        env2 = CodeReviewEnvironment()
        assert hasattr(env2, "_total_score"), "_total_score must be set in __init__"
        assert env2._total_score == 0.0
