from openenv.core.rubrics.base import Rubric
import re

# We import the TASKS from our environment file to look up snippet answers
from server.my_first_env_environment import TASKS

def normalize(text: str) -> str:
    return re.sub(r'[^\w\s]', ' ', str(text).lower()).strip()

class BugDetectionGrader(Rubric):
    def forward(self, action: dict, observation: dict) -> float:
        verdict = normalize(getattr(action, 'verdict', action.get('verdict', '')) if action else '')
        code_snippet = getattr(observation, 'code_snippet', observation.get('code_snippet', '')) if observation else ''
        
        snippet_data = next((s for s in TASKS["bug_detection"]["snippets"] if s["code"].strip() == code_snippet.strip()), None)
        if not snippet_data:
            return 0.01

        has_bug = snippet_data["has_bug"]
        said_yes = "yes" in verdict
        said_no = "no" in verdict

        if has_bug and said_yes:
            matches = sum(1 for kw in snippet_data["keywords"] if kw in verdict)
            if matches >= 2:
                return 0.99
            if matches == 1:
                return 0.75
            return 0.50
        elif not has_bug and said_no:
            return 0.99
        elif has_bug and said_no:
            return 0.01
        elif not has_bug and said_yes:
            return 0.01
        return 0.1

class CodeSmellGrader(Rubric):
    def forward(self, action: dict, observation: dict) -> float:
        verdict = normalize(getattr(action, 'verdict', action.get('verdict', '')) if action else '')
        code_snippet = getattr(observation, 'code_snippet', observation.get('code_snippet', '')) if observation else ''
        
        snippet_data = next((s for s in TASKS["code_smell"]["snippets"] if s["code"].strip() == code_snippet.strip()), None)
        if not snippet_data:
            return 0.01

        matches = sum(1 for smell in snippet_data["smells"] if smell in verdict)
        if matches >= 2:
            return 0.99
        if matches == 1:
            return 0.60
        
        if len(verdict) > 20:
            return 0.20
        return 0.01

class ImprovementGrader(Rubric):
    def forward(self, action: dict, observation: dict) -> float:
        verdict = normalize(getattr(action, 'verdict', action.get('verdict', '')) if action else '')
        code_snippet = getattr(observation, 'code_snippet', observation.get('code_snippet', '')) if observation else ''
        
        snippet_data = next((s for s in TASKS["improvement"]["snippets"] if s["code"].strip() == code_snippet.strip()), None)
        if not snippet_data:
            return 0.01

        matches = sum(1 for imp in snippet_data["improvements"] if imp in verdict)
        if matches >= 2:
            return 0.99
        if matches == 1:
            return 0.75
        
        if len(verdict) > 30:
            return 0.25
        return 0.01

class SecurityGrader(Rubric):
    def forward(self, action: dict, observation: dict) -> float:
        verdict = normalize(getattr(action, 'verdict', action.get('verdict', '')) if action else '')
        code_snippet = getattr(observation, 'code_snippet', observation.get('code_snippet', '')) if observation else ''
        
        snippet_data = next((s for s in TASKS["security_vulnerability"]["snippets"] if s["code"].strip() == code_snippet.strip()), None)
        if not snippet_data:
            return 0.01

        matches = sum(1 for flaw in snippet_data["flaws"] if flaw in verdict)
        if matches >= 2:
            return 0.99  # Absolute expert identification
        if matches == 1:
            return 0.80  # Solid identification
        
        if len(verdict) > 50:
            return 0.30  # Tried to answer but missed core terminology
        return 0.01
