"""
Unit tests for requirements.txt

requirements.txt is what `meta-notes init` installs into a notes root's
.venv. It is generated from uv.lock, so a lock change must come with a
regenerated file:

    uv export --no-dev --no-hashes --no-emit-project --no-header --no-annotate -o requirements.txt
"""

import shutil
import subprocess
from pathlib import Path

import pytest

repo_dir = Path(__file__).parent.parent.parent

EXPORT = ['uv', 'export', '--locked', '--no-dev', '--no-hashes',
          '--no-emit-project', '--no-header', '--no-annotate']


@pytest.mark.skipif(shutil.which('uv') is None, reason='uv not installed')
def test_requirements_txt_matches_uv_lock():
    result = subprocess.run(EXPORT, cwd=repo_dir, capture_output=True,
                            text=True)
    assert result.returncode == 0, result.stderr
    assert (repo_dir / 'requirements.txt').read_text() == result.stdout, \
        'requirements.txt is stale; regenerate it with: ' + ' '.join(c for c in EXPORT if c != '--locked') + ' -o requirements.txt'
