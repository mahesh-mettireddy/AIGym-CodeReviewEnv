import pytest
from server.my_first_env_environment import CodeReviewEnvironment
from models import CodeReviewAction

def test_environment_initialization():
    """
    Ensure the environment initializes cleanly and can be stepped
    without requiring an explicit reset() call, verifying that
    _total_score and other attributes are set properly.
    """
    env = CodeReviewEnvironment()
    
    # Should be initialized via _load_task(0) in __init__
    assert env._total_score == 0.0
    assert env._current_task == "bug_detection"
    assert env._current_snippet is not None

def test_environment_step():
    """
    Ensure the environment can process a step and return a valid observation.
    """
    env = CodeReviewEnvironment()
    
    # Simulate an agent action
    action = CodeReviewAction(
        task="bug_detection",
        verdict="I think there is a bug here.",
        confidence=0.8
    )
    
    # If the semantic judge isn't running (missing API keys), it should fallback to 0.01 safely
    obs = env.step(action)
    
    assert obs.task is not None
    assert isinstance(obs.score, float)
    assert obs.last_reward >= 0.01
