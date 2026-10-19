"""PyInstaller entry point: absolute import, plus a crash log for windowed builds."""

from __future__ import annotations

import faulthandler
import sys
import traceback
from pathlib import Path

from steadytype_client.app import main


def _log_path() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "SteadyType"
    elif sys.platform == "win32":
        base = Path.home() / "AppData" / "Local" / "SteadyType"
    else:
        base = Path.home() / ".local" / "share" / "steadytype"
    base.mkdir(parents=True, exist_ok=True)
    return base / "crash.log"


if __name__ == "__main__":
    log = _log_path()
    with open(log, "a", encoding="utf-8") as handle:
        faulthandler.enable(file=handle)
        try:
            code = main()
        except SystemExit:
            raise
        except BaseException:
            handle.write("\n--- crash ---\n")
            handle.write(traceback.format_exc())
            handle.flush()
            raise
    raise SystemExit(code)
