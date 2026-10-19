from steadytype_client.config import AppPaths, default_paths


def test_override_wins(monkeypatch, tmp_path):
    monkeypatch.setenv("STEADYTYPE_DATA_DIR", str(tmp_path))
    assert default_paths().data_dir == tmp_path


def test_database_sits_under_the_data_dir(tmp_path):
    paths = AppPaths(tmp_path)
    assert paths.database == tmp_path / "steadytype.db"
    assert paths.sounds.name == "sounds"
