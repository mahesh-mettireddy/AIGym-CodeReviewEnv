import pytest
import asyncio
from server.my_first_env_environment import CodeReviewEnvironment
from models import CodeReviewAction

@pytest.mark.asyncio
async def test_env_initialization():
    env = CodeReviewEnvironment()
    obs = await env.reset_async()
    assert obs.task == "bug_detection"
    assert obs.done is False
    assert obs.score == 0.0

@pytest.mark.asyncio
async def test_env_full_loop():
    env = CodeReviewEnvironment()
    obs = await env.reset_async()
    
    total_steps = 0
    while not obs.done and total_steps < 20:
        action = CodeReviewAction(
            task=obs.task,
            verdict="Test verdict",
            confidence=0.5
        )
        obs = await env.step_async(action)
        total_steps += 1
    
    assert obs.done is True
    assert env._task_index == len(env.TASKS)

@pytest.mark.asyncio
async def test_multi_turn_refinement():
    env = CodeReviewEnvironment()
    obs = await env.reset_async()
    
    # First step with poor answer should trigger REFINEMENT
    action = CodeReviewAction(
        task=obs.task,
        verdict="I don't know",
        confidence=0.1
    )
    obs = await env.step_async(action)
    
    assert "REFINEMENT" in obs.instruction
    assert obs.done is False
    assert env._substep_index == 1

def test_normalization():
    env = CodeReviewEnvironment()
    assert env._normalize("Hello, World!") == "hello  world"
    assert env._normalize("  STrInG WITH   space ") == "string with   space"
