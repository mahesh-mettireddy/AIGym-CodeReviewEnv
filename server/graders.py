from openenv.core.rubrics.base import Rubric
import re

# We import the TASKS from our standalone tasks file
from .tasks import TASKS

def normalize(text: str) -> str:
    return re.sub(r'[^\w\s]', ' ', str(text).lower()).strip()

def get_line_match(text: str, target_line: int) -> bool:
    if target_line is None: return True
    found_lines = re.findall(r'line\s*(?::|#)?\s*(\d+)', text.lower())
    return any(int(l) == target_line for l in found_lines)

class BugDetectionGrader(Rubric):
    def forward(self, action: dict, observation: dict) -> float:
        # Support both Pydantic objects and raw dicts
        v_raw = action.verdict if hasattr(action, 'verdict') else action.get('verdict', '')
        verdict = normalize(v_raw)
        
        o_code = observation.code_snippet if hasattr(observation, 'code_snippet') else observation.get('code_snippet', '')
        
        snippet_data = next((s for s in TASKS["bug_detection"]["snippets"] if s["code"].strip() == o_code.strip()), None)
        if not snippet_data: return 0.01

        has_bug = snippet_data["has_bug"]
        has_correct_line = get_line_match(str(v_raw), snippet_data["target_line"])
        said_yes = "yes" in verdict
        said_no = "no" in verdict

        if has_bug and said_yes:
            matches = sum(1 for kw in snippet_data["keywords"] if kw in verdict)
            if has_correct_line:
                if matches >= 2: return 0.99
                return 0.75
            return 0.40
        elif not has_bug and said_no:
            return 0.99
        elif has_bug and said_no:
            return 0.01
        elif not has_bug and said_yes:
            return 0.01
        return 0.1

class CodeSmellGrader(Rubric):
    def forward(self, action: dict, observation: dict) -> float:
        v_raw = action.verdict if hasattr(action, 'verdict') else action.get('verdict', '')
        verdict = normalize(v_raw)
        o_code = observation.code_snippet if hasattr(observation, 'code_snippet') else observation.get('code_snippet', '')
        
        snippet_data = next((s for s in TASKS["code_smell"]["snippets"] if s["code"].strip() == o_code.strip()), None)
        if not snippet_data: return 0.01

        has_correct_line = get_line_match(str(v_raw), snippet_data["target_line"])
        matches = sum(1 for smell in snippet_data["smells"] if smell in verdict)
        
        if has_correct_line:
            if matches >= 2: return 0.99
            if matches == 1: return 0.75
        if matches >= 1: return 0.40
        return 0.01

class ImprovementGrader(Rubric):
    def forward(self, action: dict, observation: dict) -> float:
        v_raw = action.verdict if hasattr(action, 'verdict') else action.get('verdict', '')
        verdict = normalize(v_raw)
        o_code = observation.code_snippet if hasattr(observation, 'code_snippet') else observation.get('code_snippet', '')
        
        snippet_data = next((s for s in TASKS["improvement"]["snippets"] if s["code"].strip() == o_code.strip()), None)
        if not snippet_data: return 0.01

        has_correct_line = get_line_match(str(v_raw), snippet_data["target_line"])
        matches = sum(1 for imp in snippet_data["improvements"] if imp in verdict)
        
        if has_correct_line:
            if matches >= 2: return 0.99
            if matches == 1: return 0.80
        if matches >= 1: return 0.40
        return 0.01

class SecurityGrader(Rubric):
    def forward(self, action: dict, observation: dict) -> float:
        v_raw = action.verdict if hasattr(action, 'verdict') else action.get('verdict', '')
        verdict = normalize(v_raw)
        o_code = observation.code_snippet if hasattr(observation, 'code_snippet') else observation.get('code_snippet', '')
        
        snippet_data = next((s for s in TASKS["security_vulnerability"]["snippets"] if s["code"].strip() == o_code.strip()), None)
        if not snippet_data: return 0.01

        has_correct_line = get_line_match(str(v_raw), snippet_data["target_line"])
        matches = sum(1 for flaw in snippet_data["flaws"] if flaw in verdict)
        
        if has_correct_line:
            if matches >= 2: return 0.99
            if matches == 1: return 0.85
        if matches >= 1: return 0.40
        return 0.01
