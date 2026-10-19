import subprocess
import sys


def test_version_flag():
    result = subprocess.run([sys.executable, "-m", "steadytype_client", "--version"],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "steadytype-client 0.1.0" in result.stdout
