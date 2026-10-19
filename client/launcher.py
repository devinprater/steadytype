"""PyInstaller entry point: absolute import, because a frozen script has no package."""

from steadytype_client.app import main

if __name__ == "__main__":
    raise SystemExit(main())
