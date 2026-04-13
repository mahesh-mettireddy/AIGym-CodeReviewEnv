import re

def normalize(text: str) -> str:
    """Normalize text for consistent comparison."""
    return re.sub(r'[^\w\s]', ' ', str(text).lower()).strip()

def get_line_match(text: str, target_line: int) -> bool:
    """Check if a specific line number is mentioned in the text."""
    if target_line is None: 
        return True
    # Look for patterns like 'line 4', 'line: 4', 'line#4'
    found_lines = re.findall(r'line\s*(?::|#)?\s*(\d+)', str(text).lower())
    return any(int(l) == target_line for l in found_lines)
