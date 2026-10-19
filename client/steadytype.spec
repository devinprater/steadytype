# PyInstaller one-folder build. Run from the client directory:
#   pyinstaller steadytype.spec
from pathlib import Path

repo = Path(SPECPATH).resolve().parent

a = Analysis(
    ["src/steadytype_client/__main__.py"],
    pathex=["src"],
    binaries=[],
    datas=[
        (str(repo.parent / "assets" / "sounds"), "assets/sounds"),
        (str(repo.parent / "content"), "content"),
    ],
    hiddenimports=["prism", "prism._prism_cffi", "wx"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="SteadyType",
          console=False, icon=None)
coll = COLLECT(exe, a.binaries, a.datas, name="SteadyType")
