# PyInstaller one-folder build. Run from the client directory:
#   pyinstaller steadytype.spec
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs

repo = Path(SPECPATH).resolve().parent

prism_datas, prism_binaries, prism_hidden = collect_all("prism")

a = Analysis(
    ["launcher.py"],
    pathex=["src"],
    binaries=collect_dynamic_libs("prism") + prism_binaries,
    datas=[
        (str(repo / "assets" / "sounds"), "assets/sounds"),
        (str(repo / "content"), "content"),
    ] + prism_datas,
    hiddenimports=["prism", "prism._prism_cffi", "_cffi_backend", "wx", "Quartz", "AppKit", "objc"] + prism_hidden,
    module_collection_mode={"prism": "py"},
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
