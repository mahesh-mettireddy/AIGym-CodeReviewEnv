from openenv.core.rubrics.base import Rubric
import re

# We import the TASKS from our environment file to look up snippet answers
from server.my_first_env_environment import TASKS

def normalize(text: str) -> str:
    return re.sub(r'[^\w\s]', ' ', str(text).lower()).strip()

class BugDetectionGrader(Rubric):
    def forward(self, action: dict, observation: dict) -> float:
        # Pydantic models might be passed as dicts or objects depending on evaluator hook
        verdict = normalize(getattr(action, 'verdict', action.get('verdict', '')) if action else '')
        code_snippet = getattr(observation, 'code_snippet', observation.get('code_snippet', '')) if observation else ''
        
        # Find snippet
        snippet_data = next((s for s in TASKS["bug_detection"]["snippets"] if s["code"].strip() == code_snippet.strip()), None)
        if not snippet_data:
            return 0.01

        has_bug = snippet_data["has_bug"]
        said_yes = "yes" in verdict
        said_no = "no" in verdict

        if has_bug and said_yes:
            for kw in snippet_data["keywords"]:
                if kw in verdict:
                    return 0.99
            return 0.6
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

        for smell in snippet_data["smells"]:
            if smell in verdict:
                return 0.99
        
        if len(verdict) > 20:
            return 0.3
        return 0.01

class ImprovementGrader(Rubric):
    def forward(self, action: dict, observation: dict) -> float:
        verdict = normalize(getattr(action, 'verdict', action.get('verdict', '')) if action else '')
        code_snippet = getattr(observation, 'code_snippet', observation.get('code_snippet', '')) if observation else ''
        
        snippet_data = next((s for s in TASKS["improvement"]["snippets"] if s["code"].strip() == code_snippet.strip()), None)
        if not snippet_data:
            return 0.01

        for imp in snippet_data["improvements"]:
            if imp in verdict:
                return 0.99
        
        if len(verdict) > 30:
            return 0.4
        return 0.01
