from openenv.core.rubrics.base import Rubric
import asyncio
from .tasks import TASKS
from .judge_client import SemanticJudge
from .utils import normalize, get_line_match

class BaseCodeReviewGrader(Rubric):
    def __init__(self):
        super().__init__()
        self.judge = SemanticJudge()

    def _get_confidence_multiplier(self, confidence: float, is_correct: bool) -> float:
        """
        Adjust reward based on agent confidence.
        High Confidence + Wrong = Penalty.
        Low Confidence + Right = Smaller Reward (hesitancy).
        """
        # Ensure confidence is a float
        try:
            conf = float(confidence)
        except (TypeError, ValueError):
            conf = 0.5

        if is_correct:
            if conf >= 0.9: return 1.1  # Decisive Correctness Bonus
            if conf <= 0.4: return 0.7  # "Lucky guess" penalty
            return 1.0  # standard
        else:
            if conf >= 0.8: return -0.2 # "Overconfident Hallucination" penalty
            return 0.0
            
    async def forward(self, action: dict, observation: dict) -> float:
        # Implementation in subclasses
        return 0.0

class BugDetectionGrader(BaseCodeReviewGrader):
    async def forward(self, action: dict, observation: dict) -> float:
        v_raw = action.verdict if hasattr(action, 'verdict') else action.get('verdict', '')
        conf_raw = action.confidence if hasattr(action, 'confidence') else action.get('confidence', 0.5)
        o_code = observation.code_snippet if hasattr(observation, 'code_snippet') else observation.get('code_snippet', '')
        
        snippet_data = next((s for s in TASKS["bug_detection"]["snippets"] if s["code"].strip() == o_code.strip()), None)
        if not snippet_data: return 0.01

        # 1. Fast Path: Brittle Keyword Check (Baseline)
        verdict = normalize(v_raw)
        has_bug = snippet_data["has_bug"]
        said_yes = "yes" in verdict
        
        is_binary_correct = (has_bug and said_yes) or (not has_bug and "no" in verdict)
        
        if not is_binary_correct:
            return 0.01 + self._get_confidence_multiplier(conf_raw, False)

        # 2. Slow Path: Semantic Judge for Nuance
        try:
            result = await self.judge.evaluate(
                "bug_detection", 
                o_code, 
                str(v_raw), 
                snippet_data["explanation"]
            )
            base_reward = result.score
        except Exception:
            # Fallback for judge timeouts or service errors
            base_reward = 0.5 if is_binary_correct else 0.01
        
        # 3. Factor in confidence
        final_reward = base_reward * self._get_confidence_multiplier(conf_raw, True)
        
        # Rigidly respect manifest [0.01, 0.99] range
        return max(0.01, min(0.99, final_reward))

class CodeSmellGrader(BaseCodeReviewGrader):
    async def forward(self, action: dict, observation: dict) -> float:
        v_raw = action.verdict if hasattr(action, 'verdict') else action.get('verdict', '')
        conf_raw = action.confidence if hasattr(action, 'confidence') else action.get('confidence', 0.5)
        o_code = observation.code_snippet if hasattr(observation, 'code_snippet') else observation.get('code_snippet', '')
        
        snippet_data = next((s for s in TASKS["code_smell"]["snippets"] if s["code"].strip() == o_code.strip()), None)
        if not snippet_data: return 0.01

        try:
            result = await self.judge.evaluate(
                "code_smell", 
                o_code, 
                str(v_raw), 
                snippet_data["explanation"]
            )
            score = result.score
        except Exception:
            score = 0.5
        
        is_correct = score >= 0.7
        multiplier = self._get_confidence_multiplier(conf_raw, is_correct)
        
        return max(0.01, min(0.99, score * multiplier))

class ImprovementGrader(BaseCodeReviewGrader):
    async def forward(self, action: dict, observation: dict) -> float:
        v_raw = action.verdict if hasattr(action, 'verdict') else action.get('verdict', '')
        conf_raw = action.confidence if hasattr(action, 'confidence') else action.get('confidence', 0.5)
        o_code = observation.code_snippet if hasattr(observation, 'code_snippet') else observation.get('code_snippet', '')
        
        snippet_data = next((s for s in TASKS["improvement"]["snippets"] if s["code"].strip() == o_code.strip()), None)
        if not snippet_data: return 0.01

        try:
            result = await self.judge.evaluate(
                "improvement", 
                o_code, 
                str(v_raw), 
                snippet_data["explanation"]
            )
            score = result.score
        except Exception:
            score = 0.5
        
        is_correct = score >= 0.7
        multiplier = self._get_confidence_multiplier(conf_raw, is_correct)
        
        return max(0.01, min(0.99, score * multiplier))

class SecurityGrader(BaseCodeReviewGrader):
    async def forward(self, action: dict, observation: dict) -> float:
        v_raw = action.verdict if hasattr(action, 'verdict') else action.get('verdict', '')
        conf_raw = action.confidence if hasattr(action, 'confidence') else action.get('confidence', 0.5)
        o_code = observation.code_snippet if hasattr(observation, 'code_snippet') else observation.get('code_snippet', '')
        
        snippet_data = next((s for s in TASKS["security_vulnerability"]["snippets"] if s["code"].strip() == o_code.strip()), None)
        if not snippet_data: return 0.01

        try:
            result = await self.judge.evaluate(
                "security_vulnerability", 
                o_code, 
                str(v_raw), 
                snippet_data["explanation"]
            )
            score = result.score
        except Exception:
            score = 0.5
        
        is_correct = score >= 0.7
        multiplier = self._get_confidence_multiplier(conf_raw, is_correct)
        
        return max(0.01, min(0.99, score * multiplier))
