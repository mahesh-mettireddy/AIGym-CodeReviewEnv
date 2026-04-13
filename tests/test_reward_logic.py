from unittest.mock import MagicMock, patch
import pytest

# Mock SemanticJudge BEFORE importing graders
with patch('server.judge_client.SemanticJudge'):
    from server.graders import BugDetectionGrader

@pytest.fixture
def mock_grader():
    with patch('server.judge_client.SemanticJudge'):
        grader = BugDetectionGrader()
        return grader

@pytest.mark.asyncio
async def test_confidence_multipliers(mock_grader):
    # Correct (score=1.0) + High Confidence (0.95) -> 1.1x
    # Signature: _get_confidence_multiplier(confidence, is_correct)
    mult_high_correct = mock_grader._get_confidence_multiplier(0.95, True)
    assert mult_high_correct > 1.0
    
    # Correct (score=1.0) + Low Confidence (0.4) -> 0.7x
    mult_low_correct = mock_grader._get_confidence_multiplier(0.4, True)
    assert mult_low_correct < 1.0
    
    # Incorrect + High Confidence (0.95) -> -0.2 penalty
    mult_high_incorrect = mock_grader._get_confidence_multiplier(0.95, False)
    assert mult_high_incorrect < 0

@pytest.mark.asyncio
async def test_normalization():
    from server.utils import normalize
    assert normalize("Race Condition!!!") == "race condition"
    assert normalize("SQL Injection") == "sql injection"

@pytest.mark.asyncio
async def test_normalization():
    from server.utils import normalize
    assert normalize("Race Condition!!!") == "race condition"
    assert normalize("SQL Injection") == "sql injection"
