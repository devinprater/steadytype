# PyInstaller one-folder build. Run from the client directory:
#   pyinstaller steadytype.spec
from pathlib import Path

from PyInstaller.utils.hooks import collect_dynamic_libs

repo = Path(SPECPATH).resolve().parent

a = Analysis(
    ["launcher.py"],
    pathex=["src"],
    binaries=collect_dynamic_libs("prism"),
    datas=[
        (str(repo / "assets" / "sounds"), "assets/sounds"),
        (str(repo / "content"), "content"),
    ],
    hiddenimports=["prism", "prism._prism_cffi", "wx", "Quartz", "objc"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="SteadyType",
          console=False, icon=None)
coll = COLLECT(exe, a.binaries, a.datas, name="SteadyType")

import sys as _sys

if _sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="SteadyType.app",
        bundle_identifier="org.devinprater.steadytype",
        info_plist={
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "11.0",
            "NSHumanReadableCopyright": "GPL-3.0-or-later",
        },
    )
