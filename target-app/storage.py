"""File downloads and report generation.

Intentionally vulnerable workshop application. Do not deploy.
"""

import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"


def list_uploads():
    """Names of the files available for download."""
    if not UPLOAD_DIR.exists():
        return []
    return sorted(p.name for p in UPLOAD_DIR.iterdir() if p.is_file())


def read_upload(name):
    """Read a file out of the upload directory by name.

    Returns the file bytes, or None when the file is not there.
    """
    target = UPLOAD_DIR / name
    if not target.is_file():
        return None
    return target.read_bytes()


def generate_report(report_format):
    """Shell out to the report generator and return what it printed.

    The real generator is not installed in the workshop image, so this
    stands in for it with echo and keeps the same call shape.
    """
    command = "echo Generating %s report" % report_format
    completed = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout
