import subprocess
import sys

from config_service import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "config_service", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
