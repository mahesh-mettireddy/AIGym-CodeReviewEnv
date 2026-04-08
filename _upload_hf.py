"""Upload to HuggingFace Spaces - Fixed version."""
import os
import sys
import shutil
import tempfile
from pathlib import Path
from huggingface_hub import HfApi

sys.stdout.reconfigure(encoding='utf-8')

token = os.environ['HF_TOKEN']
api = HfApi(token=token)
repo_id = 'mahesh16/code-review-env'
env_dir = Path(r'C:\Users\Admin\PycharmProjects\openenv-hackathon\my_first_env')

with tempfile.TemporaryDirectory() as tmpdir:
    staging = Path(tmpdir) / 'staging'

    def ignore(d, names):
        return {n for n in names if n in ('__pycache__', '.git', '.idea', '_upload_hf.py')}

    shutil.copytree(env_dir, staging, ignore=ignore)

    # Move Dockerfile from server/ to root
    src_df = staging / 'server' / 'Dockerfile'
    dst_df = staging / 'Dockerfile'
    if src_df.exists() and not dst_df.exists():
        shutil.move(str(src_df), str(dst_df))
        print('Moved Dockerfile to root', flush=True)

    # Rewrite Dockerfile cleanly with ENABLE_WEB_INTERFACE before CMD
    dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \\
    apt-get install -y --no-install-recommends curl && \\
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY server/requirements.txt /app/server/requirements.txt
RUN pip install --no-cache-dir -r server/requirements.txt

# Copy all project files
COPY . /app

# Set PYTHONPATH so imports work correctly
ENV PYTHONPATH="/app:$PYTHONPATH"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:7860/health || exit 1

# Expose port 7860
EXPOSE 7860

# Enable web interface
ENV ENABLE_WEB_INTERFACE=true

# Run the FastAPI server
CMD ["python", "-c", "import uvicorn; uvicorn.run('server.app:app', host='0.0.0.0', port=7860)"]
"""
    dst_df.write_text(dockerfile_content)
    print('Wrote clean Dockerfile', flush=True)

    # Write README with HF frontmatter
    readme = staging / 'README.md'
    if readme.exists():
        content = readme.read_text(encoding='utf-8')
        if not content.startswith('---'):
            frontmatter = (
                "---\n"
                "title: Code Review Env\n"
                "emoji: \U0001f50d\n"
                "colorFrom: blue\n"
                "colorTo: purple\n"
                "sdk: docker\n"
                "pinned: false\n"
                "app_port: 7860\n"
                "base_path: /web\n"
                "tags:\n"
                "  - openenv\n"
                "---\n\n"
            )
            readme.write_text(frontmatter + content, encoding='utf-8')
            print('Added HF frontmatter to README', flush=True)

    print('Uploading...', flush=True)
    api.upload_folder(
        folder_path=str(staging),
        repo_id=repo_id,
        repo_type='space',
        ignore_patterns=['__pycache__', '*.pyc', '.git*'],
    )
    print('Upload complete!', flush=True)
    print(f'Space URL: https://huggingface.co/spaces/{repo_id}', flush=True)
